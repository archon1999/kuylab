import hashlib
from django.test import SimpleTestCase
from apps.scores.midi import parse_midi
from apps.studio.content import localize
from apps.studio.midi_authoring import lesson_stage_midi
from apps.studio.repertoire import SOURCES, repertoire_source
from apps.studio.repertoire_studies import repertoire_items


class RepertoireSourceTests(SimpleTestCase):
    def test_all_original_bytes_notes_and_unknown_metadata_are_preserved(self):
        counts = {"youth": 833, "star": 597, "tears": 688, "my-memory": 1058,
                  "premonition": 784, "memories": 500}
        for source in SOURCES[1:]:
            raw, parsed = repertoire_source(source.code)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), source.sha256)
            self.assertEqual(len(parsed["events"]), counts[source.code])
            self.assertIsNone(parsed["metadata"]["key"])
            self.assertIsNone(parsed["metadata"]["time"])
            self.assertEqual(parsed["pedal_events"], [])
            self.assertEqual({event["hand_evidence"] for event in parsed["events"]}, {"curated_track_role_inference"})
            self.assertEqual(SOURCES[-1].composer, "")
            self.assertEqual(SOURCES[-1].title, "Memories")

    def test_every_piece_has_specific_localized_lessons_and_a_complete_path(self):
        items = repertoire_items()
        self.assertEqual(len(items), 84)
        self.assertEqual(len({item["id"] for item in items}), 84)
        for source in SOURCES[1:]:
            selected = [item for item in items if item["_composition"] == source.code]
            lessons = [item for item in selected if item["kind"] == "lesson"]
            paths = [item for item in selected if item["kind"] == "journey"]
            self.assertEqual((len(lessons), len(paths)), (6, 8))
            parts = [item for item in paths if ":part-" in item["id"]]
            self.assertEqual(parts[0]["source"]["start_seconds"], 0)
            self.assertEqual([part["source"]["end_seconds"] for part in parts[:-1]],
                             [part["source"]["start_seconds"] for part in parts[1:]])
            _, parsed = repertoire_source(source.code)
            self.assertEqual(parts[-1]["source"]["end_seconds"], parsed["metadata"]["duration_seconds"])
            self.assertTrue(paths[-1]["stages"][-1]["_reuse_original"])
            self.assertEqual(paths[-1]["stages"][-1]["_asset_key"], source.asset_key)
            for lesson in lessons:
                for language in ["uz", "ru", "en"]:
                    value = localize(lesson, language)
                    self.assertGreater(len(value["explanation"][1]["text"]), 180)
                    self.assertTrue(value["ready_when"])
            self.assertEqual(len({lesson["explanation"][1]["text"]["en"] for lesson in lessons}), 6)

    def test_each_stage_preserves_selected_pitches_velocities_holds_and_source_timing(self):
        for item in repertoire_items():
            _, original = repertoire_source(item["_composition"])
            lookup = {event["id"]: event for event in original["events"]}
            selections = []
            for stage in item["stages"]:
                spec = stage["_generator"]
                raw, identifiers = lesson_stage_midi(original, **spec)
                parsed = parse_midi(raw)
                self.assertEqual(len(parsed["events"]), len(identifiers), stage["id"])
                scale = 100 / spec["speed_percent"]
                expected = sorted((lookup[key]["pitch"]["midi"], lookup[key]["hand"], lookup[key]["velocity"],
                                   (lookup[key]["onset_seconds"] - spec["start"]) * scale,
                                   min(lookup[key]["duration_seconds"], spec["end"] - lookup[key]["onset_seconds"]) * scale)
                                  for key in identifiers)
                actual = sorted((event["pitch"]["midi"], event["hand"], event["velocity"],
                                 event["onset_seconds"], event["duration_seconds"]) for event in parsed["events"])
                for source_note, study_note in zip(expected, actual):
                    self.assertEqual(source_note[:3], study_note[:3], stage["id"])
                    self.assertAlmostEqual(source_note[3], study_note[3], delta=.002, msg=stage["id"])
                    self.assertAlmostEqual(source_note[4], study_note[4], delta=.002, msg=stage["id"])
                self.assertAlmostEqual(parsed["metadata"]["duration_seconds"],
                                       (spec["end"] - spec["start"]) * scale, delta=.002)
                self.assertIsNone(parsed["metadata"]["time"])
                selections.append(set(identifiers))
            self.assertTrue(selections[0] <= selections[1] <= selections[2])
            self.assertEqual(selections[2], {event["id"] for event in original["events"]
                                           if item["source"]["start_seconds"] <= event["onset_seconds"] < item["source"]["end_seconds"]})

    def test_taught_landmarks_match_the_actual_files(self):
        def near(code, hand, seconds):
            _, parsed = repertoire_source(code)
            return {event["pitch"]["midi"] for event in parsed["events"]
                    if event["hand"] == hand and abs(event["onset_seconds"] - seconds) < .045}
        self.assertEqual(near("youth", "right", 0), {71, 83})
        self.assertIn(95, near("youth", "right", 151.75))
        self.assertIn(23, near("youth", "left", 151.76))
        self.assertIn(50, near("star", "left", 0))
        self.assertIn(63, near("tears", "left", .94))
        self.assertIn(64, near("tears", "left", 6.41))
        self.assertIn(67, near("my-memory", "left", 0))
        self.assertIn(76, near("my-memory", "right", .42))
        _, premonition = repertoire_source("premonition")
        bass = sorted((event for event in premonition["events"] if event["hand"] == "left" and event["onset_seconds"] < 30), key=lambda event: event["onset_seconds"])
        self.assertEqual([event["pitch"]["midi"] for event in bass], [48, 47, 46, 45, 44, 43, 41, 43])
        study = next(item for item in repertoire_items() if item["id"] == "lesson:memories:two-upper-voices")
        _, source = repertoire_source("memories")
        raw, _ = lesson_stage_midi(source, **study["stages"][0]["_generator"])
        upper = parse_midi(raw)["events"]
        self.assertEqual([event["pitch"]["midi"] for event in upper[:5]], [81, 79, 77, 76, 74])
        self.assertTrue(all(event["pitch"]["midi"] >= 72 for event in upper))

    def test_study_boundaries_do_not_turn_a_new_long_tone_into_a_tiny_final_click(self):
        for item in repertoire_items():
            _, source = repertoire_source(item["_composition"])
            end = item["source"]["end_seconds"]
            for event in source["events"]:
                if item["source"]["start_seconds"] <= event["onset_seconds"] < end:
                    self.assertFalse(end - event["onset_seconds"] < .05 and event["duration_seconds"] > .3,
                                     (item["id"], event["onset_seconds"], event["pitch"]["midi"]))
