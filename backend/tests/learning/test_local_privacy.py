from unittest.mock import patch
from django.db import OperationalError
from tests.support import LearnerTestCase as APITestCase
from apps.learning.models import Composition, PracticeSession, Profile
from apps.learning.serializers import ProfileSerializer


class LocalApiPrivacyTests(APITestCase):
    def setUp(self):
        self.profile = Profile.objects.create(pk=1, display_name="Aziz", language="ru", theme="dark")
        self.composition = Composition.objects.create(title="Personal repertoire")

    def test_foreign_site_cannot_modify_profile_or_post_a_session_form(self):
        for headers in [{"HTTP_ORIGIN": "https://unrelated.example"}, {"HTTP_ORIGIN": "null"},
                        {"HTTP_SEC_FETCH_SITE": "cross-site"}]:
            with self.subTest(headers=headers):
                response = self.client.patch("/api/profile/", {"display_name": "Changed"}, format="json", **headers)
                self.assertEqual(response.status_code, 403)
                response = self.client.post("/api/sessions/", {"composition": self.composition.id, "minutes": 30}, **headers)
                self.assertEqual(response.status_code, 403)
        self.profile.refresh_from_db()
        self.assertEqual((self.profile.display_name, self.profile.language, self.profile.theme), ("Aziz", "ru", "dark"))
        self.assertEqual(PracticeSession.objects.count(), 0)

    def test_expected_frontend_same_origin_and_local_cli_requests_remain_available(self):
        for headers in [{"HTTP_ORIGIN": "http://127.0.0.1:5173"}, {"HTTP_ORIGIN": "http://localhost:5174"},
                        {"HTTP_ORIGIN": "http://testserver"}, {}]:
            with self.subTest(headers=headers):
                response = self.client.patch("/api/profile/", {"display_name": "Aziz"}, format="json", **headers)
                self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Cache-Control"], "private, no-store")

    def test_independent_profile_patches_do_not_overwrite_fields_from_stale_snapshots(self):
        name_snapshot = Profile.objects.get(pk=1)
        theme_snapshot = Profile.objects.get(pk=1)
        name = ProfileSerializer(name_snapshot, data={"display_name": "New name"}, partial=True)
        theme = ProfileSerializer(theme_snapshot, data={"theme": "light"}, partial=True)
        name.is_valid(raise_exception=True)
        theme.is_valid(raise_exception=True)
        name.save()
        theme.save()
        self.profile.refresh_from_db()
        self.assertEqual((self.profile.display_name, self.profile.theme, self.profile.language), ("New name", "light", "ru"))
    def test_local_database_failure_has_a_safe_api_response_without_changing_profile(self):
        with patch("apps.learning.serializers.ProfileSerializer.update", side_effect=OperationalError("private path or SQL")):
            response = self.client.patch("/api/profile/", {"display_name": "Unsaved"}, format="json")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private path", str(response.data))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.display_name, "Aziz")
