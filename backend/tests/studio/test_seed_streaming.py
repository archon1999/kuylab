"""The production seed validates completely without retaining every note graph."""
import hashlib
import io
from pathlib import Path
import tempfile
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from apps.learning.models import Arrangement, Composition
from apps.scores.midi import parse_midi
from apps.scores.models import Score
from apps.studio.management.commands import seed_studio
from apps.studio.midi_authoring import midi_bytes
from apps.studio.models import StudioAsset


class StreamingSeedTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        self.override = override_settings(MEDIA_ROOT=self.media.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.source = seed_studio.SOURCE_BY_CODE['still']
        raw = midi_bytes([(0,1,60,'right',80)],end_quarters=1)
        self.asset = (self.source.asset_key,'Validated test source',raw,parse_midi(raw),
                      {'kind':'user_supplied_original_midi','filename':'test.mid',
                       'source_sha256':hashlib.sha256(raw).hexdigest(),'preserved_original_bytes':True})

    def run_seed(self,factory):
        with patch.object(seed_studio,'SOURCES',(self.source,)), \
             patch.object(seed_studio,'iter_prepared_assets',side_effect=factory), \
             patch.object(seed_studio,'prepared_assets',side_effect=AssertionError('Do not materialize the catalog')):
            call_command('seed_studio',stdout=io.StringIO())

    def assert_no_persistent_writes(self):
        for model in (Composition,Arrangement,Score,StudioAsset):
            self.assertEqual(model.objects.count(),0)
        self.assertEqual(list(Path(self.media.name).rglob('*.mid')),[])

    def test_a_late_parser_failure_occurs_before_any_database_or_file_write(self):
        def broken():
            yield self.asset
            raise ValueError('A later source could not be parsed')

        with patch.object(Composition.objects,'update_or_create') as write:
            with self.assertRaisesMessage(ValueError,'later source'):
                self.run_seed(broken)
            write.assert_not_called()
        self.assert_no_persistent_writes()

    def test_complete_validation_precedes_transactional_streaming(self):
        baseline = len(connection.atomic_blocks)
        passes = []

        def stream():
            passes.append(len(connection.atomic_blocks))
            yield self.asset

        self.run_seed(stream)
        self.assertEqual(passes,[baseline,baseline+1])
        self.assertEqual(Score.objects.count(),1)
        self.assertEqual(StudioAsset.objects.get().score.content_sha256,hashlib.sha256(self.asset[2]).hexdigest())

    def test_between_pass_changes_are_rejected_and_rolled_back(self):
        changed = (*self.asset[:-1],{**self.asset[-1],'hand_assignment':'changed after validation'})
        calls = iter([(self.asset,),(changed,)])
        with self.assertRaisesMessage(CommandError,'changed after validation'):
            self.run_seed(lambda:iter(next(calls)))
        self.assert_no_persistent_writes()

    def test_missing_late_asset_rolls_back_and_removes_only_new_files(self):
        second = ('test:later',*self.asset[1:])
        calls = iter([(self.asset,second),(self.asset,)])
        with self.assertRaisesMessage(CommandError,'disappeared after validation'):
            self.run_seed(lambda:iter(next(calls)))
        self.assert_no_persistent_writes()

    def test_idempotent_lookup_does_not_select_historical_parsed_note_graphs(self):
        self.run_seed(lambda:iter((self.asset,)))
        original_id = StudioAsset.objects.get().score_id
        files = sorted(path.name for path in Path(self.media.name).rglob('*.mid'))
        with CaptureQueriesContext(connection) as queries:
            self.run_seed(lambda:iter((self.asset,)))
        lookups = [query['sql'] for query in queries if 'JOIN "scores_score"' in query['sql']]
        self.assertTrue(lookups)
        self.assertTrue(all('"parsed"' not in query for query in lookups))
        self.assertEqual(StudioAsset.objects.get().score_id,original_id)
        self.assertEqual(Score.objects.count(),1)
        self.assertEqual(sorted(path.name for path in Path(self.media.name).rglob('*.mid')),files)
