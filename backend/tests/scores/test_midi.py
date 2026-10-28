"""SMF tests assert musical facts, not a copy of the parser's implementation."""
import hashlib
import io
import json
from pathlib import Path
import mido
from django.test import SimpleTestCase
from apps.scores.midi import parse_midi, quarters_at_seconds
from apps.scores.parser import ScoreImportError


def midi_bytes(*tracks, midi_type=1, ticks_per_beat=480):
    result = mido.MidiFile(type=midi_type, ticks_per_beat=ticks_per_beat)
    for messages in tracks:
        result.tracks.append(mido.MidiTrack(messages))
    stream = io.BytesIO()
    result.save(file=stream)
    return stream.getvalue()


def on(pitch=60, time=0, channel=0, velocity=64):
    return mido.Message("note_on", note=pitch, time=time, channel=channel, velocity=velocity)


def off(pitch=60, time=480, channel=0):
    return mido.Message("note_off", note=pitch, time=time, channel=channel)


def end(time=0):
    return mido.MetaMessage("end_of_track", time=time)


def control(number, value, time=0, channel=0):
    return mido.Message("control_change", control=number, value=value, time=time, channel=channel)


class MidiParserTests(SimpleTestCase):
    def test_nul_padded_display_metadata_is_portable_without_changing_performance(self):
        raw = midi_bytes([
            mido.MetaMessage("track_name", name="Right hand\x00\x00"),
            mido.MetaMessage("copyright", text="Edition credit\x00"),
            on(pitch=69, velocity=83), off(pitch=69, time=720), end(),
        ])
        parsed = parse_midi(raw, "Piano\x00 study")
        self.assertEqual(parsed["metadata"]["title"], "Piano study")
        self.assertEqual(parsed["parts"][0]["name"], "Right hand")
        self.assertEqual(parsed["metadata"]["copyright"], ["Edition credit"])
        self.assertNotIn("\\u0000", json.dumps(parsed))
        event = parsed["events"][0]
        self.assertEqual((event["pitch"]["midi"], event["velocity"], event["hand"]), (69, 83, "right"))
        self.assertEqual((event["onset_seconds"], event["duration_seconds"]), (0, .75))
        self.assertIn("original MIDI bytes are unchanged", parsed["warnings"][0])

    def test_malformed_truncated_async_and_missing_boundaries_are_rejected(self):
        valid = midi_bytes([on(), off(), end()])
        for content in [b"", b"not MIDI", valid[:-1], valid[:20],
                        midi_bytes([on(), off(), end()], midi_type=2)]:
            with self.subTest(content=content[:20]), self.assertRaises(ScoreImportError):
                parse_midi(content)
        # Drop just the end-of-track event and repair the track byte length.
        missing_eot = valid[:-4]
        missing_eot = missing_eot[:18] + (int.from_bytes(valid[18:22], "big") - 4).to_bytes(4, "big") + missing_eot[22:]
        with self.assertRaisesRegex(ScoreImportError, "end-of-track"):
            parse_midi(missing_eot)

    def test_unreleased_and_note_free_files_cannot_be_complete_timelines(self):
        for source in [midi_bytes([on(), end(480)]), midi_bytes([end(480)])]:
            with self.assertRaises(ScoreImportError):
                parse_midi(source)

    def test_tempo_changes_integrate_seconds_and_meter_change_only_changes_navigation(self):
        source = midi_bytes([
            mido.MetaMessage("time_signature", numerator=6, denominator=8),
            mido.MetaMessage("set_tempo", tempo=500000),
            mido.MetaMessage("set_tempo", tempo=1000000, time=960),
            mido.MetaMessage("time_signature", numerator=3, denominator=4, time=480), end(480),
        ], [on(), off(time=1920), end()])
        parsed = parse_midi(source)
        self.assertEqual(parsed["metadata"]["duration_seconds"], 3)
        self.assertEqual(parsed["events"][0]["duration_seconds"], 3)
        self.assertEqual([entry["quarter_bpm"] for entry in parsed["tempo_map"]], [120, 60])
        self.assertEqual([entry["onset_seconds"] for entry in parsed["tempo_map"]], [0, 1])
        self.assertEqual([(window["start_quarters"], window["length_quarters"]) for window in parsed["measures"]], [(0, 3), (3, 1)])
        self.assertEqual(parsed["measures"][1]["time"]["beats"], "3")
        self.assertAlmostEqual(quarters_at_seconds(parsed, 1.5), 2.5)
        self.assertTrue(all(window["provenance"] == "midi_beat_navigation_window" for window in parsed["measures"]))

    def test_overlapping_same_pitch_attacks_and_zero_velocity_release_remain_distinct(self):
        parsed = parse_midi(midi_bytes([on(), on(time=240), on(time=240, velocity=0), off(time=480), end()]))
        events = parsed["events"]
        self.assertEqual(len({event["id"] for event in events}), 2)
        self.assertEqual([event["duration_quarters"] for event in events], [1, 1.5])
        self.assertEqual(events[0]["end_reason"], "note_on_zero_velocity")
        self.assertEqual(events[1]["onset_quarters"], 0.5)

    def test_key_hold_and_sustain_sound_tail_are_separate_and_eot_caps_open_pedal(self):
        released = parse_midi(midi_bytes([control(64, 127), on(), off(), control(64, 0, 480), end(480)]))["events"][0]
        self.assertEqual(released["duration_quarters"], 1)
        self.assertEqual(released["sound_duration_quarters"], 2)
        open_pedal = parse_midi(midi_bytes([control(64, 127), on(), off(), end(960)]))
        self.assertEqual(open_pedal["events"][0]["sound_end_ticks"], open_pedal["metadata"]["file_end_ticks"])
        self.assertEqual(open_pedal["events"][0]["sound_duration_quarters"], 3)

    def test_reset_controllers_releases_sustained_sound_but_preserves_held_keys(self):
        source = midi_bytes([control(64, 127), on(60), on(64), off(60), control(121, 0, 480), off(64, 480), end()])
        events = {event["pitch"]["midi"]: event for event in parse_midi(source)["events"]}
        self.assertEqual(events[60]["sound_duration_quarters"], 2)
        self.assertEqual(events[64]["duration_quarters"], 3)
        self.assertEqual(events[64]["sound_duration_quarters"], 3)

    def test_midi_ports_isolate_sustain_and_cross_track_channel_release_is_valid(self):
        parsed = parse_midi(midi_bytes([
            mido.MetaMessage("midi_port", port=0), control(64, 127), end(1440),
        ], [mido.MetaMessage("midi_port", port=1), on(), off(), end(960)]))
        self.assertEqual(parsed["events"][0]["port"], 1)
        self.assertEqual(parsed["events"][0]["sound_duration_quarters"], 1)
        cross_track = parse_midi(midi_bytes([on(), end(480)], [off(), end()]))
        self.assertEqual(cross_track["events"][0]["duration_quarters"], 1)
        self.assertEqual(cross_track["warnings"], [])

    def test_track_hints_preserve_unknown_hands_and_percussion_without_pitch_guessing(self):
        parsed = parse_midi(midi_bytes([
            mido.MetaMessage("track_name", name="Right Hand"), on(40), off(40), end(),
        ], [mido.MetaMessage("track_name", name="Piano"), on(84), off(84), end()],
            [on(36, channel=9), off(36, channel=9), end()]))
        self.assertEqual([event["hand"] for event in parsed["events"]], ["right", "unknown", "unknown"])
        self.assertTrue(parsed["events"][2]["percussion"])
        self.assertIn("percussion", " ".join(parsed["warnings"]))
        self.assertIsNone(parsed["metadata"]["key"])
        self.assertIsNone(parsed["metadata"]["time"])
        self.assertFalse(parsed["metadata"]["tempo"]["explicit"])
        self.assertFalse(parsed["metadata"]["notation_available"])

    def test_verified_complete_internet_source_matches_independent_hash_hands_and_ending(self):
        asset = Path(__file__).parents[2] / "apps/learning/reference_assets/bitmidi-pirate/pirate-piano.mid"
        content = asset.read_bytes()
        self.assertEqual(len(content), 11918)
        self.assertEqual(hashlib.sha256(content).hexdigest(), "853c5d63d49fdfc685f4215092affa83794298347a52e328ee24fe2ee86da522")
        parsed = parse_midi(content)
        self.assertEqual(parsed["metadata"]["event_count"], 1255)
        self.assertEqual({part["name"]: part["note_count"] for part in parsed["parts"]}, {"Right Hand": 557, "Left Hand": 698})
        self.assertEqual(parsed["metadata"]["duration_seconds"], 77.625)
        self.assertEqual(parsed["metadata"]["total_quarters"], 258.75)
        self.assertEqual(parsed["metadata"]["tempo"]["quarter_bpm"], 200)
        self.assertEqual(parsed["metadata"]["key"]["midi_key"], "F")
        self.assertEqual((parsed["metadata"]["time"]["beats"], parsed["metadata"]["time"]["beat_type"]), ("6", 8))
        self.assertEqual({event["pitch"]["midi"] for event in parsed["events"] if event["onset_quarters"] == 255}, {26, 38, 62})
        self.assertTrue(all(event["sound_end_ticks"] <= parsed["metadata"]["file_end_ticks"] for event in parsed["events"]))
        self.assertTrue(all(21 <= event["pitch"]["midi"] <= 108 and event["duration_quarters"] > 0 for event in parsed["events"]))
        self.assertEqual(parsed["warnings"], [])
