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
from apps.studio.content import all_items, LESSONS, localize
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
        self.assertEqual(Composition.objects.count(),1)
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
        self.assertEqual((len(data["compositions"]),len(data["lessons"]),len(data["exercises"]),len(data["theory"])),(1,12,36,18))
        self.assertEqual(len({item["id"] for kind in ["lessons","exercises","theory"] for item in data[kind]}),66)
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

    def test_all_36_stages_resolve_in_each_language_without_private_generator_fields(self):
        for language in ["uz","ru","en"]:
            catalog = self.client.get("/api/studio/catalog/",HTTP_ACCEPT_LANGUAGE=language).json()
            for lesson in catalog["lessons"]:
                self.assertEqual(len(lesson["stages"]),3)
                self.assertEqual(lesson["score_id"],lesson["stages"][0]["score_id"])
                self.assertEqual([s["source_speed_percent"] for s in lesson["stages"]],[60,80,100])
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
        for family in ["five-finger","scales","arpeggios","chords","coordination","rhythm","leaps","octaves","articulation","balance","pedal","continuity"]:
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
        self.assertEqual(len(set(hashes)),36)

    def test_theory_examples_have_expected_musical_differences(self):
        parsed=parse_midi(theory_midi("major-minor"))
        self.assertEqual(sorted(event["pitch"]["midi"] for event in parsed["events"] if event["onset_quarters"]==0),[60,64,67])
        self.assertEqual(sorted(event["pitch"]["midi"] for event in parsed["events"] if event["onset_quarters"]==4),[60,63,67])
        pedal=parse_midi(theory_midi("pedal"))
        self.assertTrue(pedal["pedal_events"])
        self.assertEqual(parse_midi(theory_midi("meter"))["metadata"]["time"]["beats"],"3")
