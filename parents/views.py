from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import ParentStudent


@login_required
def parent_dashboard(request):
    if getattr(request.user, "role", None) != "PARENT":
        return redirect("/dashboard/")

    today = timezone.localdate()

    links = ParentStudent.objects.filter(parent=request.user).select_related("student")
    students = [l.student for l in links]

    # Günlük plan + tekrar + stats
    from content.models import DailyPlan, ReviewItem

    plans = DailyPlan.objects.filter(user__in=students, date=today).select_related("user")
    plan_map = {p.user_id: p for p in plans}

    review_map = {}
    for r in ReviewItem.objects.filter(user__in=students, is_active=True, next_review_at__date__lte=today).values("user_id"):
        uid = r["user_id"]
        review_map[uid] = review_map.get(uid, 0) + 1

    stats_map = {}
    try:
        from accounts.models import StudentStats
        stats_map = {s.user_id: s for s in StudentStats.objects.filter(user__in=students)}
    except Exception:
        pass

    return render(request, "parents/dashboard.html", {
        "today": today,
        "links": links,
        "plan_map": plan_map,
        "review_map": review_map,
        "stats_map": stats_map,
    })
