from django.urls import path
from . import views

urlpatterns = [
    # Öğrenci
    path("messages/", views.student_inbox, name="student_inbox"),
    path("messages/course/<int:course_id>/", views.course_chat, name="course_chat"),

    # Öğretmen
    path("teacher/messages/", views.teacher_inbox, name="teacher_inbox"),
    path("teacher/messages/<int:conversation_id>/", views.teacher_chat, name="teacher_chat"),

    # Mesaj silme (sadece gönderen silebilir)
    path("message/<int:message_id>/delete/", views.delete_message, name="delete_message"),
]
