from django.urls import path
from . import views

urlpatterns = [
    path("manager/", views.manager_courses, name="manager_home"),

    path("manager/courses/", views.manager_courses, name="manager_courses"),
    path("manager/courses/new/", views.manager_course_new, name="manager_course_new"),
    path("manager/courses/<int:course_id>/assign-teacher/", views.manager_assign_teacher, name="manager_assign_teacher"),
    path("manager/courses/<int:course_id>/students/", views.manager_course_students, name="manager_course_students"),
    path("manager/courses/<int:course_id>/ready-lessons/", views.manager_ready_lessons, name="manager_ready_lessons"),
]
