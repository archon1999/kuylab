import hashlib
import io
import json
from pathlib import Path
import tempfile

import mido
from django.core.management import call_command
from django.core.files.base import ContentFile
from django.db.models import Max
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone

from apps.activity.models import PersonalLibrary, PracticeNote
from apps.learning.models import Composition, Profile
from apps.scores.midi import parse_midi
from apps.scores.models import Score
from apps.studio.content import all_items
from apps.studio.ivory_import import trim_channel_intro
from apps.studio.ivory_repertoire import GROUPS, GROUP_BY_CODE, ROOT, performance_source, performance_provenance
from apps.studio.models import StudioAsset
from apps.studio.repertoire import SOURCES, SOURCE_BY_CODE
from apps.studio.services import studio_catalog


class IntroCutTests(SimpleTestCase):
    def source(self):
        midi = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        midi.tracks.append(track)
        track.extend([
            mido.MetaMessage('set_tempo',tempo=500000),
            mido.Message('program_change',program=0),
            mido.Message('note_on',note=84,velocity=70),
            mido.Message('note_off',note=84,time=480),
            mido.MetaMessage('set_tempo',tempo=1000000),
            mido.Message('note_on',note=60,velocity=88,time=480),
            mido.Message('note_off',note=60,time=240),
            mido.Message('note_on',note=64,velocity=91,time=240),
            mido.Message('note_off',note=64,time=480),
            mido.MetaMessage('end_of_track')])
        output = io.BytesIO()
        midi.save(file=output)
        return output.getvalue()

    def test_reviewed_intro_cut_preserves_later_tempo_attacks_holds_and_velocity(self):
        data = self.source()
        trimmed, tick, seconds = trim_channel_intro(data,1.5)
        self.assertEqual((tick,seconds),(960,1.5))
        parsed = parse_midi(trimmed)
        self.assertEqual([e['pitch']['midi'] for e in parsed['events']],[60,64])
        self.assertEqual([e['velocity'] for e in parsed['events']],[88,91])
        self.assertEqual([e['onset_seconds'] for e in parsed['events']],[0,1])
        self.assertEqual([e['duration_seconds'] for e in parsed['events']],[.5,1])
        self.assertEqual(parsed['tempo_map'][0]['quarter_bpm'],60)

    def test_a_note_crossing_intro_boundary_is_not_retriggered(self):
        trimmed,_,_ = trim_channel_intro(self.source(),.25)
        parsed = parse_midi(trimmed)
        self.assertEqual([e['pitch']['midi'] for e in parsed['events']],[60,64])
        self.assertAlmostEqual(parsed['events'][0]['onset_seconds'],1.25)
        self.assertEqual(parsed['warnings'],[])

    def test_no_cut_keeps_every_original_byte_and_out_of_range_is_rejected(self):
        data = self.source()
        self.assertEqual(trim_channel_intro(data,0),(data,0,0.0))
        with self.assertRaises(ValueError):
            trim_channel_intro(data,100)

    def test_shared_channel_state_uses_last_global_update_not_track_order(self):
        midi = mido.MidiFile(ticks_per_beat=480)
        midi.tracks.append(mido.MidiTrack([
            mido.Message('program_change',program=5,time=960),
            mido.Message('control_change',control=7,value=65),
            mido.Message('pitchwheel',pitch=100),mido.MetaMessage('end_of_track',time=960)]))
        midi.tracks.append(mido.MidiTrack([
            mido.Message('program_change',program=10),
            mido.Message('control_change',control=7,value=25),
            mido.Message('pitchwheel',pitch=-100),
            mido.Message('note_on',note=60,velocity=80,time=1440),
            mido.Message('note_off',note=60,time=480),mido.MetaMessage('end_of_track')]))
        output = io.BytesIO()
        midi.save(file=output)
        trimmed,_,_ = trim_channel_intro(output.getvalue(),1.25)
        current = mido.MidiFile(file=io.BytesIO(trimmed))
        state = {}
        for message in mido.merge_tracks(current.tracks):
            if message.type=='program_change': state['program']=message.program
            if message.type=='control_change' and message.control==7: state['volume']=message.value
            if message.type=='pitchwheel': state['bend']=message.pitch
            if message.type=='note_on' and message.velocity:
                self.assertEqual(state,{'program':5,'volume':65,'bend':100})


class IvorySourceTests(SimpleTestCase):
    def test_playback_revision_follows_each_import_and_leaves_legacy_sources_unchanged(self):
        from apps.studio.composition_showcase import presentation

        for group in GROUPS:
            if group.get('base_variant'):
                self.assertNotIn('playback_revision',presentation(group['code']))
                self.assertNotIn('playback_revision',presentation(group['code'],group['base_variant']['id']))
            else:
                self.assertEqual(presentation(group['code'])['playback_revision'],group['variants'][0]['sha256'][:16])
            for variant in group['variants']:
                self.assertEqual(presentation(group['code'],variant['id'])['playback_revision'],variant['sha256'][:16])
        self.assertNotIn('playback_revision',presentation('all-in','easy'))
        self.assertNotIn('playback_revision',presentation('still'))

    def test_all_87_performances_are_grouped_pinned_and_playable(self):
        variants = [(group,variant) for group in GROUPS for variant in group['variants']]
        self.assertEqual(len(GROUPS),72)
        self.assertEqual(len(variants),87)
        self.assertEqual(len({variant['filename'] for _,variant in variants}),87)
        self.assertEqual(len({source.slug for source in SOURCES}),103)
        for group,variant in variants:
            content,parsed = performance_source(group['code'],variant['id'])
            self.assertEqual(hashlib.sha256(content).hexdigest(),variant['sha256'])
            self.assertTrue(parsed['events'])
            self.assertFalse(parsed['pedal_events'])
            self.assertTrue(all(e['hand'] in {'left','right'} for e in parsed['events']))
            self.assertIn(variant['difficulty'],range(1,6))
            self.assertLess(variant['preview_start'],parsed['metadata']['duration_seconds'])

    def test_nine_reviewed_jingles_are_removed_without_changing_retained_notes(self):
        trimmed = [(group,variant) for group in GROUPS for variant in group['variants'] if variant['trim_start_seconds']]
        self.assertEqual(len(trimmed),9)
        for group,variant in trimmed:
            raw = (ROOT/'originals'/variant['filename']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),variant['source_sha256'])
            original = parse_midi(raw)
            _,current = performance_source(group['code'],variant['id'])
            expected = sorted((e['track_index'],e['pitch']['midi'],e['velocity'],e['onset_seconds']-variant['trim_start_seconds'],e['duration_seconds'])
                              for e in original['events'] if e['start_ticks']>=variant['trim_start_ticks'])
            actual = sorted((e['track_index'],e['pitch']['midi'],e['velocity'],e['onset_seconds'],e['duration_seconds']) for e in current['events'])
            self.assertEqual(len(expected),len(actual))
            for before,after in zip(expected,actual):
                self.assertEqual(before[:3],after[:3])
                self.assertAlmostEqual(before[3],after[3],places=5)
                self.assertAlmostEqual(before[4],after[4],places=5)
            provenance = performance_provenance(group['code'],variant['id'])
            self.assertFalse(provenance['preserved_original_bytes'])
            self.assertTrue(provenance['trim_reason'])

    def test_six_replacements_keep_composition_identity_and_do_not_reuse_old_midi_lessons(self):
        codes = {'ode-to-joy','moonlight-sonata','rondo-alla-turca','time','hes-a-pirate','my-heart-will-go-on'}
        self.assertEqual({group['code'] for group in GROUPS if group['replaces_existing']},codes)
        for code in codes:
            self.assertEqual(SOURCE_BY_CODE[code].course_kind,'ivory')
            self.assertEqual(SOURCE_BY_CODE[code].slug,GROUP_BY_CODE[code]['slug'])
        self.assertFalse(any(item.get('_composition') in codes for item in all_items()))


class IvorySeedTests(TestCase):
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
        Profile.objects.create(display_name='Kept learner')
        call_command('seed_studio',stdout=io.StringIO())

    def test_variants_are_distinct_arrangements_of_one_composition_and_localized(self):
        catalogs = {lang:studio_catalog(lang) for lang in ('uz','ru','en')}
        self.assertEqual(len(catalogs['uz']['compositions']),103)
        for group in GROUPS:
            piece = next(p for p in catalogs['uz']['compositions'] if p['slug']==group['slug'])
            base = group.get('base_variant')
            if base:
                self.assertEqual(len(piece['lesson_ids']),6)
                self.assertNotIn('playback_revision',piece)
            else:
                self.assertEqual(piece['lesson_ids'],[])
                self.assertEqual(piece['playback_revision'],group['variants'][0]['sha256'][:16])
            variants = piece.get('variants',[])
            self.assertEqual(len(variants),len(group['variants']) + bool(base) if base or len(group['variants'])>1 else 0)
            if variants:
                self.assertEqual(piece['default_variant_id'],base['id'] if base else group['variants'][0]['id'])
                arrangements = Score.objects.filter(pk__in=[v['score_id'] for v in variants]).values_list('arrangement_id',flat=True)
                self.assertEqual(len(set(arrangements)),len(variants))
                self.assertEqual({v['id'] for v in variants},{v['id'] for v in group['variants']} | ({base['id']} if base else set()))
                expected = {v['id']:v['sha256'][:16] for v in group['variants']}
                self.assertEqual({v['id']:v['playback_revision'] for v in variants if 'playback_revision' in v},expected)
        self.assertEqual(Profile.objects.get().display_name,'Kept learner')

    def test_second_seed_changes_neither_scores_nor_composition_ids(self):
        source = SOURCE_BY_CODE['youth']
        original = StudioAsset.objects.select_related('score__arrangement').get(pk=source.asset_key)
        composition_id = original.score.arrangement.composition_id
        lesson_id = next(item['id'] for item in all_items() if item['kind']=='lesson' and item.get('_composition')=='youth')
        library = PersonalLibrary.objects.create(profile=Profile.objects.get(),
            favorites=[f'composition:{composition_id}',lesson_id],progress={lesson_id:'mastered'},
            positions={f'composition:{composition_id}':42.5})
        note = PracticeNote.objects.create(profile=library.profile,content_id=f'composition:{composition_id}',
            position_seconds=42.5,text='Keep my original course timestamp')
        before = list(Composition.objects.values_list('seed_key','id'))
        assets = list(StudioAsset.objects.order_by('key').values_list('key','score_id'))
        scores = Score.objects.count()
        call_command('seed_studio',stdout=io.StringIO())
        self.assertEqual(list(Composition.objects.values_list('seed_key','id')),before)
        self.assertEqual(list(StudioAsset.objects.order_by('key').values_list('key','score_id')),assets)
        self.assertEqual(Score.objects.count(),scores)
        original.refresh_from_db()
        self.assertEqual(original.score.content_sha256,source.sha256)
        self.assertEqual(original.score.arrangement.composition_id,composition_id)
        library.refresh_from_db()
        self.assertEqual(library.positions,{f'composition:{composition_id}':42.5})
        self.assertEqual(library.favorites,[f'composition:{composition_id}',lesson_id])
        self.assertEqual(library.progress,{lesson_id:'mastered'})
        note.refresh_from_db()
        self.assertEqual((note.position_seconds,note.text),(42.5,'Keep my original course timestamp'))

    def test_added_recording_preserves_the_youth_course_source_and_preview(self):
        from apps.studio.composition_showcase import composition_preview
        from apps.studio.repertoire import repertoire_source

        catalog = studio_catalog('en')
        piece = next(p for p in catalog['compositions'] if p['slug']=='what-is-a-youth')
        self.assertEqual(piece['default_variant_id'],'original')
        raw, parsed = repertoire_source('youth')
        self.assertEqual(hashlib.sha256(raw).hexdigest(),SOURCE_BY_CODE['youth'].sha256)
        self.assertEqual({event['pitch']['midi'] for event in parsed['events'] if event['onset_seconds']==0},{71,83})
        self.assertEqual(len(piece['lesson_ids']),6)
        base, added = piece['variants']
        self.assertEqual((base['id'],added['id']),('original','fabrizio-caligaris'))
        self.assertEqual(composition_preview(piece['id'])['score_id'],base['score_id'])
        self.assertEqual(composition_preview(piece['id'],'original')['score_id'],base['score_id'])
        self.assertEqual(composition_preview(piece['id'],added['id'])['score_id'],added['score_id'])
        stages = [stage for item in all_items() if item['kind']=='lesson' and item.get('_composition')=='youth' for stage in item['stages']]
        for stage in stages:
            score = StudioAsset.objects.get(pk=stage['_asset_key']).score
            self.assertEqual(score.source_provenance['source_sha256'],SOURCE_BY_CODE['youth'].sha256)
        added_score = Score.objects.get(pk=added['score_id'])
        self.assertEqual(added_score.source_provenance['kind'],'owner_supplied_ivory_performance')
        self.assertEqual(added_score.original_filename,'romeo-juliet-a-time-for-us-fabrizio-caligaris.mid')

    def test_replacement_retires_old_active_midi_but_preserves_learner_and_source_history(self):
        from apps.studio.curated_repertoire import edition_source

        asset = StudioAsset.objects.select_related('score').get(pk='composition:ode-to-joy:original')
        composition_id = asset.score.arrangement.composition_id
        old_bytes,old_parsed = edition_source('ode-to-joy')
        legacy = Score.objects.create(arrangement=asset.score.arrangement,
            version=Score.objects.filter(arrangement=asset.score.arrangement).aggregate(last=Max('version'))['last']+1,
            file_format='midi',title='Previous Ode to Joy edition',original_filename='previous-ode.mid',
            content_sha256=hashlib.sha256(old_bytes).hexdigest(),parsed=old_parsed,
            rights_confirmed_at=timezone.now(),source_provenance={'kind':'previous_curated_edition'})
        legacy.musicxml.save('previous-ode.mid',ContentFile(old_bytes))
        asset.score = legacy
        asset.save(update_fields=['score'])
        profile = Profile.objects.get()
        lesson_id = 'lesson:ode-to-joy:melody'
        library = PersonalLibrary.objects.create(profile=profile,
            favorites=[f'composition:{composition_id}',lesson_id],progress={lesson_id:'mastered'},
            positions={f'composition:{composition_id}':12.5})
        note = PracticeNote.objects.create(profile=profile,content_id=lesson_id,
            position_seconds=2,text='Keep my old edition note')
        call_command('seed_studio',stdout=io.StringIO())
        asset.refresh_from_db()
        self.assertEqual(asset.score.arrangement.composition_id,composition_id)
        self.assertNotEqual(asset.score_id,legacy.pk)
        self.assertEqual(asset.score.content_sha256,SOURCE_BY_CODE['ode-to-joy'].sha256)
        library.refresh_from_db()
        self.assertEqual(library.progress,{lesson_id:'mastered'})
        self.assertEqual(library.favorites,[f'composition:{composition_id}',lesson_id])
        note.refresh_from_db()
        self.assertEqual(note.text,'Keep my old edition note')
        with legacy.musicxml.open('rb') as source:
            self.assertEqual(source.read(),old_bytes)
        self.assertFalse(any(item['id']==lesson_id for item in studio_catalog('uz')['lessons']))
