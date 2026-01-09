from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from content.models import Lesson, LessonProgress
from courses.models import Enrollment

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
