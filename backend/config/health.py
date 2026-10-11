"""Minimal probes: no settings, user details, or database errors in responses."""
from django.db import connections, DatabaseError
from django.http import JsonResponse
from django.views.decorators.http import require_safe


@require_safe
def live(request):
    return JsonResponse({"status": "ok"})


@require_safe
def ready(request):
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
