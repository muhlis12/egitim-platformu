from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import get_user_model

from courses.models import Enrollment
from content.models import Lesson, LessonProgress
from .models import Grade, Subject, TopicTemplate, DailyPlan, DailyPlanItem
from .forms import DailyPlanAssignForm

User = get_user_model()


# ---------------------------
# Lessons
# ---------------------------

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user = request.user

    # erişim kontrol
    if user.role == "ADMIN":
        allowed = True
    elif user.role == "TEACHER":
        allowed = (lesson.course.owner_id == user.id)
    else:
        allowed = Enrollment.objects.filter(course=lesson.course, user=user).exists()

    if not allowed:
        return render(request, "courses/forbidden.html", status=403)

    prog, _ = LessonProgress.objects.get_or_create(lesson=lesson, user=user)
    return render(request, "content/lesson_detail.html", {"lesson": lesson, "prog": prog})


@login_required
def lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user = request.user

    # sadece enrolled student tamamlasın
    if user.role != "STUDENT":
        return redirect("lesson_detail", lesson_id=lesson_id)

    if not Enrollment.objects.filter(course=lesson.course, user=user).exists():
        return render(request, "courses/forbidden.html", status=403)

    prog, _ = LessonProgress.objects.get_or_create(lesson=lesson, user=user)
    prog.completed = True
    prog.completed_at = timezone.now()
    prog.save()
    return redirect("lesson_detail", lesson_id=lesson_id)


# ---------------------------
# Topics UI
# ---------------------------

@login_required
def topics_home(request):
    grades = Grade.objects.order_by("number")
    subjects = Subject.objects.order_by("name")
    return render(request, "content/topics_home.html", {
        "grades": grades,
        "subjects": subjects,
    })


@login_required
def topic_page(request, topic_id: int):
    topic = get_object_or_404(TopicTemplate, id=topic_id)
    return render(request, "content/topic_page.html", {"topic": topic})


# ---------------------------
# Daily Plan UI
# ---------------------------

@login_required
def daily_plan_page(request):
    return render(request, "content/daily_plan.html")


def _teacher_or_admin_required(user):
    return getattr(user, "role", None) in ("TEACHER", "ADMIN")


@login_required
def daily_plan_assign(request):
    """
    Teacher/Admin: günlük plana görev ekler.
    Form artık username değil, student dropdown kullanıyor.
    """
    if not _teacher_or_admin_required(request.user):
        return redirect("/dashboard/")

    if request.method == "POST":
        form = DailyPlanAssignForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data["student"]   # ✅ username yerine student
            date = form.cleaned_data["date"]
            typ = form.cleaned_data["type"]
            title = form.cleaned_data["title"]
            topic = form.cleaned_data["topic"]

            # güvenlik: sadece student rolü
            if getattr(student, "role", None) != "STUDENT":
                messages.error(request, "Seçilen kullanıcı STUDENT değil.")
                return redirect("daily_plan_assign")

            plan, _ = DailyPlan.objects.get_or_create(user=student, date=date)

            last_order = plan.items.order_by("-order").values_list("order", flat=True).first() or 0
            DailyPlanItem.objects.create(
                plan=plan,
                type=typ,
                title=title,
                topic=topic,
                order=last_order + 1
            )

            messages.success(request, f"{student.username} için {date} tarihli plana görev eklendi.")
            return redirect("daily_plan_assign")
    else:
        form = DailyPlanAssignForm()

    return render(request, "content/daily_plan_assign.html", {"form": form})
