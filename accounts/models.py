from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)

    def is_teacher(self):
        return self.role == self.Role.TEACHER

    def is_student(self):
        return self.role == self.Role.STUDENT
        


from django.db import models
from django.conf import settings
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone_e164 = models.CharField(max_length=30, blank=True)   # örn: +905xxxxxxxxx
    whatsapp_opt_in = models.BooleanField(default=False)
    opt_in_at = models.DateTimeField(null=True, blank=True)
    last_seen = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} profile"
