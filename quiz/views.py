from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from courses.models import Enrollment
from .models import Exam, Attempt, Answer


@login_required
def exam_start(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    user = request.user

    # Sadece öğrenci sınava girebilir
    if user.role != "STUDENT":
        return redirect(f"/courses/{exam.course.id}/")

    # Kursa kayıtlı değilse yasak
    if not Enrollment.objects.filter(course=exam.course, user=user).exists():
        return render(request, "courses/forbidden.html", status=403)

    # Attempt oluştur + deadline ayarla
    attempt = Attempt.objects.create(
        exam=exam,
        user=user,
        deadline_at=timezone.now() + timedelta(minutes=exam.duration_minutes),
    )

    # Her soru için boş answer oluştur
    for q in exam.questions.all():
        Answer.objects.create(attempt=attempt, question=q, selected=None)

    return redirect("exam_take", attempt_id=attempt.id)


@login_required
def exam_take(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id)
    user = request.user

    # Başkasının attempt'ine erişemez
    if attempt.user_id != user.id:
        return render(request, "courses/forbidden.html", status=403)

    # Süre dolduysa otomatik bitir (GET/POST fark etmez)
    if attempt.finished_at is None and attempt.deadline_at and timezone.now() >= attempt.deadline_at:
        return redirect("exam_finish", attempt_id=attempt.id)

    if request.method == "POST":
        # POST anında da tekrar kontrol (hileye kapalı)
        if attempt.deadline_at and timezone.now() >= attempt.deadline_at:
            return redirect("exam_finish", attempt_id=attempt.id)

        # Seçimleri kaydet
        for ans in attempt.answers.select_related("question").all():
            key = f"q_{ans.question.id}"
            sel = request.POST.get(key)
            if sel in ("A", "B", "C", "D"):
                ans.selected = sel
                ans.save()

        return redirect("exam_finish", attempt_id=attempt.id)

    answers = attempt.answers.select_related("question").all()
    return render(request, "quiz/exam_take.html", {"attempt": attempt, "answers": answers})


@login_required
def exam_finish(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id)
    user = request.user

    if attempt.user_id != user.id:
        return render(request, "courses/forbidden.html", status=403)

    # Daha önce bitmişse tekrar hesaplama yapma
    if attempt.finished_at is not None:
        return render(request, "quiz/exam_result.html", {"attempt": attempt})

    # Puan hesapla
    total = attempt.answers.count()
    correct = 0
    wrong = 0

    for ans in attempt.answers.select_related("question").all():
        if ans.selected is None:
            continue
        if ans.selected == ans.question.correct:
            correct += 1
        else:
            wrong += 1

    score = (correct / total) * 100 if total > 0 else 0

    attempt.correct_count = correct
    attempt.wrong_count = wrong
    attempt.score = round(score, 2)
    attempt.finished_at = timezone.now()
    attempt.save()

    return render(request, "quiz/exam_result.html", {"attempt": attempt})
