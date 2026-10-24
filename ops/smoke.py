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
    public = Browser()
    status, home, public_headers = public.request("/")
    assert status == 200 and b"boot-screen" not in home, "Public homepage must be prerendered"
    assert b'<html lang="uz"' in home and b'application/ld+json' in home
    assert not public_headers.get("X-Robots-Tag"), "Public homepage must remain indexable"
    public_scripts = StartupScripts()
    public_scripts.feed(home.decode())
    for script in public_scripts.scripts:
        digest = base64.b64encode(hashlib.sha256(script.replace("\r\n", "\n").encode()).digest()).decode()
        assert f"'sha256-{digest}'" in public_headers["Content-Security-Policy"], "CSP blocks public-page scripts"
    status, robots, robot_headers = public.request("/robots.txt")
    assert status == 200 and b"Sitemap: https://kuylab.uz/sitemap.xml" in robots
    assert "text/plain" in robot_headers["Content-Type"]
    status, sitemap, _ = public.request("/sitemap.xml")
    assert status == 200 and sitemap.count(b"<loc>") == 15 and b"/studio" not in sitemap
    for path in ["/musiqa-nazariyasi/", "/ru/", "/en/learn-piano/"]:
        status, page, _ = public.request(path)
        assert status == 200 and b'<h1>' in page and b'boot-screen' not in page
    status, missing, _ = public.request("/not-a-real-public-page/")
    assert status == 404 and b"noindex" in missing, "Unknown public URLs need a real branded 404"
    status, studio, studio_headers = public.request("/studio")
    assert status == 200 and b"boot-screen" in studio and "noindex" in studio_headers["X-Robots-Tag"]
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
    assert len(catalog["journeys"]) == 8 and sum(len(item["challenges"]) for item in catalog["theory"]) == 19
    note_path = "/api/activity/notes/"
    status, note, _ = a.request(note_path, "POST", {"contentId": "theory:triads", "position": 2.5, "text": "Deployment notebook check"})
    assert status == 201 and note["position"] == 2.5
    assert b.request(note_path)[1] == []
    target = note_path + note["id"] + "/"
    assert b.request(target, "PATCH", {"text": "Other account"})[0] == 404
    assert a.request(target, "PATCH", {"text": "Edited notebook check"})[0] == 200
    assert a.request(target, "DELETE")[0] == 204
    assert a.request(target, "PATCH", {"deleted": False})[0] == 200
    context_path = "/api/auth/player-preferences/?context=theory%3Atriads"
    assert a.request(context_path, "PATCH", {"speed": 0.7, "left": False})[0] == 200
    assert a.request(context_path)[1]["speed"] == 0.7 and b.request(context_path)[1] == {}
    state = a.request("/api/activity/state/")[1]
    stage_id = catalog["journeys"][-1]["stages"][0]["id"]
    state["progress"][stage_id] = "learning"
    state["comfortableSpeeds"][stage_id] = 65
    assert a.request("/api/activity/state/", "PATCH", state)[0] == 200
    assert a.request("/api/activity/state/")[1]["comfortableSpeeds"][stage_id] == 65
    assert b.request("/api/activity/state/")[1]["comfortableSpeeds"] == {}
    from apps.studio.models import StudioAsset
    original = StudioAsset.objects.get(pk="composition:still:original").score
    status, content, _ = a.request(f"/api/scores/{original.pk}/file/")
    assert status == 200
    assert hashlib.sha256(content).hexdigest() == original.content_sha256
    status, page, headers = a.request(f"/practice/{original.arrangement.composition_id}")
    assert status == 200, "SPA deep link failed"
    assert "noindex" in headers["X-Robots-Tag"], "Private studio routes must not be indexed"
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
    print("Production smoke passed: secure cookies, CSRF, two-user isolation, notes, stage progress, scoped preferences, catalog, original MIDI, clean URL and logout.")
finally:
    users = get_user_model().objects.filter(username__in=names)
    ids = {str(value) for value in users.values_list("pk", flat=True)}
    for session in Session.objects.filter(expire_date__gt=timezone.now()):
        if str(session.get_decoded().get("_auth_user_id")) in ids:
            session.delete()
    users.delete()
