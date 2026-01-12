from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.utils import admin_required
from courses.models import Course, Enrollment
from content.models import Lesson, TopicTemplate
from parents.models import ParentStudent

from .forms import (
    CourseCreateForm, AssignTeacherForm, EnrollStudentForm, ReadyLessonsForm,
    AdminUserCreateForm, AdminUserEditForm,
    StudentWithParentCreateForm,
)

User = get_user_model()


# ---------------------------
# Courses
# ---------------------------

@login_required
@admin_required
def manager_courses(request):
    courses = Course.objects.all().order_by("-id")
    return render(request, "manager/courses.html", {"courses": courses})


@login_required
@admin_required
def manager_course_new(request):
    if request.method == "POST":
        form = CourseCreateForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.owner = request.user  # NOT NULL fix
            course.save()
            messages.success(request, "Kurs oluşturuldu. İstersen şimdi öğretmen atayabilirsin.")
            return redirect("manager_courses")
    else:
        form = CourseCreateForm()

    return render(request, "manager/course_new.html", {"form": form})


@login_required
@admin_required
def manager_assign_teacher(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        form = AssignTeacherForm(request.POST)
        if form.is_valid():
            teacher = form.cleaned_data["teacher"]
            course.owner = teacher
            course.save()
            messages.success(request, f"{teacher.username} öğretmen olarak atandı.")
            return redirect("manager_courses")
    else:
        form = AssignTeacherForm()

    return render(request, "manager/assign_teacher.html", {"course": course, "form": form})


@login_required
@admin_required
def manager_course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    form = EnrollStudentForm(request.POST or None)

    if request.method == "POST" and "add_student" in request.POST:
        if form.is_valid():
            uname = form.cleaned_data["username"].strip()
            try:
                student = User.objects.get(username=uname, role="STUDENT")
            except User.DoesNotExist:
                messages.error(request, "Öğrenci bulunamadı veya rol STUDENT değil.")
                return redirect("manager_course_students", course_id=course.id)

            Enrollment.objects.get_or_create(course=course, user=student)
            messages.success(request, f"{student.username} kursa eklendi.")
            return redirect("manager_course_students", course_id=course.id)

    if request.method == "POST" and "remove_student" in request.POST:
        enrollment_id = request.POST.get("enrollment_id")
        Enrollment.objects.filter(id=enrollment_id, course=course).delete()
        messages.success(request, "Öğrenci kurstan çıkarıldı.")
        return redirect("manager_course_students", course_id=course.id)

    enrollments = Enrollment.objects.filter(course=course).select_related("user").order_by("user__username")

    return render(request, "manager/course_students.html", {
        "course": course,
        "form": form,
        "enrollments": enrollments,
    })


@login_required
@admin_required
def manager_ready_lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    form = ReadyLessonsForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        grade = form.cleaned_data["grade"]
        subject = form.cleaned_data["subject"]

        parents = TopicTemplate.objects.filter(
            grade=grade, subject=subject, parent__isnull=True
        ).order_by("order", "id")

        created = 0
        for p in parents:
            _, created_parent = Lesson.objects.get_or_create(
                course=course,
                title=p.title,
                defaults={"order": p.order * 100},
            )
            if created_parent:
                created += 1

            for c in p.children.all().order_by("order", "id"):
                child_title = f"— {c.title}"
                _, created_child = Lesson.objects.get_or_create(
                    course=course,
                    title=child_title,
                    defaults={"order": (p.order * 100) + c.order},
                )
                if created_child:
                    created += 1

        course.grade = grade.number
        course.save()

        messages.success(request, f"{grade.number}. sınıf {subject.name} için {created} ders eklendi.")
        return redirect("manager_courses")

    return render(request, "manager/ready_lessons.html", {"course": course, "form": form})


# ---------------------------
# Users (Admin)
# ---------------------------

@login_required
@admin_required
def manager_users(request):
    q = (request.GET.get("q") or "").strip()
    role = (request.GET.get("role") or "").strip().upper()

    qs = User.objects.all().order_by("-id")

    if role in ("STUDENT", "TEACHER", "ADMIN", "PARENT"):
        qs = qs.filter(role=role)

    if q:
        qs = qs.filter(username__icontains=q)

    return render(request, "manager/users.html", {"users": qs[:200], "q": q, "role": role})


@login_required
@admin_required
def manager_user_new(request):
    if request.method == "POST":
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Kullanıcı oluşturuldu.")
            return redirect("manager_users")
    else:
        form = AdminUserCreateForm()

    return render(request, "manager/user_new.html", {"form": form})


@login_required
@admin_required
def manager_user_edit(request, user_id: int):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Kullanıcı güncellendi.")
            return redirect("manager_users")
    else:
        form = AdminUserEditForm(instance=user)

    return render(request, "manager/user_edit.html", {"form": form, "u": user})


# ---------------------------
# PRO: Student + Parent create + link
# ---------------------------

@login_required
@admin_required
def manager_student_new_with_parent(request):
    """
    Tek ekranda Öğrenci + Veli oluşturur ve ParentStudent ile eşleştirir.
    """
    if request.method == "POST":
        form = StudentWithParentCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Student
                su = form.cleaned_data["student_username"].strip()
                sp = form.cleaned_data["student_password"]

                student = User(
                    username=su,
                    first_name=form.cleaned_data.get("student_first_name", ""),
                    last_name=form.cleaned_data.get("student_last_name", ""),
                    role="STUDENT",
                )
                student.set_password(sp)
                student.save()

                # Parent
                pu = form.cleaned_data["parent_username"].strip()
                pp = form.cleaned_data["parent_password"]

                parent = User(
                    username=pu,
                    first_name=form.cleaned_data.get("parent_first_name", ""),
                    last_name=form.cleaned_data.get("parent_last_name", ""),
                    role="PARENT",
                )
                parent.set_password(pp)
                parent.save()

                # Link
                ParentStudent.objects.get_or_create(parent=parent, student=student)

            messages.success(request, "Öğrenci + Veli oluşturuldu ve eşleştirildi ✅")
            return redirect("manager_users")
    else:
        form = StudentWithParentCreateForm()

    return render(request, "manager/student_new_with_parent.html", {"form": form})
