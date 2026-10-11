from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import OperationalError
from django.test import override_settings
from tests.support import LearnerTestCase as APITestCase
from apps.learning.models import Arrangement, Composition
from apps.scores.models import Score


# Historical authoring API behavior; the live curated studio remains read-only.
@override_settings(CURATED_STUDIO_READ_ONLY=False)
class ScoreBoundaryTests(APITestCase):
    def setUp(self):
        media = TemporaryDirectory()
        override = override_settings(MEDIA_ROOT=media.name)
        override.enable()
        self.addCleanup(media.cleanup)
        self.addCleanup(override.disable)
        self.media = Path(media.name)
        self.arrangement = Arrangement.objects.create(composition=Composition.objects.create(title="Boundary fixture"))
        self.content = (Path(__file__).resolve().parents[2] / "apps/scores/demo.musicxml").read_bytes()

    def upload(self, **fields):
        return self.client.post("/api/scores/", {"arrangement_id": self.arrangement.id,
            "rights_confirmed": True, "file": SimpleUploadedFile("fixture.musicxml", self.content), **fields}, format="multipart")

    def test_non_object_json_gets_400_instead_of_internal_error(self):
        score = self.upload().data
        for url in ["/api/scores/", f"/api/scores/{score['id']}/"]:
            for payload in [23, [{"title": "not an object"}], [None], "text"]:
                with self.subTest(url=url, payload=payload):
                    response = self.client.post(url, payload, format="json") if url == "/api/scores/" else self.client.patch(url, payload, format="json")
                    self.assertEqual(response.status_code, 400)
        self.assertEqual(Score.objects.count(), 1)

    def test_huge_or_non_integer_arrangement_id_has_no_database_overflow_or_coercion(self):
        for identifier in ["9" * 80, "1.5", "-1", "0", "True"]:
            with self.subTest(identifier=identifier):
                self.assertEqual(self.upload(arrangement_id=identifier).status_code, 400)
        self.assertEqual(Score.objects.count(), 0)

    def test_storage_failure_and_database_failure_leave_no_version_or_orphan_import(self):
        with patch("django.core.files.storage.FileSystemStorage._save", side_effect=PermissionError("private local path")):
            response = self.upload()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private local path", str(response.data))
        self.assertEqual(Score.objects.count(), 0)
        with patch("apps.scores.models.Score.save", side_effect=OperationalError("database is locked")):
            response = self.upload()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(Score.objects.count(), 0)
        self.assertEqual([path for path in self.media.rglob("*") if path.is_file()], [])
        self.assertEqual(self.upload().status_code, 201)

    def test_unreadable_file_returns_safe_error_and_missing_file_remains_404(self):
        score = self.upload().data
        for url in [score["file_url"], score["musicxml_url"]]:
            with patch("django.core.files.storage.FileSystemStorage._open", side_effect=PermissionError("private path")):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 503)
            self.assertNotIn("private path", str(response.data))
            with patch("django.core.files.storage.FileSystemStorage._open", side_effect=FileNotFoundError("private path")):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_first_import_by_composition_atomically_creates_and_reuses_one_arrangement(self):
        composition = Composition.objects.create(title="My favourite")
        before = self.client.get("/api/compositions/").data
        self.assertIsNone(next(item for item in before if item["id"] == composition.id)["arrangement"])
        self.assertFalse(composition.arrangements.exists())
        def import_for_composition():
            return self.client.post("/api/scores/", {"composition_id": composition.id, "rights_confirmed": True,
                "title": "My exact version", "source_url": "https://example.org/source",
                "file": SimpleUploadedFile("fixture.musicxml", self.content)}, format="multipart")
        first = import_for_composition()
        second = import_for_composition()
        self.assertEqual(first.status_code, 201, first.data)
        self.assertEqual(second.status_code, 201, second.data)
        self.assertEqual((first.data["version"], second.data["version"]), (1, 2))
        self.assertEqual(first.data["arrangement_id"], second.data["arrangement_id"])
        self.assertEqual(composition.arrangements.count(), 1)
        self.assertEqual(composition.arrangements.get().source_url, "https://example.org/source")
        self.assertIsNone(first.data["completeness_verified_at"])
        self.assertTrue(Score.objects.filter(pk=first.data["id"]).exists())

    def test_composition_target_requires_one_target_and_failed_import_never_leaves_an_arrangement(self):
        composition = Composition.objects.create(title="Unconfigured favourite")
        for targets in [{}, {"composition_id": composition.id, "arrangement_id": self.arrangement.id}]:
            response = self.client.post("/api/scores/", {"rights_confirmed": True,
                "file": SimpleUploadedFile("fixture.musicxml", self.content), **targets}, format="multipart")
            self.assertEqual(response.status_code, 400)
        with patch("apps.scores.models.Score.save", side_effect=OperationalError("database is locked")):
            response = self.client.post("/api/scores/", {"composition_id": composition.id, "rights_confirmed": True,
                "file": SimpleUploadedFile("fixture.musicxml", self.content)}, format="multipart")
        self.assertEqual(response.status_code, 503)
        self.assertFalse(composition.arrangements.exists())
        self.assertEqual(Score.objects.count(), 0)
        self.assertEqual([path for path in self.media.rglob("*") if path.is_file()], [])
