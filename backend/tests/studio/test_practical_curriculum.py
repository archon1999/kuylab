"""Musical regressions: pitches, real releases, pulse alignment and teaching copy."""
import hashlib
from django.test import SimpleTestCase
from apps.scores.midi import parse_midi
from apps.studio.content import exercise_items, theory_items, THEORY, localize
from apps.studio.midi_authoring import exercise_notes, theory_midi
from apps.studio.comparisons import comparison_midi
from apps.studio.interactive import challenges


class PracticalCurriculumTests(SimpleTestCase):
    def exercise(self, family, level):
        data, _ = exercise_notes(family, level)
        return parse_midi(data)

    def theory(self, topic):
        return parse_midi(theory_midi(topic))

    def hand(self, parsed, hand):
        return [event for event in parsed["events"] if event["hand"] == hand]

    def pitches(self, events):
        return [event["pitch"]["midi"] for event in events]

    def at(self, parsed, quarter, hand="right"):
        return [event for event in self.hand(parsed, hand) if abs(event["onset_quarters"]-quarter) < 1e-6]

    def test_existing_study_ids_remain_stable_and_independent(self):
        exercises, theory = exercise_items(), theory_items()
        self.assertEqual((len(exercises), len(theory)), (48, 24))
        old_families = {"five-finger", "scales", "arpeggios", "chords", "coordination", "rhythm", "leaps", "octaves", "articulation", "balance", "pedal", "continuity"}
        self.assertTrue({f"exercise:{family}:{level}" for family in old_families for level in ["easy", "intermediate", "advanced"]} <= {item["id"] for item in exercises})
        known_ids = {item["id"] for item in exercises+theory}
        for item in exercises+theory:
            self.assertNotIn("composition_id", item)
            self.assertTrue(set(item["related_ids"]) <= known_ids, item["id"])
            self.assertNotIn(item["id"], item["related_ids"])

    def test_all_material_has_source_specific_multilingual_coaching(self):
        items = exercise_items()+theory_items()
        for item in items:
            with self.subTest(item=item["id"]):
                self.assertEqual(len(item["explanation"]), 5)
                self.assertEqual(len(item["steps"]), 3)
                self.assertTrue(item["related_ids"])
                self.assertTrue(4 <= item["minutes"] <= 10)
                for language in ["uz", "ru", "en"]:
                    value = localize(item, language)
                    self.assertGreater(len(value["ready_when"]), 60)
                    self.assertTrue(all(len(part["text"]) > 50 for part in value["explanation"]))
                    self.assertGreater(sum(len(part["text"]) for part in value["explanation"]), 500)
        # Every level explains its own actual example, rather than copying a family paragraph.
        self.assertEqual(len({item["explanation"][1]["text"]["en"] for item in exercise_items()}), 48)
        self.assertEqual(len({item["explanation"][1]["text"]["en"] for item in theory_items()}), 24)

    def test_c_major_scales_are_diatonic_and_return_to_tonic(self):
        for level in range(3):
            parsed = self.exercise("scales", level)
            self.assertEqual({event["pitch"]["midi"] % 12 for event in parsed["events"]}, {0,2,4,5,7,9,11})
            rh = self.hand(parsed, "right")
            self.assertEqual(self.pitches(rh)[0], 60)
            self.assertEqual(self.pitches(rh)[-1], 60)
            self.assertEqual(max(self.pitches(rh)), 72 if level == 0 else 84)
        contrary = self.exercise("scales", 2)
        self.assertEqual(self.pitches(self.hand(contrary, "left"))[:15], [48,47,45,43,41,40,38,36,35,33,31,29,28,26,24])
        self.assertLess(max(self.pitches(self.hand(contrary,"left"))), min(self.pitches(self.hand(contrary,"right"))))

    def test_scale_subdivisions_and_phrase_end_hold_are_explicit(self):
        for level, count, cycle in [(0,15,8), (1,29,16), (2,29,16)]:
            rh = self.hand(self.exercise("scales", level), "right")
            self.assertEqual([e["onset_quarters"] for e in rh[:count]], [i*.5 for i in range(count)])
            self.assertGreater(rh[count-1]["duration_quarters"], .5)
            self.assertEqual(rh[count]["onset_quarters"], cycle)

    def test_arpeggios_end_each_cycle_on_the_starting_root(self):
        for level, count, cycle, peak in [(0,5,4,67), (1,7,4,72), (2,13,8,84)]:
            rh = self.hand(self.exercise("arpeggios",level), "right")
            self.assertEqual(self.pitches(rh[:count])[0], 60)
            self.assertEqual(self.pitches(rh[:count])[-1], 60)
            self.assertEqual(max(self.pitches(rh)), peak)
            self.assertEqual(rh[count]["onset_quarters"], cycle)
            self.assertEqual({p % 12 for p in self.pitches(rh)}, {0,4,7})

    def test_easy_chords_do_not_change_the_bass_harmony(self):
        parsed = self.exercise("chords",0)
        self.assertEqual(set(self.pitches(self.hand(parsed,"left"))), {48})
        for at in [0,4,8,12,16,20,24,28]:
            self.assertEqual(sorted(self.pitches(self.at(parsed,at))), [60,64,67])

    def test_advanced_chords_have_the_named_sevenths(self):
        parsed = self.exercise("chords",2)
        for at, pitches, bass in [(0,[60,64,67,71],48), (4,[60,64,65,69],41), (8,[59,62,65,67],43), (12,[60,64,67,71],48)]:
            self.assertEqual(sorted(self.pitches(self.at(parsed,at))), pitches)
            self.assertEqual(self.pitches(self.at(parsed,at,"left")), [bass])

    def test_three_against_two_has_no_phase_reset_at_block_boundaries(self):
        parsed = self.exercise("coordination",2)
        rh = [e["onset_quarters"] for e in self.hand(parsed,"right")]
        lh = [e["onset_quarters"] for e in self.hand(parsed,"left")]
        self.assertEqual(rh, [i*.5 for i in range(96)])
        self.assertEqual(lh, [i*.75 for i in range(64)])
        self.assertEqual(sorted(set(rh) & set(lh)), [i*1.5 for i in range(32)])
        self.assertAlmostEqual(parsed["metadata"]["duration_seconds"], 48*60/96, places=4)

    def test_pedal_clears_on_the_next_chord_and_finishes_released(self):
        for level in range(3):
            parsed = self.exercise("pedal",level)
            changes = [e for e in parsed["pedal_events"] if e["channel"] == 1]
            off = [e["onset_quarters"] for e in changes if not e["down"]]
            on = [e["onset_quarters"] for e in changes if e["down"]]
            self.assertIn(4, off)
            self.assertNotIn(3.85, off)
            self.assertTrue(any(abs(at-4.12) <= 1/480 for at in on))
            self.assertFalse(changes[-1]["down"])
            first = self.at(parsed,0,"left")[0]
            self.assertEqual(first["duration_quarters"], 1.2)
            self.assertEqual(first["sound_duration_quarters"], 2 if level == 2 else 4)

    def test_continuity_rest_keeps_the_other_hand_pulse(self):
        parsed = self.exercise("continuity",2)
        self.assertFalse(self.at(parsed,3))
        self.assertEqual(len(self.at(parsed,3,"left")),1)
        self.assertFalse(self.at(parsed,7))
        self.assertEqual(len(self.at(parsed,7,"left")),1)

    def test_double_notes_are_thirds_or_sixths_in_the_expected_register(self):
        for level, expected in [(0,{3,4}),(1,{8,9}),(2,{3,4})]:
            parsed = self.exercise("intervals",level)
            rh = self.hand(parsed,"right")
            for at in sorted({e["onset_quarters"] for e in rh}):
                pitches = sorted(self.pitches(self.at(parsed,at)))
                self.assertEqual(len(pitches),2)
                self.assertIn(pitches[1]-pitches[0],expected)
            self.assertEqual(bool(self.hand(parsed,"left")),level==2)

    def test_alberti_order_and_chord_changes_match_the_lesson(self):
        for level in range(3):
            parsed = self.exercise("broken-chords",level)
            self.assertEqual(self.pitches(self.hand(parsed,"left"))[:8], [48,55,52,55]*2)
            self.assertEqual(bool(self.hand(parsed,"right")), level>0)
        advanced = self.hand(self.exercise("broken-chords",2),"left")
        self.assertEqual(self.pitches(advanced)[8:16], [53,60,57,60]*2)
        self.assertEqual(self.pitches(advanced)[16:24], [55,62,59,62]*2)

    def test_syncopated_holds_cross_the_next_pulse_without_an_extra_attack(self):
        for level in [0,1]:
            parsed = self.exercise("syncopation",level)
            first = self.at(parsed,.5)[0]
            self.assertGreater(first["onset_quarters"]+first["duration_quarters"],1)
            self.assertFalse(self.at(parsed,1))
            self.assertTrue(self.at(parsed,1,"left"))
        advanced = self.exercise("syncopation",2)
        self.assertEqual([e["onset_quarters"] for e in self.hand(advanced,"right")[:3]], [.5,2,3.5])

    def test_within_hand_voicing_changes_velocity_and_then_holds(self):
        for level in range(3):
            parsed = self.exercise("voicing",level)
            for at in sorted({e["onset_quarters"] for e in self.hand(parsed,"right")}):
                chord = sorted(self.at(parsed,at),key=lambda e:e["pitch"]["midi"])
                self.assertTrue(all(e["velocity"] < chord[-1]["velocity"] for e in chord[:-1]))
                if level == 2:
                    self.assertTrue(all(e["duration_quarters"] < chord[-1]["duration_quarters"] for e in chord[:-1]))
            self.assertFalse(parsed["pedal_events"])

    def test_major_scales_preserve_whole_and_half_step_formula(self):
        events = self.theory("major-scale")["events"]
        self.assertEqual(len(events),24)
        for start in [0,8,16]:
            pitches = self.pitches(events[start:start+8])
            self.assertEqual([b-a for a,b in zip(pitches,pitches[1:])], [2,2,1,2,2,2,1])
        self.assertIn(78,self.pitches(events[8:16]))
        self.assertIn(70,self.pitches(events[16:24]))

    def test_natural_and_harmonic_minor_change_only_the_seventh(self):
        events = self.theory("minor-scales")["events"]
        natural, harmonic = events[:15], events[15:]
        self.assertEqual(len(harmonic),15)
        self.assertEqual([(a["pitch"]["midi"],b["pitch"]["midi"]) for a,b in zip(natural,harmonic) if a["pitch"] != b["pitch"]], [(79,80),(79,80)])
        self.assertEqual(self.pitches(natural)[-1],69)
        self.assertEqual(self.pitches(harmonic)[-1],69)

    def test_theory_sevenths_and_voice_leading_have_exact_chord_tones(self):
        seventh = self.theory("seventh-chords")
        for at, pitches in [(0,[60,64,67,71]),(4,[60,64,67,70]),(8,[60,63,67,70])]:
            self.assertEqual(sorted(self.pitches(self.at(seventh,at))),pitches)
        leading = self.theory("voice-leading")
        chords = [sorted(self.pitches(self.at(leading,at))) for at in [0,4,8,12]]
        self.assertEqual(chords,[[60,64,67],[60,65,69],[59,62,67],[60,64,67]])
        self.assertEqual(set(chords[0]) & set(chords[1]),{60})
        self.assertEqual(set(chords[1]) & set(chords[2]),set())
        self.assertTrue(all(abs(a-b)<=3 for left,right in zip(chords,chords[1:]) for a,b in zip(left,right)))

    def test_six_eighths_have_matched_timing_and_different_groupings(self):
        a,b = [parse_midi(comparison_midi("compound-meter",code)) for code in ["three-beats","two-beats"]]
        self.assertEqual(a["metadata"]["time"]["beats"],"3")
        self.assertEqual(b["metadata"]["time"]["beats"],"6")
        self.assertEqual((a["metadata"]["time"]["beat_type"],b["metadata"]["time"]["beat_type"]),(4,8))
        fields = lambda p:[(e["pitch"]["midi"],e["onset_seconds"],e["duration_seconds"]) for e in p["events"]]
        self.assertEqual(fields(a),fields(b))
        self.assertEqual([e["onset_quarters"] for e in a["events"] if e["velocity"]>=72],[0,1,2,3,4,5])
        self.assertEqual([e["onset_quarters"] for e in b["events"] if e["velocity"]>=72],[0,1.5,3,4.5])
        self.assertEqual(fields(self.theory("compound-meter")),fields(b))

    def test_cadence_endings_are_tonic_tonic_dominant_and_separated(self):
        parsed = self.theory("cadences")
        self.assertEqual([self.pitches(self.at(parsed,at,"left")) for at in [0,4,12,16,24,28]],[[43],[48],[41],[48],[48],[43]])
        for start,end in [(8,12),(20,24)]:
            self.assertFalse([e for e in parsed["events"] if start <= e["onset_quarters"] < end])
        self.assertEqual(sorted(self.pitches(self.at(parsed,28))),[59,62,67])

    def test_new_optional_answers_match_actual_harmony_and_meter(self):
        for topic, pitches in [("major-scale",[66]),("minor-scales",[68]),("seventh-chords",[60,64,67,70]),("voice-leading",[60])]:
            self.assertEqual(challenges(topic)[0]["answerPitches"],pitches)
        task = challenges("compound-meter")[0]
        self.assertEqual(task["answerChoice"],"0")
        self.assertEqual([n["onset"] for n in task["audio"] if n["velocity"]>=74],[0,.75,1.5,2.25])
        cadence = challenges("cadences")[0]
        self.assertEqual(cadence["answerChoice"],"1")
        self.assertEqual(sorted(n["pitch"] for n in cadence["audio"] if n["onset"]==2),[43,59,62,67])

    def test_all_new_authored_examples_are_deterministic_and_not_pedal_extended(self):
        hashes = []
        for topic,*_ in THEORY:
            first = theory_midi(topic)
            self.assertEqual(first,theory_midi(topic))
            parsed = parse_midi(first)
            self.assertTrue(parsed["events"])
            hashes.append(hashlib.sha256(first).hexdigest())
            if topic != "pedal":
                self.assertFalse(parsed["pedal_events"])
                self.assertTrue(all(e["duration_quarters"] == e["sound_duration_quarters"] for e in parsed["events"]))
        self.assertEqual(len(set(hashes)),len(THEORY))
