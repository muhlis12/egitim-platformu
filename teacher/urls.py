from django.urls import path
from . import views

urlpatterns = [
    path("", views.teacher_home, name="teacher_home"),

    # Kurs
    path("course/new/", views.course_new, name="teacher_course_new"),
    path("course/<int:course_id>/lesson/new/", views.lesson_new, name="teacher_lesson_new"),

    # Ders içerikleri
    path("lesson/<int:lesson_id>/file/new/", views.file_new, name="teacher_file_new"),
    path("lesson/<int:lesson_id>/video/new/", views.video_new, name="teacher_video_new"),

    # Sınav
    path("course/<int:course_id>/exam/new/", views.exam_new, name="teacher_exam_new"),
    path("exam/<int:exam_id>/question/new/", views.question_new, name="teacher_question_new"),
    path("exam/<int:exam_id>/results/", views.exam_results, name="teacher_exam_results"),
    path("attempt/<int:attempt_id>/", views.attempt_detail, name="teacher_attempt_detail"),

    # Canlı ders
    path("course/<int:course_id>/live/new/", views.live_lesson_new, name="teacher_live_new"),

    # Öğrenciler
    path("course/<int:course_id>/students/", views.course_students, name="teacher_course_students"),
    path(
    "course/<int:course_id>/student/<int:student_id>/message/",
    views.teacher_message_student,
    name="teacher_message_student",),

    # Öğrenci ilerleme (GENEL)
    path("course/<int:course_id>/progress/", views.course_progress, name="teacher_course_progress"),

    # ✅ ÖĞRENCİ DETAY RAPORU (İSTEDİĞİN KISIM)
    path(
        "course/<int:course_id>/progress/<int:student_id>/",
        views.course_progress_student_detail,
        name="teacher_course_progress_student_detail",
    ),

    # Hazır ders
    path("course/<int:course_id>/add-ready-lessons/", views.add_ready_lessons, name="teacher_add_ready_lessons"),

    # Ödeme
    path("course/<int:course_id>/payments/", views.purchase_requests, name="teacher_purchase_requests"),
    path("purchase/<int:pr_id>/approve/", views.purchase_request_approve, name="teacher_purchase_request_approve"),

    # Ders düzenleme
    path("lesson/<int:lesson_id>/edit/", views.edit_lesson, name="teacher_lesson_edit"),
    path("lesson/<int:lesson_id>/delete/", views.delete_lesson, name="teacher_lesson_delete"),
    path("course/<int:course_id>/lessons/reorder/", views.reorder_lessons, name="teacher_reorder_lessons"),
]
