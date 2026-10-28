from collections import Counter
from hashlib import sha256
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

import mido
from django.test import SimpleTestCase

from apps.scores.midi import parse_midi
from apps.studio.ivory_import import add_reviewed_notes, build_catalog
from apps.studio.ivory_repertoire import ROOT, performance_provenance, performance_source, variant_entry


BLUE_BELL_REPAIR = {
    "track_index": 1, "channel": 0, "pitch": 83,
    "start_ticks": 164, "end_ticks": 959, "velocity": 48,
    "reason": "User-directed restoration of sequential E-G-B: B5 follows G5. Timing and velocity are editorial inferences from the accompaniment and phrase landmarks, not a recovered original MIDI event.",
}


def note_signature(event):
    return (event["track_index"], event["channel"], event.get("port", 0), event["pitch"]["midi"], event["velocity"], event["start_ticks"], event["end_ticks"], event["sound_end_ticks"])


class ReviewedNoteAdditionTests(SimpleTestCase):
    def source(self):
        midi = mido.MidiFile(ticks_per_beat=480)
        midi.tracks.append(mido.MidiTrack([
            mido.MetaMessage("set_tempo", tempo=500000),
            mido.Message("note_on", note=60, velocity=70),
            mido.Message("note_off", note=60, time=480),
            mido.Message("note_on", note=64, velocity=80),
            mido.Message("note_off", note=64, time=480),
            mido.MetaMessage("end_of_track"),
        ]))
        output = io.BytesIO()
        midi.save(file=output)
        return output.getvalue()

    def addition(self, **overrides):
        return {"track_index": 0, "channel": 0, "pitch": 67,
                "start_ticks": 240, "end_ticks": 720, "velocity": 65,
                "reason": "Explicit test repair", **overrides}

    def test_only_the_requested_note_is_added_and_all_source_messages_keep_absolute_ticks(self):
        raw = self.source()
        content = add_reviewed_notes(raw, [self.addition()])
        before, after = parse_midi(raw), parse_midi(content)
        originals = Counter(map(note_signature, before["events"]))
        result = Counter(map(note_signature, after["events"]))
        self.assertFalse(originals-result)
        self.assertEqual(list((result-originals).elements()), [(0, 0, 0, 67, 65, 240, 720, 720)])
        self.assertEqual(before["metadata"]["duration_seconds"], after["metadata"]["duration_seconds"])

        def messages(data):
            result, tick = [], 0
            for message in mido.MidiFile(file=io.BytesIO(data)).tracks[0]:
                tick += message.time
                result.append((tick, str(message.copy(time=0))))
            return result

        # Original message order and absolute timing survive the insertion.
        actual = [row for row in messages(content) if "note=67 " not in row[1]]
        self.assertEqual(actual, messages(raw))

    def test_empty_review_is_an_exact_byte_noop(self):
        raw = self.source()
        self.assertEqual(add_reviewed_notes(raw, []), raw)

    def test_invalid_unbounded_or_ambiguous_repairs_are_rejected(self):
        raw = self.source()
        invalid = [None, {}, [self.addition()]*9,
                   [self.addition(track_index=1)], [self.addition(track_index=-1)],
                   [self.addition(channel=9)], [self.addition(channel=16)],
                   [self.addition(pitch=128)], [self.addition(pitch=-1)],
                   [self.addition(velocity=0)], [self.addition(velocity=128)],
                   [self.addition(start_ticks=-1)], [self.addition(start_ticks=720)],
                   [self.addition(end_ticks=961)], [self.addition(end_ticks=240)],
                   [self.addition(start_ticks=1.5)], [self.addition(velocity=True)],
                   [self.addition(reason="")], [self.addition(reason=" ")],
                   [self.addition(reason="a"*1001)], [self.addition(unreviewed_field=True)],
                   [self.addition(pitch=60)],
                   [self.addition(), self.addition(start_ticks=480, end_ticks=800)]]
        for additions in invalid:
            with self.subTest(additions=additions):
                with self.assertRaises(ValueError):
                    add_reviewed_notes(raw, additions)

        midi = mido.MidiFile(ticks_per_beat=480)
        midi.tracks.append(mido.MidiTrack())
        empty = io.BytesIO()
        midi.save(file=empty)
        with self.assertRaises(ValueError):
            add_reviewed_notes(empty.getvalue(), [self.addition()])

    def test_builder_preserves_raw_bytes_and_counts_omitted_and_added_notes_separately(self):
        raw = self.source()
        digest = sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory)/"source", Path(directory)/"output"
            source.mkdir()
            (source/"example.mid").write_bytes(raw)
            (source/"manifest.json").write_text(json.dumps({"items": [{
                "filename": "example.mid", "url": "https://example.com/source",
                "ivory_player_url": "https://example.com/player",
                "validation": {"sha256": digest, "note_count": 2},
            }]}), encoding="utf-8")
            plan = [{"code": "example", "slug": "example", "title": "Example", "existing_code": "example",
                     "composer": "", "collection": "", "variants": [{
                         "id": "performance-1", "filename": "example.mid",
                         "source_sha256": digest, "difficulty": 2,
                         "preview_start": 0, "note_additions": [self.addition()],
                     }]}]
            groups = build_catalog(plan, source, output, expected_count=1)
            entry = groups[0]["variants"][0]
            self.assertEqual((entry["omitted_note_count"], entry["added_note_count"], entry["note_count"]), (0, 1, 3))
            self.assertEqual((output/"originals"/"example.mid").read_bytes(), raw)
            self.assertEqual(entry["source_sha256"], digest)
            self.assertNotEqual(entry["sha256"], digest)
            # The checked-in output manifest is itself a reproducible plan.
            self.assertEqual(build_catalog(groups, source, Path(directory)/"rebuilt", expected_count=1), groups)
            with patch("apps.studio.ivory_repertoire.variant_entry", return_value={**entry, "hand_roles": {"evidence": "test"}}):
                provenance = performance_provenance("example")
            self.assertFalse(provenance["preserved_original_bytes"])
            self.assertTrue(provenance["editorial_repair"])
            self.assertEqual(provenance["added_note_count"], 1)
            self.assertIn("Explicit test repair", provenance["editorial_repair_reason"])


class BlueBellEditorialRepairTests(SimpleTestCase):
    def test_checked_in_asset_and_provenance_reproduce_the_explicit_repair(self):
        raw = (ROOT/"originals"/"shiki-blue-bell.mid").read_bytes()
        content, parsed = performance_source("shiki-blue-bell", "performance-1")
        entry = variant_entry("shiki-blue-bell", "performance-1")
        self.assertEqual(entry["note_additions"], [BLUE_BELL_REPAIR])
        self.assertEqual((entry["omitted_note_count"], entry["added_note_count"], entry["note_count"]), (0, 1, 309))
        self.assertEqual(sha256(raw).hexdigest(), entry["source_sha256"])
        self.assertEqual(sha256(content).hexdigest(), entry["sha256"])
        self.assertEqual(content, add_reviewed_notes(raw, entry["note_additions"]))
        self.assertEqual(len(parsed["events"]), 309)
        provenance = performance_provenance("shiki-blue-bell", "performance-1")
        self.assertFalse(provenance["preserved_original_bytes"])
        self.assertTrue(provenance["editorial_repair"])
        self.assertEqual(provenance["added_note_count"], 1)
        self.assertEqual(provenance["note_additions"], [BLUE_BELL_REPAIR])
        self.assertIn("editorial inferences", provenance["editorial_repair_reason"])

        def source_messages(data, exclude_added=False):
            result = []
            for track_index, track in enumerate(mido.MidiFile(file=io.BytesIO(data)).tracks):
                tick = 0
                for message in track:
                    tick += message.time
                    if exclude_added and track_index == 1 and message.type in {"note_on", "note_off"} and message.note == 83 and tick in {164, 959}:
                        continue
                    result.append((track_index, tick, str(message.copy(time=0))))
            return result

        self.assertEqual(source_messages(content, exclude_added=True), source_messages(raw))

    def test_b5_follows_g5_with_every_original_note_unchanged(self):
        original = ROOT/"originals"/"shiki-blue-bell.mid"
        raw = (original if original.exists() else ROOT/"shiki-blue-bell.mid").read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), "6c39f9c7f5a5eea8a14c91da966ab29936eb76f71d67c3f557e795e3e0103d20")
        content = add_reviewed_notes(raw, [BLUE_BELL_REPAIR])
        before, after = parse_midi(raw), parse_midi(content)
        originals = Counter(map(note_signature, before["events"]))
        result = Counter(map(note_signature, after["events"]))
        self.assertFalse(originals-result)
        self.assertEqual(list((result-originals).elements()), [(1, 0, 0, 83, 48, 164, 959, 959)])
        self.assertEqual((len(before["events"]), len(after["events"])), (308, 309))
        b5 = next(event for event in after["events"] if event["pitch"]["midi"] == 83 and event["start_ticks"] == 164)
        self.assertAlmostEqual(b5["onset_seconds"], .8541666666666666)
        self.assertAlmostEqual(b5["onset_seconds"]+b5["duration_seconds"], 4.994791666666667)
        self.assertFalse(after["warnings"])
        self.assertFalse(after["pedal_events"])
