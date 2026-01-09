from django.db import models
from django.conf import settings
from courses.models import Course

class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="exams")
    title = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField(default=20)  # süre (dk)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    choice_a = models.CharField(max_length=255)
    choice_b = models.CharField(max_length=255)
    choice_c = models.CharField(max_length=255)
    choice_d = models.CharField(max_length=255)

    # A/B/C/D
    correct = models.CharField(max_length=1, choices=[
        ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")
    ])

    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Soru {self.order}"

class Attempt(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts")

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)  # 👈 BURASI
    deadline_at = models.DateTimeField(null=True, blank=True)

    score = models.FloatField(default=0)  # 0–100
    correct_count = models.IntegerField(default=0)
    wrong_count = models.IntegerField(default=0)


    class Meta:
        ordering = ["-started_at"]

class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected = models.CharField(max_length=1, choices=[
        ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")
    ], null=True, blank=True)

    class Meta:
        unique_together = ("attempt", "question")

