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
    assert len(catalog["compositions"]) == 38 and len(catalog["lessons"]) == 147 and len(catalog["journeys"]) == 91
    assert len(catalog["exercises"]) == 48 and len(catalog["theory"]) == 24
    assert sum(len(item["challenges"]) for item in catalog["theory"]) == 49
    for piece in catalog["compositions"]:
        assert piece["difficulty"] in range(1, 6)
        assert a.request(f"/compositions/{piece['slug']}")[0] == 200
        status, excerpt, _ = a.request(f"/api/studio/compositions/{piece['id']}/preview/")
        assert status == 200 and excerpt["score_id"] == piece["score_id"]
        assert len(excerpt["notes"]) > 10
        assert {note["hand"] for note in excerpt["notes"]} == {"left", "right"}
        assert b.request(f"/api/studio/compositions/{piece['id']}/preview/")[0] == 200
    assert all(task.get("preparation") for item in catalog["theory"] for task in item["challenges"])
    compound = next(item for item in catalog["theory"] if item["id"] == "theory:compound-meter")
    assert len(compound["comparisons"]) == 2 and compound["ready_when"]
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
    result_key = "theory:triads:challenge:build-major"
    state["challengeResults"][result_key] = "correct"
    assert a.request("/api/activity/state/", "PATCH", state)[0] == 200
    assert a.request("/api/activity/state/")[1]["challengeResults"][result_key] == "correct"
    assert b.request("/api/activity/state/")[1]["challengeResults"] == {}
    shared_context = "/api/auth/player-preferences/?context=study%3Ashared"
    assert a.request(shared_context, "PATCH", {"volume": 44, "speed": 0.8})[0] == 200
    assert a.request(shared_context)[1]["volume"] == 44
    assert b.request(shared_context)[1] == {}
    from apps.studio.models import StudioAsset
    from apps.studio.repertoire import SOURCES
    for source in SOURCES:
        source_score = StudioAsset.objects.get(pk=source.asset_key).score
        status, original_bytes, _ = a.request(f"/api/scores/{source_score.pk}/file/")
        assert status == 200 and hashlib.sha256(original_bytes).hexdigest() == source.sha256
        piece = next(item for item in catalog["compositions"] if item["id"] == source_score.arrangement.composition_id)
        paths = [item for item in catalog["journeys"] if item["composition_id"] == piece["id"]]
        expected = (3, 1) if source.course_kind == "curated" else (9, 5) if source.code == "all-in" else (12 if source.code == "still" else 6, 8)
        assert (len(piece["lesson_ids"]), len(paths)) == expected
        assert paths[-1]["stages"][-1]["score_id"] == source_score.pk
        if source.code == "all-in":
            assert len(piece["variants"]) == 2 and piece["default_variant_id"] == "easy"
            for variant in piece["variants"]:
                status, data, _ = a.request(f"/api/scores/{variant['score_id']}/file/")
                assert status == 200 and data.startswith(b"MThd")
                assert a.request(f"/practice/{piece['id']}/variants/{variant['id']}?t=67.04")[0] == 200
            easy_context = f"/api/auth/player-preferences/?context=composition:{piece['id']}:variant:easy"
            hard_context = f"/api/auth/player-preferences/?context=composition:{piece['id']}:variant:hard"
            assert a.request(easy_context, "PATCH", {"speed": 0.65, "compactNoteLengths": False})[0] == 200
            assert a.request(easy_context)[1]["speed"] == 0.65
            assert a.request(easy_context)[1]["compactNoteLengths"] is False
            assert a.request(hard_context)[1] == {} and b.request(easy_context)[1] == {}
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
    print("Production smoke passed: secure cookies, CSRF, two-user isolation, notes, stage progress, variant-scoped preferences, 38 compositions, Easy/Hard MIDI files, complete paths, clean URLs and logout.")
finally:
    users = get_user_model().objects.filter(username__in=names)
    ids = {str(value) for value in users.values_list("pk", flat=True)}
    for session in Session.objects.filter(expire_date__gt=timezone.now()):
        if str(session.get_decoded().get("_auth_user_id")) in ids:
            session.delete()
    users.delete()
