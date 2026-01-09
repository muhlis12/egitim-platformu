from django.db import models
from django.conf import settings
from courses.models import Course


class Conversation(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="conversations")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_conversations")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✅ BURADA, Conversation içinde olacak

    class Meta:
        unique_together = ("course", "student", "teacher")

    def __str__(self):
        return f"{self.course.title} | {self.student.username} -> {self.teacher.username}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to="message_files/", null=True, blank=True)  # ✅ burada
    created_at = models.DateTimeField(auto_now_add=True)
    read_by_teacher = models.BooleanField(default=False)
    read_by_student = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    
    def __str__(self):
        return f"Msg #{self.id} by {self.sender.username}"
