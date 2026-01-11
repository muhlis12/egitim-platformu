# content/services.py
from django.utils import timezone
from datetime import timedelta

from .models import DailyPlan, DailyPlanItem, ReviewItem, TopicTemplate, StudentTopicProgress


def _first_incomplete_topic(user):
    # En basit: tamamlanmamış ilk konu
    # (İstersen grade/subject filtreyi sonra ekleriz)
    completed_topic_ids = StudentTopicProgress.objects.filter(
        user=user, completed=True
    ).values_list("topic_id", flat=True)

    return TopicTemplate.objects.exclude(id__in=completed_topic_ids).order_by("id").first()


def generate_daily_plan(user):
    today = timezone.now().date()

    plan, created = DailyPlan.objects.get_or_create(user=user, date=today)
    if not created:
        return plan

    order = 1

    # 1) Bugünkü tekrarlar
    reviews = ReviewItem.objects.filter(
        user=user,
        is_active=True,
        next_review_at__date__lte=today
    ).select_related("topic").order_by("next_review_at")

    for r in reviews:
        DailyPlanItem.objects.create(
            plan=plan,
            type="review",
            title=f"Tekrar: {r.topic.title}",
            topic=r.topic,
            review_item=r,
            order=order
        )
        order += 1

    # 2) 1 yeni konu
    next_topic = _first_incomplete_topic(user)
    if next_topic:
        DailyPlanItem.objects.create(
            plan=plan,
            type="topic",
            title=f"Yeni Konu: {next_topic.title}",
            topic=next_topic,
            order=order
        )
        order += 1

        # 3) aynı konudan mini test
        DailyPlanItem.objects.create(
            plan=plan,
            type="test",
            title=f"Mini Test: {next_topic.title}",
            topic=next_topic,
            order=order
        )

    return plan
