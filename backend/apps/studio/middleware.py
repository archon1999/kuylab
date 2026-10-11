"""Enforce a curated, read-only musical catalog on the server as well as the UI."""
import re
from django.conf import settings
from django.http import JsonResponse


class CuratedContentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, "CURATED_STUDIO_READ_ONLY", True):
            if request.method not in {"GET", "HEAD", "OPTIONS"}:
                if re.match(r"^/api/(?:scores|compositions|arrangements|lessons|tasks|sessions)(?:/|$)", request.path):
                    return JsonResponse({"detail": "This studio has a curated catalog. Content is prepared outside the website."}, status=405)
            if re.match(r"^/api/(?:overview|compositions|arrangements|lessons|tasks|sessions)(?:/|$)", request.path) or request.path.startswith("/api/scores/demo/"):
                # Old curriculum GETs can lazily create lessons. Do not merely
                # hide those routes in the new UI: prevent all side effects.
                return JsonResponse({"detail": "This older learning route is retired. Use the curated studio catalog."}, status=410)
        return self.get_response(request)
