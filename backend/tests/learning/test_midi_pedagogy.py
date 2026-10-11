from types import SimpleNamespace
import mido
from django.test import SimpleTestCase
from apps.scores.midi import parse_midi
from tests.scores.test_midi import midi_bytes, on, off, end
from apps.learning.midi_curriculum import midi_definitions


def definitions(*tracks, sections=None, overrides=None):
    parsed = parse_midi(midi_bytes(*tracks))
    score = SimpleNamespace(id=77, version=1, title="Exact fixture", source_url="https://example.org/source.mid",
                            content_sha256="a" * 64, parsed=parsed, sections=sections or [], hand_overrides=overrides or {})
    arrangement = SimpleNamespace(id=5, composition_id=3, source_url=score.source_url)
    return midi_definitions(arrangement, score), parsed


class MidiPedagogyTests(SimpleTestCase):
    def test_late_left_hand_pair_is_inside_the_register_exercise(self):
        lessons, parsed = definitions([
            mido.MetaMessage("track_name", name="Left Hand"),
            on(48), off(48), on(50, 9120), on(62), off(50), off(62, 0), end(),
        ])
        lesson = next(item for item in lessons if item["content"]["midi_topic"] == "midi-register")
        exercise = lesson["content"]["exercise"]
        pair_ids = {event["id"] for event in parsed["events"] if event["onset_quarters"] == 20}
        self.assertEqual(lesson["content"]["midi_facts"]["span_semitones"], 12)
        self.assertTrue(pair_ids.issubset(exercise["event_ids"]))
        self.assertEqual(exercise["start_seconds"], 10)

    def test_selected_mid_piece_opening_identifies_its_own_first_note_and_meter(self):
        sections = [{"id": "chosen", "title": "Chosen phrase", "start_index": 1, "end_index": 1}]
        lessons, parsed = definitions([
            mido.MetaMessage("time_signature", numerator=6, denominator=8), on(62), off(62),
            mido.MetaMessage("time_signature", numerator=3, denominator=4, time=960),
            on(65), off(65), end(960),
        ], sections=sections)
        opening = next(item for item in lessons if item["content"]["midi_topic"] == "midi-pulse")
        self.assertEqual(opening["content"]["midi_facts"]["first_note"], "F4")
        self.assertEqual(opening["content"]["midi_facts"]["meter_label"], "3/4")
        self.assertEqual(opening["content"]["exercise"]["event_ids"], [parsed["events"][1]["id"]])
        self.assertEqual(opening["quiz"]["questions"][0]["choices"][0]["label"], "F4")

    def test_single_tone_cannot_invent_a_melodic_pair_or_simultaneous_chord(self):
        lessons, _ = definitions([on(), off(), end()])
        topics = {item["content"]["midi_topic"] for item in lessons}
        self.assertNotIn("midi-interval", topics)
        self.assertNotIn("midi-chord", topics)

    def test_sequential_three_notes_and_separate_channels_are_not_a_chord(self):
        for track in [[on(60), off(60), on(64), off(64), on(67), off(67), end()],
                      [on(60), on(64, channel=1), on(67, channel=2), off(60), off(64, 0, 1), off(67, 0, 2), end()]]:
            with self.subTest(track=track):
                lessons, _ = definitions(track)
                self.assertNotIn("midi-chord", {item["content"]["midi_topic"] for item in lessons})

    def test_a_silent_selected_window_does_not_substitute_unrelated_last_notes(self):
        lessons, _ = definitions([on(), off(), on(64, 7200), off(64), end()],
                                 sections=[{"id": "silence", "title": "Silent gap", "start_index": 1, "end_index": 1}])
        self.assertNotIn("midi-pulse", {item["content"]["midi_topic"] for item in lessons})

    def test_mixed_hand_override_group_does_not_count_right_hand_pitch_as_left_span(self):
        source = [mido.MetaMessage("track_name", name="Left Hand"), on(48), on(72), off(48), off(72, 0), end()]
        _, parsed = definitions(source)
        upper = next(event for event in parsed["events"] if event["pitch"]["midi"] == 72)
        lessons, _ = definitions(source, overrides={upper["id"]: "right"})
        register = next(item for item in lessons if item["content"]["midi_topic"] == "midi-register")
        self.assertEqual(register["content"]["midi_facts"]["span_semitones"], 0)

    def test_long_eot_silence_does_not_move_the_ending_excerpt_away_from_actual_notes(self):
        lessons, parsed = definitions([on(), off(), end(20000)])
        ending = next(item for item in lessons if item["content"]["midi_topic"] == "midi-recall")
        self.assertIn(parsed["events"][-1]["id"], ending["content"]["exercise"]["event_ids"])
