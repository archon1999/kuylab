import hashlib
from django.test import SimpleTestCase
from apps.studio.still_journey import journey_items
from apps.studio.midi_authoring import source_data, lesson_stage_midi, SOURCE_SHA256
from apps.scores.midi import parse_midi
from apps.studio.interactive import challenges
from apps.studio.content import THEORY, localize


class JourneyTests(SimpleTestCase):
    def test_complete_path_preserves_source_and_has_nested_reductions(self):
        original, source = source_data()
        items = journey_items()
        self.assertEqual(len(items),8)
        self.assertEqual([(item['source']['start_seconds'],item['source']['end_seconds']) for item in items[:4]],[(0,48),(48,112),(112,196),(196,source['metadata']['duration_seconds'])])
        for item in items:
            identifiers=[]
            for stage in item['stages']:
                data,ids=lesson_stage_midi(source,**stage['_generator'])
                parsed=parse_midi(data,'Test')
                expected=(item['source']['end_seconds']-item['source']['start_seconds'])*100/stage['source_speed_percent']
                self.assertAlmostEqual(parsed['metadata']['duration_seconds'],expected,places=3)
                self.assertEqual(len(parsed['events']),len(ids))
                identifiers.append(set(ids))
            self.assertTrue(identifiers[0] <= identifiers[1] <= identifiers[2])
        complete=items[-1]
        self.assertEqual(complete['stages'][-1]['_asset_key'],'composition:still:original')
        self.assertTrue(complete['stages'][-1]['_reuse_original'])
        self.assertEqual(len(identifiers[-1]),1092)
        self.assertEqual(hashlib.sha256(original).hexdigest(),SOURCE_SHA256)

    def test_interactive_activities_cover_topics_and_have_valid_localized_answers(self):
        total=0
        for topic,*_ in THEORY:
            tasks=challenges(topic)
            self.assertTrue(tasks,topic)
            total+=len(tasks)
            for task in tasks:
                for language in ['uz','ru','en']:
                    value=localize(task,language)
                    self.assertIsInstance(value['prompt'],str)
                    self.assertIsInstance(value['explanation'],str)
                    self.assertGreater(len(value['preparation']),80)
                    if task['mode']=='choice': self.assertIn(task['answerChoice'],[choice['id'] for choice in value['choices']])
                    else: self.assertTrue(all(60<=pitch<=84 for pitch in task['answerPitches']))
                for note in task['audio']:
                    self.assertTrue(21<=note['pitch']<=108 and 0<note['velocity']<=127 and note['duration']>0 and note['onset']>=0)
        self.assertEqual(total,49)
