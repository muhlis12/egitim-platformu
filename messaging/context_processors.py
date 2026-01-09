from django.db.models import Count, Q
from .models import Conversation

def unread_message_counts(request):
    if not request.user.is_authenticated:
        return {"unread_total": 0}

    u = request.user

    if u.role == "TEACHER":
        qs = Conversation.objects.filter(teacher=u).annotate(
            unread=Count("messages", filter=Q(messages__read_by_teacher=False))
        )
        total = sum(x.unread for x in qs)
        return {"unread_total": total}

    if u.role == "STUDENT":
        qs = Conversation.objects.filter(student=u).annotate(
            unread=Count("messages", filter=Q(messages__read_by_student=False))
        )
        total = sum(x.unread for x in qs)
        return {"unread_total": total}

    return {"unread_total": 0}
