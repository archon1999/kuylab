import hashlib
from pathlib import Path

from django.test import SimpleTestCase

from apps.scores.midi import parse_midi
from apps.studio.content import localize
from apps.studio.curated_lessons import audible_example, curated_items
from apps.studio.curated_repertoire import ENTRIES, edition_provenance, edition_source
from apps.studio.midi_authoring import lesson_stage_midi
from apps.studio.repertoire import SOURCES


class CuratedRepertoireTests(SimpleTestCase):
    def test_all_thirty_editions_are_pinned_playable_and_have_both_display_layers(self):
        self.assertEqual(len(ENTRIES), 30)
        self.assertEqual(len(SOURCES), 101)
        self.assertEqual(len({source.slug for source in SOURCES}), 101)
        for entry in ENTRIES:
            raw, parsed = edition_source(entry["code"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"])
            self.assertEqual(len(parsed["events"]), entry["note_count"])
            self.assertAlmostEqual(parsed["metadata"]["duration_seconds"], entry["duration_seconds"])
            self.assertEqual({e["hand"] for e in parsed["events"]}, {"left", "right"})
            self.assertFalse(any(e.get("percussion") for e in parsed["events"]))
            self.assertTrue(all(21 <= e["pitch"]["midi"] <= 108 for e in parsed["events"]))
            self.assertLess(max(e["onset_seconds"] + e["duration_seconds"] for e in parsed["events"]), entry["duration_seconds"] + .01)
            self.assertLessEqual(entry["preview_start"] + entry["preview_duration"], entry["duration_seconds"])

    def test_rights_and_rendered_source_are_not_mislabeled_as_unmodified_public_domain(self):
        modern = [entry for entry in ENTRIES if entry["rights_basis"] == "owner_confirmed_redistribution"]
        self.assertEqual(len(modern), 20)
        for entry in modern:
            self.assertEqual(entry["storage"], "public")
            self.assertEqual(entry["permission_confirmed_on"], "2026-10-26")
            self.assertIn("public GitHub", entry["permission_scope"])
            self.assertIn("original rights retained", entry["license"])
            self.assertTrue(entry["source_url"].startswith("https://"))
            self.assertTrue(entry["credit"])
            self.assertTrue(edition_provenance(entry["code"])["preserved_original_bytes"])
        waltz = next(e for e in ENTRIES if e["code"] == "waltz-a-minor")
        source = Path(__file__).resolve().parents[2] / "apps/studio/assets/catalog/sources/waltz-a-minor.mxl"
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), waltz["source_document_sha256"])
        self.assertFalse(edition_provenance("waltz-a-minor")["preserved_original_bytes"])
        self.assertIn("grace notes", waltz["edition_note"])
        self.assertIn("CC BY-SA 2.5", edition_provenance("moonlight-sonata")["license"])
        self.assertIn("CC BY-SA 3.0", edition_provenance("nocturne-op-9-no-2")["license"])

    def test_every_piece_has_localized_theory_actual_note_examples_and_a_complete_finale(self):
        items = curated_items()
        self.assertEqual(len(items), 96)
        self.assertEqual(len({item["id"] for item in items}), 96)
        self.assertEqual(len({entry["learning_focus"]["en"] for entry in ENTRIES}), 30)
        for entry in ENTRIES:
            if not any(source.code == entry["code"] and source.course_kind == "curated" for source in SOURCES):
                continue
            selected = [item for item in items if item["_composition"] == entry["code"]]
            self.assertEqual([item["kind"] for item in selected], ["lesson"] * 3 + ["journey"])
            self.assertTrue(selected[-1]["stages"][-1]["_reuse_original"])
            self.assertEqual(selected[-1]["stages"][-1]["_asset_key"], f"composition:{entry['code']}:original")
            _, source = edition_source(entry["code"])
            for window in entry["lesson_windows"]:
                hand = "left" if window["mode"] == "bass" else "right"
                example = audible_example(source, window["start"], window["end"], hand)
                self.assertGreaterEqual(len(example), 3)
            for item in selected:
                for language in ("uz", "ru", "en"):
                    localized = localize(item, language)
                    self.assertGreater(len(localized["explanation"][0]["text"]), 150)
                    self.assertTrue(localized["steps"])
                    self.assertEqual([stage["source_speed_percent"] for stage in localized["stages"]], [60, 80, 60, 80, 100])

    def test_all_teaching_stages_retain_source_notes_and_restore_the_complete_texture(self):
        for item in curated_items():
            _, source = edition_source(item["_composition"])
            lookup = {event["id"]: event for event in source["events"]}
            sets = []
            for stage in item["stages"]:
                if stage.get("_reuse_original"):
                    sets.append(set(lookup))
                    continue
                spec = stage["_generator"]
                raw, identifiers = lesson_stage_midi(source, **spec)
                parsed = parse_midi(raw)
                self.assertEqual(len(parsed["events"]), len(identifiers), stage["id"])
                scale = 100 / spec["speed_percent"]
                expected = sorted((lookup[i]["pitch"]["midi"], lookup[i]["hand"], lookup[i]["velocity"],
                                   (lookup[i]["onset_seconds"] - spec["start"]) * scale,
                                   min(lookup[i]["duration_seconds"], spec["end"] - lookup[i]["onset_seconds"]) * scale)
                                  for i in identifiers)
                actual = sorted((e["pitch"]["midi"], e["hand"], e["velocity"], e["onset_seconds"], e["duration_seconds"])
                                for e in parsed["events"])
                for a, b in zip(actual, expected):
                    self.assertEqual(a[:3], b[:3], stage["id"])
                    self.assertAlmostEqual(a[3], b[3], delta=.002, msg=stage["id"])
                    self.assertAlmostEqual(a[4], b[4], delta=.002, msg=stage["id"])
                sets.append(set(identifiers))
            self.assertTrue(sets[0] <= sets[1] <= sets[2])
            self.assertEqual(sets[2], sets[3])
            self.assertEqual(sets[3], sets[4])
            self.assertLess(len(sets[0]), len(sets[4]))
            self.assertEqual(sets[4], {e["id"] for e in source["events"]
                                      if item["source"]["start_seconds"] <= e["onset_seconds"] < item["source"]["end_seconds"]})
