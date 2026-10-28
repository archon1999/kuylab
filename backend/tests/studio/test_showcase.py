import io
import tempfile
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient
from tests.support import LearnerClient
from apps.scores.models import Score
from apps.studio.models import StudioAsset
from apps.studio.composition_showcase import excerpt_notes


class ExcerptBoundaryTests(SimpleTestCase):
    def test_sustain_can_outlast_the_key_block_but_not_the_preview_boundary(self):
        events = [dict(id='held',onset_seconds=0,duration_seconds=4,sound_duration_seconds=8,
                       pitch={'midi':60},hand='right',velocity=73)]
        note = excerpt_notes(events,3,3)[0]
        self.assertEqual((note['onset'],note['duration'],note['soundDuration']), (0,1,3))

    def test_held_notes_and_both_hands_survive_without_inventing_or_sampling_attacks(self):
        def note(id, onset, duration, hand='right', **other):
            return dict(id=id, onset_seconds=onset, duration_seconds=duration,
                        pitch={'midi':60}, hand=hand, velocity=73, **other)
        events = [note('held',-2,6,'left'),note('inside',2,4),
                  note('before',-2,2),note('after',4,2),
                  note('drums',0,1,percussion=True),note('rest',0,1,rest=True)]
        notes = excerpt_notes(events,0,4)
        self.assertEqual([note['id'] for note in notes],['held','inside'])
        self.assertEqual([(note['onset'],note['duration']) for note in notes],[(0,4),(2,2)])
        self.assertEqual({note['hand'] for note in notes},{'left','right'})
        self.assertEqual({note['velocity'] for note in notes},{73})
        self.assertEqual(events[0]['onset_seconds'],-2)


class CompositionShowcaseTests(TestCase):
    client_class = LearnerClient

    @classmethod
    def setUpClass(cls):
        cls.media = tempfile.TemporaryDirectory()
        cls.override = override_settings(MEDIA_ROOT=cls.media.name)
        cls.override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.override.disable()
        cls.media.cleanup()

    @classmethod
    def setUpTestData(cls):
        call_command('seed_studio',stdout=io.StringIO())

    def catalog(self):
        return self.client.get('/api/studio/catalog/').json()['compositions']

    def test_each_current_arrangement_has_a_reviewed_rating_and_source_landmark(self):
        pieces = self.catalog()
        self.assertEqual(len(pieces),101)
        for piece in pieces:
            self.assertIn(piece['difficulty'],range(1,6))
            self.assertGreaterEqual(piece['preview_start_seconds'],0)
            for variant in piece.get('variants',[]):
                self.assertIn(variant['difficulty'],range(1,6))
        package = next(piece for piece in pieces if piece['slug']=='all-in-soundtrack')
        self.assertEqual([(v['id'],v['difficulty']) for v in package['variants']],[('easy',2),('hard',4)])

    def test_every_preview_contains_all_overlapping_source_notes_in_both_hands(self):
        before = (StudioAsset.objects.count(),Score.objects.count())
        for piece in self.catalog():
            response = self.client.get(f"/api/studio/compositions/{piece['id']}/preview/")
            self.assertEqual(response.status_code,200)
            preview = response.json()
            self.assertEqual(preview['score_id'],piece['score_id'])
            score = Score.objects.get(pk=preview['score_id'])
            start = preview['start_seconds']
            end = start+preview['duration_seconds']
            source = {event['id']:event for event in score.parsed['events'] if event.get('pitch') and not event.get('rest') and not event.get('percussion') and event['onset_seconds']<end and event['onset_seconds']+event['duration_seconds']>start}
            self.assertEqual({note['id'] for note in preview['notes']},set(source))
            self.assertGreater(len(preview['notes']),0)
            self.assertEqual({note['hand'] for note in preview['notes']},{event['hand'] for event in source.values()},piece['slug'])
            for note in preview['notes']:
                event = source[note['id']]
                self.assertEqual(note['pitch'],event['pitch']['midi'])
                self.assertEqual(note['velocity'],event['velocity'])
                self.assertAlmostEqual(note['onset']+start,max(start,event['onset_seconds']))
                self.assertGreater(note['duration'],0)
                self.assertLessEqual(note['onset']+note['duration'],preview['duration_seconds']+1e-7)
        self.assertEqual((StudioAsset.objects.count(),Score.objects.count()),before)

    def test_variants_resolve_to_their_own_full_texture_and_unknown_ids_are_not_exposed(self):
        piece = next(piece for piece in self.catalog() if piece['slug']=='all-in-soundtrack')
        for variant in piece['variants']:
            response = self.client.get(f"/api/studio/compositions/{piece['id']}/preview/?variant={variant['id']}")
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.json()['score_id'],variant['score_id'])
            self.assertEqual(response.json()['variant_id'],variant['id'])
        self.assertEqual(self.client.get(f"/api/studio/compositions/{piece['id']}/preview/?variant=bad").status_code,404)
        self.assertEqual(self.client.get('/api/studio/compositions/9999999/preview/').status_code,404)
        self.assertEqual(APIClient().get(f"/api/studio/compositions/{piece['id']}/preview/").status_code,403)
        self.assertEqual(self.client.post(f"/api/studio/compositions/{piece['id']}/preview/",{}).status_code,405)
