"""Pinned editions bundled with their individual source and rights records.

Import never downloads music. Public-domain/CC editions retain their stated
terms; other editions record the owner's explicit redistribution confirmation.
Changed bytes fail preparation instead of silently substituting a performance.
"""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

from apps.scores.midi import parse_midi


CATALOG_ROOT = Path(__file__).with_name("assets") / "catalog"
ENTRIES = tuple(json.loads((CATALOG_ROOT / "manifest.json").read_text(encoding="utf-8")))
ENTRY_BY_CODE = {entry["code"]: entry for entry in ENTRIES}


def active_entries():
    return ENTRIES


def source_path(entry):
    filename = entry["code"] + ".mid"
    return CATALOG_ROOT / filename


@lru_cache(maxsize=40)
def edition_source(code):
    entry = ENTRY_BY_CODE[code]
    path = source_path(entry)
    try:
        content = path.read_bytes()
    except FileNotFoundError as error:
        raise ValueError(f"{code}: the reviewed repertoire file is missing.") from error
    if sha256(content).hexdigest() != entry["sha256"]:
        raise ValueError(f"{code}: MIDI checksum changed; review this edition before importing it.")
    parsed = parse_midi(content, entry["title"])
    if len(parsed["events"]) != entry["note_count"]:
        raise ValueError(f"{code}: source note count differs from the reviewed edition.")
    roles = entry["hand_roles"]
    for event in parsed["events"]:
        if event.get("percussion") or not event.get("pitch"):
            continue
        if roles["method"] == "tracks":
            role = roles["tracks"].get(str(event["track_index"]))
        else:
            role = "left" if event["pitch"]["midi"] < roles["split_pitch"] else "right"
        if role not in {"left", "right"}:
            raise ValueError(f"{code}: every pitched source layer needs a reviewed display role.")
        event["hand"] = role
        event["hand_evidence"] = roles["evidence"]
    for part in parsed["parts"]:
        part["hand"] = roles.get("tracks", {}).get(str(part["index"]), "unknown")
        part["hand_evidence"] = roles["evidence"]
    parsed["capabilities"]["hand_assignment"] = roles["evidence"]
    return content, parsed


def edition_provenance(code):
    entry = ENTRY_BY_CODE[code]
    value = {"kind": "curated_public_edition" if entry["rights_basis"] == "published_open_license" else "owner_authorized_edition",
            "composition_code": code, "filename": code + ".mid", "source_sha256": entry["sha256"],
            "preserved_original_bytes": not entry.get("rendered_from_musicxml", False), "source_url": entry["source_url"],
            "credit": entry["credit"], "license": entry["license"],
            "license_url": entry.get("license_url", ""),
            "hand_assignment": entry["hand_roles"]["evidence"],
            "note_release_basis": "Source MIDI note-on/note-off durations; CC64 sustain is stored separately by the MIDI parser.",
            "completeness_scope": f"All {entry['note_count']} notes of this pinned edition; not a claim of equivalence to another published arrangement.",
            "permission_basis": entry["rights_basis"],
            "source_document_sha256": entry.get("source_document_sha256", ""),
            "edition_note": entry["edition_note"]}
    if entry.get("source_cleanup"):
        value.update({"preserved_original_bytes": False, "source_cleanup": entry["source_cleanup"],
                      "original_sha256": entry["source_cleanup"]["original_sha256"]})
    return value
