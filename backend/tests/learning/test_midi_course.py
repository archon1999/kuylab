import hashlib
import io
import mido
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import parse_qs, urlsplit
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from tests.support import LearnerTestCase as APITestCase
from apps.scores.models import Score
from tests.scores.test_midi import midi_bytes, on, off, end
from apps.learning.curriculum import diagnostic_definitions
from apps.learning.models import Composition, DiagnosticAttempt, LearningLesson, LessonProgress, Profile, QuizAttempt
from apps.learning.serializers import ArrangementSerializer


# Historical authoring API behavior; the live curated studio remains read-only.
@override_settings(CURATED_STUDIO_READ_ONLY=False)
class MidiCourseTests(APITestCase):
    def setUp(self):
        media = TemporaryDirectory()
        override = override_settings(MEDIA_ROOT=media.name)
        override.enable()
        self.addCleanup(media.cleanup)
        self.addCleanup(override.disable)
        call_command("seed_demo", stdout=io.StringIO())
        self.composition = Composition.objects.get(seed_key="hes-a-pirate")
        self.arrangement = self.composition.arrangements.first()
        self.score = self.arrangement.scores.first()
        self.base = f"/api/compositions/{self.composition.id}/curriculum/"

    def curriculum(self, language="uz"):
        response = self.client.get(self.base, {"lang": language})
        self.assertEqual(response.status_code, 200, response.data)
        return response.data

    def test_default_complete_source_bytes_and_status_are_midi_not_demo_or_notation(self):
        data = self.curriculum()
        self.assertEqual(data["readiness"], "composition_ready")
        self.assertEqual(data["arrangement"]["active_score_format"], "midi")
        self.assertEqual(data["arrangement"]["active_score_id"], self.score.id)
        self.assertIsNotNone(data["arrangement"]["active_score_completeness_verified_at"])
        self.assertEqual(data["arrangement"]["full_score_pages"], [])
        score = self.client.get(f"/api/scores/{self.score.id}/").data
        self.assertEqual(score["rights_basis"], "public_download_source")
        self.assertEqual(score["musicxml_url"], "")
        self.assertEqual(score["metadata"]["event_count"], 1255)
        download = self.client.get(score["file_url"])
        self.assertEqual(download.status_code, 200)
        content = b"".join(download.streaming_content)
        self.assertEqual(hashlib.sha256(content).hexdigest(), self.score.content_sha256)
        self.assertEqual(download["Content-Type"], "audio/midi")
        self.assertEqual(self.client.get(f"/api/scores/{self.score.id}/musicxml/").status_code, 404)

    def test_all_six_lessons_use_exact_source_ids_timestamps_and_coherent_clips_in_three_languages(self):
        source_events = {event["id"]: event for event in self.score.parsed["events"]}
        titles = []
        for language in ["uz", "ru", "en"]:
            curriculum = self.curriculum(language)
            self.assertEqual(len(curriculum["lessons"]), 6)
            titles.append(curriculum["lessons"][0]["title"])
            for lesson in curriculum["lessons"]:
                with self.subTest(language=language, lesson=lesson["id"]):
                    exercise = lesson["exercise"]
                    self.assertEqual(exercise["type"], "midi_source_fragment")
                    self.assertFalse(exercise["original"])
                    self.assertEqual(lesson["arrangement_id"], self.arrangement.id)
                    self.assertEqual(exercise["score_id"], self.score.id)
                    self.assertTrue(lesson["explanation"] and lesson["steps"])
                    self.assertTrue(all("correct_choice" not in question for question in lesson["quiz"]["questions"]))
                    start, finish = exercise["start_seconds"], exercise["end_seconds"]
                    expected_ids = {event["id"] for event in source_events.values()
                                    if start - 1e-9 <= event["onset_seconds"] < finish - 1e-9}
                    self.assertEqual(set(exercise["event_ids"]), expected_ids)
                    params = parse_qs(urlsplit(lesson["practice_link"]).query)
                    self.assertEqual(int(params["score"][0]), self.score.id)
                    self.assertEqual(float(params["start_seconds"][0]), start)
                    self.assertEqual(float(params["end_seconds"][0]), finish)
                    self.assertEqual(params["beat_unit"], ["quarter"])
                    fragment_response = self.client.get(exercise["fragment_url"], {"lang": language})
                    self.assertEqual(fragment_response.status_code, 200)
                    fragment = fragment_response.data["parsed"]
                    self.assertEqual(set(event["id"] for event in fragment["events"]), expected_ids)
                    self.assertEqual(fragment["fragment"]["source_score_id"], self.score.id)
                    self.assertEqual(fragment["fragment"]["start_seconds"], start)
                    self.assertAlmostEqual(fragment["metadata"]["duration_seconds"], finish - start)
                    self.assertAlmostEqual(fragment["metadata"]["total_quarters"], exercise["end_quarters"] - exercise["start_quarters"])
                    self.assertEqual(fragment["metadata"]["event_count"], len(expected_ids))
                    self.assertEqual(fragment["metadata"]["part_count"], len(fragment["parts"]))
                    self.assertEqual(fragment["tempo_map"][0]["onset_quarters"], 0)
                    self.assertEqual(fragment["tempo_map"][0]["onset_seconds"], 0)
                    for event in fragment["events"]:
                        original = source_events[event["id"]]
                        self.assertEqual(event["pitch"], original["pitch"])
                        self.assertEqual(event["source_duration_quarters"], original["duration_quarters"])
                        self.assertEqual(event["source_onset_seconds"], original["onset_seconds"])
                        self.assertAlmostEqual(event["onset_seconds"], original["onset_seconds"] - start)
                        self.assertAlmostEqual(event["onset_quarters"], original["onset_quarters"] - exercise["start_quarters"])
                        self.assertGreater(event["duration_quarters"], 0)
                        self.assertLessEqual(event["onset_seconds"] + event["sound_duration_seconds"], finish - start + 1e-8)
        self.assertEqual(len(set(titles)), 3)

    def test_seed_is_idempotent_and_preserves_preferences_quiz_and_source_history(self):
        lesson = LearningLesson.objects.filter(arrangement=self.arrangement).first()
        answers = {question["id"]: question["correct_choice"] for question in lesson.quiz["questions"]}
        self.assertEqual(self.client.post(f"/api/lessons/{lesson.id}/quiz/", {"answers": answers}, format="json").status_code, 201)
        learner = Profile.objects.get(pk=1)
        learner.display_name, learner.language, learner.theme = "Aziz", "ru", "dark"
        learner.save()
        call_command("seed_demo", stdout=io.StringIO())
        self.assertEqual(Score.objects.count(), 1)
        self.assertEqual(Composition.objects.count(), 6)
        self.assertEqual(LearningLesson.objects.filter(arrangement=self.arrangement).count(), 6)
        self.assertEqual(QuizAttempt.objects.get().lesson_id, lesson.id)
        self.assertEqual(LessonProgress.objects.get().quiz_score, 100)
        learner.refresh_from_db()
        self.assertEqual((learner.display_name, learner.language, learner.theme), ("Aziz", "ru", "dark"))

    def test_midi_diagnostic_checks_keyboard_and_timing_without_requiring_staff_notation(self):
        definitions = diagnostic_definitions(self.arrangement)
        answers = {question["id"]: question["correct_choice"] if question["kind"] == "knowledge" else "0" for question in definitions}
        answers["rhythm_self"] = "1"
        titles = []
        for language in ["uz", "ru", "en"]:
            data = self.curriculum(language)
            ids = {question["id"] for question in data["diagnostic"]["questions"]}
            self.assertNotIn("clef", ids)
            self.assertNotIn("reading_self", ids)
            self.assertIn("midi-keyboard", ids)
            self.assertTrue(all("correct_choice" not in question for question in data["diagnostic"]["questions"]))
            titles.append(data["diagnostic"]["questions"][0]["title"])
            response = self.client.post(f"/api/compositions/{self.composition.id}/diagnostic/?lang={language}", {"answers": answers}, format="json")
            self.assertEqual(response.status_code, 201, response.data)
            rhythm = next(skill for skill in response.data["skills"] if skill["id"] == "rhythm")
            self.assertEqual((rhythm["knowledge_score"], rhythm["self_reported_score"]), (100, 0))
        self.assertEqual(len(set(titles)), 3)
        self.assertEqual(DiagnosticAttempt.objects.count(), 3)
        self.assertEqual(DiagnosticAttempt.objects.last().answers, answers)

    def test_opening_rhythm_theory_and_quiz_follow_actual_gaps_not_key_holds(self):
        for language in ["uz", "ru", "en"]:
            first = self.curriculum(language)["lessons"][0]
            stored = LearningLesson.objects.get(pk=first["id"])
            facts = stored.content["midi_facts"]
            self.assertEqual(facts["opening_attacks_quarters"], [0, 1, 1.5, 2.5, 3])
            self.assertEqual(facts["opening_gaps_quarters"], [1, 0.5, 1, 0.5])
            self.assertTrue(facts["compound_long_short"])
            self.assertNotEqual(facts["first_key_duration_quarters"], facts["opening_gaps_quarters"][0])
            self.assertIn("(2 + 1) / (2 + 1)", " ".join(block["text"] for block in first["explanation"]))
            question = next(question for question in stored.quiz["questions"] if question["id"] == "midi-pulse-group")
            self.assertEqual(question["choices"][int(question["correct_choice"])]["label"], "(2 + 1) / (2 + 1)")

    def test_fragment_rebases_tempo_key_meter_and_partial_window_phase(self):
        source = midi_bytes([
            mido.MetaMessage("time_signature", numerator=6, denominator=8),
            mido.MetaMessage("key_signature", key="F"),
            mido.MetaMessage("set_tempo", tempo=500000),
            mido.MetaMessage("set_tempo", tempo=1000000, time=960),
            mido.MetaMessage("time_signature", numerator=3, denominator=4, time=480),
            mido.MetaMessage("key_signature", key="Dm"),
            mido.MetaMessage("set_tempo", tempo=333333, time=480), end(480),
        ], [on(), off(), on(62, 720), off(62, 960), end(240)])
        imported = self.client.post("/api/scores/", {"arrangement_id": self.arrangement.id,
            "file": SimpleUploadedFile("changing.mid", source), "rights_confirmed": True}, format="multipart").data
        event = imported["parsed"]["events"][1]
        start_s = event["onset_seconds"]
        finish_s = start_s + event["duration_seconds"]
        lesson = LearningLesson.objects.create(arrangement=self.arrangement, code="manual-fragment-fixture", order=99,
            title="Exact source fixture", skill="rhythm", score_version_id=imported["id"],
            content={"exercise": {"type": "midi_source_fragment", "start_seconds": start_s, "end_seconds": finish_s,
                                  "start_quarters": 2.5, "end_quarters": 4.5, "event_ids": [event["id"]]}})
        response = self.client.get(f"/api/lessons/{lesson.id}/exercise/?lang=uz")
        self.assertEqual(response.status_code, 200)
        parsed = response.data["parsed"]
        self.assertEqual([(window["start_quarters"], window["length_quarters"]) for window in parsed["measures"]], [(0, .5), (.5, 1.5)])
        self.assertEqual(parsed["measures"][0]["meter_offset_quarters"], 2.5)
        self.assertEqual(parsed["measures"][1]["time"]["beats"], "3")
        self.assertEqual(parsed["tempo_map"][0]["quarter_bpm"], 60)
        self.assertEqual(parsed["tempo_map"][1]["onset_quarters"], 1.5)
        self.assertEqual(parsed["tempo_map"][1]["onset_seconds"], 1.5)
        self.assertEqual(parsed["tempo_map"][1]["onset_ticks"], 720)
        self.assertEqual(parsed["metadata"]["key"]["midi_key"], "F")
        self.assertEqual(parsed["key_signature_map"][1]["midi_key"], "Dm")
        self.assertEqual(parsed["key_signature_map"][1]["onset_quarters"], .5)
        self.assertEqual(parsed["metadata"]["file_end_ticks"], 960)
        self.assertEqual(parsed["events"][0]["start_ticks"], 0)
        self.assertEqual(response.data["sections"], [])

    def test_percussion_only_import_has_no_piano_lesson_and_other_meters_do_not_get_assumed_6_8_pattern(self):
        source = midi_bytes([on(36, channel=9), off(36, channel=9), end()])
        imported = self.client.post("/api/scores/", {"arrangement_id": self.arrangement.id,
            "file": SimpleUploadedFile("drums.mid", source), "rights_confirmed": True}, format="multipart")
        self.assertEqual(imported.status_code, 201)
        self.assertEqual(self.curriculum()["lessons"], [])
        source = midi_bytes([mido.MetaMessage("time_signature", numerator=3, denominator=4), on(), off(), end()])
        imported = self.client.post("/api/scores/", {"arrangement_id": self.arrangement.id,
            "file": SimpleUploadedFile("three-four.mid", source), "rights_confirmed": True}, format="multipart")
        self.assertEqual(imported.status_code, 201)
        first = self.curriculum()["lessons"][0]
        stored = LearningLesson.objects.get(pk=first["id"])
        self.assertFalse(stored.content["midi_facts"]["compound_long_short"])
        self.assertIn("3/4", " ".join(block["text"] for block in first["explanation"]))
        self.assertNotIn("midi-pulse-group", [question["id"] for question in first["quiz"]["questions"]])

    def test_latest_import_has_own_identity_without_inheriting_complete_source_verification(self):
        old_lesson = LearningLesson.objects.filter(arrangement=self.arrangement).first()
        LessonProgress.objects.create(profile_id=1, lesson=old_lesson, quiz_score=100)
        content = midi_bytes([on(), off(), end()])
        response = self.client.post("/api/scores/", {"arrangement_id": self.arrangement.id,
            "file": SimpleUploadedFile("my-version.mid", content), "rights_confirmed": True,
            "exact_version_confirmed": True}, format="multipart")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["version"], 2)
        self.assertIsNone(response.data["completeness_verified_at"])
        data = self.curriculum()
        self.assertEqual(data["arrangement"]["active_score_id"], response.data["id"])
        self.assertEqual(data["arrangement"]["active_score_format"], "midi")
        self.assertIsNone(data["arrangement"]["active_score_completeness_verified_at"])
        self.assertEqual(data["arrangement"]["midi_file_url"], response.data["file_url"])
        self.assertTrue(all(lesson["exercise"]["score_id"] == response.data["id"] for lesson in data["lessons"]))
        for language in ["uz", "ru", "en"]:
            imported_curriculum = self.curriculum(language)
            self.assertTrue(all(lesson["sources"] == [] for lesson in imported_curriculum["lessons"]))
            self.assertTrue(all("Tekshirilgan to'liq manba" not in lesson["context"] and "verified complete source" not in lesson["context"] and "проверенный полный источник" not in lesson["context"] for lesson in imported_curriculum["lessons"]))
        self.assertTrue(all(not lesson["progress"]["quiz_passed"] for lesson in data["lessons"]))
        self.assertTrue(LearningLesson.objects.filter(pk=old_lesson.id).exists())
        self.assertEqual(LessonProgress.objects.get(lesson=old_lesson).quiz_score, 100)
        # A notation source does not advertise a previous MIDI as active download.
        self.score.file_format = "musicxml"
        self.score.version = 3
        self.score.id = None
        self.score.save()
        arrangement = ArrangementSerializer(self.arrangement).data
        self.assertEqual(arrangement["active_score_format"], "musicxml")
        self.assertEqual(arrangement["midi_file_url"], "")

    def test_malformed_midi_and_unsupported_input_do_not_create_versions(self):
        for content in [b"MThd truncated", midi_bytes([on(), end(480)])]:
            response = self.client.post("/api/scores/", {"arrangement_id": self.arrangement.id,
                "file": SimpleUploadedFile("broken.mid", content), "rights_confirmed": True}, format="multipart")
            self.assertEqual(response.status_code, 400)
        self.assertEqual(Score.objects.count(), 1)
        self.assertEqual(self.client.get(self.base, {"arrangement_id": "9" * 80}).status_code, 400)
        self.assertEqual(self.client.post(f"/api/lessons/{LearningLesson.objects.first().id}/quiz/", {"answers": {"invented": "1"}}, format="json").status_code, 400)

    def test_only_known_seed_titles_are_localized_in_lists_overview_and_curriculum(self):
        expected_arrangements = {"uz": "He's a Pirate · to'liq ikki qo'lli piano MIDI",
                                 "en": "He's a Pirate · complete two-hand piano MIDI",
                                 "ru": "He's a Pirate · полный MIDI для двух рук"}
        expected_suffixes = {"uz": "trek tanlanmagan", "en": "track not selected", "ru": "трек не выбран"}
        original_preferences = (Profile.objects.get(pk=1).language, Profile.objects.get(pk=1).theme)
        for language in ["uz", "ru", "en"]:
            data = self.curriculum(language)
            self.assertEqual(data["arrangement"]["title"], expected_arrangements[language])
            overview = self.client.get("/api/overview/", HTTP_ACCEPT_LANGUAGE=language).data
            self.assertEqual(overview["active_composition"]["arrangement"]["title"], expected_arrangements[language])
            self.assertEqual(overview["active_plan"]["arrangement"]["title"], expected_arrangements[language])
            titles = {item["title"] for item in self.client.get("/api/compositions/", {"lang": language}).data}
            self.assertIn(f"Winter Sonata OST — {expected_suffixes[language]}", titles)
            self.assertIn("The Sound of Silence", titles)
            self.assertIn("What Is a Youth", titles)
        self.arrangement.refresh_from_db()
        self.assertEqual(self.arrangement.title, expected_arrangements["uz"])
        self.assertEqual(self.score.content_sha256, "853c5d63d49fdfc685f4215092affa83794298347a52e328ee24fe2ee86da522")
        self.assertEqual((Profile.objects.get(pk=1).language, Profile.objects.get(pk=1).theme), original_preferences)

    def test_custom_titles_are_preserved_even_on_system_seed_records(self):
        self.arrangement.title = "Aziz's selected version"
        self.arrangement.save(update_fields=["title"])
        winter = Composition.objects.get(seed_key="winter-sonata-ost")
        winter.title = "Winter Sonata — my favourite"
        winter.save(update_fields=["title"])
        winter.arrangements.update(title="My winter variation")
        for language in ["uz", "ru", "en"]:
            self.assertEqual(self.curriculum(language)["arrangement"]["title"], "Aziz's selected version")
            item = next(item for item in self.client.get("/api/compositions/", {"lang": language}).data if item["id"] == winter.id)
            self.assertEqual(item["title"], "Winter Sonata — my favourite")
            self.assertEqual(item["arrangement"]["title"], "My winter variation")

    def test_unconfigured_favourite_can_import_midi_and_receive_its_own_curriculum(self):
        favourite = Composition.objects.create(title="My new favourite")
        source = (Path(__file__).resolve().parents[2] / "apps/learning/reference_assets") / "bitmidi-pirate" / "pirate-piano.mid"
        response = self.client.post("/api/scores/", {"composition_id": favourite.id, "rights_confirmed": True,
            "file": SimpleUploadedFile("chosen-full.mid", source.read_bytes())}, format="multipart")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["file_format"], "midi")
        self.assertEqual(favourite.arrangements.count(), 1)
        arrangement = favourite.arrangements.get()
        self.assertEqual(response.data["arrangement_id"], arrangement.id)
        self.assertEqual(response.data["version"], 1)
        curriculum = self.client.get(f"/api/compositions/{favourite.id}/curriculum/?lang=en")
        self.assertEqual(curriculum.status_code, 200)
        self.assertEqual(len(curriculum.data["lessons"]), 6)
        self.assertTrue(all(lesson["exercise"]["score_id"] == response.data["id"] for lesson in curriculum.data["lessons"]))
        self.assertTrue(all(lesson["arrangement_id"] == arrangement.id for lesson in curriculum.data["lessons"]))
        self.assertEqual(self.score.arrangement_id, self.arrangement.id)
        self.assertTrue(Score.objects.filter(pk=self.score.id).exists())
