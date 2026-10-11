from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
from xml.etree import ElementTree as ET
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from tests.support import LearnerTestCase as APITestCase
from apps.learning.adaptive import allocate_minutes
from apps.learning.curriculum import DIAGNOSTIC_QUESTIONS
from apps.learning.exercises import drill_xml
from apps.learning.models import Composition, DiagnosticAttempt, LearningLesson, LessonPracticeAttempt, LessonProgress, Profile, QuizAttempt


# Historical authoring API behavior; the live curated studio remains read-only.
@override_settings(CURATED_STUDIO_READ_ONLY=False)
class TeachingApiTests(APITestCase):
    def setUp(self):
        self.media = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(self.media.cleanup)
        call_command("seed_pdf_reference", verbosity=0)
        self.composition = Composition.objects.get(seed_key="hes-a-pirate")
        self.arrangement = self.composition.arrangements.first()
        self.base = f"/api/compositions/{self.composition.pk}"

    def curriculum(self):
        response = self.client.get(self.base + "/curriculum/")
        self.assertEqual(response.status_code, 200)
        return response.data

    def quiz_answers(self, lesson):
        return {question["id"]: question["correct_choice"] for question in LearningLesson.objects.get(pk=lesson["id"]).quiz["questions"]}

    def import_score(self, fifths=0, mode="major", signature="4/4", notes=None):
        content = {"exercise": {"notes": notes or ["C4", "E4", "G4", "C5"], "key_signature": {"fifths": fifths, "mode": mode}, "time_signature": signature}}
        xml = drill_xml(SimpleNamespace(title="Original import fixture", content=content))
        response = self.client.post("/api/scores/", {"arrangement_id": self.arrangement.id,
                                    "file": SimpleUploadedFile("original.musicxml", xml), "rights_confirmed": True,
                                    "exact_version_confirmed": True}, format="multipart")
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def test_curriculum_is_arrangement_bound_substantive_and_does_not_leak_answers(self):
        data = self.curriculum()
        self.assertEqual(data["readiness"], "preparation")
        self.assertEqual(len(data["lessons"]), 7)
        self.assertTrue(all(lesson["arrangement_id"] == self.arrangement.id for lesson in data["lessons"]))
        self.assertEqual(sum(lesson["exercise"]["original"] for lesson in data["lessons"]), 6)
        self.assertEqual(data["lessons"][0]["exercise"]["type"], "pdf_source_excerpt")
        self.assertTrue(all(lesson["explanation"] and lesson["steps"] and lesson["quiz"]["questions"] for lesson in data["lessons"]))
        self.assertTrue(all(skill["score"] is None for skill in data["skills"]))
        self.assertIsNone(data["diagnostic"]["latest_attempt"])
        for lesson in data["lessons"]:
            for question in lesson["quiz"]["questions"]:
                self.assertNotIn("correct_choice", question)
                self.assertNotIn("explanation", question)
        for question in data["diagnostic"]["questions"]:
            self.assertNotIn("correct_choice", question)

    def test_each_original_drill_has_real_distinct_notation_and_duration(self):
        drills = []
        for lesson in self.curriculum()["lessons"]:
            if not lesson["exercise"]["original"]:
                continue
            response = self.client.get(lesson["exercise"]["score_url"])
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.data["is_demo"])
            self.assertEqual(response.data["rights_basis"], "original_cc0")
            events = [event for event in response.data["parsed"]["events"] if not event["rest"]]
            self.assertTrue(events)
            self.assertTrue(all(event["duration_quarters"] > 0 for event in events))
            drills.append(tuple(event["pitch"]["midi"] for event in events))
            xml = self.client.get(response.data["musicxml_url"])
            self.assertEqual(xml.status_code, 200)
            self.assertIn(b"Original exercise authored", xml.content)
            if lesson["code"] == "compound-pulse":
                self.assertEqual(drills[-1], (62,) * 6)
                self.assertEqual(response.data["metadata"]["tempo"]["bpm"], 50)
                self.assertEqual(response.data["metadata"]["tempo"]["quarter_bpm"], 75)
            if lesson["code"] == "hands-meeting":
                self.assertEqual({event["hand"] for event in events}, {"left", "right"})
        self.assertEqual(len(set(drills)), 6)

    def test_diagnostic_persists_distinct_knowledge_self_report_and_changes_order(self):
        answers = {question["id"]: question["correct_choice"] if question["kind"] == "knowledge" else "4" for question in DIAGNOSTIC_QUESTIONS}
        answers["rhythm_self"] = "1"
        response = self.client.post(self.base + "/diagnostic/", {"answers": answers}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(DiagnosticAttempt.objects.get().answers, answers)
        data = self.curriculum()
        rhythm = next(skill for skill in data["skills"] if skill["id"] == "rhythm")
        self.assertEqual(rhythm["knowledge_score"], 100)
        self.assertEqual(rhythm["self_reported_score"], 0)
        first = data["adaptive_plan"]["items"][0]
        self.assertEqual(LearningLesson.objects.get(pk=first["lesson_id"]).kind, "source_excerpt")
        rhythm_item = data["adaptive_plan"]["items"][1]
        self.assertEqual(LearningLesson.objects.get(pk=rhythm_item["lesson_id"]).skill, "rhythm")
        self.assertIn("0/100", rhythm_item["reason"])
        self.assertEqual(data["diagnostic"]["latest_attempt"]["answers"], answers)

    def test_unknown_self_report_stays_unassessed(self):
        answers = {question["id"]: question["correct_choice"] if question["kind"] == "knowledge" else "0" for question in DIAGNOSTIC_QUESTIONS}
        response = self.client.post(self.base + "/diagnostic/", {"answers": answers}, format="json")
        self.assertEqual(response.status_code, 201)
        coordination = next(skill for skill in response.data["skills"] if skill["id"] == "coordination")
        self.assertIsNone(coordination["score"])
        self.assertEqual(coordination["evidence"], "not_assessed")

    def test_quiz_correctness_latest_evidence_and_no_automatic_performance_mastery(self):
        lesson = self.curriculum()["lessons"][0]
        response = self.client.post(f"/api/lessons/{lesson['id']}/quiz/", {"answers": self.quiz_answers(lesson)}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["score"], 100)
        self.assertTrue(all(item["correct"] for item in response.data["feedback"]))
        self.assertFalse(response.data["progress"]["drill_completed"])
        self.assertIsNone(response.data["progress"]["review_due_at"])
        wrong = {question["id"]: next(choice["id"] for choice in question["choices"] if choice["id"] != question["correct_choice"]) for question in LearningLesson.objects.get(pk=lesson["id"]).quiz["questions"]}
        response = self.client.post(f"/api/lessons/{lesson['id']}/quiz/", {"answers": wrong}, format="json")
        self.assertEqual(response.data["score"], 0)
        self.assertFalse(response.data["progress"]["quiz_passed"])
        self.assertEqual(QuizAttempt.objects.count(), 2)

    def test_retention_requires_delayed_quiz_and_practice_not_repeated_clicks(self):
        lesson = self.curriculum()["lessons"][0]
        quiz_url = f"/api/lessons/{lesson['id']}/quiz/"
        practice_url = f"/api/lessons/{lesson['id']}/practice/"
        now = timezone.now()
        with patch("apps.learning.teaching_views.timezone.now", return_value=now):
            self.client.post(quiz_url, {"answers": self.quiz_answers(lesson)}, format="json")
            response = self.client.post(practice_url, {"successful_repetitions": 3, "comfort": 4, "bpm": 50, "reflection": "Ikki katta puls qulay."}, format="json")
            self.assertEqual(response.data["progress"]["status"], "ready_for_review")
            self.assertEqual(response.data["progress"]["evidence"], "quiz_and_self_report")
            self.assertEqual(LessonProgress.objects.get().review_due_at, now + timedelta(days=2))
            repeat = self.client.post(practice_url, {"successful_repetitions": 3, "comfort": 5}, format="json")
            self.assertEqual(repeat.data["progress"]["review_count"], 0)
        future = now + timedelta(days=3)
        with patch("apps.learning.teaching_views.timezone.now", return_value=future):
            response = self.client.post(practice_url, {"successful_repetitions": 3, "comfort": 5}, format="json")
            self.assertEqual(response.data["progress"]["review_count"], 0)
            self.client.post(quiz_url, {"answers": self.quiz_answers(lesson)}, format="json")
            response = self.client.post(practice_url, {"successful_repetitions": 3, "comfort": 5}, format="json")
            self.assertEqual(response.data["progress"]["review_count"], 1)
            self.assertEqual(response.data["progress"]["status"], "retained")
            self.assertEqual(LessonProgress.objects.get().review_due_at, future + timedelta(days=7))
        self.assertEqual(LessonPracticeAttempt.objects.count(), 4)

    def test_minutes_exact_and_source_pending_does_not_invent_hours_of_teaching(self):
        for minutes in [5, 7, 15, 30, 45, 180]:
            response = self.client.get(self.base + f"/adaptive-plan/?minutes={minutes}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(sum(item["minutes"] for item in response.data["items"]), minutes)
            self.assertTrue(all(item["minutes"] > 0 for item in response.data["items"]))
        Profile.objects.filter(pk=1).update(practice_minutes=17)
        self.assertEqual(self.client.get(self.base + "/adaptive-plan/").data["minutes"], 17)
        pending = Composition.objects.get(seed_key="naruto-ost")
        data = self.client.get(f"/api/compositions/{pending.id}/curriculum/").data
        self.assertEqual(data["readiness"], "source_pending")
        self.assertEqual([lesson["kind"] for lesson in data["lessons"]], ["source"])
        self.assertEqual(data["lessons"][0]["quiz"]["questions"], [])
        response = self.client.get(f"/api/compositions/{pending.id}/adaptive-plan/?minutes=180")
        self.assertEqual(response.data["minutes"], 10)
        self.assertEqual(response.data["requested_minutes"], 180)

    def test_safe_invalid_input_never_creates_attempts(self):
        lesson = self.curriculum()["lessons"][0]
        for payload in [{"answers": {}}, {"answers": {"unknown": "0"}}, {"answers": "wrong"}, {"answers": self.quiz_answers(lesson), "score": 100}, []]:
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post(f"/api/lessons/{lesson['id']}/quiz/", payload, format="json").status_code, 400)
        for payload in [{"successful_repetitions": 4, "comfort": 4}, {"successful_repetitions": 3, "comfort": 6}, {"successful_repetitions": 3, "comfort": 4, "evidence": "midi"}, {"successful_repetitions": 3, "comfort": 4, "bpm": 999}]:
            self.assertEqual(self.client.post(f"/api/lessons/{lesson['id']}/practice/", payload, format="json").status_code, 400)
        for minutes in [0, 4, 181, "oops"]:
            self.assertEqual(self.client.get(self.base + f"/adaptive-plan/?minutes={minutes}").status_code, 400)
        self.assertEqual(self.client.get(self.base + "/curriculum/?arrangement_id=oops").status_code, 400)
        self.assertEqual(self.client.get(self.base + "/curriculum/?arrangement_id=99999").status_code, 404)
        self.assertEqual(self.client.get(self.base + "/curriculum/?arrangement_id=" + "9" * 100).status_code, 400)
        self.assertEqual(QuizAttempt.objects.count(), 0)
        self.assertEqual(LessonPracticeAttempt.objects.count(), 0)

    def test_imported_key_meter_drills_focus_links_and_score_version_progress_isolation(self):
        score = self.import_score(fifths=-4, mode="minor", signature="3/4", notes=["F4", "A♭4", "C5"])
        data = self.curriculum()
        self.assertEqual(data["score_binding"]["score_id"], score["id"])
        harmony = next(lesson for lesson in data["lessons"] if lesson["skill"] == "harmony")
        self.assertIn("F minor", harmony["title"])
        self.assertEqual(harmony["exercise"]["notes"][:4], ["F4", "G4", "A♭4", "B♭4"])
        rhythm = next(lesson for lesson in data["lessons"] if lesson["skill"] == "rhythm")
        self.assertIn("3/4", rhythm["title"])
        hands = next(lesson for lesson in data["lessons"] if lesson["skill"] == "coordination")
        self.assertEqual(hands["exercise"]["time_signature"], "3/4")
        self.assertEqual(hands["exercise"]["notes"][:3], ["F4", "A♭4", "C5"])
        self.client.post(f"/api/lessons/{harmony['id']}/quiz/", {"answers": self.quiz_answers(harmony)}, format="json")
        score2 = self.import_score()
        data2 = self.curriculum()
        harmony2 = next(lesson for lesson in data2["lessons"] if lesson["skill"] == "harmony")
        self.assertNotEqual(harmony["id"], harmony2["id"])
        self.assertEqual(harmony2["score_version_id"], score2["id"])
        self.assertIsNone(harmony2["progress"]["quiz_score"])
        self.assertEqual(harmony2["exercise"]["notes"][:3], ["C4", "D4", "E4"])
        response = self.client.patch(f"/api/scores/{score2['id']}/", {"sections": [{"id": "transition", "title": "Mening o'tishim", "start_index": 0, "end_index": 0}]}, format="json")
        self.assertEqual(response.status_code, 200)
        data3 = self.curriculum()
        self.assertTrue(all("section=transition" in lesson["practice_link"] for lesson in data3["lessons"]))
        self.assertTrue(all("Mening o'tishim" in lesson["context"] for lesson in data3["lessons"]))

    def test_same_score_focus_key_change_creates_new_lesson_and_does_not_keep_old_mastery(self):
        xml = drill_xml(SimpleNamespace(title="Original key change fixture", content={"exercise": {"notes": ["D4", "F4", "A4", "D5", "C4", "E4", "G4", "C5"], "key_signature": {"fifths": -1, "mode": "minor"}}}))
        tree = ET.fromstring(xml)
        measure = tree.find("part").findall("measure")[1]
        attributes = ET.Element("attributes")
        key = ET.SubElement(attributes, "key")
        ET.SubElement(key, "fifths").text = "0"
        ET.SubElement(key, "mode").text = "major"
        measure.insert(0, attributes)
        response = self.client.post("/api/scores/", {"arrangement_id": self.arrangement.id, "file": SimpleUploadedFile("original-key-change.musicxml", ET.tostring(tree)), "rights_confirmed": True}, format="multipart")
        self.assertEqual(response.status_code, 201)
        score_id = response.data["id"]
        before = self.curriculum()
        harmony = next(lesson for lesson in before["lessons"] if lesson["skill"] == "harmony")
        self.assertIn("D minor", harmony["title"])
        self.client.post(f"/api/lessons/{harmony['id']}/quiz/", {"answers": self.quiz_answers(harmony)}, format="json")
        self.client.patch(f"/api/scores/{score_id}/", {"sections": [{"id": "new-key", "title": "Keyingi tonallik", "start_index": 1, "end_index": 1}]}, format="json")
        after = self.curriculum()
        harmony2 = next(lesson for lesson in after["lessons"] if lesson["skill"] == "harmony")
        self.assertIn("C major", harmony2["title"])
        self.assertNotEqual(harmony["id"], harmony2["id"])
        self.assertIsNone(harmony2["progress"]["quiz_score"])
        self.assertEqual(harmony2["exercise"]["notes"][:3], ["C4", "D4", "E4"])

    def test_single_treble_flat_pitch_does_not_change_authored_hand(self):
        self.import_score(fifths=-7, mode="major", notes=["C♭4", "E♭4", "G♭4", "C♭5"])
        harmony = next(lesson for lesson in self.curriculum()["lessons"] if lesson["skill"] == "harmony")
        response = self.client.get(harmony["exercise"]["score_url"])
        self.assertEqual(response.status_code, 200)
        events = [event for event in response.data["parsed"]["events"] if not event["rest"]]
        self.assertEqual(events[0]["pitch"]["midi"], 59)
        self.assertEqual(response.data["hand_overrides"][events[0]["id"]], "right")

    def test_source_excerpt_teaches_real_import_events_and_is_first_recommendation(self):
        xml = (Path(__file__).resolve().parents[2] / "apps/scores/demo.musicxml").read_bytes()
        response = self.client.post("/api/scores/", {"arrangement_id": self.arrangement.id,
                                    "file": SimpleUploadedFile("original-source-fixture.musicxml", xml),
                                    "rights_confirmed": True, "exact_version_confirmed": False}, format="multipart")
        self.assertEqual(response.status_code, 201)
        score_id = response.data["id"]
        data = self.curriculum()
        source = next(lesson for lesson in data["lessons"] if lesson["kind"] == "source_excerpt")
        self.assertEqual(len(data["lessons"]), 7)
        self.assertFalse(source["exercise"]["original"])
        self.assertEqual(source["exercise"]["score_url"], f"/api/scores/{score_id}/")
        self.assertEqual(source["exercise"]["start_index"], 0)
        self.assertEqual(source["exercise"]["end_index"], 1)
        self.assertIn("start_index=0", source["practice_link"])
        self.assertIn("end_index=1", source["practice_link"])
        self.assertIn("bpm=40", source["practice_link"])
        self.assertIn("beat_unit=quarter", source["practice_link"])
        self.assertEqual(source["exercise"]["bpm"], 40)
        self.assertEqual(source["exercise"]["beat_unit"], "quarter")
        self.assertNotIn("Original mashq", source["context"])
        self.assertIn("1-versiya", source["context"])
        self.assertIn("1, 2 raqamli", source["context"])
        self.assertIn("nota yozuvi", source["explanation"][0]["text"])
        self.assertNotIn("pitch hodisasi", source["explanation"][0]["text"])
        self.assertNotIn("ijro sifati", source["explanation"][0]["text"])
        self.assertNotIn("avtomatik", source["success_criterion"])
        self.assertNotIn("avtomatik", source["transfer"])
        self.assertTrue(all("bpm=" not in lesson["practice_link"] for lesson in data["lessons"] if lesson["kind"] != "source_excerpt"))
        analysis = source["source_analysis"]
        self.assertEqual(analysis["provenance"], "imported_musicxml_events")
        self.assertEqual(analysis["facts"]["pitched_note_count"], 16)
        self.assertEqual(analysis["facts"]["attack_count"], 15)
        self.assertEqual(analysis["facts"]["chord_group_count"], 4)
        self.assertEqual(analysis["facts"]["tie_count"], 2)
        self.assertEqual(analysis["facts"]["rest_count"], 0)
        self.assertFalse(analysis["claims"]["fingering_inferred"])
        self.assertFalse(analysis["claims"]["performance_assessed"])
        self.assertEqual(source["steps"][2]["tempo"]["beat_unit"], "quarter")
        self.assertEqual(source["steps"][2]["basis"], "practice_choice")
        self.assertEqual(data["adaptive_plan"]["items"][0]["lesson_id"], source["id"])
        self.assertIn("Asosiy maqsad", data["adaptive_plan"]["items"][0]["reason"])
        self.assertIn("hali siz tomonidan tasdiqlanmagan", source["context"])
        quiz = self.client.post(f"/api/lessons/{source['id']}/quiz/", {"answers": self.quiz_answers(source)}, format="json")
        self.assertEqual(quiz.status_code, 201)
        self.assertEqual(quiz.data["score"], 100)
        self.assertFalse(quiz.data["progress"]["drill_completed"])
        first_right = next(event for event in response.data["parsed"]["events"] if event["pitch"] and event["hand"] == "right")
        updated = self.client.patch(f"/api/scores/{score_id}/", {"hand_overrides": {first_right["id"]: "left"}}, format="json")
        self.assertEqual(updated.status_code, 200)
        refreshed = next(lesson for lesson in self.curriculum()["lessons"] if lesson["kind"] == "source_excerpt")
        self.assertEqual(refreshed["id"], source["id"])
        self.assertEqual(refreshed["source_analysis"]["facts"]["hand_counts"]["left"], analysis["facts"]["hand_counts"]["left"] + 1)
        self.assertEqual(refreshed["source_analysis"]["facts"]["hand_counts"]["right"], analysis["facts"]["hand_counts"]["right"] - 1)
        self.assertEqual(refreshed["progress"]["quiz_score"], 100)

    def test_seed_keeps_stable_identity_after_rename_and_existing_progress(self):
        lesson = self.curriculum()["lessons"][0]
        self.client.post(f"/api/lessons/{lesson['id']}/quiz/", {"answers": self.quiz_answers(lesson)}, format="json")
        self.composition.title = "Mening pirate variantim"
        self.composition.save(update_fields=["title"])
        call_command("seed_pdf_reference", verbosity=0)
        self.assertEqual(Composition.objects.count(), 6)
        self.assertEqual(Composition.objects.get(seed_key="hes-a-pirate").title, "Mening pirate variantim")
        self.assertEqual(LessonProgress.objects.get(lesson_id=lesson["id"]).quiz_score, 100)

    def test_authored_editorial_correction_refreshes_without_losing_quiz_progress(self):
        harmony = next(lesson for lesson in self.curriculum()["lessons"] if lesson["code"] == "d-minor-map")
        self.client.post(f"/api/lessons/{harmony['id']}/quiz/", {"answers": self.quiz_answers(harmony)}, format="json")
        stored = LearningLesson.objects.get(pk=harmony["id"])
        stored.content["explanation"][2]["text"] = "C tabiiy minor tarkibida; eski noaniq matn."
        stored.save(update_fields=["content"])
        refreshed = next(lesson for lesson in self.curriculum()["lessons"] if lesson["code"] == "d-minor-map")
        self.assertIn("D tabiiy minor gammasida C bor", refreshed["explanation"][2]["text"])
        self.assertIn("D garmonik minor gammasida", refreshed["explanation"][2]["text"])
        self.assertEqual(refreshed["id"], harmony["id"])
        self.assertEqual(refreshed["progress"]["quiz_score"], 100)
        self.assertEqual(QuizAttempt.objects.filter(lesson_id=harmony["id"]).count(), 1)

    def test_allocation_largest_remainder(self):
        self.assertEqual(allocate_minutes(9, [1, 1, 1]), [3, 3, 3])
        self.assertEqual(sum(allocate_minutes(17, [3, 5, 7])), 17)
        with self.assertRaises(ValueError):
            allocate_minutes(1, [1, 2])
