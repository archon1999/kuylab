from django.test import override_settings
from django.core.management import call_command
from tests.support import LearnerTestCase as APITestCase
from apps.learning.models import Composition, PracticeSession, Profile


# Historical authoring API behavior; the live curated studio remains read-only.
@override_settings(CURATED_STUDIO_READ_ONLY=False)
class LearningApiTests(APITestCase):
    def setUp(self):
        call_command("seed_demo", verbosity=0)
        self.composition = Composition.objects.get(title="He's a Pirate")

    def test_seed_is_idempotent_and_no_fabricated_history(self):
        call_command("seed_demo", verbosity=0)
        response = self.client.get("/api/overview/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["compositions"]), 6)
        self.assertEqual(response.data["stats"]["total_sessions"], 0)
        self.assertFalse(response.data["capabilities"]["automatic_evaluation"])
        self.assertEqual(response.data["active_plan"]["readiness"], "ready")
        self.assertEqual(response.data["active_plan"]["arrangement"]["workflow_status"], "full_midi_ready")
        self.assertEqual(response.data["active_plan"]["arrangement"]["tempo_bpm"], 200)
        self.assertIsNone(response.data["active_plan"]["arrangement"]["page_count"])
        self.assertEqual(response.data["active_plan"]["arrangement"]["full_score_pages"], [])

    def test_create_composition_creates_pending_arrangement_and_plan(self):
        response = self.client.post("/api/compositions/", {
            "title": "Mening asarim", "source_url": "https://example.org/my-version",
            "arrangement_title": "Mening tanlagan versiyam",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["arrangement"]["source_url"], "https://example.org/my-version")
        self.assertEqual(response.data["arrangement"]["rights_status"], "unconfirmed")
        self.assertEqual(response.data["arrangement"]["title"], "Mening tanlagan versiyam")
        plan = self.client.get(f"/api/compositions/{response.data['id']}/plan/")
        self.assertEqual(plan.status_code, 200)
        self.assertEqual(plan.data["readiness"], "needs_arrangement")
        self.assertTrue(plan.data["is_demo"])
        self.assertEqual(len(plan.data["tasks"]), 5)

    def test_session_is_manual_and_updates_real_totals(self):
        response = self.client.post("/api/sessions/", {
            "composition": self.composition.pk, "minutes": 25, "bpm": 72,
            "comfort": 4, "notes": "O'zim baholadim.",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["evidence"], "user_reported")
        self.assertEqual(response.data["input_mode"], "manual")
        self.assertNotIn("accuracy", response.data)
        overview = self.client.get("/api/overview/").data
        self.assertEqual(overview["stats"]["total_minutes"], 25)
        self.assertEqual(overview["stats"]["total_sessions"], 1)

    def test_session_rejects_bad_minutes_bpm_and_fake_accuracy(self):
        for extra in [{"minutes": 0}, {"minutes": 241}, {"bpm": 0}, {"bpm": 300}, {"comfort": 6}, {"accuracy": 98}]:
            data = {"composition": self.composition.pk, "minutes": 10, **extra}
            with self.subTest(extra=extra):
                self.assertEqual(self.client.post("/api/sessions/", data, format="json").status_code, 400)
        self.assertEqual(PracticeSession.objects.count(), 0)

    def test_short_timer_session_preserves_seconds(self):
        response = self.client.post("/api/sessions/", {
            "composition": self.composition.pk, "duration_seconds": 2,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["duration_seconds"], 2)
        self.assertEqual(self.client.get("/api/overview/").data["stats"]["total_minutes"], 0.03)
        for seconds in [0, 14401]:
            self.assertEqual(self.client.post("/api/sessions/", {
                "composition": self.composition.pk, "duration_seconds": seconds,
            }, format="json").status_code, 400)

    def test_profile_and_task_edits_persist(self):
        response = self.client.patch("/api/profile/", {"practice_minutes": 45}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/profile/").data["practice_minutes"], 45)
        task = self.client.get(f"/api/compositions/{self.composition.pk}/plan/").data["tasks"][0]
        response = self.client.patch(f"/api/tasks/{task['id']}/", {"completed": True}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["completed"])

    def test_missing_plan_returns_404(self):
        self.assertEqual(self.client.get("/api/compositions/99999/plan/").status_code, 404)

    def test_seed_preserves_user_practice_minutes(self):
        self.client.patch("/api/profile/", {"practice_minutes": 35}, format="json")
        call_command("seed_demo", verbosity=0)
        self.assertEqual(Profile.objects.get(pk=1).practice_minutes, 35)

    def test_seed_handles_duplicate_composition_titles(self):
        for title in ["He's a Pirate", "The Sound of Silence"]:
            response = self.client.post("/api/compositions/", {"title": title, "arrangement_title": "Boshqa variant"}, format="json")
            self.assertEqual(response.status_code, 201)
        call_command("seed_demo", verbosity=0)
        self.assertEqual(Composition.objects.count(), 8)
        self.assertEqual(Composition.objects.filter(title="He's a Pirate").count(), 2)
