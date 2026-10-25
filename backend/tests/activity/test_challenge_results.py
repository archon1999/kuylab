from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class ChallengeResultTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="challenge-owner")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.other = APIClient()
        self.other.force_authenticate(get_user_model().objects.create_user(username="challenge-other"))
        self.key = "theory:triads:challenge:build-major"

    def state(self, **changes):
        return {**self.client.get("/api/activity/state/").data, **changes}

    def test_results_are_private_durable_and_legacy_updates_do_not_clear_them(self):
        self.assertEqual(self.client.patch("/api/activity/state/", self.state(challengeResults={self.key: "correct"}), format="json").status_code, 200)
        fresh = APIClient()
        fresh.force_authenticate(self.user)
        self.assertEqual(fresh.get("/api/activity/state/").data["challengeResults"], {self.key: "correct"})
        self.assertEqual(self.other.get("/api/activity/state/").data["challengeResults"], {})
        old_payload = self.state()
        del old_payload["challengeResults"]
        old_payload["favorites"] = ["theory:triads"]
        self.assertEqual(self.client.patch("/api/activity/state/", old_payload, format="json").status_code, 200)
        self.assertEqual(self.client.get("/api/activity/state/").data["challengeResults"], {self.key: "correct"})

    def test_wrong_answers_can_be_replaced_without_deleting_other_results(self):
        second = "theory:triads:challenge:build-d-major"
        initial = {self.key: "correct", second: "incorrect"}
        self.client.patch("/api/activity/state/", self.state(challengeResults=initial, progress={"theory:triads": "struggling"}), format="json")
        self.client.patch("/api/activity/state/", self.state(challengeResults={**initial, second: "correct"}, progress={"theory:triads": "mastered"}), format="json")
        restored = self.client.get("/api/activity/state/").data
        self.assertEqual(restored["challengeResults"], {self.key: "correct", second: "correct"})
        self.assertEqual(restored["progress"]["theory:triads"], "mastered")

    def test_invalid_or_unbounded_result_payloads_are_rejected(self):
        for results in [{"../../bad": "correct"}, {self.key: "mastered"}, {self.key: {}}, {"q"+str(i): "correct" for i in range(2001)}]:
            self.assertEqual(self.client.patch("/api/activity/state/", self.state(challengeResults=results), format="json").status_code, 400)

    def test_common_study_settings_do_not_change_composition_settings_or_other_users(self):
        common = "/api/auth/player-preferences/?context=study:shared"
        composition = "/api/auth/player-preferences/?context=composition:15:variant:hard"
        self.client.patch(composition, {"speed": .9}, format="json")
        self.assertEqual(self.client.patch(common, {"speed": .7, "volume": 41}, format="json").status_code, 200)
        self.assertEqual(self.client.get(common).data, {"speed": .7, "volume": 41})
        self.assertEqual(self.client.get(composition).data, {"speed": .9})
        self.assertEqual(self.other.get(common).data, {})

    def test_current_curriculum_fits_in_progress_storage_with_a_bounded_limit(self):
        progress = {"stage:"+str(i): "learning" for i in range(700)}
        positions = {key: 2 for key in progress}
        self.assertEqual(self.client.patch("/api/activity/state/", self.state(progress=progress, positions=positions), format="json").status_code, 200)
        self.assertEqual(len(self.client.get("/api/activity/state/").data["progress"]), 700)
        too_many = {"stage:"+str(i): "learning" for i in range(2001)}
        self.assertEqual(self.client.patch("/api/activity/state/", self.state(progress=too_many), format="json").status_code, 400)
