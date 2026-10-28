"""Technical checks; this cannot prove fidelity to an unknown original score.

No timing, overlapping voice, velocity or long hold is silently rewritten.
Known source diagnostics are reviewed against their exact byte hashes.
"""
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path

from .all_in_package import package_source
from .curated_repertoire import edition_source
from .ivory_repertoire import GROUPS, performance_source
from .repertoire import SOURCES, repertoire_source

REVIEW_PATH = Path(__file__).with_name("midi_quality_review.json")


def inspect_performance(code, variant, data, parsed):
    events = parsed["events"]
    issues = list(parsed["warnings"])
    duration = parsed["metadata"]["duration_seconds"]
    if not math.isfinite(duration) or duration <= 0 or not events:
        issues.append("The performance needs a finite, nonempty timeline.")
    if len({e["id"] for e in events}) != len(events):
        issues.append("Source event IDs must be unique.")
    signatures, active, overlaps = Counter(), {}, 0
    for event in sorted(events, key=lambda e: e["onset_seconds"]):
        pitch = event["pitch"]["midi"]
        voice = (event["track_index"], event.get("port", 0), event["channel"], pitch)
        signatures[(*voice, event["start_ticks"], event["end_ticks"], event["velocity"])] += 1
        values = [event["onset_seconds"], event["duration_seconds"], event["sound_duration_seconds"]]
        if not all(math.isfinite(v) for v in values) or event["onset_seconds"] < 0 or event["duration_seconds"] <= 0 or event["onset_seconds"] + event["sound_duration_seconds"] > duration + 1e-5:
            issues.append(f"{event['id']}: invalid note timeline.")
        if not 21 <= pitch <= 108:
            issues.append(f"{event['id']}: outside the 88-key piano range.")
        if event.get("hand") not in {"left", "right"} or event.get("percussion"):
            issues.append(f"{event['id']}: the display layer needs review.")
        if not 1 <= event["velocity"] <= 127:
            issues.append(f"{event['id']}: invalid attack velocity.")
        if active.get(voice, -1) > event["start_ticks"]:
            overlaps += 1
        active[voice] = max(active.get(voice, -1), event["end_ticks"])
    return {
        "code": code, "variant": variant, "sha256": sha256(data).hexdigest(),
        "notes": len(events), "duration_seconds": duration,
        "duplicate_attacks": sum(count-1 for count in signatures.values()),
        "same_voice_overlaps": overlaps,
        "holds_at_least_eight_seconds": sum(e["duration_seconds"] >= 8 for e in events),
        "pedal_events": len(parsed["pedal_events"]), "issues": issues,
    }


def iter_catalog_performances():
    for source in SOURCES:
        data, parsed = repertoire_source(source.code)
        yield inspect_performance(source.code, "original", data, parsed)
        for loader in (repertoire_source, performance_source, edition_source):
            loader.cache_clear()
    for group in GROUPS:
        variants = group["variants"] if group.get("base_variant") else group["variants"][1:]
        for variant in variants:
            data, parsed = performance_source(group["code"], variant["id"])
            yield inspect_performance(group["code"], variant["id"], data, parsed)
            performance_source.cache_clear()
    data, parsed = package_source("All_In_Plus5_Easy_LH.mid")
    yield inspect_performance("all-in", "easy", data, parsed)
    package_source.cache_clear()


def unreviewed_diagnostics(row, reviews):
    if not row["duplicate_attacks"] and not row["same_voice_overlaps"]:
        return False
    return not any(
        entry["code"] == row["code"] and entry["variant"] == row["variant"]
        and entry["sha256"] == row["sha256"]
        and entry["duplicate_attacks"] == row["duplicate_attacks"]
        and entry["same_voice_overlaps"] == row["same_voice_overlaps"]
        and entry.get("review_reason")
        for entry in reviews)


def audit_catalog():
    reviews = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    rows = list(iter_catalog_performances())
    for row in rows:
        if unreviewed_diagnostics(row, reviews):
            row["issues"].append("New duplicate/overlapping source attacks require a review of this exact MIDI.")
    return rows
