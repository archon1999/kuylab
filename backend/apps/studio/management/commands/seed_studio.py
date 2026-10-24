"""Prepare the curated library. Repertoire replacement requires an explicit flag."""
import hashlib
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from apps.learning.models import Arrangement, Composition
from apps.scores.models import Score
from apps.scores.midi import parse_midi
from apps.studio.comparisons import definitions, comparison_midi
from apps.studio.content import REVISION, all_items
from apps.studio.midi_authoring import SOURCE_SHA256, source_data, lesson_stage_midi, exercise_notes, theory_midi
from apps.studio.models import StudioAsset

COMPOSITION_KEY = "studio-winter-sonata-still"
ORIGINAL_KEY = "composition:still:original"


def prepared_assets():
    content, parsed = source_data()
    assets = [(ORIGINAL_KEY, "Winter Sonata — Still", content, parsed, {
        "kind": "user_supplied_original_midi", "filename": "Winter Sonata Classics - Still.mid",
        "source_sha256": SOURCE_SHA256, "preserved_original_bytes": True,
        "completeness_scope": "All bytes and all 1092 notes of the user-supplied file; not independently verified against a published arrangement.",
        "hand_assignment": "Track 0 upper/melody => right; track 1 lower/accompaniment => left. Curated role inference, not source metadata.",
        "unknown_metadata": ["composer", "arranger", "key_signature", "time_signature"],
    })]
    for item in all_items():
        provenance = {"kind":"original_authored_study", "catalog_id":item["id"], "revision":REVISION}
        if item["kind"] in {"lesson", "journey"}:
            for stage in item["stages"]:
                if stage.get("_reuse_original"):
                    continue
                spec = stage["_generator"]
                data, identifiers = lesson_stage_midi(parsed, **spec)
                stage_provenance = {**provenance, "kind":"teaching_adaptation", "stage_id": stage["id"],
                    "source_sha256":SOURCE_SHA256, "source_event_ids":identifiers,
                    "source_start_seconds":spec["start"], "source_end_seconds":spec["end"],
                    "selection":spec["selection"], "source_speed_percent": spec["speed_percent"],
                    "source_timing_preserved":spec["speed_percent"] == 100,
                    "uniform_time_scale":100/spec["speed_percent"], "end_boundary_clipped":True,
                    "transformation_description": stage["instruction"]["en"]}
                title = item["title"]["uz"] + " · " + stage["title"]["uz"]
                assets.append((stage["_asset_key"], title, data, parse_midi(data,title), stage_provenance))
            continue
        spec = item["_generator"]
        if item["kind"] == "exercise":
            data, details = exercise_notes(spec["family"],spec["level"])
            provenance.update(details)
        else:
            data = theory_midi(spec["topic"])
        assets.append((item["id"], item["title"]["uz"], data, parse_midi(data,item["title"]["uz"]), provenance))
    for topic in ["voicing", "meter", "legato", "dynamics"]:
        for variant in definitions(topic):
            data = comparison_midi(topic, variant["id"].split(":")[-1])
            title = variant["title"]["uz"]
            assets.append((variant["id"], title, data, parse_midi(data, title), {"kind":"original_authored_comparison", "topic":topic, "variant":variant["id"]}))
    return assets


class Command(BaseCommand):
    help = "Seed the Still studio and authored examples; preserve the profile. Back up the DB before --replace-compositions."

    def add_arguments(self, parser):
        parser.add_argument("--replace-compositions", action="store_true", help="Explicitly delete other compositions and their dependent records.")

    def handle(self, *args, **options):
        # Validate every byte and teaching example before a destructive transaction.
        assets = prepared_assets()
        others = Composition.objects.exclude(seed_key=COMPOSITION_KEY)
        if others.exists() and not options["replace_compositions"]:
            raise CommandError("Other compositions exist. Take a database snapshot, then pass --replace-compositions to replace them explicitly.")
        newly_written = []
        try:
            with transaction.atomic():
                if options["replace_compositions"]:
                    others.delete()
                composition, _ = Composition.objects.update_or_create(seed_key=COMPOSITION_KEY, defaults={
                    "title":"Winter Sonata — Still", "composer":"", "category":"Dorama OST", "status":"active",
                    "goal":"Still orqali ravon va ifodali chalishni o‘rganish", "color":"#B98460"})
                arrangement, _ = Arrangement.objects.update_or_create(seed_key="studio-still-original", defaults={
                    "composition":composition,"is_default":True,"title":"Winter Sonata Classics - Still.mid",
                    "source_kind":"own","rights_status":"user_owned","rights_note":"User-supplied MIDI copy for this personal studio; publisher, arranger and redistribution license not supplied.",
                    "exact_version_confirmed":True,"workflow_status":"curated_studio","tempo_bpm":120,
                    "tempo_beat_unit":"quarter","key_signature":"","time_signature":"","arranger":"",
                    "full_score_format":"midi","full_score_verified_at":None})
                for key, title, content, parsed, provenance in assets:
                    digest = hashlib.sha256(content).hexdigest()
                    old = StudioAsset.objects.select_related("score").filter(pk=key).first()
                    # Teaching copy can change without changing a MIDI version.
                    # Keep the original score's historical description; source,
                    # selected events and timing still participate in identity.
                    descriptive_fields = {"revision", "transformation_description"}
                    same_provenance = old and {k:v for k,v in old.score.source_provenance.items() if k not in descriptive_fields} == {k:v for k,v in provenance.items() if k not in descriptive_fields}
                    if old and old.score.content_sha256 == digest and same_provenance and old.score.musicxml.storage.exists(old.score.musicxml.name):
                        if old.revision != REVISION:
                            old.revision = REVISION
                            old.save(update_fields=["revision"])
                        continue
                    version = (Score.objects.filter(arrangement=arrangement).aggregate(last=Max("version"))["last"] or 0)+1
                    score = Score(arrangement=arrangement,version=version,file_format="midi",title=title,
                                  original_filename="Winter Sonata Classics - Still.mid" if key==ORIGINAL_KEY else key.replace(":","-")+".mid",
                                  content_sha256=digest,source_provenance=provenance,parsed=parsed,
                                  rights_note="User-provided source, preserved without modification." if key==ORIGINAL_KEY else "Teaching adaptation of the user's source; not a publisher edition." if key.startswith("lesson:") else "Original practice example authored for this studio.",
                                  rights_confirmed_at=timezone.now(),exact_version_confirmed=True,
                                  completeness_verified_at=None)
                    score.musicxml.save("source.mid", ContentFile(content),save=False)
                    newly_written.append(score.musicxml.name)
                    score.save()
                    StudioAsset.objects.update_or_create(key=key,defaults={"score":score,"revision":REVISION})
        except Exception:
            storage = Score._meta.get_field("musicxml").storage
            for name in newly_written:
                try: storage.delete(name)
                except OSError: pass
            raise
        self.stdout.write(self.style.SUCCESS(f"Still studio ready: composition {composition.pk}, 12 lessons / 36 lesson stages, 8 continuity studies, 36 exercises, 18 theory topics / 19 interactive activities. Profile preserved."))
