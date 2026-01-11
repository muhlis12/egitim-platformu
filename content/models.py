from django.db import models
from django.conf import settings
from django.utils import timezone

from courses.models import Course


# ---------------------------
# Lessons (mevcut)
# ---------------------------

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class LessonFile(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="files")
    title = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to="lesson_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class LessonVideo(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="videos")
    title = models.CharField(max_length=200, blank=True)
    video = models.FileField(upload_to="lesson_videos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Video #{self.id}"


class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "lesson")

    def __str__(self):
        return f"{self.user} - {self.lesson} ({'✓' if self.completed else '…'})"


# ---------------------------
# Topic Tree
# ---------------------------

class Grade(models.Model):
    number = models.IntegerField()  # 1–12

    def __str__(self):
        return f"{self.number}. Sınıf"


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TopicTemplate(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children"
    )

    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        if self.parent:
            return f"{self.grade} {self.subject} - {self.parent.title} > {self.title}"
        return f"{self.grade} {self.subject} - {self.title}"


# ---------------------------
# Sprint-1: Topic Content + Questions + Progress
# ---------------------------

class TopicContent(models.Model):
    class ContentType(models.TextChoices):
        VIDEO = "video", "Video"
        PDF = "pdf", "PDF"
        TEXT = "text", "Text"

    topic = models.ForeignKey(TopicTemplate, on_delete=models.CASCADE, related_name="contents")
    content_type = models.CharField(max_length=10, choices=ContentType.choices)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="topic_contents/", null=True, blank=True)
    url = models.URLField(blank=True)  # youtube vb
    duration_sec = models.PositiveIntegerField(default=0)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.topic.title} - {self.title}"


class TopicQuestion(models.Model):
    topic = models.ForeignKey(TopicTemplate, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    choice_a = models.CharField(max_length=255)
    choice_b = models.CharField(max_length=255)
    choice_c = models.CharField(max_length=255)
    choice_d = models.CharField(max_length=255)

    correct = models.CharField(max_length=1, choices=[
        ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")
    ])

    difficulty = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.topic.title} - Soru {self.order}"


class StudentTopicProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topic_progress")
    topic = models.ForeignKey(TopicTemplate, on_delete=models.CASCADE, related_name="progress")

    video_progress = models.PositiveIntegerField(default=0)  # 0-100
    video_completed = models.BooleanField(default=False)

    test_score = models.FloatField(default=0)  # 0-100
    completed = models.BooleanField(default=False)

    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "topic")

    def __str__(self):
        return f"{self.user.username} - {self.topic.title} ({'✓' if self.completed else '…'})"


# ---------------------------
# Sprint-2: Review System
# ---------------------------

class ReviewItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_items")
    topic = models.ForeignKey(TopicTemplate, on_delete=models.CASCADE, related_name="review_items")

    stage = models.PositiveIntegerField(default=0)  # 0->1g,1->3g,2->7g,3->14g
    next_review_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    wrong_count_total = models.PositiveIntegerField(default=0)
    last_wrong_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "topic")
        indexes = [
            models.Index(fields=["user", "next_review_at"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.topic.title} (stage={self.stage})"


class ReviewAttempt(models.Model):
    item = models.ForeignKey(ReviewItem, on_delete=models.CASCADE, related_name="attempts")
    at = models.DateTimeField(auto_now_add=True)

    score = models.FloatField(default=0)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Attempt {self.item_id} @ {self.at}"


# ---------------------------
# Sprint-3: Daily Plan
# ---------------------------

class DailyPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="daily_plans")
    date = models.DateField(default=timezone.localdate)  # ✅ DateField için en sağlıklısı

    is_completed = models.BooleanField(default=False)
    completion_rate = models.PositiveIntegerField(default=0)  # 0-100

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class DailyPlanItem(models.Model):
    PLAN_TYPE_CHOICES = [
        ("review", "Tekrar"),
        ("topic", "Konu"),
        ("video", "Video"),
        ("test", "Test"),
        ("custom", "Özel"),
    ]

    plan = models.ForeignKey(DailyPlan, on_delete=models.CASCADE, related_name="items")
    type = models.CharField(max_length=10, choices=PLAN_TYPE_CHOICES)

    title = models.CharField(max_length=255)
    topic = models.ForeignKey(TopicTemplate, null=True, blank=True, on_delete=models.SET_NULL)
    review_item = models.ForeignKey(ReviewItem, null=True, blank=True, on_delete=models.SET_NULL)

    is_done = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.title}"

