# pgf_core/settings/base.py ESTE ES EL SETTIGS PRINCIPAL, LOS DEMÁS IMPORTAN DESDE AQUÍ
import os
from pathlib import Path
from datetime import timedelta
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# -------- Core --------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",  # Django Channels para WebSockets
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "django_filters",
    "corsheaders",
    "apps.users",
    "apps.vehicles",
    "apps.workorders",
    "apps.inventory",
    "apps.reports",
    "apps.drivers",
    "apps.scheduling",
    "apps.emergencies",
    "apps.notifications",
]

AUTH_USER_MODEL = "users.User"
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # "apps.workorders.middleware.RateLimitMiddleware",  # Descomentar cuando se necesite rate limiting
    "django.contrib.sessions.middleware.SessionMiddleware",         # ✔ requerido
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",                    # opcional pero recomendado
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",       # ✔ requerido
    "django.contrib.messages.middleware.MessageMiddleware",          # ✔ requerido
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "pgf_core.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

WSGI_APPLICATION = "pgf_core.wsgi.application"
ASGI_APPLICATION = "pgf_core.asgi.application"

# -------- DB --------
db_url = os.getenv("DATABASE_URL", "postgres://pgf:pgf@db:5432/pgf")
u = urlparse(db_url)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": u.path[1:], "USER": u.username, "PASSWORD": u.password,
        "HOST": u.hostname, "PORT": u.port or 5432,
        "CONN_MAX_AGE": 60,
    }
}

# -------- i18n --------
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# -------- Static --------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -------- DRF --------

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",  
    "DEFAULT_AUTHENTICATION_CLASSES": [
        
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}
SPECTACULAR_SETTINGS = {
    "TITLE": "PGF API",
    "DESCRIPTION": "Plataforma de Gestión de Flota",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api",
    "SERVERS": [{"url": os.getenv("PUBLIC_URL", "http://127.0.0.1:8000")}],
    "SECURITY": [{"BearerAuth": []}],
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},
    "COMPONENT_SPLIT_REQUEST": True,
    
}

# -------- JWT --------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# -------- Logging --------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
}

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = "Lax"
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

# -------- Channels (WebSockets) --------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv("REDIS_HOST", "redis"), int(os.getenv("REDIS_PORT", "6379")))],
        },
    },
}

# -------- AWS S3 --------


import os
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "pgf-evidencias-dev")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL", "http://localstack:4566")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
AWS_PUBLIC_URL_PREFIX = os.getenv("AWS_PUBLIC_URL_PREFIX", "http://localhost:4566")

# -------- EMAIL --------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "kui.peer1402@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")  # Configurar en .env
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "kui.peer1402@gmail.com")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# URL del frontend para enlaces de recuperación
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# -------- CACHING (Redis) --------
# Nota: Requiere django-redis instalado
try:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/2"),  # DB 2 para cache (0 y 1 son para Celery)
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": "pgf",
            "TIMEOUT": 300,  # 5 minutos por defecto
        }
    }
except ImportError:
    # Fallback a cache en memoria si django-redis no está instalado
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }