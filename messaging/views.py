from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count, Q, Max

from courses.models import Course, Enrollment
from .models import Conversation, Message


def _try_send_whatsapp(to_e164: str, body: str) -> None:
    """WhatsApp opsiyonel: token/requests yoksa sessizce pas geçer."""
    try:
        from .whatsapp import send_whatsapp_text_safely
        send_whatsapp_text_safely(to_e164=to_e164, body=body)
    except Exception:
        pass


@login_required
def student_inbox(request):
    if request.user.role != "STUDENT":
        return render(request, "courses/forbidden.html", status=403)

    courses = Course.objects.filter(enrollments__user=request.user).order_by("-id")

    convos = (
        Conversation.objects
        .filter(student=request.user)
        .select_related("course", "teacher")
        .annotate(
            unread_count=Count("messages", filter=Q(messages__read_by_student=False)),
            last_msg_time=Max("messages__created_at"),
        )
        .order_by("-last_msg_time", "-created_at", "-id")
    )

    unread_by_course = {c.course_id: c.unread_count for c in convos}

    return render(request, "messaging/student_inbox.html", {
        "courses": courses,
        "unread_by_course": unread_by_course,
    })


@login_required
def course_chat(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.role != "STUDENT":
        return render(request, "courses/forbidden.html", status=403)

    if not Enrollment.objects.filter(course=course, user=request.user).exists():
        return render(request, "courses/forbidden.html", status=403)

    teacher = course.owner
    if not teacher:
        messages.error(request, "Bu kursta öğretmen ataması yok.")
        return redirect("/messages/")

    convo, _ = Conversation.objects.get_or_create(course=course, student=request.user, teacher=teacher)

    q = (request.GET.get("q") or "").strip()

    if request.method == "POST":
        text = (request.POST.get("text") or "").strip()
        f = request.FILES.get("file")

        if text or f:
            msg = Message.objects.create(
                conversation=convo,
                sender=request.user,
                text=text,
                file=f,
                read_by_student=True,
                read_by_teacher=False,
            )

            # öğretmen offline ise WhatsApp bildirimi (opsiyonel)
            try:
                prof = teacher.profile
                offline = timezone.now() - prof.last_seen > timedelta(minutes=5)
                if offline and prof.whatsapp_opt_in and prof.phone_e164:
                    body = f"[{course.title}] Öğrenci: {request.user.username}\n{text[:700]}"
                    _try_send_whatsapp(to_e164=prof.phone_e164, body=body)
            except Exception:
                pass

        return redirect("course_chat", course_id=course.id)

    # öğrenci okudu işaretle (karşı tarafın mesajları)
    Message.objects.filter(conversation=convo).exclude(sender=request.user).update(read_by_student=True)

    msgs = convo.messages.select_related("sender").order_by("created_at")
    if q:
        msgs = msgs.filter(text__icontains=q)

    return render(request, "messaging/course_chat.html", {
        "course": course,
        "convo": convo,
        "msgs": msgs,
        "q": q,
    })


@login_required
def teacher_inbox(request):
    if request.user.role not in ("TEACHER", "ADMIN"):
        return render(request, "courses/forbidden.html", status=403)

    convos = (
        Conversation.objects
        .filter(teacher=request.user)
        .select_related("course", "student")
        .annotate(
            unread_count=Count("messages", filter=Q(messages__read_by_teacher=False)),
            last_msg_time=Max("messages__created_at"),
        )
        .order_by("-last_msg_time", "-created_at", "-id")
    )

    return render(request, "messaging/teacher_inbox.html", {"convos": convos})


@login_required
def teacher_chat(request, conversation_id):
    if request.user.role not in ("TEACHER", "ADMIN"):
        return render(request, "courses/forbidden.html", status=403)

    convo = get_object_or_404(Conversation, id=conversation_id, teacher=request.user)

    q = (request.GET.get("q") or "").strip()

    if request.method == "POST":
        text = (request.POST.get("text") or "").strip()
        f = request.FILES.get("file")

        if text or f:
            Message.objects.create(
                conversation=convo,
                sender=request.user,
                text=text,
                file=f,
                read_by_teacher=True,
                read_by_student=False,
            )
        return redirect("teacher_chat", conversation_id=convo.id)

    # öğretmen okudu işaretle
    Message.objects.filter(conversation=convo).exclude(sender=request.user).update(read_by_teacher=True)

    msgs = convo.messages.select_related("sender").order_by("created_at")
    if q:
        msgs = msgs.filter(text__icontains=q)

    return render(request, "messaging/teacher_chat.html", {
        "convo": convo,
        "msgs": msgs,
        "q": q,
    })


@login_required
def delete_message(request, message_id):
    msg = get_object_or_404(Message, id=message_id)

    if msg.sender_id != request.user.id:
        return render(request, "courses/forbidden.html", status=403)

    if request.method != "POST":
        return render(request, "courses/forbidden.html", status=403)

    convo = msg.conversation
    msg.is_deleted = True
    msg.deleted_at = timezone.now()
    msg.text = ""          # istersek metni boşaltırız
    msg.file = None        # ek varsa kaldır (opsiyonel)
    msg.save(update_fields=["is_deleted", "deleted_at", "text", "file"])

    if request.user.role == "STUDENT":
        return redirect("course_chat", course_id=convo.course_id)
    return redirect("teacher_chat", conversation_id=convo.id)

