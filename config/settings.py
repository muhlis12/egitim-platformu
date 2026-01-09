"""
Django settings for config project.
"""

import os
from pathlib import Path

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------
# ENV / WHATSAPP (Şimdilik sadece ayar okuma, WhatsApp sonra)
# -------------------------------------------------
os.environ.setdefault("WHATSAPP_API_VERSION", "v18.0")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v18.0")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")

# -------------------------------------------------
# SECURITY
# -------------------------------------------------
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-b6+okwo2cb&d=70s(mbly3n(iz8vsutowhrvdd0$+1hh3pu85p"
)

DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# (Localde CSRF sıkıntısı olursa aç)
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# -------------------------------------------------
# APPS
# -------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 3rd party
    "rest_framework",

    # local apps
    "accounts.apps.AccountsConfig",
    "courses",
    "content",
    "live",
    "quiz",
    "assignments",
    "payments",
    "manager",
    "dashboard",
    "messaging",
]

# -------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # teacher online/offline için last_seen güncelle
    "accounts.middleware.LastSeenMiddleware",
]

# -------------------------------------------------
# URLS / TEMPLATES
# -------------------------------------------------
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                # ✅ Menüde mesaj unread badge için
                "messaging.context_processors.unread_message_counts",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# -------------------------------------------------
# DATABASE
# -------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -------------------------------------------------
# AUTH
# -------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "/login/student/"
LOGIN_REDIRECT_URL = "/after-login/"
LOGOUT_REDIRECT_URL = "/login/student/"

# -------------------------------------------------
# I18N / TZ
# -------------------------------------------------
LANGUAGE_CODE = "tr-tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------
# STATIC / MEDIA
# -------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------
# DRF
# -------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
