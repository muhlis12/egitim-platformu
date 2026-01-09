from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from courses.models import Course, Enrollment
from content.models import LessonProgress

@login_required
def dashboard(request):
    user = request.user

    # Admin / Teacher / Student kurs listesi
    if user.role == "ADMIN":
        courses = Course.objects.all().order_by("-id")
    elif user.role == "TEACHER":
        courses = Course.objects.filter(owner=user).order_by("-id")
    else:
        courses = Course.objects.filter(enrollments__user=user).order_by("-id")

    progress_by_course = {}
    continue_lesson_by_course = {}

    if user.role == "STUDENT":
        # toplam ders sayıları (kurs bazlı)
        total_by_course = {c.id: c.lessons.count() for c in courses}

        # tamamlanan ders sayıları (kurs bazlı)
        done_qs = (
            LessonProgress.objects
            .filter(user=user, completed=True, lesson__course__in=courses)
            .values("lesson__course_id")
            .annotate(done=Count("id"))
        )
        done_by_course = {row["lesson__course_id"]: row["done"] for row in done_qs}

        # Continue: ilk tamamlanmamış ders
        for c in courses:
            total = total_by_course.get(c.id, 0)
            done = done_by_course.get(c.id, 0)
            percent = int((done / total) * 100) if total else 0

            progress_by_course[c.id] = {
                "done": done,
                "total": total,
                "percent": percent,
                "remaining": max(0, total - done),
            }

            # ilk tamamlanmamış dersi bul
            completed_ids = set(
                LessonProgress.objects
                .filter(user=user, lesson__course=c, completed=True)
                .values_list("lesson_id", flat=True)
            )

            next_lesson = (
                c.lessons
                .exclude(id__in=completed_ids)
                .order_by("order", "id")
                .first()
            )

            # hepsi tamamlandıysa ilk dersi göster
            if not next_lesson:
                next_lesson = c.lessons.order_by("order", "id").first()

            continue_lesson_by_course[c.id] = next_lesson

    return render(request, "dashboard/dashboard.html", {
        "courses": courses,
        "progress_by_course": progress_by_course,
        "continue_lesson_by_course": continue_lesson_by_course,
        "role": user.role,
    })
