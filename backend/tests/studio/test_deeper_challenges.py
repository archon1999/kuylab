from django.test import SimpleTestCase
from apps.studio.content import THEORY, localize
from apps.studio.interactive import challenges


class DeeperChallengeTests(SimpleTestCase):
    def test_every_topic_keeps_its_foundation_and_gains_one_prepared_application(self):
        total = 0
        for topic, *_ in THEORY:
            tasks = challenges(topic)
            self.assertGreaterEqual(len(tasks), 2)
            self.assertNotEqual(tasks[0].get("difficulty"), "deeper")
            self.assertEqual(sum(task.get("difficulty") == "deeper" for task in tasks), 1)
            self.assertEqual(len({task["id"] for task in tasks}), len(tasks))
            for language in ["uz", "ru", "en"]:
                task = localize(tasks[-1], language)
                self.assertGreater(len(task["preparation"]), 100)
                self.assertGreater(len(task["explanation"]), 100)
                self.assertGreater(len(task["prompt"]), 30)
            total += len(tasks)
        self.assertEqual(total, 49)

    def test_transferred_keyboard_answers_match_the_taught_musical_relationships(self):
        expected = {"keyboard": [71], "intervals": [62,66], "major-minor": [60,63,67], "triads": [62,66,69], "arpeggio": [62,65,69], "major-scale": [70], "minor-scales": [67,68], "seventh-chords": [60,63,67,70], "voice-leading": [64,67]}
        for topic, pitches in expected.items():
            self.assertEqual(challenges(topic)[-1]["answerPitches"], pitches, topic)
        self.assertEqual(66-62, 4)
        self.assertEqual([66-62,69-66], [4,3])

    def test_listening_comparisons_have_the_claimed_timing_and_harmonic_content(self):
        pulse = challenges("pulse")[-1]["audio"]
        self.assertEqual([round(n["onset"], 2) for n in pulse if n["pitch"] == 48], [0,.6,1.2,1.8,3,3.6,4.2,4.8])
        durations = challenges("durations")[-1]["audio"]
        self.assertEqual(sum(n["duration"] for n in durations), 1)
        self.assertEqual([n["onset"] for n in challenges("rests")[-1]["audio"]], [0,.5,1.5])
        dynamics = challenges("dynamics")[-1]["audio"]
        self.assertEqual({n["velocity"] for n in dynamics}, {76})
        self.assertEqual([round(b["onset"]-a["onset"],2) for a,b in zip(dynamics,dynamics[1:])], [.8,.6,.4])
        cadence = challenges("cadences")[-1]["audio"]
        self.assertEqual({n["pitch"] % 12 for n in cadence if n["onset"] == 0}, {7,11,2,5})
        self.assertEqual({n["pitch"] % 12 for n in cadence if n["onset"] == 2}, {0,4,7})
        self.assertEqual(challenges("compound-meter")[-1]["answerChoice"], "1")
