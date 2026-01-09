from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from courses.models import Course, Enrollment
from payments.models import PurchaseRequest
from content.models import LessonProgress


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user

    # Öğrenci kursa kayıtlı mı?
    if user.role == "STUDENT":
        if not Enrollment.objects.filter(course=course, user=user).exists():
            return render(request, "courses/forbidden.html", status=403)

        # Ücretli kurs kontrolü
        if getattr(course, "is_paid", False):
            ok = PurchaseRequest.objects.filter(
                user=user,
                course=course,
                status="APPROVED"
            ).exists()
            if not ok:
                return render(request, "courses/paywall.html", {"course": course}, status=402)

    lessons = course.lessons.order_by("order")

    # ===== Öğrenci ilerleme =====
    progress_map = {}
    completed_ids = set()
    completed_count = 0
    total_lessons = lessons.count()

    if user.role == "STUDENT":
        qs = LessonProgress.objects.filter(user=user, lesson__course=course)
        progress_map = {p.lesson_id: p.completed for p in qs}
        completed_ids = {lid for lid, done in progress_map.items() if done}
        completed_count = len(completed_ids)

    percent = int((completed_count / total_lessons) * 100) if total_lessons else 0
    
        # ✅ Devam Et: ilk tamamlanmamış ders
    next_lesson = None
    if user.role == "STUDENT":
        next_lesson = (
            lessons.exclude(id__in=completed_ids)
            .order_by("order", "id")
            .first()
        )
        # hepsi bittiyse ilk dersi göster
        if not next_lesson:
            next_lesson = lessons.order_by("order", "id").first()

    return render(request, "courses/course_detail.html", {
        "course": course,
        "lessons": lessons,
        "progress_map": progress_map,        # istersen kalsın
        "completed_ids": completed_ids,      # template tik için
        "completed_count": completed_count,
        "total_lessons": total_lessons,
        "percent": percent,
        "next_lesson": next_lesson,
    })
