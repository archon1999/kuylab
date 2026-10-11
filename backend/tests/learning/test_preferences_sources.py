import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from django.conf import settings
from django.core.management import call_command
from django.test import override_settings
from tests.support import LearnerTestCase as APITestCase
from apps.learning.curriculum import DIAGNOSTIC_QUESTIONS
from apps.learning.models import Arrangement, Composition, LearningLesson, Profile
from apps.learning.management.commands.seed_demo import FULL_SOURCE_SHA256


# Historical authoring API behavior; the live curated studio remains read-only.
@override_settings(CURATED_STUDIO_READ_ONLY=False)
class PreferencesAndFullSourceTests(APITestCase):
    def setUp(self):
        self.media = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(self.media.cleanup)
        call_command("seed_pdf_reference", verbosity=0)
        self.composition = Composition.objects.get(seed_key="hes-a-pirate")
        self.arrangement = self.composition.arrangements.first()
        self.base = f"/api/compositions/{self.composition.id}"

    def test_complete_source_is_default_portable_and_all_four_pages_are_served(self):
        data = self.client.get(self.base + "/curriculum/").data
        arrangement = data["arrangement"]
        self.assertEqual(arrangement["id"], self.arrangement.id)
        self.assertEqual(arrangement["workflow_status"], "full_score_ready")
        self.assertEqual(arrangement["page_count"], 4)
        self.assertIsNone(arrangement["tempo_bpm"])
        self.assertEqual(arrangement["tempo_beat_unit"], "")
        self.assertIn("unpianiste.com", arrangement["source_url"])
        self.assertEqual(len(arrangement["full_score_pages"]), 4)
        pdf = self.client.get(arrangement["full_score_file_url"])
        self.assertEqual(pdf.status_code, 200)
        self.assertEqual(pdf["Content-Type"], "application/pdf")
        self.assertEqual(pdf["X-Frame-Options"], "SAMEORIGIN")
        self.assertIn("frame-ancestors 'self'", pdf["Content-Security-Policy"])
        self.assertEqual(hashlib.sha256(b"".join(pdf.streaming_content)).hexdigest(), FULL_SOURCE_SHA256)
        # Exhausting the test client's streaming iterator already closes it.
        # A second close emits request_finished inside TestCase's transaction,
        # closing a PostgreSQL connection that later assertions still need.
        hashes = set()
        for page in arrangement["full_score_pages"]:
            response = self.client.get(page["url"])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "image/png")
            content = b"".join(response.streaming_content)
            self.assertTrue(content.startswith(b"\x89PNG\r\n\x1a\n"))
            hashes.add(hashlib.sha256(content).hexdigest())
        self.assertEqual(len(hashes), 4)
        self.assertEqual(self.client.get(f"/api/arrangements/{self.arrangement.id}/full-score/pages/0/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/arrangements/{self.arrangement.id}/full-score/pages/5/").status_code, 404)
        serialized = str(data["lessons"]) + data["source_notice"]
        for obsolete in ["MN0224234", "Chrissy", "= 120", "To'liq nota yo'q", "to'liq notasiz"]:
            self.assertNotIn(obsolete, serialized)

    def test_partial_render_set_is_never_advertised_as_complete(self):
        (Path(self.media.name) / "reference" / "unpianiste-hes-a-pirate-page-4.png").unlink()
        data = self.client.get(self.base + "/curriculum/").data
        self.assertEqual(data["arrangement"]["full_score_pages"], [])
        self.assertEqual(self.client.get(f"/api/arrangements/{self.arrangement.id}/full-score/pages/1/").status_code, 404)

    def test_media_path_cannot_escape_root(self):
        self.arrangement.full_score_file.name = "../outside.pdf"
        self.arrangement.save(update_fields=["full_score_file"])
        self.assertEqual(self.client.get(f"/api/arrangements/{self.arrangement.id}/full-score/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/arrangements/{self.arrangement.id}/full-score/pages/1/").status_code, 404)

    def test_source_replacement_archives_old_arrangement_without_deleting_history(self):
        # Simulate an existing metadata-only default before the full source seed.
        self.arrangement.delete()
        legacy = Arrangement.objects.create(composition=self.composition, title="My old version",
            source_url="https://www.musicnotes.com/sheetmusic/MN0224234", key_signature="D minor", time_signature="6/8")
        call_command("seed_pdf_reference", verbosity=0)
        legacy.refresh_from_db()
        self.assertFalse(legacy.is_default)
        self.assertEqual(legacy.workflow_status, "archived_source")
        self.assertEqual(legacy.title, "My old version")
        self.assertNotEqual(self.composition.arrangements.first().id, legacy.id)
        call_command("seed_pdf_reference", verbosity=0)
        self.assertEqual(self.composition.arrangements.count(), 2)

    def test_profile_preferences_persist_and_reject_invalid_values(self):
        response = self.client.patch("/api/profile/", {"display_name": "  Ada  ", "language": "ru", "theme": "dark"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["display_name"], "Ada")
        call_command("seed_pdf_reference", verbosity=0)
        saved = self.client.get("/api/profile/").data
        self.assertEqual(saved["language"], "ru")
        self.assertEqual(saved["theme"], "dark")
        self.assertEqual(saved["display_name"], "Ada")
        for payload in [{"display_name": " "}, {"display_name": "A\nB"}, {"language": "xx"}, {"theme": "blue"}]:
            self.assertEqual(self.client.patch("/api/profile/", payload, format="json").status_code, 400)

    def test_all_three_languages_translate_content_without_changing_quiz_identity(self):
        responses = {language: self.client.get(self.base + f"/curriculum/?lang={language}").data for language in ["uz", "ru", "en"]}
        for language, data in responses.items():
            self.assertEqual(data["language"], language)
            self.assertEqual(len(data["lessons"]), 7)
            self.assertEqual([lesson["id"] for lesson in data["lessons"]], [lesson["id"] for lesson in responses["uz"]["lessons"]])
            for original, translated in zip(responses["uz"]["lessons"], data["lessons"]):
                self.assertEqual([question["id"] for question in original["quiz"]["questions"]], [question["id"] for question in translated["quiz"]["questions"]])
                if language != "uz":
                    self.assertNotEqual(original["title"], translated["title"])
                    self.assertTrue(all(block["text"] for block in translated["explanation"]))
            self.assertEqual([question["id"] for question in data["diagnostic"]["questions"]], [question["id"] for question in responses["uz"]["diagnostic"]["questions"]])
        self.assertIn("четыре", responses["ru"]["lessons"][0]["title"])
        self.assertIn("four-page", responses["en"]["lessons"][0]["title"])
        self.assertIn("40", responses["en"]["lessons"][0]["explanation"][1]["text"])
        self.client.patch("/api/profile/", {"language": "ru"}, format="json")
        self.assertEqual(self.client.get(self.base + "/curriculum/").data["language"], "ru")
        self.assertEqual(self.client.get(self.base + "/curriculum/", HTTP_ACCEPT_LANGUAGE="en-US,en;q=0.8,ru;q=0.3").data["language"], "en")
        self.assertEqual(self.client.get(self.base + "/curriculum/?lang=uz", HTTP_ACCEPT_LANGUAGE="ru").data["language"], "uz")
        self.assertEqual(self.client.get(self.base + "/curriculum/?lang=xx").status_code, 400)
        lesson = responses["en"]["lessons"][0]
        stored = LearningLesson.objects.get(pk=lesson["id"])
        answers = {question["id"]: question["correct_choice"] for question in stored.quiz["questions"]}
        submitted = self.client.post(f"/api/lessons/{lesson['id']}/quiz/?lang=en", {"answers": answers}, format="json")
        self.assertEqual(submitted.status_code, 201)
        self.assertEqual(submitted.data["score"], 100)
        self.assertIn("measure 40", submitted.data["feedback"][1]["explanation"])
        diagnostic_answers = {question["id"]: question["correct_choice"] if question["kind"] == "knowledge" else "0" for question in DIAGNOSTIC_QUESTIONS}
        diagnostic = self.client.post(self.base + "/diagnostic/?lang=ru", {"answers": diagnostic_answers}, format="json")
        self.assertEqual(diagnostic.status_code, 201)
        self.assertIn("Обычно", diagnostic.data["feedback"][0]["explanation"])
