"""Protect the local learner API from writes initiated by unrelated websites."""
from django.conf import settings
from django.http import JsonResponse


class LocalLearnerApiMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_api = request.path.startswith("/api/")
        if is_api and request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("Origin")
            allowed = {*settings.CORS_ALLOWED_ORIGINS, f"{request.scheme}://{request.get_host()}"}
            if origin and origin not in allowed or not origin and request.headers.get("Sec-Fetch-Site") == "cross-site":
                response = JsonResponse({"detail": "This local API accepts browser changes only from the piano app."}, status=403)
                response["Cache-Control"] = "private, no-store"
                return response
        response = self.get_response(request)
        if is_api:
            response["Cache-Control"] = "private, no-store"
        return response


class AccountIdentityMiddleware:
    """Reject queued writes from a tab whose account changed in another tab."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        expected = request.headers.get("X-KuyLab-User")
        if request.path.startswith("/api/") and expected and (not request.user.is_authenticated or expected != str(request.user.pk)):
            return JsonResponse({"detail": "Account changed. Reload this page."}, status=401)
        return self.get_response(request)
