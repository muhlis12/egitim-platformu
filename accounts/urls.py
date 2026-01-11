from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from .views import after_login, gate_student, gate_teacher, gate_admin, logout_get
from .api import users_search

urlpatterns = [
    # 3 ayrı login ekranı
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

    # /login/ -> öğrenci login
    path("login/", RedirectView.as_view(url="/login/student/", permanent=False), name="login"),

    path("logout/", logout_get, name="logout"),

    # login sonrası yönlendirme
    path("after-login/", after_login, name="after_login"),

    # rol kapıları
    path("gate/student/", gate_student, name="gate_student"),
    path("gate/teacher/", gate_teacher, name="gate_teacher"),
    path("gate/admin/", gate_admin, name="gate_admin"),

    # şifre sıfırlama
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), name="password_reset_complete"),
    path("api/v1/users/search", users_search, name="api_users_search"),
]
