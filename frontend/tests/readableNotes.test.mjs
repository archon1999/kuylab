import assert from 'node:assert/strict';
import test from 'node:test';
import { readableRollNotes } from '../src/modules/practice/domain/readableNotes.ts';
import { normalizeStudioPreferences, defaultStudioPreferences } from '../src/modules/practice/domain/studioPreferences.ts';
import { notesForWindow } from '../src/modules/practice/domain/studioTransport.ts';

const note = (id, onset, duration, hand = 'left', pitch = 50) => ({ id, onset, duration, hand, pitch, velocity: 75, soundDuration: duration });
test('baked long holds are abbreviated for reading without changing the source or audible scheduling', () => {
  const notes = [note('bass', 0, 5), note('fifth', .3, 4.7, 'left', 57), note('third', .6, 4.4, 'left', 65), note('end', 2, 3)];
  const original = structuredClone(notes);
  const displayed = readableRollNotes(notes);
  assert.ok(displayed[0].duration < .3);
  assert.ok(displayed[1].duration < .3);
  assert.ok(displayed[2].duration < 1.4);
  assert.equal(displayed[3].duration, 3);
  assert.deepEqual(notes, original);
  assert.deepEqual(displayed.map(({ duration, ...rest }) => rest), notes.map(({ duration, ...rest }) => rest));
  const window = { sourceFrom: .1, sourceTo: 1, wallFrom: 0, speed: 1, resume: true, sourceEnd: 5 };
  const audio = (sounds) => sounds.map(({ note, ...sound }) => ({ ...sound, pitch: note.pitch, velocity: note.velocity, hand: note.hand }));
  assert.deepEqual(audio(notesForWindow(displayed, window)), audio(notesForWindow(notes, window)));
});
test('chord micro-offsets form one group and the other hand cannot cut its duration', () => {
  const notes = [note('a', 0, 4), note('b', .02, 3.9, 'left', 62), note('rh', .1, .2, 'right', 80), note('c', 1, .8)];
  const displayed = readableRollNotes(notes);
  assert.ok(displayed[0].duration > .8 && displayed[0].duration < 1);
  assert.ok(displayed[1].duration > .8 && displayed[1].duration < 1);
  assert.equal(displayed[2].duration, .2);
});
test('ordinary legato, sparse melody and final resonance keep their actual lengths', () => {
  const notes = [note('a', 0, .95), note('b', 1, 1.1), note('c', 2, 4)];
  assert.deepEqual(readableRollNotes(notes), notes);
  assert.deepEqual(readableRollNotes([note('solo', 0, 6, 'right')]), [note('solo', 0, 6, 'right')]);
});
test('compact display defaults on for reviewed sources but can be persistently disabled', () => {
  assert.equal(defaultStudioPreferences.compactNoteLengths, true);
  assert.equal(normalizeStudioPreferences({ compactNoteLengths: false }).compactNoteLengths, false);
  assert.equal(normalizeStudioPreferences({ compactNoteLengths: 'false' }).compactNoteLengths, true);
});
