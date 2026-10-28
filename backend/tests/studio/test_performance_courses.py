from collections import Counter
from hashlib import sha256
import io
import json
from unittest.mock import patch

import mido
from django.test import SimpleTestCase

from apps.scores.midi import parse_midi
from apps.studio.content import all_items, localize
from apps.studio.curated_repertoire import CATALOG_ROOT, edition_source, edition_provenance
from apps.studio.ivory_import import trim_channel_outro
from apps.studio.ivory_repertoire import ROOT, performance_source, performance_provenance, variant_entry
from apps.studio.midi_authoring import lesson_stage_midi
from apps.studio.midi_quality import audit_catalog, inspect_performance, unreviewed_diagnostics
from apps.studio.performance_courses import NOTE_REVIEW, performance_items
from apps.studio.performance_course_plans import PLANS
from apps.studio.repertoire import SOURCE_BY_CODE, repertoire_source


def signatures(parsed):
    return Counter((e['track_index'], e['channel'], e.get('port', 0), e['pitch']['midi'],
                    e['velocity'], e['start_ticks'], e['end_ticks'], e['sound_end_ticks']) for e in parsed['events'])


class ReviewedCleanupTests(SimpleTestCase):
    def test_gymnopedie_only_discards_the_two_reviewed_orphan_releases(self):
        raw = (CATALOG_ROOT / 'originals/gymnopedie-no-1.mid').read_bytes()
        clean, parsed = edition_source('gymnopedie-no-1')
        self.assertEqual(len(parse_midi(raw)['warnings']), 2)
        self.assertEqual(parsed['warnings'], [])
        self.assertEqual(signatures(parse_midi(raw)), signatures(parsed))
        def messages(data):
            result = []
            for track_index, track in enumerate(mido.MidiFile(file=io.BytesIO(data)).tracks):
                tick = 0
                for message_index, message in enumerate(track):
                    tick += message.time
                    result.append((track_index, message_index, tick, str(message.copy(time=0))))
            return result
        expected = [(t, tick, message) for t, index, tick, message in messages(raw) if not (t == 1 and index in {106, 109})]
        self.assertEqual(expected, [(t, tick, message) for t, _, tick, message in messages(clean)])
        provenance = edition_provenance('gymnopedie-no-1')
        self.assertEqual(provenance['original_sha256'], sha256(raw).hexdigest())
        self.assertFalse(provenance['preserved_original_bytes'])

    def test_rondo_retains_every_musical_event_and_omits_only_the_reviewed_outro(self):
        entry = variant_entry('rondo-alla-turca')
        raw = (ROOT / 'originals' / entry['filename']).read_bytes()
        data, parsed = performance_source('rondo-alla-turca')
        rebuilt, tick, seconds = trim_channel_outro(raw, 186.5)
        self.assertEqual(data, rebuilt)
        self.assertAlmostEqual(seconds, 186.5)
        self.assertEqual(parsed['metadata']['duration_seconds'], 186.5)
        expected = parse_midi(raw)
        expected['events'] = [e for e in expected['events'] if e['start_ticks'] < tick]
        self.assertEqual(signatures(expected), signatures(parsed))
        self.assertEqual(len(parsed['events']), 2482)
        self.assertEqual(parsed['warnings'], [])
        self.assertLess(max(e['onset_seconds'] + e['duration_seconds'] for e in parsed['events']), 183)
        self.assertEqual(performance_provenance('rondo-alla-turca')['omitted_outro_note_count'], 113)

    def test_outro_boundary_uses_tempo_map_and_never_clips_a_note_or_pedal_tail(self):
        midi = mido.MidiFile(ticks_per_beat=480)
        midi.tracks.append(mido.MidiTrack([
            mido.MetaMessage('set_tempo', tempo=500000),
            mido.Message('note_on', note=60, velocity=75),
            mido.Message('note_off', note=60, time=480),
            mido.MetaMessage('set_tempo', tempo=1000000),
            mido.Message('note_on', note=64, velocity=80, time=480),
            mido.Message('control_change', control=64, value=127),
            mido.Message('note_off', note=64, time=240),
            mido.Message('control_change', control=64, value=0, time=240),
            mido.Message('note_on', note=67, velocity=90, time=480),
            mido.Message('note_off', note=67, time=480)]))
        output = io.BytesIO()
        midi.save(file=output)
        data = output.getvalue()
        trimmed, tick, seconds = trim_channel_outro(data, 3)
        self.assertEqual((tick, seconds), (1680, 3))
        self.assertEqual([e['pitch']['midi'] for e in parse_midi(trimmed)['events']], [60, 64])
        self.assertEqual(trim_channel_outro(data, None), (data, None, None))
        for boundary in [0, -1, .25, 1.7, 2.2, 4.5, float('nan'), True]:
            with self.subTest(boundary=boundary), self.assertRaises(ValueError):
                trim_channel_outro(data, boundary)
        # An attack exactly on the cut belongs to the omitted suffix.
        exact, _, _ = trim_channel_outro(data, 3.5)
        self.assertEqual(len(parse_midi(exact)['events']), 2)


class PerformanceCourseTests(SimpleTestCase):
    def test_course_coverage_localizations_and_links_are_complete(self):
        items = performance_items()
        self.assertEqual(Counter(i['kind'] for i in items), {'lesson': 33, 'journey': 11})
        self.assertEqual(len({i['_composition'] for i in items}), 11)
        self.assertTrue(all(i['id'].endswith(':performance-complete') for i in items if i['kind'] == 'journey'))
        ids = {i['id'] for i in all_items()}
        for item in items:
            self.assertTrue(all(key in ids for key in item['related_ids']))
            self.assertEqual(item['source']['playback_revision'], SOURCE_BY_CODE[item['_composition']].sha256[:16])
            for language in ('uz', 'ru', 'en'):
                public = localize(item, language)
                self.assertGreater(len(public['intro']), 30)
                self.assertTrue(public['title'])
                if item['kind'] == 'lesson':
                    self.assertEqual(len(public['explanation']), 6)
                    self.assertTrue(all(b['title'] and b['text'] for b in public['explanation']))
        interstellar = next(i for i in items if i['_composition'] == 'interstellar-main-theme')
        self.assertEqual(interstellar['source']['composition_variant_id'], 'patrik-pietschmann')

    def test_stage_reductions_are_nested_and_preserve_source_timing_pitch_and_velocity(self):
        for item in performance_items():
            _, source = repertoire_source(item['_composition'])
            lookup = {e['id']: e for e in source['events']}
            sets = []
            for stage in item['stages']:
                if stage.get('_reuse_original'):
                    self.assertEqual(stage['_asset_key'], SOURCE_BY_CODE[item['_composition']].asset_key)
                    self.assertEqual(stage['source_speed_percent'], 100)
                    continue
                spec = stage['_generator']
                data, identifiers = lesson_stage_midi(source, **spec)
                parsed = parse_midi(data)
                self.assertFalse(parsed['warnings'], stage['id'])
                self.assertFalse(parsed['pedal_events'])
                self.assertEqual(len(parsed['events']), len(identifiers))
                scale = 100 / spec['speed_percent']
                expected = sorted((lookup[key]['pitch']['midi'], lookup[key]['hand'], lookup[key]['velocity'],
                                   (lookup[key]['onset_seconds'] - spec['start']) * scale,
                                   min(lookup[key]['duration_seconds'], spec['end'] - lookup[key]['onset_seconds']) * scale) for key in identifiers)
                actual = sorted((e['pitch']['midi'], e['hand'], e['velocity'], e['onset_seconds'], e['duration_seconds']) for e in parsed['events'])
                for before, after in zip(expected, actual):
                    self.assertEqual(before[:3], after[:3], stage['id'])
                    self.assertAlmostEqual(before[3], after[3], delta=.003)
                    self.assertAlmostEqual(before[4], after[4], delta=.003)
                self.assertAlmostEqual(parsed['metadata']['duration_seconds'], (spec['end'] - spec['start']) * scale, delta=.003)
                sets.append(set(identifiers))
            if item['kind'] == 'lesson':
                self.assertEqual([s['source_speed_percent'] for s in item['stages']], [60, 80, 60, 80, 100])
                self.assertLess(sets[0], sets[1], item['id'])
                self.assertTrue(sets[1] <= sets[2], item['id'])
                self.assertEqual(sets[2], sets[3])
                self.assertEqual(sets[3], sets[4])
                complete = {e['id'] for e in source['events'] if item['source']['start_seconds'] <= e['onset_seconds'] < item['source']['end_seconds']}
                self.assertEqual(sets[-1], complete)
            else:
                self.assertEqual([s['source_speed_percent'] for s in item['stages']], [60, 80, 100])
                self.assertEqual(sets[0], set(lookup))
                self.assertEqual(sets[1], set(lookup))
            repertoire_source.cache_clear()

    def test_a_changed_recording_requires_review_before_course_generation(self):
        import copy
        modified = copy.deepcopy(NOTE_REVIEW)
        modified['time']['source_sha256'] = '0' * 64
        performance_items.cache_clear()
        try:
            with patch('apps.studio.performance_courses.NOTE_REVIEW', modified), self.assertRaisesRegex(ValueError, 'review the course'):
                performance_items()
        finally:
            performance_items.cache_clear()

    def test_blue_bell_foundation_retains_joint_eg_then_the_restored_b(self):
        item = next(i for i in performance_items() if i['id'] == 'lesson:shiki-blue-bell:e-g-then-b')
        _, source = repertoire_source('shiki-blue-bell')
        data, _ = lesson_stage_midi(source, **item['stages'][0]['_generator'])
        events = parse_midi(data)['events']
        e, g, b = [next(e for e in events if e['pitch']['midi'] == pitch) for pitch in (76, 79, 83)]
        self.assertLess(abs(e['onset_seconds'] - g['onset_seconds']), .02)
        self.assertGreater(b['onset_seconds'], g['onset_seconds'] + 1)


class MidiQualityTests(SimpleTestCase):
    def test_all_performances_pass_without_erasing_legitimate_holds_or_voices(self):
        rows = audit_catalog()
        self.assertEqual(len(rows), 120)
        self.assertEqual(sum(r['notes'] for r in rows), 156382)
        self.assertFalse(any(r['issues'] for r in rows))
        self.assertTrue(any(r['holds_at_least_eight_seconds'] for r in rows))
        self.assertTrue(any(r['duplicate_attacks'] for r in rows))

    def test_review_receipts_cannot_silence_new_bytes_or_new_diagnostics(self):
        row = dict(code='example', variant='original', sha256='a', duplicate_attacks=1, same_voice_overlaps=1)
        reviews = [{**row, 'review_reason': 'Reviewed source voices'}]
        self.assertFalse(unreviewed_diagnostics(row, reviews))
        self.assertTrue(unreviewed_diagnostics({**row, 'sha256': 'b'}, reviews))
        self.assertTrue(unreviewed_diagnostics({**row, 'duplicate_attacks': 2}, reviews))

    def test_invalid_timeline_outside_keyboard_and_unknown_roles_are_reported(self):
        import copy
        data, original = repertoire_source('time')
        parsed = copy.deepcopy(original)
        parsed['events'][0].update(hand='unknown', duration_seconds=float('nan'))
        parsed['events'][0]['pitch']['midi'] = 120
        row = inspect_performance('time', 'original', data, parsed)
        self.assertTrue(any('timeline' in issue for issue in row['issues']))
        self.assertTrue(any('88-key' in issue for issue in row['issues']))
        self.assertTrue(any('layer' in issue for issue in row['issues']))
