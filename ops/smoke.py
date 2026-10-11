"""Run through manage.py shell inside backend, against the real frontend proxy.

Creates isolated random accounts, checks CSRF/account isolation/MIDI delivery,
then removes only those accounts. Never prints credentials or personal responses.
"""
import hashlib
import json
import secrets
import urllib.request
import urllib.error
from http.cookies import SimpleCookie
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils import timezone


class Browser:
    def __init__(self):
        self.cookies = {}
        self.csrf = ""

    def request(self, path, method="GET", data=None, csrf=True):
        headers = {"Host": "kuylab.uz", "X-Forwarded-Proto": "https",
                   "X-Forwarded-For": "127.0.0.1", "Origin": "https://kuylab.uz",
                   "Referer": "https://kuylab.uz/", "Content-Type": "application/json",
                   "Cookie": "; ".join(f"{key}={value}" for key, value in self.cookies.items())}
        if csrf:
            headers["X-CSRFToken"] = self.csrf
        request = urllib.request.Request("http://frontend:8080" + path, headers=headers,
                                        method=method, data=None if data is None else json.dumps(data).encode())
        # The Docker service is local; never send this traffic to a host proxy.
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            response = opener.open(request, timeout=15)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            for value in response.headers.get_all("Set-Cookie", []):
                cookie = SimpleCookie(value)
                for key, morsel in cookie.items():
                    assert morsel["secure"], "Production cookies must be secure"
                    self.cookies[key] = morsel.value
            raw = response.read()
            body = json.loads(raw) if "application/json" in response.headers.get("Content-Type", "") else raw
            if isinstance(body, dict) and body.get("csrfToken"):
                self.csrf = body["csrfToken"]
            return response.status, body, response.headers


names = ["deploy-check-" + secrets.token_hex(8) for _ in range(2)]
browsers = [Browser(), Browser()]
try:
    for browser, name in zip(browsers, names):
        assert browser.request("/api/auth/session/")[0] == 200
        assert browser.request("/api/auth/register/", "POST", {}, csrf=False)[0] == 403
        status, _, _ = browser.request("/api/auth/register/", "POST", {
            "username": name, "password": secrets.token_urlsafe(32), "display_name": "Deployment check"})
        assert status == 201, "Registration failed"
    a, b = browsers
    assert a.request("/api/auth/player-preferences/", "PATCH", {"volume": 0.37})[0] == 200
    assert a.request("/api/auth/player-preferences/")[1] == {"volume": 0.37}
    assert b.request("/api/auth/player-preferences/")[1] == {}
    status, catalog, headers = a.request("/api/studio/catalog/")
    assert status == 200 and "no-store" in headers["Cache-Control"]
    from apps.studio.models import StudioAsset
    original = StudioAsset.objects.get(pk="composition:still:original").score
    status, content, _ = a.request(f"/api/scores/{original.pk}/file/")
    assert status == 200
    assert hashlib.sha256(content).hexdigest() == original.content_sha256
    assert a.request("/practice/8")[0] == 200, "SPA deep link failed"
    assert a.request("/media/private.json")[0] == 404, "Media directory must stay private"
    assert a.request("/api/auth/logout/", "POST", {})[0] == 200
    assert a.request("/api/auth/session/")[1]["user"] is None
    print("Production smoke passed: secure cookies, CSRF, two-user isolation, catalog, original MIDI, clean URL and logout.")
finally:
    users = get_user_model().objects.filter(username__in=names)
    ids = {str(value) for value in users.values_list("pk", flat=True)}
    for session in Session.objects.filter(expire_date__gt=timezone.now()):
        if str(session.get_decoded().get("_auth_user_id")) in ids:
            session.delete()
    users.delete()
