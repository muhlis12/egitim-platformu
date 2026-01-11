from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    TopicTemplate, TopicContent, TopicQuestion, StudentTopicProgress, Grade, Subject,
    ReviewItem, ReviewAttempt,
    DailyPlan, DailyPlanItem
)
from .services import generate_daily_plan


# ---------------------------
# Helpers
# ---------------------------

def _node(t):
    return {"id": t.id, "title": t.title, "order": t.order, "children": []}


def _next_days(stage: int) -> int:
    schedule = [1, 3, 7, 14]
    return schedule[stage] if stage < len(schedule) else -1


def _recalc_plan(plan: DailyPlan):
    total = plan.items.count()
    done = plan.items.filter(is_done=True).count()
    plan.completion_rate = int((done / total) * 100) if total else 0
    plan.is_completed = (plan.completion_rate == 100)
    plan.save()


def _mark_plan_items_done_for_topic(user, topic):
    today = timezone.localdate()
    plan = DailyPlan.objects.filter(user=user, date=today).first()
    if not plan:
        return

    DailyPlanItem.objects.filter(
        plan=plan,
        topic=topic,
        type__in=["topic", "test", "video"]
    ).update(is_done=True)

    _recalc_plan(plan)


def _ensure_review_for_wrong(user, topic, wrong_count: int):
    if wrong_count <= 0:
        return

    item, created = ReviewItem.objects.get_or_create(user=user, topic=topic)
    item.is_active = True
    item.wrong_count_total += wrong_count
    item.last_wrong_at = timezone.now()

    if created or item.stage == 0:
        item.stage = 0
        item.next_review_at = timezone.now() + timedelta(days=1)
    else:
        item.next_review_at = min(item.next_review_at, timezone.now() + timedelta(days=1))

    item.save()


def _award_xp_and_streak_if_available(user, plan: DailyPlan, just_completed_item: bool):
    """
    XP: item done +10
    Günü bitirince +50 ve streak.
    StudentStats yoksa sessizce geçer.
    """
    try:
        from accounts.models import StudentStats
        stats, _ = StudentStats.objects.get_or_create(user=user)

        if just_completed_item:
            stats.xp += 10

        if plan.is_completed:
            today = timezone.localdate()
            yesterday = today.fromordinal(today.toordinal() - 1)

            if stats.last_streak_date == yesterday:
                stats.streak += 1
            else:
                stats.streak = 1

            stats.last_streak_date = today
            stats.xp += 50

        stats.save()
    except Exception:
        pass


# ---------------------------
# Sprint-1: Topics
# ---------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def topics_tree(request):
    grade_val = request.GET.get("grade")
    subject_name = request.GET.get("subject")

    if not grade_val or not subject_name:
        return Response({"ok": False, "error": "grade ve subject zorunlu"}, status=400)

    grade = get_object_or_404(Grade, number=int(grade_val))
    subject = get_object_or_404(Subject, name=subject_name)

    qs = (
        TopicTemplate.objects
        .filter(grade=grade, subject=subject)
        .select_related("parent")
        .order_by("order", "id")
    )

    by_id = {}
    roots = []
    for t in qs:
        by_id[t.id] = _node(t)

    for t in qs:
        n = by_id[t.id]
        if t.parent_id and t.parent_id in by_id:
            by_id[t.parent_id]["children"].append(n)
        else:
            roots.append(n)

    return Response({"ok": True, "data": roots})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def topic_detail(request, topic_id: int):
    topic = get_object_or_404(TopicTemplate, id=topic_id)

    contents = TopicContent.objects.filter(topic=topic, is_active=True).order_by("order", "id")
    questions = TopicQuestion.objects.filter(topic=topic).order_by("order", "id")
    prog = StudentTopicProgress.objects.filter(user=request.user, topic=topic).first()

    return Response({
        "ok": True,
        "data": {
            "topic": {"id": topic.id, "title": topic.title},
            "contents": [{
                "id": c.id,
                "type": c.content_type,
                "title": c.title,
                "file": c.file.url if c.file else None,
                "url": c.url,
                "duration_sec": c.duration_sec
            } for c in contents],
            "questions": [{
                "id": q.id,
                "text": q.text,
                "a": q.choice_a,
                "b": q.choice_b,
                "c": q.choice_c,
                "d": q.choice_d,
            } for q in questions],
            "progress": None if not prog else {
                "video_progress": prog.video_progress,
                "video_completed": prog.video_completed,
                "test_score": prog.test_score,
                "completed": prog.completed,
            }
        }
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def topic_video_progress(request, topic_id: int):
    topic = get_object_or_404(TopicTemplate, id=topic_id)
    progress = int(request.data.get("progress", 0))
    progress = max(0, min(100, progress))
    video_completed = progress >= 80

    prog, _ = StudentTopicProgress.objects.get_or_create(user=request.user, topic=topic)
    prog.video_progress = progress
    prog.video_completed = video_completed

    if prog.video_completed and prog.test_score >= 70:
        prog.completed = True

    prog.save()

    if prog.completed:
        _mark_plan_items_done_for_topic(request.user, topic)

    return Response({"ok": True, "data": {
        "video_progress": prog.video_progress,
        "video_completed": prog.video_completed,
        "completed": prog.completed
    }})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def topic_test_submit(request, topic_id: int):
    topic = get_object_or_404(TopicTemplate, id=topic_id)
    answers = request.data.get("answers", [])

    if not isinstance(answers, list) or len(answers) == 0:
        return Response({"ok": False, "error": "answers zorunlu"}, status=400)

    q_ids = [a.get("question_id") for a in answers if a.get("question_id")]
    qs = TopicQuestion.objects.filter(topic=topic, id__in=q_ids)
    correct_map = {q.id: q.correct for q in qs}

    total, correct = 0, 0
    for a in answers:
        qid = a.get("question_id")
        ans = (a.get("answer") or "").strip().upper()
        if qid in correct_map:
            total += 1
            if ans == (correct_map[qid] or "").strip().upper():
                correct += 1

    score = (correct / total) * 100 if total else 0
    wrong = total - correct

    prog, _ = StudentTopicProgress.objects.get_or_create(user=request.user, topic=topic)
    prog.test_score = score

    if prog.video_completed and prog.test_score >= 70:
        prog.completed = True

    prog.save()

    if wrong > 0:
        _ensure_review_for_wrong(request.user, topic, wrong)

    if prog.completed:
        _mark_plan_items_done_for_topic(request.user, topic)

    return Response({"ok": True, "data": {
        "score": score,
        "correct": correct,
        "total": total,
        "wrong": wrong,
        "completed": prog.completed
    }})


# ---------------------------
# Sprint-2: Reviews
# ---------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_reviews_today(request):
    now = timezone.now()
    until = now + timedelta(days=1)

    items = (
        ReviewItem.objects
        .filter(user=request.user, is_active=True, next_review_at__lte=until)
        .select_related("topic")
        .order_by("next_review_at")
    )

    return Response({"ok": True, "data": [{
        "id": it.id,
        "topic_id": it.topic_id,
        "topic_title": it.topic.title,
        "stage": it.stage,
        "next_review_at": it.next_review_at,
        "wrong_count_total": it.wrong_count_total,
    } for it in items]})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def review_mark_done(request, review_id: int):
    item = get_object_or_404(ReviewItem, id=review_id, user=request.user, is_active=True)

    score = float(request.data.get("score", 0) or 0)
    ReviewAttempt.objects.create(item=item, score=score)

    item.stage += 1
    nd = _next_days(item.stage)

    if nd == -1:
        item.is_active = False
    else:
        item.next_review_at = timezone.now() + timedelta(days=nd)

    item.save()

    return Response({"ok": True, "data": {
        "is_active": item.is_active,
        "stage": item.stage,
        "next_review_at": item.next_review_at if item.is_active else None
    }})


# ---------------------------
# Sprint-3: Daily Plan
# ---------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_daily_plan(request):
    plan = generate_daily_plan(request.user)
    items = plan.items.order_by("order")

    return Response({"ok": True, "data": {
        "date": plan.date,
        "completion_rate": plan.completion_rate,
        "items": [{
            "id": it.id,
            "type": it.type,
            "title": it.title,
            "is_done": it.is_done,
            "topic_id": it.topic_id,
        } for it in items]
    }})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def daily_plan_item_done(request, item_id):
    item = get_object_or_404(DailyPlanItem, id=item_id, plan__user=request.user)
    plan = item.plan

    just_completed_item = False
    if not item.is_done:
        item.is_done = True
        item.save()
        just_completed_item = True

    _recalc_plan(plan)

    # XP/Streak
    _award_xp_and_streak_if_available(request.user, plan, just_completed_item)

    return Response({"ok": True, "data": {
        "completion_rate": plan.completion_rate,
        "is_completed": plan.is_completed
    }})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_stats(request):
    """
    GET /api/me/stats
    """
    try:
        from accounts.models import StudentStats
        s, _ = StudentStats.objects.get_or_create(user=request.user)
        return Response({"ok": True, "data": {"xp": s.xp, "streak": s.streak}})
    except Exception:
        return Response({"ok": True, "data": {"xp": 0, "streak": 0}})
