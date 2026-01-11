from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def users_search(request):
    q = (request.GET.get("q") or "").strip()
    role = (request.GET.get("role") or "").strip().upper()

    qs = User.objects.all()

    if role:
        qs = qs.filter(role=role)

    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))

    qs = qs.order_by("username")[:25]

    return Response({
        "results": [{"id": u.id, "text": f"{u.username} ({u.first_name} {u.last_name})".strip()} for u in qs]
    })
