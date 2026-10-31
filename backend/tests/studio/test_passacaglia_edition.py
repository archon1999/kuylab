from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from django.test import SimpleTestCase

from apps.studio.composition_showcase import presentation
from apps.studio.ivory_repertoire import ROOT, performance_source, performance_provenance
from apps.studio.passacaglia_edition import notation_source, rendered_midi
from apps.studio.performance_courses import performance_items
from apps.studio.midi_authoring import lesson_stage_midi
from apps.scores.midi import parse_midi


class PassacagliaEditionTests(SimpleTestCase):
    def test_every_written_note_has_its_staff_hand_even_above_middle_c(self):
        raw, notation = notation_source()
        data, midi = performance_source('passacaglia')
        self.assertEqual(data, rendered_midi())
        self.assertEqual(len(midi['events']), 1030)
        self.assertEqual(Counter(e['hand'] for e in midi['events']), {'left':544, 'right':486})
        self.assertFalse(midi['warnings'])
        self.assertFalse(midi['pedal_events'])
        scale = 60 / midi['metadata']['tempo']['quarter_bpm']
        expected = sorted((int(e['pitch']['midi']), e['hand'], e['onset_quarters']*scale,
                           e['duration_quarters']*scale)
                          for e in notation['events'] if e['pitch'] and not e['rest'])
        actual = sorted((e['pitch']['midi'], e['hand'], e['onset_seconds'], e['duration_seconds'])
                        for e in midi['events'])
        for before, after in zip(expected, actual):
            self.assertEqual(before[:2], after[:2])
            self.assertAlmostEqual(before[2], after[2], places=6)
            self.assertAlmostEqual(before[3], after[3], places=6)
        # The opening A4 belongs to the left staff, despite lying above C4.
        opening_a4 = next(e for e in midi['events'] if e['pitch']['midi'] == 69)
        self.assertEqual(opening_a4['hand'], 'left')
        provenance = performance_provenance('passacaglia')
        self.assertEqual(provenance['kind'], 'notation_rendered_midi')
        self.assertEqual(provenance['source_sha256'], sha256(raw).hexdigest())
        self.assertIn('CC0', provenance['permission_basis'])
        self.assertFalse(provenance['preserved_original_bytes'])
        self.assertTrue((ROOT / 'originals' / 'passacaglia.mid').exists())

    def test_lesson_ids_remain_stable_and_finals_use_every_new_source_note(self):
        _, source = performance_source('passacaglia')
        items = [i for i in performance_items() if i['_composition'] == 'passacaglia']
        self.assertEqual({i['id'] for i in items}, {
            'lesson:passacaglia:upper-repeated-c', 'lesson:passacaglia:a-broken-support',
            'lesson:passacaglia:repeats-over-moving-bass', 'journey:passacaglia:performance-complete'})
        for item in items:
            self.assertEqual(item['source']['playback_revision'], sha256(rendered_midi()).hexdigest()[:16])
            if item['kind'] == 'journey':
                self.assertEqual(item['source']['end_seconds'], source['metadata']['duration_seconds'])
                continue
            self.assertEqual([s['source_speed_percent'] for s in item['stages']], [60,80,60,80,100])
            spec = item['stages'][-1]['_generator']
            data, ids = lesson_stage_midi(source, **spec)
            expected = [e for e in source['events'] if spec['start'] <= e['onset_seconds'] < spec['end']]
            self.assertEqual(set(ids), {e['id'] for e in expected})
            self.assertEqual(Counter(e['hand'] for e in parse_midi(data)['events']), Counter(e['hand'] for e in expected))


class LearnerCalibratedDifficultyTests(SimpleTestCase):
    def test_every_active_edition_has_a_rating_review_bound_to_its_current_bytes(self):
        from apps.studio.repertoire import SOURCES
        from apps.studio.performance_variants import variant_definitions
        from apps.studio.ivory_repertoire import GROUP_BY_CODE, variant_entry
        from apps.studio.all_in_package import HASHES
        receipt = json.loads((Path(__file__).parents[2] / 'apps/studio/difficulty_review.json').read_text(encoding='utf-8'))
        rows = {(r['code'], r['variant']): r for r in receipt['editions']}
        expected = set()
        for source in SOURCES:
            values = variant_definitions(source.code)
            for variant in [v['id'] for v in values] if values else [None]:
                key = (source.code, variant)
                expected.add(key)
                group = GROUP_BY_CODE.get(source.code)
                if group and variant and variant != (group.get('base_variant') or {}).get('id'):
                    digest = variant_entry(source.code, variant)['sha256']
                elif source.code == 'all-in' and variant == 'easy':
                    digest = HASHES['All_In_Plus5_Easy_LH.mid']
                else:
                    digest = source.sha256
                self.assertEqual(rows[key]['source_sha256'], digest, key)
                self.assertEqual(rows[key]['rating'], presentation(*key)['difficulty'], key)
                self.assertTrue(rows[key]['review_note'])
        self.assertEqual(set(rows), expected)
        self.assertEqual(len(rows), len(receipt['editions']))

    def test_requested_current_arrangements_and_their_explicit_easier_variant(self):
        for code, rating in {'naruto-hyouhaku-kokuten':5, 'youth':3, 'premonition':3,
                             'all-in':4, 'ode-to-joy':5, 'my-heart-will-go-on':4, 'passacaglia':4}.items():
            self.assertEqual(presentation(code)['difficulty'], rating, code)
        self.assertEqual(presentation('youth', 'fabrizio-caligaris')['difficulty'],3)
        self.assertEqual(presentation('all-in','easy')['difficulty'],3)
        self.assertEqual(presentation('all-in','hard')['difficulty'],4)
