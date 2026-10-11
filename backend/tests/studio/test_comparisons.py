from django.test import SimpleTestCase
from apps.scores.midi import parse_midi
from apps.studio.comparisons import comparison_midi, definitions
from apps.studio.still_lessons import lesson_items


class ComparisonTests(SimpleTestCase):
    def events(self, topic, code):
        return parse_midi(comparison_midi(topic,code),topic)['events']

    def identity(self, events):
        return [(e['pitch']['midi'],e['onset_seconds']) for e in events]

    def test_ab_examples_keep_pitch_and_attacks_constant(self):
        for topic,a,b in [('meter','even','accent'),('legato','detached','connected'),('dynamics','flat','shaped')]:
            left,right=self.events(topic,a),self.events(topic,b)
            self.assertEqual(self.identity(left),self.identity(right))
            if topic == 'legato':
                self.assertEqual([e['velocity'] for e in left],[e['velocity'] for e in right])
                self.assertTrue(all(a['duration_seconds'] < b['duration_seconds'] for a,b in zip(left,right)))
            else:
                self.assertEqual([e['duration_seconds'] for e in left],[e['duration_seconds'] for e in right])
                self.assertNotEqual([e['velocity'] for e in left],[e['velocity'] for e in right])

    def test_separated_layers_use_the_correct_hand(self):
        self.assertEqual({e['hand'] for e in self.events('voicing','melody')},{'right'})
        self.assertEqual({e['hand'] for e in self.events('voicing','accompaniment')},{'left'})

    def test_all_lessons_have_specific_multilingual_coaching_and_outcomes(self):
        lessons=lesson_items()
        self.assertEqual(len(lessons),12)
        for lesson in lessons:
            self.assertEqual(len(lesson['stages']),3)
            movement=lesson['explanation'][-1]['text']
            for language in ['uz','ru','en']:
                self.assertGreater(len(movement[language]),90)
                self.assertTrue(lesson['ready_when'][language])
        self.assertEqual(len({lesson['explanation'][-1]['text']['en'] for lesson in lessons}),12)

    def test_comparison_copy_is_complete_in_three_languages(self):
        for topic in ['voicing','meter','legato','dynamics']:
            self.assertEqual(len(definitions(topic)),2)
            for example in definitions(topic):
                for field in ['title','instruction']:
                    self.assertEqual(set(example[field]),{'uz','ru','en'})
