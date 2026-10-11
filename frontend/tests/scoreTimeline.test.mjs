import assert from 'node:assert/strict';
import test from 'node:test';
import { attacksInWindow, beatQuarters, pitchLabel, validateRequestedTempo, timeline } from '../src/modules/practice/domain/score.ts';

const requestedTempoFromParams=params=>validateRequestedTempo(params.get('bpm'),params.get('beat_unit'));
function event(id, measure, offset, pitch, overrides = {}) {
  return { id, part_id: 'P1', measure_index: measure, measure_number: String(measure + 1), offset_quarters: offset, onset_quarters: measure * 3 + offset, duration_quarters: 0.5, pitch: pitch === null ? null : { step: 'D', alter: 0, octave: 4, midi: pitch }, staff: 1, voice: '1', hand: 'right', rest: pitch === null, chord: false, grace: false, ties: [], ...overrides };
}
function score(events, overrides = {}) {
  return { parsed: { events, playback_order: [0, 1], measures: [0, 1].map(index => ({ index, number: String(index + 1), start_quarters: index * 3, length_quarters: 3 })) }, ...overrides };
}

test('BPM converts the declared beat unit, including dotted quarter in 6/8', () => {
  assert.equal(beatQuarters('quarter'), 1);
  assert.equal(beatQuarters('quarter', 1), 1.5);
  assert.equal(beatQuarters('dotted_quarter'), 1.5);
  assert.equal(beatQuarters('quarter', 2), 1.75);
  assert.equal(beatQuarters('eighth'), 0.5);
  assert.equal(60 * beatQuarters('quarter', 1), 90);
  assert.equal(pitchLabel(60), 'C4');
});

test('Tied continuation sustains one attack across adjacent measures', () => {
  const result = timeline(score([event('a', 0, 2.5, 62, { ties: ['start'] }), event('b', 1, 0, 62, { ties: ['stop'], duration_quarters: 1 })]), 0, 1, 'both');
  assert.equal(result.notes.length, 1);
  assert.equal(result.notes[0].play_onset, 2.5);
  assert.equal(result.notes[0].play_duration, 1.5);
  assert.equal(result.length, 6);
});

test('Starting a selected fragment on a tied stop produces a playable attack', () => {
  const result = timeline(score([event('a', 0, 2.5, 62, { ties: ['start'] }), event('b', 1, 0, 62, { ties: ['stop'], duration_quarters: 1 })]), 1, 1, 'right');
  assert.equal(result.notes.length, 1);
  assert.equal(result.notes[0].play_onset, 0);
  assert.equal(result.notes[0].onset_quarters, 3);
  assert.equal(result.length, 3);
});

test('Full score expands repeat itinerary while selected fragment follows written order', () => {
  const source = score([event('a', 0, 0, 62), event('b', 1, 0, 65)], { parsed: { events: [event('a', 0, 0, 62), event('b', 1, 0, 65)], playback_order: [0, 1, 0, 1], measures: [0, 1].map(index => ({ index, number: String(index + 1), start_quarters: index * 3, length_quarters: 3 })) } });
  const all = timeline(source, 0, 1, 'both');
  assert.deepEqual(all.notes.map(note => note.play_onset), [0, 3, 6, 9]);
  assert.deepEqual(all.notes.map(note => note.onset_quarters), [0, 3, 0, 3]);
  assert.equal(all.length, 12);
  assert.equal(timeline(source, 1, 1, 'both').notes.length, 1);
});

test('Chord attacks remain simultaneous; hand overrides and silent events are respected', () => {
  const source = score([event('a', 0, 0, 62), event('b', 0, 0, 65, { chord: true }), event('c', 0, 0, 57, { hand: 'left' }), event('d', 0, 1, null), event('e', 0, 1, 60, { grace: true }), event('f', 0, 2, 60, { cue: true })], { hand_overrides: { b: 'left' } });
  assert.deepEqual(timeline(source, 0, 1, 'right').notes.map(note => note.id), ['a']);
  assert.deepEqual(timeline(source, 0, 1, 'left').notes.map(note => note.id), ['b', 'c']);
  assert.deepEqual(timeline(source, 0, 1, 'both').notes.map(note => note.play_onset), [0, 0, 0]);
});

test('lookahead stops at the final boundary without scheduling a second first note', () => {
  const notes = [{ id: 'first', play_onset: 0 }, { id: 'last', play_onset: 0.9 }];
  assert.deepEqual(attacksInWindow(notes, 1, 1, 0, 0.96, 1.08), []);
});

test('adjacent scheduling windows neither duplicate boundary chord attacks nor restart at the end', () => {
  const notes = [{ id: 'a', play_onset: 0 }, { id: 'b', play_onset: 0 }, { id: 'c', play_onset: 0.5 }];
  const windows = [[0, 0.5], [0.5, 1], [1, 1.5], [1.5, 2]].flatMap(([from, until]) => attacksInWindow(notes, 1, 1, 0, from, until));
  assert.deepEqual(windows.map(item => [item.event.id, item.when]), [['a', 0], ['b', 0], ['c', 0.5]]);
});

test('Source lesson URL uses its declared practice pulse without changing XML tempo', () => {
  const sourceTempo = { bpm: 60, beat_unit: 'quarter', beat_unit_dots: 1 };
  const override = requestedTempoFromParams(new URLSearchParams('bpm=40&beat_unit=quarter'));
  assert.deepEqual(override, { bpm: 40, beat_unit: 'quarter' });
  assert.equal(override.bpm * beatQuarters(override.beat_unit), 40);
  assert.equal(sourceTempo.bpm * beatQuarters(sourceTempo.beat_unit, sourceTempo.beat_unit_dots), 90);
  assert.deepEqual(sourceTempo, { bpm: 60, beat_unit: 'quarter', beat_unit_dots: 1 });
  for (const query of ['bpm=0&beat_unit=quarter', 'bpm=241&beat_unit=quarter', 'bpm=40&beat_unit=unexpected', 'bpm=40.5&beat_unit=quarter', 'bpm=40', 'beat_unit=quarter']) assert.equal(requestedTempoFromParams(new URLSearchParams(query)), null);
});
