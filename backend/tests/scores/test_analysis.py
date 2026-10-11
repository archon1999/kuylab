from pathlib import Path
from django.test import SimpleTestCase
from apps.scores.analysis import analyze_passage
from apps.scores.parser import parse_musicxml


def note(step="C", octave=4, duration=2, extra="", voice="1", staff=1):
    return f"<note>{extra}<pitch><step>{step}</step><octave>{octave}</octave></pitch><duration>{duration}</duration><voice>{voice}</voice><staff>{staff}</staff></note>"


def score(bodies, staves=1):
    attributes = f"<attributes><divisions>2</divisions><time><beats>4</beats><beat-type>4</beat-type></time><staves>{staves}</staves></attributes>"
    measures = "".join(f'<measure number="{index + 1}">{attributes if index == 0 else ""}{body}</measure>' for index, body in enumerate(bodies))
    return parse_musicxml((f'<score-partwise><part-list><score-part id="P1"><part-name>Piano</part-name></score-part></part-list><part id="P1">{measures}</part></score-partwise>').encode())


class PassageAnalysisTests(SimpleTestCase):
    def test_actual_demo_counts_chords_ties_and_never_claims_mastery(self):
        parsed = parse_musicxml((Path(__file__).resolve().parents[2] / "apps/scores/demo.musicxml").read_bytes())
        result = analyze_passage(parsed, 0, 1, tempo_bpm=40, beat_unit="dotted_quarter")
        facts = result["facts"]
        self.assertEqual(result["range"]["measure_numbers"], ["1", "2"])
        self.assertEqual(facts["pitched_note_count"], 16)
        self.assertEqual(facts["playable_pitch_count"], 16)
        self.assertEqual(facts["attack_count"], 15)
        self.assertEqual(facts["chord_group_count"], 4)
        self.assertEqual(facts["tie_count"], 2)
        self.assertEqual(facts["hand_counts"], {"right": 8, "left": 8, "unknown": 0})
        self.assertIsNone(facts["max_leaps"]["left"])
        self.assertEqual(facts["max_leaps"]["right"]["semitones"], 4)
        self.assertEqual(len(result["steps"]), 4)
        self.assertIn("nuqtali chorak = 40/min", result["steps"][2]["instruction"])
        self.assertFalse(any(result["claims"].values()))

    def test_selected_tied_continuation_is_not_new_attack(self):
        parsed = score([note(duration=8, extra='<tie type="start"/>'), note(duration=8, extra='<tie type="stop"/>')])
        result = analyze_passage(parsed, 1, 1)
        self.assertEqual(result["facts"]["pitched_note_count"], 1)
        self.assertEqual(result["facts"]["attack_count"], 0)
        self.assertEqual(result["steps"][3]["range"]["start_index"], 0)
        self.assertEqual(result["steps"][3]["range"]["end_index"], 1)

    def test_rhythm_matches_are_distinguished_from_pitch_matches(self):
        rest = "<note><rest/><duration>4</duration><voice>1</voice><staff>1</staff></note>"
        first = note("C") + note("D") + rest
        second = note("E") + note("F") + rest
        parsed = score([first, second, first])
        patterns = analyze_passage(parsed, 0, 2)["facts"]["rhythm_repetition"]
        self.assertEqual(patterns["pair_count"], 3)
        self.assertEqual(patterns["note_pair_count"], 1)
        self.assertEqual(patterns["rhythm_only_pair_count"], 2)
        self.assertEqual(patterns["note_pairs"][0]["first_index"], 0)
        self.assertEqual(patterns["note_pairs"][0]["second_index"], 2)
        self.assertEqual(patterns["pitch_sequence_pair_count"], 1)

    def test_same_pitches_with_different_rhythm_have_separate_fact(self):
        parsed = score([note("C", duration=2) + note("D", duration=6), note("C", duration=4) + note("D", duration=4)])
        patterns = analyze_passage(parsed, 0, 1)["facts"]["rhythm_repetition"]
        self.assertEqual(patterns["pair_count"], 0)
        self.assertEqual(patterns["note_pair_count"], 0)
        self.assertEqual(patterns["pitch_sequence_pair_count"], 1)

    def test_chord_roots_and_other_voices_are_excluded_from_leap_path(self):
        body = note("C") + note("E") + note("G", extra="<chord/>") + note("D")
        body += '<backup><duration>6</duration></backup>' + note("C", octave=6, duration=6, voice="2")
        parsed = score([body])
        result = analyze_passage(parsed, hand_overrides={event["id"]: "right" for event in parsed["events"]})
        self.assertEqual(result["facts"]["chord_group_count"], 1)
        self.assertEqual(result["facts"]["max_leaps"]["right"]["semitones"], 2)
        self.assertEqual(result["facts"]["max_leaps"]["right"]["from"]["pitch"], "C4")
        self.assertEqual(result["facts"]["max_leaps"]["right"]["to"]["pitch"], "D4")

    def test_manual_hand_mapping_and_factual_large_leap_drive_landing_step(self):
        parsed = score([note("C", duration=4) + note("G", octave=5, duration=4)])
        overrides = {event["id"]: "left" for event in parsed["events"]}
        result = analyze_passage(parsed, 0, 0, overrides)
        leap = result["facts"]["max_leaps"]["left"]
        self.assertEqual(leap["semitones"], 19)
        self.assertEqual(leap["to"]["measure_number"], "1")
        self.assertEqual(result["facts"]["hand_counts"], {"right": 0, "left": 2, "unknown": 0})
        self.assertIn("C4 → G5", result["steps"][1]["instruction"])
        self.assertIn("barmoqlarni majburan cho'zmang", result["steps"][1]["instruction"])
        self.assertFalse(any("staff" in caution for caution in result["cautions"]))

    def test_grace_cue_microtones_and_keyboard_range_are_honest(self):
        grace = '<note><grace/><pitch><step>D</step><octave>4</octave></pitch><voice>1</voice><staff>1</staff></note>'
        micro = note("C", duration=2).replace("<octave>", "<alter>0.5</alter><octave>")
        parsed = score([grace + note("E", extra="<cue/>") + micro + note("C", octave=9, duration=4)])
        facts = analyze_passage(parsed)["facts"]
        self.assertEqual(facts["grace_count"], 1)
        self.assertEqual(facts["cue_count"], 1)
        self.assertEqual(facts["pitched_note_count"], 2)
        self.assertEqual(facts["playable_pitch_count"], 0)
        self.assertEqual(facts["short_pitch_names"], ["C(+0.5)4", "C9"])
        self.assertTrue(any("88 klavish" in caution for caution in analyze_passage(parsed)["cautions"]))

    def test_repetition_examples_are_bounded_but_total_count_remains_exact(self):
        parsed = score([note(duration=8)] * 40)
        result = analyze_passage(parsed, 0, 39)
        patterns = result["facts"]["rhythm_repetition"]
        self.assertEqual(patterns["pair_count"], 780)
        self.assertEqual(len(patterns["pairs"]), 24)
        self.assertTrue(patterns["examples_truncated"])
        self.assertIsNone(result["facts"]["short_pitch_names"])

    def test_invalid_ranges_and_undeclared_tempo_are_rejected(self):
        parsed = score([note(duration=8)])
        for start, end in [(-1, 0), (0, 1), (1, 0), (True, 0), (0, "0")]:
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                analyze_passage(parsed, start, end)
        for fields in [{"tempo_bpm": 0}, {"tempo_bpm": float("nan")}, {"beat_unit": "guessed"}, {"hand_overrides": {"a": "fingering"}}]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                analyze_passage(parsed, **fields)
