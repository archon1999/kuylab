import hashlib
import io
import tempfile
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings

from apps.scores.midi import parse_midi
from apps.studio.all_in_package import HASHES, package_source, study_file, variant_definitions
from apps.studio.all_in_lessons import PLANS, all_in_items
from apps.studio.content import all_items, localize
from apps.studio.midi_authoring import lesson_stage_midi
from apps.studio.models import StudioAsset
from apps.studio.services import CatalogNotPrepared, studio_catalog
from tests.support import LearnerClient


def notes(parsed, hand):
    return sorted((e["pitch"]["midi"], round(e["onset_seconds"], 8),
                   round(e["duration_seconds"], 8), e["velocity"])
                  for e in parsed["events"] if e["hand"] == hand)


class AllInMusicTests(SimpleTestCase):
    def test_all_thirteen_sources_are_pinned_and_main_variants_share_exact_right_hand(self):
        for filename, digest in HASHES.items():
            data, parsed = package_source(filename)
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest)
            self.assertTrue(parsed["events"])
        _, easy = package_source("All_In_Plus5_Easy_LH.mid")
        _, hard = package_source("All_In_Plus5_Full.mid")
        self.assertEqual(notes(easy, "right"), notes(hard, "right"))
        self.assertEqual(len(notes(hard, "right")), 1049)
        self.assertEqual((len(notes(easy, "left")), len(notes(hard, "left"))), (424, 1171))
        for key in ["tempo_map", "time_signature_map", "key_signature_map"]:
            self.assertEqual(easy[key], hard[key])
        self.assertEqual(len(hard["tempo_map"]), 117)
        self.assertAlmostEqual(easy["metadata"]["duration_seconds"], 287.8129523333333)
        self.assertEqual(easy["metadata"]["duration_seconds"], hard["metadata"]["duration_seconds"])
        self.assertEqual(hard["metadata"]["key"]["midi_key"], "Dm")
        self.assertFalse(any(event["down"] for event in hard["pedal_events"]))
        self.assertEqual({e["hand_evidence"] for e in hard["events"]}, {"track_name_hint"})

    def test_left_only_sources_match_their_complete_variants_including_initial_silence(self):
        for name, count in [("Easy", 424), ("Full", 1171)]:
            filename = "All_In_Plus5_Easy_LH.mid" if name == "Easy" else "All_In_Plus5_Full.mid"
            _, complete = package_source(filename)
            _, left = package_source(f"All_In_Plus5_LH_Only_{name}.mid")
            self.assertEqual(notes(complete, "left"), notes(left, "left"))
            self.assertEqual(len(left["events"]), count)
            self.assertEqual(left["metadata"]["duration_seconds"], complete["metadata"]["duration_seconds"])
            self.assertGreater(min(e["onset_seconds"] for e in left["events"]), 15.7)

    def test_drums_are_not_rendered_as_piano_but_piano_attacks_holds_and_four_preparation_beats_survive(self):
        for plan in PLANS:
            filename = "Mashqlar/" + plan["file"]
            _, original = package_source(filename)
            data, provenance = study_file(filename)
            prepared = parse_midi(data)
            self.assertFalse(any(e["channel"] == 9 for e in prepared["events"]))
            for hand in ["left", "right"]:
                self.assertEqual(notes(original, hand), notes(prepared, hand), filename)
            self.assertEqual(prepared["metadata"]["duration_seconds"], original["metadata"]["duration_seconds"])
            self.assertAlmostEqual(min(e["onset_seconds"] for e in prepared["events"]), 240 / plan["bpm"], delta=.00001)
            self.assertEqual(provenance["source_sha256"], HASHES[filename])
            self.assertEqual(data, study_file(filename)[0])

    def test_actual_motif_and_chorus_pitch_landmarks_match_the_explanations(self):
        _, hard = package_source("All_In_Plus5_Full.mid")
        left = sorted((e for e in hard["events"] if e["hand"] == "left"), key=lambda e: e["onset_seconds"])
        self.assertEqual([e["pitch"]["midi"] for e in left[:8]], [50, 57, 62, 65, 64, 62, 65, 67])
        drill = parse_midi(study_file("Mashqlar/07_Naqarot_oson_LH_60bpm.mid")[0])
        for second, expected in [(4, {38,50}), (5, {53,57}), (6, {33,45}), (7, {49,55})]:
            self.assertEqual({e["pitch"]["midi"] for e in drill["events"] if e["onset_seconds"] == second}, expected)

    def test_common_course_has_nine_distinct_drills_complete_localization_and_valid_related_links(self):
        lessons = [item for item in all_in_items() if item["kind"] == "lesson"]
        self.assertEqual(len(lessons), 9)
        self.assertEqual(len({s["_package_file"] for item in lessons for s in item["stages"] if s.get("_package_file")}), 9)
        all_ids = {item["id"] for item in all_items()}
        for item in all_in_items():
            self.assertTrue(set(item["related_ids"]) <= all_ids)
            for lang in ["uz", "ru", "en"]:
                value = localize(item, lang)
                self.assertTrue(value["ready_when"])
                self.assertGreaterEqual(len(value["explanation"]), 3)
                for section in value["explanation"]:
                    self.assertGreater(len(section["text"]), 80)
            self.assertEqual(len({s["id"] for s in item["stages"]}), len(item["stages"]))

    def test_easy_and_hard_excerpts_are_taken_from_the_declared_variant_without_extra_transposition(self):
        for item in all_in_items():
            for stage in item["stages"]:
                if stage.get("_package_file") or stage.get("_reuse_original"):
                    continue
                filename = "All_In_Plus5_Easy_LH.mid" if stage["_source_variant"] == "easy" else "All_In_Plus5_Full.mid"
                _, source = package_source(filename)
                data, identifiers = lesson_stage_midi(source, **stage["_generator"])
                parsed = parse_midi(data)
                spec = stage["_generator"]
                scale = 100 / spec["speed_percent"]
                expected = sorted((e["pitch"]["midi"], e["hand"], e["velocity"],
                                   (e["onset_seconds"] - spec["start"]) * scale,
                                   min(e["duration_seconds"], spec["end"] - e["onset_seconds"]) * scale)
                                  for e in source["events"] if e["id"] in identifiers)
                actual = sorted((e["pitch"]["midi"], e["hand"], e["velocity"], e["onset_seconds"], e["duration_seconds"]) for e in parsed["events"])
                self.assertEqual(len(actual), len(expected))
                for a, b in zip(actual, expected):
                    self.assertEqual(a[:3], b[:3])
                    self.assertAlmostEqual(a[3], b[3], delta=.002)
                    self.assertAlmostEqual(a[4], b[4], delta=.002)
                self.assertAlmostEqual(parsed["metadata"]["duration_seconds"], (spec["end"] - spec["start"]) * scale, delta=.002)


class AllInCatalogTests(TestCase):
    client_class = LearnerClient

    @classmethod
    def setUpClass(cls):
        cls.media = tempfile.TemporaryDirectory()
        cls.settings_override = override_settings(MEDIA_ROOT=cls.media.name, CURATED_STUDIO_READ_ONLY=True)
        cls.settings_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.settings_override.disable()
        cls.media.cleanup()

    @classmethod
    def setUpTestData(cls):
        call_command("seed_studio", stdout=io.StringIO())

    def test_one_composition_two_variant_scores_and_one_shared_course_in_all_languages(self):
        for lang in ["uz", "ru", "en"]:
            catalog = studio_catalog(lang)
            pieces = [c for c in catalog["compositions"] if c["slug"] == "all-in-soundtrack"]
            self.assertEqual(len(pieces), 1)
            piece = pieces[0]
            self.assertEqual(piece["title"], "All in — Soundtrack")
            self.assertEqual(piece["default_variant_id"], "hard")
            self.assertTrue(piece["readable_holds"])
            self.assertEqual([v["id"] for v in piece["variants"]], ["easy", "hard"])
            self.assertEqual(len(piece["lesson_ids"]), 9)
            for variant, definition in zip(piece["variants"], variant_definitions("all-in")):
                score = StudioAsset.objects.get(pk=definition["_asset_key"]).score
                self.assertEqual(score.pk, variant["score_id"])
                self.assertEqual(score.arrangement.composition_id, piece["id"])
                self.assertEqual(score.content_sha256, HASHES[definition["_filename"]])
                self.assertTrue(variant["description"])
                self.assertNotIn("_filename", variant)
                self.assertNotIn("_asset_key", variant)
                self.assertTrue(score.source_provenance["preserved_original_bytes"])
            self.assertEqual(piece["score_id"], piece["variants"][1]["score_id"])
            paths = [i for i in catalog["journeys"] if i["composition_id"] == piece["id"]]
            self.assertEqual(len(paths), 5)
            complete = next(i for i in paths if i["id"] == "journey:all-in:complete")
            self.assertEqual(complete["stages"][-1]["score_id"], piece["variants"][1]["score_id"])

    def test_missing_easy_variant_fails_closed_instead_of_falling_back_to_hard(self):
        StudioAsset.objects.filter(key="composition:all-in:easy").delete()
        with self.assertRaises(CatalogNotPrepared):
            studio_catalog("uz")

    def test_all_drills_and_stages_stay_under_the_same_composition_and_keep_variant_provenance(self):
        for item in all_in_items():
            for stage in item["stages"]:
                score = StudioAsset.objects.get(pk=stage["_asset_key"]).score
                self.assertEqual(score.arrangement.composition.seed_key, "studio-all-in-soundtrack")
                provenance = score.source_provenance
                if not stage.get("_reuse_original") and not stage.get("_package_file"):
                    filename = "All_In_Plus5_Easy_LH.mid" if stage["_source_variant"] == "easy" else "All_In_Plus5_Full.mid"
                    self.assertEqual(provenance["source_sha256"], HASHES[filename])
                    self.assertEqual(provenance["source_variant"], stage["_source_variant"])
