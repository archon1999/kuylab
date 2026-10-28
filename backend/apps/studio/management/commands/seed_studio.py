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
from apps.studio.comparisons import COMPARISONS, definitions, comparison_midi
from apps.studio.content import REVISION, all_items
from apps.studio.midi_authoring import SOURCE_SHA256, source_data, lesson_stage_midi, exercise_notes, theory_midi
from apps.studio.models import StudioAsset
from apps.studio.repertoire import SOURCES, SOURCE_BY_CODE, repertoire_source
from apps.studio.all_in_package import additional_assets, package_source, study_file, HASHES
from apps.studio.curated_repertoire import ENTRY_BY_CODE, edition_provenance
from apps.studio.ivory_repertoire import GROUP_BY_CODE as IVORY_BY_CODE, additional_assets as ivory_assets, performance_provenance, performance_source

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
    for source in SOURCES[1:]:
        content, source_parsed = repertoire_source(source.code)
        if source.course_kind == "ivory":
            assets.append((source.asset_key, source.title, content, source_parsed, performance_provenance(source.code)))
            continue
        if source.course_kind == "curated":
            assets.append((source.asset_key, source.title, content, source_parsed, edition_provenance(source.code)))
            continue
        if source.course_kind == "package":
            assets.append((source.asset_key, source.title, content, source_parsed, {
                "kind": "user_supplied_original_midi", "filename": source.filename,
                "composition_code": source.code, "source_sha256": source.sha256,
                "preserved_original_bytes": True, "hand_assignment": "supplied_track_names",
                "completeness_scope": "Complete supplied Full +5 arrangement, not independently verified against a published edition.",
                "unknown_metadata": ["composer", "arranger", "redistribution_license"],
            }))
            continue
        assets.append((source.asset_key, source.title, content, source_parsed, {
            "kind": "user_supplied_original_midi", "filename": source.filename,
            "composition_code": source.code, "source_sha256": source.sha256,
            "preserved_original_bytes": True,
            "completeness_scope": f"All bytes and all {len(source_parsed['events'])} notes of the supplied file; not independently verified against a published arrangement.",
            "hand_assignment": "Reviewed unnamed export layers: track 0 upper => right, track 1 lower => left; not literal fingering or physical hand metadata.",
            "unknown_metadata": ["arranger", "key_signature", "time_signature"] + ([] if source.composer else ["composer"]),
            "composer_evidence": "user_supplied_filename" if source.composer else "not_supplied",
            "note_release_basis": "User's replacement performance export without pedal-extended note durations; no CC64 events supplied.",
        }))
    assets.extend(additional_assets())
    assets.extend(ivory_assets())
    for item in all_items():
        provenance = {"kind":"original_authored_study", "catalog_id":item["id"], "revision":REVISION}
        if item["kind"] in {"lesson", "journey"}:
            source_code = item.get("_composition", "still")
            _, item_source = repertoire_source(source_code)
            source = SOURCE_BY_CODE[source_code]
            for stage in item["stages"]:
                if stage.get("_reuse_original"):
                    continue
                if stage.get("_package_file"):
                    data, details = study_file(stage["_package_file"])
                    title = item["title"]["uz"] + " · " + stage["title"]["uz"]
                    assets.append((stage["_asset_key"], title, data, parse_midi(data, title), {
                        **provenance, **details, "stage_id": stage["id"],
                    }))
                    continue
                if source_code == "all-in":
                    filename = "All_In_Plus5_Easy_LH.mid" if stage.get("_source_variant") == "easy" else "All_In_Plus5_Full.mid"
                    _, stage_source = package_source(filename)
                    source_digest = HASHES[filename]
                else:
                    stage_source, source_digest = item_source, source.sha256
                spec = stage["_generator"]
                data, identifiers = lesson_stage_midi(stage_source, **spec)
                stage_provenance = {**provenance, "kind":"teaching_adaptation", "stage_id": stage["id"],
                    "source_sha256":source_digest, "source_event_ids":identifiers,
                    "source_start_seconds":spec["start"], "source_end_seconds":spec["end"],
                    "selection":spec["selection"], "source_speed_percent": spec["speed_percent"],
                    "source_timing_preserved":spec["speed_percent"] == 100,
                    "uniform_time_scale":100/spec["speed_percent"], "end_boundary_clipped":True,
                    "transformation_description": stage["instruction"]["en"]}
                if source_code != "still":
                    stage_provenance["composition_code"] = source_code
                    stage_provenance["note_release_basis"] = "Supplied package key holds, uniformly scaled; source CC64 messages only reset sustain off." if source_code == "all-in" else "Replacement source note-off, uniformly scaled; no pedal tail baked into key holds."
                if source.course_kind == "curated":
                    stage_provenance.update({"source_url": ENTRY_BY_CODE[source_code]["source_url"],
                                             "license": ENTRY_BY_CODE[source_code]["license"],
                                             "credit": ENTRY_BY_CODE[source_code]["credit"],
                                             "note_release_basis": "Source note-on/off timing, uniformly scaled; sustain is not baked into key holds."})
                if source_code == "all-in":
                    stage_provenance["source_variant"] = stage["_source_variant"]
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
    for topic in COMPARISONS:
        for variant in definitions(topic):
            data = comparison_midi(topic, variant["id"].split(":")[-1])
            title = variant["title"]["uz"]
            assets.append((variant["id"], title, data, parse_midi(data, title), {"kind":"original_authored_comparison", "topic":topic, "variant":variant["id"]}))
    return assets


class Command(BaseCommand):
    help = "Prepare the curated repertoire and authored studies; preserve users and existing score identities."

    def add_arguments(self, parser):
        parser.add_argument("--replace-compositions", action="store_true", help="Explicitly delete other compositions and their dependent records.")

    def handle(self, *args, **options):
        # Validate every byte and teaching example before a destructive transaction.
        assets = prepared_assets()
        others = Composition.objects.exclude(seed_key__in=[source.composition_key for source in SOURCES])
        if others.exists() and not options["replace_compositions"]:
            raise CommandError("Other compositions exist. Take a database snapshot, then pass --replace-compositions to replace them explicitly.")
        newly_written = []
        try:
            with transaction.atomic():
                if options["replace_compositions"]:
                    others.delete()
                arrangements = {}
                variant_arrangements = {}
                for source in SOURCES:
                    composition, _ = Composition.objects.update_or_create(seed_key=source.composition_key, defaults={
                        "title":source.title, "composer":source.composer,
                        "category":"Dorama OST" if source.collection == "Winter Sonata" else "Repertuar", "status":"active",
                        "goal":source.title + " orqali ravon va ifodali chalishni o‘rganish", "color":"#B98460"})
                    arrangement, _ = Arrangement.objects.update_or_create(seed_key=source.arrangement_key, defaults={
                        "composition":composition,"is_default":True,"title":source.filename,
                        "source_kind":"own","rights_status":"user_owned","rights_note":"User-supplied MIDI copy for this personal studio; publisher, arranger and redistribution license not supplied.",
                        "exact_version_confirmed":True,"workflow_status":"curated_studio","tempo_bpm":120,
                        "tempo_beat_unit":"quarter","key_signature":"","time_signature":"","arranger":"",
                        "full_score_format":"midi","full_score_verified_at":None})
                    arrangements[source.code] = arrangement
                    if source.course_kind == "ivory":
                        for index, variant in enumerate(IVORY_BY_CODE[source.code]["variants"]):
                            _, parsed = performance_source(source.code, variant["id"])
                            title = variant["title"]
                            label = title["uz"] if isinstance(title, dict) else title
                            defaults = {"composition": composition, "is_default": index == 0,
                                "title": source.title + " · " + label,
                                "source_url": variant["source_url"], "reference_video_url": variant["source_url"],
                                "source_kind": "own", "rights_status": "user_owned",
                                "rights_note": "Owner-supplied Ivory Performance MIDI; owner instructed import. Original musical rights retained.",
                                "arranger": variant.get("performer", "")[:120],
                                "exact_version_confirmed": True, "workflow_status": "curated_studio",
                                "tempo_bpm": round(parsed["metadata"]["tempo"]["quarter_bpm"]),
                                "tempo_beat_unit": "quarter", "key_signature": "", "time_signature": "",
                                "full_score_format": "midi", "full_score_verified_at": None}
                            if index == 0:
                                for field, value in defaults.items():
                                    setattr(arrangement, field, value)
                                arrangement.save(update_fields=list(defaults))
                                selected_arrangement = arrangement
                            else:
                                key = f"studio-{source.code}-{variant['id']}"
                                if len(key) > 80:
                                    key = f"studio-{source.code[:48]}-{hashlib.sha256(variant['id'].encode()).hexdigest()[:16]}"
                                selected_arrangement, _ = Arrangement.objects.update_or_create(seed_key=key, defaults=defaults)
                            variant_arrangements[(source.code, variant["id"])] = selected_arrangement
                    if source.course_kind == "curated":
                        entry = ENTRY_BY_CODE[source.code]
                        arrangement.source_url = entry["source_url"]
                        arrangement.source_kind = "public_domain" if entry["license"] == "Public Domain" else "licensed" if entry["storage"] == "public" else "link"
                        arrangement.rights_status = "public_domain" if entry["license"] == "Public Domain" else "licensed" if entry["storage"] == "public" else "unconfirmed"
                        arrangement.rights_note = entry["license"] + ". " + entry["credit"] + ". " + entry["edition_note"]
                        arrangement.arranger = entry["credit"][:120]
                        arrangement.tempo_bpm = round(entry["quarter_bpm"])
                        arrangement.key_signature = entry["key_label"]
                        arrangement.time_signature = entry["time_label"]
                        arrangement.save(update_fields=["source_url", "source_kind", "rights_status", "rights_note", "arranger", "tempo_bpm", "key_signature", "time_signature"])
                    if source.course_kind == "package":
                        _, parsed = repertoire_source(source.code)
                        arrangement.tempo_bpm = round(parsed["metadata"]["tempo"]["quarter_bpm"])
                        arrangement.key_signature = "D minor"
                        arrangement.time_signature = "mixed"
                        arrangement.save(update_fields=["tempo_bpm", "key_signature", "time_signature"])
                for key, title, content, parsed, provenance in assets:
                    source = SOURCE_BY_CODE[provenance.get("composition_code", "still")]
                    arrangement = variant_arrangements.get((source.code, provenance.get("variant_id")), arrangements[source.code])
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
                                  source_url=provenance.get("source_url", ""),
                                  original_filename=provenance.get("filename", source.filename) if provenance.get("preserved_original_bytes") or source.course_kind == "ivory" else key.replace(":","-")+".mid",
                                  content_sha256=digest,source_provenance=provenance,parsed=parsed,
                                  rights_note=(ENTRY_BY_CODE[source.code]["license"] + ". " + ENTRY_BY_CODE[source.code]["credit"]) if source.course_kind == "curated" else "Owner-supplied Ivory performance; original musical rights retained. Only a separately documented channel intro may be omitted." if source.course_kind == "ivory" else "User-provided source, preserved without modification." if provenance.get("preserved_original_bytes") else "Teaching adaptation of the user's source; not a publisher edition." if provenance["kind"] == "teaching_adaptation" else "User-supplied course drill; separate percussion track omitted for piano study." if provenance["kind"] == "supplied_course_drill" else "Original practice example authored for this studio.",
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
        items = all_items()
        counts = {kind: sum(item["kind"] == kind for item in items) for kind in ("lesson", "journey", "exercise", "theory")}
        self.stdout.write(self.style.SUCCESS(f"Curated studio ready: {len(SOURCES)} compositions, {sum(len(group['variants']) for group in IVORY_BY_CODE.values())} Ivory performances, {counts['lesson']} lessons, {counts['journey']} continuity studies, {counts['exercise']} exercises, {counts['theory']} theory topics. Users and historical sources preserved."))
