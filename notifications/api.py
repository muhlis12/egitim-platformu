from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Notification

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_notifications(request):
    qs = Notification.objects.filter(user=request.user).order_by("-created_at")[:50]
    unread = Notification.objects.filter(user=request.user, is_read=False).count()

    return Response({
        "ok": True,
        "data": {
            "unread": unread,
            "items": [{
                "id": n.id,
                "title": n.title,
                "body": n.body,
                "url": n.url,
                "level": n.level,
                "is_read": n.is_read,
                "created_at": n.created_at,
            } for n in qs]
        }
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_read(request, nid: int):
    n = get_object_or_404(Notification, id=nid, user=request.user)
    n.is_read = True
    n.save()
    return Response({"ok": True})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({"ok": True})
