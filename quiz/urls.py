from django.urls import path
from .views import exam_start, exam_take, exam_finish

urlpatterns = [
    path("exams/<int:exam_id>/start/", exam_start, name="exam_start"),
    path("attempts/<int:attempt_id>/take/", exam_take, name="exam_take"),
    path("attempts/<int:attempt_id>/finish/", exam_finish, name="exam_finish"),
]
