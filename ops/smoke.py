"""Run through manage.py shell inside backend, against the real frontend proxy.

Creates isolated random accounts, checks CSRF/account isolation/MIDI delivery,
then removes only those accounts. Never prints credentials or personal responses.
"""
import hashlib
import json
import secrets
import base64
from html.parser import HTMLParser
import urllib.request
import urllib.error
from http.cookies import SimpleCookie
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils import timezone


class StartupScripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.current = None
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and "src" not in dict(attrs):
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.current is not None:
            self.scripts.append("".join(self.current))
            self.current = None


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
                    if morsel.value and morsel["max-age"] != "0":
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
    status, page, headers = a.request(f"/practice/{original.arrangement.composition_id}")
    assert status == 200, "SPA deep link failed"
    csp = headers["Content-Security-Policy"]
    startup = StartupScripts()
    startup.feed(page.decode())
    assert len(startup.scripts) == 2
    for script in startup.scripts:
        if script.strip():
            digest = base64.b64encode(hashlib.sha256(script.replace("\r\n", "\n").encode()).digest()).decode()
            assert f"'sha256-{digest}'" in csp, "CSP blocks a startup script"
    assert "__BOOT_CSP_HASHES__" not in csp
    status, manifest, _ = a.request("/audio/splendid/manifest.json")
    assert status == 200
    for asset in manifest["files"][:2]:
        status, content, _ = a.request(asset["path"])
        assert status == 200 and hashlib.sha256(content).hexdigest() == asset["sha256"]
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
