"""Reviewed, owner-supplied Ivory performances and arrangement variants.

The source recording and export are identified separately from a possible
reviewed channel-intro cut. Display hand roles are layer inferences, not claims
about the pianist's actual fingering. No music is downloaded at seed time.
"""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

from apps.scores.midi import parse_midi


ROOT = Path(__file__).with_name("assets") / "ivory"
GROUPS = tuple(json.loads((ROOT / "manifest.json").read_text(encoding="utf-8")))
GROUP_BY_CODE = {group["code"]: group for group in GROUPS}


def asset_key(code, variant):
    group = GROUP_BY_CODE[code]
    primary = not group.get("base_variant") and variant["id"] == group["variants"][0]["id"]
    return f"composition:{code}:original" if primary else f"composition:{code}:{variant['id']}"


def variant_definitions(code):
    group = GROUP_BY_CODE.get(code)
    if not group or (not group.get("base_variant") and len(group["variants"]) < 2):
        return []
    base = group.get("base_variant")
    values = [{**base, "_asset_key": f"composition:{code}:original"}] if base else []
    return values + [{"id": variant["id"], "title": variant["title"],
             "description": variant.get("description", {"uz": "", "ru": "", "en": ""}),
             "_asset_key": asset_key(code, variant)} for variant in group["variants"]]


def variant_entry(code, variant_id=None):
    group = GROUP_BY_CODE[code]
    if variant_id is None:
        return group["variants"][0]
    return next(variant for variant in group["variants"] if variant["id"] == variant_id)


@lru_cache(maxsize=96)
def performance_source(code, variant_id=None):
    entry = variant_entry(code, variant_id)
    content = (ROOT / entry["filename"]).read_bytes()
    if sha256(content).hexdigest() != entry["sha256"]:
        raise ValueError(f"{code}: reviewed Ivory MIDI checksum changed.")
    parsed = parse_midi(content, GROUP_BY_CODE[code]["title"])
    if len(parsed["events"]) != entry["note_count"]:
        raise ValueError(f"{code}: reviewed Ivory note count changed.")
    roles = entry["hand_roles"]
    for event in parsed["events"]:
        if event.get("percussion") or not event.get("pitch"):
            continue
        hand = roles["tracks"].get(str(event["track_index"])) if roles["method"] == "tracks" else "left" if event["pitch"]["midi"] < roles["split_pitch"] else "right"
        if hand not in {"left", "right"}:
            raise ValueError(f"{code}: missing display layer role.")
        event["hand"] = hand
        event["hand_evidence"] = roles["evidence"]
    for part in parsed["parts"]:
        part["hand"] = roles.get("tracks", {}).get(str(part["index"]), "unknown")
        part["hand_evidence"] = roles["evidence"]
    parsed["capabilities"]["hand_assignment"] = roles["evidence"]
    return content, parsed


def performance_provenance(code, variant_id=None):
    entry = variant_entry(code, variant_id)
    value = {"kind": "owner_supplied_ivory_performance", "composition_code": code,
            "variant_id": entry["id"], "filename": entry["filename"],
            "source_url": entry["source_url"], "ivory_player_url": entry.get("ivory_player_url", ""),
            "source_sha256": entry["source_sha256"], "import_sha256": entry["sha256"],
            "preserved_original_bytes": entry["trim_start_seconds"] == 0 and not entry.get("added_note_count", 0) and not entry.get("transpose_semitones", 0),
            "trim_start_seconds": entry["trim_start_seconds"],
            "trim_start_ticks": entry.get("trim_start_ticks", 0),
            "trim_reason": entry.get("trim_reason", ""),
            "omitted_note_count": entry.get("omitted_note_count", 0),
            "added_note_count": entry.get("added_note_count", 0),
            "note_additions": entry.get("note_additions", []),
            "editorial_repair": bool(entry.get("added_note_count", 0)),
            "editorial_repair_reason": "; ".join(note["reason"] for note in entry.get("note_additions", [])),
            "retained_timing_and_velocity_preserved": True,
            "pedal_extended": False, "hand_assignment": entry["hand_roles"]["evidence"],
            "completeness_scope": "All source performance notes after the explicitly reviewed channel-intro boundary, plus any separately documented user-directed editorial note additions; no musical introduction is automatically removed.",
            "permission_basis": "Owner supplied these files and instructed import; original rights retained."}
    if entry.get("transpose_semitones"):
        value.update({"transpose_semitones": entry["transpose_semitones"],
                      "transpose_reason": entry["transpose_reason"],
                      "transpose_scope": "Every note-on/off pitch; original rhythm, key-hold duration, velocity and non-note events retained."})
    return value


def additional_assets():
    for group in GROUPS:
        variants = group["variants"] if group.get("base_variant") else group["variants"][1:]
        for variant in variants:
            content, parsed = performance_source(group["code"], variant["id"])
            yield asset_key(group["code"], variant), group["title"], content, parsed, performance_provenance(group["code"], variant["id"])
