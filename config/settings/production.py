"""Strict deployment configuration: DJANGO_SETTINGS_MODULE=config.settings.production."""
import os
from .base import *  # noqa: F401,F403

if DEBUG:
    raise RuntimeError("Production requires DJANGO_DEBUG=0")
if not os.getenv("DATABASE_URL", "").strip():
    raise RuntimeError("Production requires DATABASE_URL for PostgreSQL")
if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
    raise RuntimeError("Production requires PostgreSQL")
if not os.getenv("DJANGO_ALLOWED_HOSTS", "").strip():
    raise RuntimeError("Set DJANGO_ALLOWED_HOSTS")
if not os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").strip():
    raise RuntimeError("Set DJANGO_CSRF_TRUSTED_ORIGINS")
