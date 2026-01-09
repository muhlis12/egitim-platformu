from django.db import models
from django.conf import settings
from courses.models import Course


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
