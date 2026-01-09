from django.urls import path
from .views import lesson_detail, lesson_complete

urlpatterns = [
    path("lessons/<int:lesson_id>/", lesson_detail, name="lesson_detail"),
    path("lessons/<int:lesson_id>/complete/", lesson_complete, name="lesson_complete"),
]
