from hashlib import sha256
import io
import json
from pathlib import Path
import tempfile

import mido
from django.test import SimpleTestCase

from apps.scores.midi import parse_midi
from apps.studio.ivory_import import build_catalog, transpose_performance
from apps.studio.ivory_repertoire import ROOT, performance_provenance, performance_source, variant_entry


class PerformanceTransposeTests(SimpleTestCase):
    def source(self, pitch=60, channel=0):
        midi = mido.MidiFile(ticks_per_beat=480)
        midi.tracks.append(mido.MidiTrack([
            mido.MetaMessage('set_tempo', tempo=600000),
            mido.Message('program_change', program=0),
            mido.Message('control_change', control=7, value=85),
            mido.Message('note_on', note=pitch, velocity=73, channel=channel, time=120),
            mido.Message('note_off', note=pitch, velocity=24, channel=channel, time=480),
            mido.MetaMessage('set_tempo', tempo=800000),
            mido.Message('note_on', note=64, velocity=91, channel=channel),
            mido.Message('note_on', note=64, velocity=0, channel=channel, time=240),
            mido.MetaMessage('end_of_track', time=120),
        ]))
        buffer = io.BytesIO()
        midi.save(file=buffer)
        return buffer.getvalue()

    def assert_pitch_only_shift(self, original, transposed, semitones):
        before = mido.MidiFile(file=io.BytesIO(original))
        after = mido.MidiFile(file=io.BytesIO(transposed))
        self.assertEqual((before.type, before.ticks_per_beat), (after.type, after.ticks_per_beat))
        self.assertEqual(len(before.tracks), len(after.tracks))
        for source_track, target_track in zip(before.tracks, after.tracks):
            self.assertEqual(len(source_track), len(target_track))
            for source, target in zip(source_track, target_track):
                expected = source.copy(note=source.note+semitones) if source.type in {'note_on', 'note_off'} else source
                self.assertEqual(target, expected)

    def test_note_on_off_and_zero_velocity_releases_shift_with_every_other_event_unchanged(self):
        raw = self.source()
        self.assert_pitch_only_shift(raw, transpose_performance(raw, -1), -1)
        self.assertEqual(transpose_performance(raw, 0), raw)

    def test_invalid_range_or_percussion_is_rejected_instead_of_clipped(self):
        for semitones in (True, 1.5, None, -25, 25):
            with self.assertRaises(ValueError):
                transpose_performance(self.source(), semitones)
        for raw, semitones in ((self.source(pitch=0), -1), (self.source(pitch=127), 1), (self.source(channel=9), -1)):
            with self.assertRaises(ValueError):
                transpose_performance(raw, semitones)

    def test_builder_retains_lesson_edition_and_reproduces_transposition_from_raw_source(self):
        raw = self.source()
        base = {'id': 'original', 'title': {'uz': 'Asl', 'ru': 'Оригинал', 'en': 'Original'},
                'description': {'uz': 'Darslar', 'ru': 'Уроки', 'en': 'Lessons'}}
        plan = [{'code': 'example', 'slug': 'example', 'title': 'Example', 'composer': '', 'collection': '',
                 'base_variant': base, 'variants': [{'id': 'new-performance', 'title': 'New',
                     'filename': 'example.mid', 'difficulty': 3, 'preview_start': 0,
                     'transpose_semitones': -1, 'transpose_reason': 'Explicit user request'}]}]
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory)/'source', Path(directory)/'output'
            source.mkdir()
            (source/'example.mid').write_bytes(raw)
            (source/'manifest.json').write_text(json.dumps({'items': [{
                'filename': 'example.mid', 'url': 'https://example.com/source',
                'ivory_player_url': 'https://example.com/player',
                'validation': {'sha256': sha256(raw).hexdigest(), 'note_count': 2}}]}), encoding='utf-8')
            groups = build_catalog(plan, source, output)
            self.assertEqual(groups[0]['base_variant'], base)
            self.assertFalse(groups[0]['replaces_existing'])
            self.assertEqual((output/'originals/example.mid').read_bytes(), raw)
            self.assert_pitch_only_shift(raw, (output/'example.mid').read_bytes(), -1)
            self.assertEqual(build_catalog(groups, source, Path(directory)/'rebuilt'), groups)
            plan[0]['existing_code'] = 'example'
            with self.assertRaises(ValueError):
                build_catalog(plan, source, output)
            del plan[0]['existing_code']
            del plan[0]['variants'][0]['transpose_reason']
            with self.assertRaises(ValueError):
                build_catalog(plan, source, output)

    def test_sound_of_silence_all_1282_notes_are_one_semitone_lower_with_original_rhythm(self):
        original = (ROOT/'originals/the-sound-of-silence.mid').read_bytes()
        content, parsed = performance_source('the-sound-of-silence')
        entry = variant_entry('the-sound-of-silence')
        self.assertEqual(sha256(original).hexdigest(), entry['source_sha256'])
        self.assertEqual(sha256(content).hexdigest(), '52303556647dc858d9e5ffc6ba0911fee6c83f61d88295c4bcadac868f55bfb9')
        self.assert_pitch_only_shift(original, content, -1)
        before = parse_midi(original)
        self.assertEqual((len(parsed['events']), len(before['events'])), (1282, 1282))
        self.assertEqual(parsed['metadata']['duration_seconds'], before['metadata']['duration_seconds'])
        self.assertFalse(parsed['pedal_events'])
        self.assertFalse(parsed['warnings'])
        provenance = performance_provenance('the-sound-of-silence')
        self.assertEqual(provenance['transpose_semitones'], -1)
        self.assertFalse(provenance['preserved_original_bytes'])
        self.assertTrue(provenance['retained_timing_and_velocity_preserved'])
