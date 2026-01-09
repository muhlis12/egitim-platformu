from django.db import models
from courses.models import Course

class LiveLesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="live_lessons")
    title = models.CharField(max_length=200)
    meet_link = models.URLField()
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"
