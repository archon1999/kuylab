"""Loopback-only development settings."""
import os

from .base import *  # noqa: F403

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, "http://localhost:5174", "http://127.0.0.1:5174"]
SESSION_COOKIE_NAME = "kuylab_sessionid"
CSRF_COOKIE_NAME = "kuylab_csrftoken"
