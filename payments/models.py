from django.db import models
from django.conf import settings
from courses.models import Course

class PurchaseRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Beklemede"
        APPROVED = "APPROVED", "Onaylandı"
        REJECTED = "REJECTED", "Reddedildi"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchase_requests")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="purchase_requests")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    note = models.CharField(max_length=255, blank=True)  # dekont no vs
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")  # aynı kursa 2 kez talep olmasın

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.status}"
