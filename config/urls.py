"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def root_redirect(request):
    # Ana sayfa → Admin giriş ekranı (custom admin login)
    return redirect("/login/admin/")


urlpatterns = [
    # ROOT (/) mutlaka en üstte olsun
    path("", root_redirect),

    # Login/Logout/After-login route'ları (accounts içinden)
    path("", include("accounts.urls")),

    # Django admin panel (opsiyonel kullanım)
    path("admin/", admin.site.urls),

    # Modüller
    path("dashboard/", include("dashboard.urls")),
    path("courses/", include("courses.urls")),
    path("teacher/", include("teacher.urls")),

    # Diğer app'ler (kendi içlerinde path'leri var)
    path("", include("content.urls")),
    path("", include("quiz.urls")),
    path("", include("payments.urls")),
    path("", include("manager.urls")),
    path("", include("messaging.urls")),
    path("", include("notifications.urls")),
    path("", include("parents.urls")),
]

# Media sadece DEBUG'da (prod'da Nginx servis etmeli)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
