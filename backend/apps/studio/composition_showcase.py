"""Reviewed presentation for the supplied arrangements, not universal work grades.

Excerpts retain every overlapping source note, including both hands and notes
already held at the boundary. No melody-only sampling or invented MIDI is used.
"""
from django.http import Http404
from rest_framework.exceptions import NotFound

from .all_in_package import variant_definitions
from .models import StudioAsset
from .repertoire import SOURCES, SOURCE_BY_CODE
from .curated_repertoire import active_entries


# Seconds refer to the exact supplied exports and their reviewed course landmarks.
# These five-star ratings describe these arrangements, not an examination grade.
SHOWCASE = {
    "still": {"difficulty": 3, "start": 16, "duration": 16},
    "youth": {"difficulty": 4, "start": 13, "duration": 16},
    "star": {"difficulty": 3, "start": 0, "duration": 16},
    "tears": {"difficulty": 3, "start": 48, "duration": 14},
    "my-memory": {"difficulty": 3, "start": 14, "duration": 16},
    "premonition": {"difficulty": 4, "start": 30, "duration": 16},
    "memories": {"difficulty": 2, "start": 11, "duration": 16},
    "all-in": {"difficulty": 2, "start": 67.04, "duration": 16,
               "variants": {"easy": 2, "hard": 4}},
}
SHOWCASE.update({entry["code"]: {"difficulty": entry["difficulty"], "start": entry["preview_start"],
                                  "duration": entry["preview_duration"]} for entry in active_entries()})


def presentation(code, variant=None):
    value = SHOWCASE[code]
    return {"difficulty": value.get("variants", {}).get(variant, value["difficulty"]),
            "collection": SOURCE_BY_CODE[code].collection,
            "preview_start_seconds": value["start"]}


def excerpt_notes(events, start, duration):
    end = start + duration
    notes = []
    for event in events:
        if not event.get("pitch") or event.get("rest") or event.get("percussion"):
            continue
        onset = event["onset_seconds"]
        release = onset + event["duration_seconds"]
        if onset >= end or release <= start:
            continue
        clipped_onset = max(start, onset)
        clipped_duration = min(end, release) - clipped_onset
        notes.append({"id": event["id"], "pitch": event["pitch"]["midi"],
                      "onset": clipped_onset - start, "duration": clipped_duration,
                      "soundDuration": clipped_duration,
                      "velocity": event.get("velocity", 85),
                      "hand": "left" if event.get("hand") == "left" else "right"})
    return sorted(notes, key=lambda note: (note["onset"], note["pitch"]))


def composition_preview(composition_id, variant=None):
    source_keys = {source.asset_key: source for source in SOURCES}
    original = StudioAsset.objects.select_related("score__arrangement").filter(
        key__in=source_keys, score__arrangement__composition_id=composition_id).first()
    if original is None:
        raise Http404("Composition not found")
    source = source_keys[original.key]
    variants = variant_definitions(source.code)
    if variant and variant not in {item["id"] for item in variants}:
        raise NotFound("Performance variant not found")
    selected = next((item for item in variants if item["id"] == variant), None)
    if variants and selected is None:
        selected = variants[0]
    if selected:
        try:
            score = StudioAsset.objects.select_related("score").get(pk=selected["_asset_key"]).score
        except StudioAsset.DoesNotExist:
            raise NotFound("Performance variant not found")
    else:
        score = original.score
    reviewed = SHOWCASE[source.code]
    start = reviewed["start"]
    duration = min(reviewed["duration"], score.parsed["metadata"]["duration_seconds"] - start)
    return {"composition_id": composition_id, "score_id": score.pk,
            "variant_id": selected["id"] if selected else None,
            "start_seconds": start, "duration_seconds": duration,
            "notes": excerpt_notes(score.parsed["events"], start, duration)}
