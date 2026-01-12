from django.urls import path
from . import views

urlpatterns = [
    path("manager/", views.manager_courses, name="manager_home"),

    path("manager/courses/", views.manager_courses, name="manager_courses"),
    path("manager/courses/new/", views.manager_course_new, name="manager_course_new"),
    path("manager/courses/<int:course_id>/assign-teacher/", views.manager_assign_teacher, name="manager_assign_teacher"),
    path("manager/courses/<int:course_id>/students/", views.manager_course_students, name="manager_course_students"),
    path("manager/courses/<int:course_id>/ready-lessons/", views.manager_ready_lessons, name="manager_ready_lessons"),

    # ✅ Kullanıcı Yönetimi
    path("manager/users/", views.manager_users, name="manager_users"),
    path("manager/users/new/", views.manager_user_new, name="manager_user_new"),
    path("manager/users/<int:user_id>/edit/", views.manager_user_edit, name="manager_user_edit"),
    path("manager/students/new/", views.manager_student_new_with_parent, name="manager_student_new_with_parent"),
]
