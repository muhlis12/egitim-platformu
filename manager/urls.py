from django.urls import path
from .views import (
    manager_home,
    manager_courses,
    manager_course_new,
    manager_assign_teacher,
    manager_course_students,
    manager_ready_lessons,
)

urlpatterns = [
    path("manager/", manager_home, name="manager_home"),
    path("manager/courses/", manager_courses, name="manager_courses"),
    path("manager/courses/new/", manager_course_new, name="manager_course_new"),
    path("manager/courses/<int:course_id>/assign-teacher/", manager_assign_teacher, name="manager_assign_teacher"),
    path("manager/courses/<int:course_id>/students/", manager_course_students, name="manager_course_students"),
    path("manager/courses/<int:course_id>/ready-lessons/", manager_ready_lessons, name="manager_ready_lessons"),
]
