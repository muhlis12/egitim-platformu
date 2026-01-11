from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    after_login,
    gate_student,
    gate_teacher,
    gate_admin,
    gate_parent,
    logout_get,
    login_choice,   # ✅ 4 kutulu giriş ekranı
)
from .api import users_search


urlpatterns = [
    # =========================
    # 4 KUTULU GİRİŞ EKRANI
    # =========================
    path("login/", login_choice, name="login"),

    # =========================
    # ROLE BAZLI LOGIN EKRANLARI
    # =========================
    path(
        "login/student/",
        auth_views.LoginView.as_view(
            template_name="accounts/login_role.html",
            extra_context={"role_key": "student"},
            redirect_authenticated_user=True,
        ),
        name="login_student",
    ),
    path(
        "login/teacher/",
        auth_views.LoginView.as_view(
            template_name="accounts/login_role.html",
            extra_context={"role_key": "teacher"},
            redirect_authenticated_user=True,
        ),
        name="login_teacher",
    ),
    path(
        "login/admin/",
        auth_views.LoginView.as_view(
            template_name="accounts/login_role.html",
            extra_context={"role_key": "admin"},
            redirect_authenticated_user=True,
        ),
        name="login_admin",
    ),
    path(
        "login/parent/",
        auth_views.LoginView.as_view(
            template_name="accounts/login_role.html",
            extra_context={"role_key": "parent"},
            redirect_authenticated_user=True,
        ),
        name="login_parent",
    ),

    # =========================
    # ÇIKIŞ
    # =========================
    path("logout/", logout_get, name="logout"),

    # =========================
    # LOGIN SONRASI YÖNLENDİRME
    # =========================
    path("after-login/", after_login, name="after_login"),

    # =========================
    # ROLE GATE (YANLIŞ LOGIN ENGELİ)
    # =========================
    path("gate/student/", gate_student, name="gate_student"),
    path("gate/teacher/", gate_teacher, name="gate_teacher"),
    path("gate/admin/", gate_admin, name="gate_admin"),
    path("gate/parent/", gate_parent, name="gate_parent"),


    # =========================
    # ŞİFRE SIFIRLAMA
    # =========================
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    # =========================
    # AJAX – USER SEARCH (Select2)
    # =========================
    path("api/v1/users/search", users_search, name="api_users_search"),
]
