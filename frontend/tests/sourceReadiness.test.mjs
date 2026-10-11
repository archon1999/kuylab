import assert from 'node:assert/strict';
import test from 'node:test';
import { classifySource } from '../src/modules/repertoire/domain/index.ts';

test('complete MIDI status requires verification of the currently selected MIDI file', () => {
  const arrangement = { id: 8, active_score_id: 1, active_score_format: 'midi' };
  assert.equal(classifySource(arrangement), 'midi_uploaded');
  assert.equal(classifySource({ ...arrangement, active_score_completeness_verified_at: '2026-10-11' }), 'full_midi_ready');
});

test('an old verified PDF or a current XML file cannot become a full MIDI claim', () => {
  assert.equal(classifySource({ active_score_id: 2, active_score_format: 'midi', full_score_verified_at: '2026-10-11' }), 'midi_uploaded');
  assert.equal(classifySource({ active_score_id: 3, active_score_format: 'musicxml', active_score_completeness_verified_at: '2026-10-11' }), 'score_uploaded');
  assert.equal(classifySource({ exact_version_confirmed: true, full_score_verified_at: '2026-10-11' }), 'source_selected');
});
