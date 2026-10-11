from django.contrib import admin
from django.urls import include, path

from apps.learning import accounts
from config import health

urlpatterns = [
    path("health/live/", health.live),
    path("health/ready/", health.ready),
    path("api/auth/session/", accounts.session),
    path("api/auth/login/", accounts.sign_in),
    path("api/auth/register/", accounts.register),
    path("api/auth/logout/", accounts.sign_out),
    path("api/auth/password/", accounts.password),
    path("api/auth/player-preferences/", accounts.player_preferences),
    path("api/", include("apps.studio.urls")),
    path("api/", include("apps.activity.urls")),
    path("admin/", admin.site.urls),
    path("api/", include("apps.learning.urls")),
    path("api/", include("apps.scores.urls")),
]
