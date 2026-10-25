import hashlib
import io
import tempfile
from unittest.mock import patch
from pathlib import Path
import mido
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from apps.learning.models import Composition, Profile, LearningLesson
from apps.scores.models import Score
from apps.scores.midi import parse_midi
from apps.studio.content import all_items, FAMILIES, LESSONS, localize
from apps.studio.midi_authoring import SOURCE_SHA256, source_data, adapt_source, exercise_notes, theory_midi
from apps.studio.models import StudioAsset


from tests.support import LearnerClient

class StudioTests(TestCase):
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
        Profile.objects.create(pk=1,display_name="Preserved learner",language="uz",theme="dark")
        call_command("seed_studio",stdout=io.StringIO())

    def test_complete_source_bytes_and_unknown_metadata_are_preserved(self):
        original=StudioAsset.objects.get(key="composition:still:original").score
        with original.musicxml.open("rb") as handle:
            content=handle.read()
        self.assertEqual(len(content),8938)
        self.assertEqual(hashlib.sha256(content).hexdigest(),SOURCE_SHA256)
        self.assertEqual(len(original.parsed["events"]),1092)
        self.assertAlmostEqual(original.parsed["metadata"]["duration_seconds"],214.60416666666666)
        self.assertIsNone(original.parsed["metadata"]["key"])
        self.assertIsNone(original.parsed["metadata"]["time"])
        self.assertEqual(original.parsed["pedal_events"],[])
        self.assertIsNone(original.completeness_verified_at)
        self.assertEqual({event["hand_evidence"] for event in original.parsed["events"]},{"curated_track_role_inference"})

    def test_seed_is_idempotent_and_preserves_profile(self):
        before=list(StudioAsset.objects.order_by("key").values_list("key","score_id"))
        scores=Score.objects.count()
        files=sorted(path.name for path in Path(self.media.name).rglob("*.mid"))
        call_command("seed_studio",stdout=io.StringIO())
        self.assertEqual(before,list(StudioAsset.objects.order_by("key").values_list("key","score_id")))
        self.assertEqual(scores,Score.objects.count())
        self.assertEqual(files,sorted(path.name for path in Path(self.media.name).rglob("*.mid")))
        self.assertEqual(Profile.objects.get(pk=1).display_name,"Preserved learner")
        self.assertEqual(Profile.objects.get(pk=1).theme,"dark")

    def test_replacement_requires_flag_and_only_then_removes_old_compositions(self):
        old=Composition.objects.create(title="Old repertoire")
        with self.assertRaises(CommandError): call_command("seed_studio",stdout=io.StringIO())
        self.assertTrue(Composition.objects.filter(pk=old.pk).exists())
        call_command("seed_studio",replace_compositions=True,stdout=io.StringIO())
        self.assertEqual(Composition.objects.count(),8)
        self.assertEqual(Profile.objects.get(pk=1).display_name,"Preserved learner")

    def test_teaching_copy_changes_keep_existing_midi_versions(self):
        from apps.studio.management.commands.seed_studio import prepared_assets

        before = list(StudioAsset.objects.order_by("key").values_list("key", "score_id"))
        count = Score.objects.count()
        assets = prepared_assets()
        for _, _, _, _, provenance in assets:
            if provenance.get("kind") == "teaching_adaptation":
                provenance["transformation_description"] = "A clearer instruction for the same music."
        with patch("apps.studio.management.commands.seed_studio.prepared_assets", return_value=assets):
            call_command("seed_studio", stdout=io.StringIO())
        self.assertEqual(before, list(StudioAsset.objects.order_by("key").values_list("key", "score_id")))
        self.assertEqual(count, Score.objects.count())

    def test_catalog_contract_and_all_scores_resolve(self):
        response=self.client.get("/api/studio/catalog/")
        self.assertEqual(response.status_code,200)
        data=response.json()
        self.assertEqual((len(data["compositions"]),len(data["lessons"]),len(data["exercises"]),len(data["theory"])),(8,57,48,24))
        self.assertEqual(len({item["id"] for kind in ["lessons","exercises","theory"] for item in data[kind]}),129)
        for kind in ["lessons","exercises","theory"]:
            for item in data[kind]:
                self.assertGreater(len(item["explanation"][0]["text"]),50)
                self.assertTrue(item["steps"])
                score=self.client.get(f'/api/scores/{item["score_id"]}/')
                self.assertEqual(score.status_code,200)
                self.assertTrue(score.json()["parsed"]["events"])
                self.assertNotIn("_generator",item)
        self.assertEqual({item["level"] for item in data["exercises"]},{"easy","intermediate","advanced"})

    def test_authored_catalog_is_localized_without_changing_identities(self):
        uz=self.client.get("/api/studio/catalog/",HTTP_ACCEPT_LANGUAGE="uz").json()
        for language in ["ru","en"]:
            response=self.client.get("/api/studio/catalog/",HTTP_ACCEPT_LANGUAGE=language)
            self.assertEqual(response["Content-Language"],language)
            translated=response.json()
            for kind in ["lessons","exercises","theory"]:
                self.assertEqual([item["id"] for item in translated[kind]],[item["id"] for item in uz[kind]])
                for translated_item, original in zip(translated[kind],uz[kind]):
                    self.assertNotEqual(translated_item["title"],original["title"])
                    self.assertNotEqual(translated_item["explanation"][0]["text"],original["explanation"][0]["text"])

    def test_every_piece_keeps_its_own_lessons_journeys_and_original(self):
        from apps.studio.repertoire import SOURCES
        from apps.studio.services import studio_catalog
        catalog = studio_catalog("en")
        for source, composition in zip(SOURCES, catalog["compositions"]):
            original = StudioAsset.objects.get(pk=source.asset_key).score
            expected_score = StudioAsset.objects.get(pk="composition:all-in:easy").score_id if source.code == "all-in" else original.pk
            self.assertEqual(composition["score_id"], expected_score)
            self.assertEqual(original.content_sha256, source.sha256)
            lessons = [item for item in catalog["lessons"] if item["id"] in composition["lesson_ids"]]
            journeys = [item for item in catalog["journeys"] if item["composition_id"] == composition["id"]]
            self.assertEqual((len(lessons), len(journeys)), (9, 5) if source.code == "all-in" else (12 if source.code == "still" else 6, 8))
            for item in lessons + journeys:
                self.assertEqual(item["composition_id"], composition["id"])
                for stage in item["stages"]:
                    self.assertEqual(Score.objects.get(pk=stage["score_id"]).arrangement.composition_id, composition["id"])
            self.assertEqual(journeys[-1]["stages"][-1]["score_id"], original.pk)

    def test_source_replacement_keeps_content_ids_progress_notes_and_historical_files(self):
        from django.core.files.base import ContentFile
        from django.db.models import Max
        from django.utils import timezone
        from apps.activity.models import PersonalLibrary, PracticeNote
        from apps.studio.midi_authoring import midi_bytes
        from apps.studio.repertoire import SOURCE_BY_CODE
        from apps.studio.services import studio_catalog

        composition_ids = dict(Composition.objects.values_list("seed_key", "pk"))
        still_id = StudioAsset.objects.get(pk="composition:still:original").score_id
        asset = StudioAsset.objects.select_related("score").get(pk="composition:memories:original")
        legacy_bytes = midi_bytes([(0, 8, 60, "right", 70)], end_quarters=8)
        legacy = Score.objects.create(
            arrangement=asset.score.arrangement,
            version=Score.objects.filter(arrangement=asset.score.arrangement).aggregate(last=Max("version"))["last"] + 1,
            file_format="midi", title="Previous performance export", original_filename="previous.mid",
            content_sha256=hashlib.sha256(legacy_bytes).hexdigest(), parsed=parse_midi(legacy_bytes),
            rights_confirmed_at=timezone.now(), source_provenance={"kind": "previous_performance_export"})
        legacy.musicxml.save("previous.mid", ContentFile(legacy_bytes))
        asset.score = legacy
        asset.save(update_fields=["score"])
        stage_id = "lesson:memories:sparse-opening:stage:3"
        library = PersonalLibrary.objects.create(profile_id=1, progress={stage_id: "mastered"},
            last_stages={"lesson:memories:sparse-opening": stage_id}, comfortable_speeds={stage_id: 70},
            favorites=[f"composition:{asset.score.arrangement.composition_id}", "lesson:memories:sparse-opening"], positions={stage_id: 3.5})
        before = {field: getattr(library, field) for field in ["progress", "last_stages", "comfortable_speeds", "favorites", "positions"]}
        note = PracticeNote.objects.create(profile_id=1, content_id=stage_id, position_seconds=3.5, text="Keep my note")

        call_command("seed_studio", stdout=io.StringIO())
        asset.refresh_from_db()
        self.assertNotEqual(asset.score_id, legacy.pk)
        self.assertEqual(asset.score.content_sha256, SOURCE_BY_CODE["memories"].sha256)
        self.assertEqual(dict(Composition.objects.values_list("seed_key", "pk")), composition_ids)
        self.assertEqual(StudioAsset.objects.get(pk="composition:still:original").score_id, still_id)
        library.refresh_from_db()
        self.assertEqual({field: getattr(library, field) for field in before}, before)
        note.refresh_from_db()
        self.assertEqual((note.content_id, note.text, note.position_seconds), (stage_id, "Keep my note", 3.5))
        legacy.refresh_from_db()
        with legacy.musicxml.open("rb") as handle:
            self.assertEqual(handle.read(), legacy_bytes)
        course = next(item for item in studio_catalog("en")["lessons"] if item["id"] == "lesson:memories:sparse-opening")
        self.assertEqual(course["stages"][-1]["id"], stage_id)
        self.assertEqual(course["stages"][-1]["source_speed_percent"], 100)
        replacement_id = asset.score_id
        call_command("seed_studio", stdout=io.StringIO())
        self.assertEqual(StudioAsset.objects.get(pk=asset.pk).score_id, replacement_id)

    def test_catalog_does_not_fetch_all_parsed_study_graphs(self):
        from apps.studio.services import studio_catalog
        with self.assertNumQueries(2):
            catalog = studio_catalog("uz")
        self.assertEqual(len(catalog["compositions"]), 8)

    def test_readonly_catalog_and_legacy_content_write_endpoints(self):
        score=StudioAsset.objects.first().score
        for url, method in [("/api/studio/catalog/","post"),("/api/compositions/","post"),("/api/scores/","post"),
                            (f"/api/scores/{score.pk}/","patch"),("/api/sessions/","post"),("/api/tasks/1/","patch"),
                            ("/api/lessons/1/quiz/","post")]:
            response=getattr(self.client,method)(url,data={},content_type="application/json")
            self.assertEqual(response.status_code,405,url)
        self.assertEqual(self.client.patch("/api/profile/",data={"language":"en"},content_type="application/json").status_code,200)

    def test_lesson_stages_restore_the_exact_source_with_uniform_slowing(self):
        _, source = source_data()
        lookup = {event["id"]:event for event in source["events"]}
        for lesson in LESSONS:
            key = f"lesson:still:{lesson['code']}"
            selections = []
            for index, speed in enumerate([60,80,100]):
                asset_key = key if index == 2 else f"{key}:stage:{index+1}"
                score = StudioAsset.objects.get(key=asset_key).score
                provenance = score.source_provenance
                ids = provenance["source_event_ids"]
                selections.append(set(ids))
                self.assertEqual(provenance["source_speed_percent"], speed)
                self.assertEqual(len(ids),len(score.parsed["events"]))
                scale = 100/speed
                expected = sorted((lookup[i]["pitch"]["midi"],lookup[i]["hand"],lookup[i]["velocity"],
                                   (lookup[i]["onset_seconds"]-lesson["start"])*scale,
                                   min(lookup[i]["duration_seconds"],lesson["end"]-lookup[i]["onset_seconds"])*scale) for i in ids)
                actual = sorted((e["pitch"]["midi"],e["hand"],e["velocity"],e["onset_seconds"],e["duration_seconds"]) for e in score.parsed["events"])
                for a,b in zip(expected,actual):
                    self.assertEqual(a[:3],b[:3],asset_key)
                    self.assertAlmostEqual(a[3],b[3],delta=.002,msg=asset_key)
                    self.assertAlmostEqual(a[4],b[4],delta=.002,msg=asset_key)
                self.assertFalse(score.parsed["pedal_events"])
                self.assertIsNone(score.parsed["metadata"]["time"])
            self.assertLess(selections[0], selections[1], key)
            self.assertLessEqual(selections[1], selections[2], key)
            self.assertEqual(selections[2], {e["id"] for e in source["events"] if lesson["start"] <= e["onset_seconds"] < lesson["end"]})

    def test_all_stages_resolve_in_each_language_without_private_generator_fields(self):
        for language in ["uz","ru","en"]:
            catalog = self.client.get("/api/studio/catalog/",HTTP_ACCEPT_LANGUAGE=language).json()
            for lesson in catalog["lessons"]:
                speeds = [60,80,100] if lesson["id"].startswith("lesson:still:") else [60,80,60,80,100]
                if not lesson["id"].startswith("lesson:all-in:"):
                    self.assertEqual(len(lesson["stages"]),len(speeds))
                    self.assertEqual([s["source_speed_percent"] for s in lesson["stages"]],speeds)
                else:
                    self.assertIn(lesson["stages"][0]["tempo_bpm"], [40, 45, 50, 60])
                self.assertEqual(lesson["score_id"],lesson["stages"][0]["score_id"])
                self.assertTrue(lesson["ready_when"])
                self.assertGreaterEqual(len(lesson["explanation"]),3)
                for stage in lesson["stages"]:
                    self.assertNotIn("_generator",stage)
                    self.assertNotIn("_asset_key",stage)
                    self.assertEqual(self.client.get(f'/api/scores/{stage["score_id"]}/file/').status_code,200)

    def test_missing_stage_is_not_silently_replaced_with_original(self):
        StudioAsset.objects.filter(key="lesson:still:opening-left:stage:1").delete()
        self.assertEqual(self.client.get("/api/studio/catalog/").status_code,503)

    def test_reviewed_landmarks_match_the_taught_note_names(self):
        bass = StudioAsset.objects.get(key="lesson:still:opening-bass:stage:1").score.parsed["events"]
        self.assertEqual([e["pitch"]["midi"] for e in bass[:5]],[45,43,42,41,40])
        melody = StudioAsset.objects.get(key="lesson:still:early-melody:stage:1").score.parsed["events"]
        self.assertEqual([e["pitch"]["midi"] for e in melody[:4]],[84,83,83,81])
        ending = StudioAsset.objects.get(key="lesson:still:ending").score.parsed["events"]
        self.assertAlmostEqual(max(e["onset_seconds"]+e["duration_seconds"] for e in ending),214.60416666666666-196,places=4)

    def test_retired_reads_cannot_generate_legacy_lessons_or_demo_content(self):
        composition=Composition.objects.first()
        before=LearningLesson.objects.count()
        for url in ["/api/overview/","/api/compositions/",f"/api/compositions/{composition.pk}/curriculum/",
                    f"/api/compositions/{composition.pk}/adaptive-plan/","/api/lessons/1/","/api/sessions/",
                    "/api/scores/demo/","/api/scores/demo/musicxml/"]:
            self.assertEqual(self.client.get(url).status_code,410,url)
        self.assertEqual(LearningLesson.objects.count(),before)
        self.assertEqual(self.client.get("/api/profile/").status_code,200)
        self.assertEqual(self.client.get("/api/studio/catalog/").status_code,200)

    def test_reductions_are_smaller_than_original_excerpt_not_synthetic_replacements(self):
        _,source=source_data()
        for mode in ["bass","melody"]:
            content,ids=adapt_source(source,0,20,mode)
            self.assertLess(len(ids),len([event for event in source["events"] if event["onset_seconds"]<20]))
            self.assertTrue(ids)
            self.assertEqual(len(parse_midi(content)["events"]),len(ids))

    def test_original_exercises_are_unique_and_include_actual_sustain(self):
        hashes=[]
        for family, *_ in FAMILIES:
            for level in range(3):
                content,_=exercise_notes(family,level)
                hashes.append(hashlib.sha256(content).hexdigest())
                parsed=parse_midi(content)
                self.assertTrue(parsed["events"])
                self.assertGreaterEqual(parsed["metadata"]["pitch_range"]["min"],21)
                self.assertLessEqual(parsed["metadata"]["pitch_range"]["max"],108)
                if family=="pedal":
                    self.assertTrue(parsed["pedal_events"])
                    self.assertTrue(any(event["sound_duration_seconds"]>event["duration_seconds"] for event in parsed["events"]))
        self.assertEqual(len(set(hashes)),48)

    def test_theory_examples_have_expected_musical_differences(self):
        parsed=parse_midi(theory_midi("major-minor"))
        self.assertEqual(sorted(event["pitch"]["midi"] for event in parsed["events"] if event["onset_quarters"]==0),[60,64,67])
        self.assertEqual(sorted(event["pitch"]["midi"] for event in parsed["events"] if event["onset_quarters"]==4),[60,63,67])
        pedal=parse_midi(theory_midi("pedal"))
        self.assertTrue(pedal["pedal_events"])
        self.assertEqual(parse_midi(theory_midi("meter"))["metadata"]["time"]["beats"],"3")
