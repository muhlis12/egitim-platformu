from django.db import models
from django.conf import settings


class ParentStudent(models.Model):
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="parent_links"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_links"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("parent", "student")
        indexes = [
            models.Index(fields=["parent"]),
            models.Index(fields=["student"]),
        ]

    def __str__(self):
        return f"{self.parent.username} -> {self.student.username}"
