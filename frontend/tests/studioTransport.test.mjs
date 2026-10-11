import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import { StudioTransport, studioTimeline, notesForWindow, pianoKeyLayout } from '../src/modules/practice/domain/studioTransport.ts';

const close = (value, expected) => assert.ok(Math.abs(value - expected) < 1e-6, `${value} != ${expected}`);
const note = (onset, duration, extra = {}) => ({ id: 'n', pitch: 60, hand: 'right', onset, duration, soundDuration: duration, velocity: 85, ...extra });

test('a speed change preserves source position and changes only future wall-clock time', () => {
  const t = new StudioTransport(100, 20);
  t.play(10);
  close(t.snapshot(15).position, 25);
  t.setSpeed(0.5, 15);
  close(t.snapshot(15).position, 25);
  close(t.snapshot(19).position, 27);
  t.setSpeed(2, 19);
  close(t.snapshot(20).position, 29);
});

test('pause excludes time, resume preserves position and exact end permits restart', () => {
  const t = new StudioTransport(12);
  t.play(0); t.pause(4);
  close(t.snapshot(100).position, 4);
  t.play(100);
  assert.deepEqual(t.snapshot(108), { position: 12, ended: true });
  t.pause(108); t.play(200);
  close(t.snapshot(201).position, 1);
});

test('initial positions are bounded and a completed recording restarts from zero', () => {
  const t = new StudioTransport(10, 999);
  close(t.snapshot(0).position, 10);
  t.play(1); close(t.snapshot(2).position, 1);
  assert.equal(new StudioTransport(10, -2).snapshot(0).position, 0);
  assert.equal(new StudioTransport(10, NaN).snapshot(0).position, 0);
});

test('playback ends once at every speed and does not schedule a second pass', () => {
  for (const speed of [0.2, 0.5, 1, 2]) {
    const t = new StudioTransport(10);
    t.setSpeed(speed, 0); t.play(3);
    const end = 3 + 10 / speed;
    assert.deepEqual(t.snapshot(end), { position: 10, ended: true });
    assert.deepEqual(t.snapshot(end + 100), { position: 10, ended: true });
    assert.deepEqual(t.windows(end, end + 100), []);
  }
});

test('seeking moves freely within the complete piece and clamps invalid positions', () => {
  const t = new StudioTransport(20);
  t.seek(14, 0); close(t.snapshot(0).position, 14);
  t.seek(2, 0); close(t.snapshot(0).position, 2);
  t.seek(50, 0); close(t.snapshot(0).position, 20);
  t.seek(-5, 0); close(t.snapshot(0).position, 0);
  t.seek(NaN, 0); close(t.snapshot(0).position, 0);
});

test('scheduling windows clip at the final source boundary', () => {
  const t = new StudioTransport(3, 1); t.play(0);
  assert.deepEqual(t.windows(1.5, 3.5), [
    { sourceFrom: 2.5, sourceTo: 3, wallFrom: 1.5, speed: 1, resume: false, sourceEnd: 3 },
  ]);
  assert.deepEqual(t.windows(2, 3), []);
});

test('adjacent scheduler windows play each boundary attack exactly once', () => {
  const t = new StudioTransport(10); t.play(0);
  const notes = [note(0, 1), note(0.15, 1), note(0.3, 1)];
  const starts = [[0, 0.15], [0.15, 0.3], [0.3, 0.45]].flatMap(([from, until]) => t.windows(from, until).flatMap(window => notesForWindow(notes, window))).map(sound => sound.when);
  assert.deepEqual(starts, [0, 0.15, 0.3]);
});

test('notes already sounding at a seek are resumed with the correct sample offset', () => {
  const t = new StudioTransport(10, 4); t.play(20);
  const sounds = notesForWindow([note(2, 6)], t.windows(20, 20.15)[0]);
  assert.equal(sounds.length, 1);
  assert.equal(sounds[0].offset, 2);
  assert.equal(sounds[0].duration, 4);
  assert.equal(sounds[0].when, 20);
});

test('pedal tails remain audible after seek without extending the visual key hold', () => {
  const t = new StudioTransport(10, 4); t.play(0);
  const original = note(2, 1, { soundDuration: 5 });
  const [sound] = notesForWindow([original], t.windows(0, 0.1)[0]);
  assert.equal(sound.duration, 3);
  assert.equal(sound.note.duration, 1);
});

test('no release tail exceeds the source ending and speed scales audible duration', () => {
  const t = new StudioTransport(12, 10);
  t.setSpeed(0.5, 0); t.play(0);
  const [sound] = notesForWindow([note(10, 8)], t.windows(0, 0.2)[0]);
  assert.equal(sound.duration, 4);
});

test('a suspended browser waking after the ending remains at the end', () => {
  const t = new StudioTransport(20); t.play(0);
  assert.deepEqual(t.snapshot(3601), { position: 20, ended: true });
  assert.deepEqual(t.windows(3601, 3601.15), []);
});

test('all 88 pitches align with 52 white keys and a final C8', () => {
  const keys = pianoKeyLayout(1040);
  assert.equal(keys.length, 88);
  assert.equal(keys.filter(key => key.white).length, 52);
  assert.equal(keys[0].pitch, 21);
  assert.equal(keys.at(-1).pitch, 108);
  close(keys.at(-1).x + keys.at(-1).width, 1040);
});

test('native MIDI seconds and velocity survive preprocessing, percussion excluded', () => {
  const event = { id: 'a', pitch: { midi: 60 }, hand: 'left', onset_quarters: 4, duration_quarters: 2, onset_seconds: 3, duration_seconds: 1, sound_duration_seconds: 2, velocity: 44 };
  const result = studioTimeline({ parsed: { metadata: { duration_seconds: 7, tempo: { quarter_bpm: 100 } }, events: [event, { ...event, id: 'drum', percussion: true }] } });
  assert.equal(result.duration, 7);
  assert.equal(result.notes.length, 1);
  assert.deepEqual(result.notes[0], { id: 'a', pitch: 60, hand: 'left', onset: 3, duration: 1, soundDuration: 2, velocity: 44 });
});

test('notes crossing a tempo-map change keep their full musical duration', () => {
  const score = { parsed: { metadata: { tempo: { quarter_bpm: 120 } }, tempo_map: [{ onset_quarters: 0, quarter_bpm: 120 }, { onset_quarters: 4, quarter_bpm: 60 }], events: [{ id: 'a', pitch: { midi: 64 }, hand: 'right', onset_quarters: 3, duration_quarters: 3 }] } };
  const [note] = studioTimeline(score).notes;
  assert.equal(note.onset, 1.5);
  assert.equal(note.duration, 2.5);
});

test('the offline sample bank has all four recorded Steinway layers and the offline worklet', () => {
  const base = new URL('../public/audio/splendid/', import.meta.url);
  const manifest = JSON.parse(fs.readFileSync(new URL('manifest.json', base), 'utf8'));
  assert.equal(manifest.license, 'Public Domain');
  assert.equal(manifest.author, 'AKAI');
  assert.equal(manifest.files.length, 227);
  let size = 0;
  for (const entry of manifest.files) {
    const bytes = fs.readFileSync(new URL('../public' + entry.path, import.meta.url));
    assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), entry.sha256);
    assert.equal(bytes.length, entry.bytes);
    assert.ok(bytes.length > 1000);
    size += bytes.length;
  }
  assert.equal(size, manifest.total_bytes);
  assert.ok(fs.readFileSync(new URL('LICENSE.txt', base), 'utf8').includes('Public Domain'));
});
