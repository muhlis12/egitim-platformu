"""
Django settings for config project.
Prod + Local uyumlu (Google Cloud VM + Nginx + Gunicorn için)
"""

import os
from pathlib import Path

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------
# ENV / WHATSAPP (şimdilik sadece okuma)
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
    "django-insecure-b6+okwo2cb&d=70s(mbly3n(iz8vsutowhrvdd0$+1hh3pu85p",
)

# Prod'da default False olsun (env: DJANGO_DEBUG=1 yaparsan açılır)
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"

# -------------------------------------------------
# HOST / CSRF (LOGIN POST için kritik)
# -------------------------------------------------
# Örn: DJANGO_ALLOWED_HOSTS="34.52.203.126,egitim.1imzakurs.com,localhost,127.0.0.1"
_allowed_hosts = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost,0.0.0.0,egitim.1imzakurs.com,34.52.203.126",
)
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(",") if h.strip()]

# Örn: DJANGO_CSRF_TRUSTED_ORIGINS="https://egitim.1imzakurs.com,http://egitim.1imzakurs.com"
_csrf = os.getenv(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "https://egitim.1imzakurs.com,http://egitim.1imzakurs.com",
)
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf.split(",") if o.strip()]

# -------------------------------------------------
# PROXY / HTTPS (NGINX arkasında)
# -------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# SSL kurunca env ile aç:
# DJANGO_SECURE_SSL_REDIRECT=1
SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "0") == "1"

# Cookie güvenliği (SSL kurmadan 0 kalsın, SSL kurunca 1 yap)
SESSION_COOKIE_SECURE = os.getenv("DJANGO_SESSION_COOKIE_SECURE", "0") == "1"
CSRF_COOKIE_SECURE = os.getenv("DJANGO_CSRF_COOKIE_SECURE", "0") == "1"

SESSION_COOKIE_SAMESITE = os.getenv("DJANGO_SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = os.getenv("DJANGO_CSRF_COOKIE_SAMESITE", "Lax")

# PROD’da header güvenliği (opsiyonel ama faydalı)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

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
    "notifications",
    "parents",
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
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "messaging.context_processors.unread_message_counts",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# -------------------------------------------------
# DATABASE
# -------------------------------------------------
DATABASE_URL = os.getenv("DJANGO_DATABASE_URL", "").strip()

if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {
            "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=False)
        }
    except Exception:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
                "OPTIONS": {"timeout": 30},
            }
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "OPTIONS": {"timeout": 30},
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
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------
# STATIC / MEDIA
# -------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

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

# -------------------------------------------------
# LOGGING (500 sebeplerini journalctl ile görmek için)
# -------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG" if DEBUG else "INFO",
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
