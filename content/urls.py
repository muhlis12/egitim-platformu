from django.urls import path

from .views import (
    lesson_detail, lesson_complete,
    topics_home, topic_page,
    daily_plan_page, daily_plan_assign,
)

from .api import (
    topics_tree, topic_detail, topic_video_progress, topic_test_submit,
    my_reviews_today, review_mark_done,
    my_daily_plan, daily_plan_item_done,
    my_stats,
)

urlpatterns = [
    # Lessons (mevcut)
    path("lessons/<int:lesson_id>/", lesson_detail, name="lesson_detail"),
    path("lessons/<int:lesson_id>/complete/", lesson_complete, name="lesson_complete"),

    # Sprint-1 UI: Konu ağacı + konu sayfası
    path("topics/", topics_home, name="topics_home"),
    path("topics/<int:topic_id>/", topic_page, name="topic_page"),

    # Sprint-3 UI: Günlük plan + atama
    path("daily-plan/", daily_plan_page, name="daily_plan_page"),
    path("daily-plan/assign/", daily_plan_assign, name="daily_plan_assign"),

    # Sprint-1 API
    path("api/topics/tree", topics_tree, name="api_topics_tree"),
    path("api/topics/<int:topic_id>", topic_detail, name="api_topic_detail"),
    path("api/topics/<int:topic_id>/video-progress", topic_video_progress, name="api_topic_video_progress"),
    path("api/topics/<int:topic_id>/test-submit", topic_test_submit, name="api_topic_test_submit"),

    # Sprint-2 API
    path("api/reviews/today", my_reviews_today, name="api_reviews_today"),
    path("api/reviews/<int:review_id>/done", review_mark_done, name="api_review_done"),

    # Sprint-3 API
    path("api/daily-plan", my_daily_plan, name="api_daily_plan"),
    path("api/daily-plan/item/<int:item_id>/done", daily_plan_item_done, name="api_daily_plan_item_done"),

    # Sprint-3 Gamification API (XP/Streak)
    path("api/me/stats", my_stats, name="api_my_stats"),
]
