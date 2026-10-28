import assert from 'node:assert/strict';
import test from 'node:test';
import { normalizeStudioPreferences, defaultStudioPreferences } from '../src/modules/practice/domain/studioPreferences.ts';
import { createStudioPreferences } from '../src/modules/practice/data-access/repository/studio-preferences.repository.impl.ts';

test('missing, malformed and non-object stored preferences restore safe defaults', () => {
  for (const input of [undefined, null, [], 42, 'bad']) assert.deepEqual(normalizeStudioPreferences(input), defaultStudioPreferences);
  const malformed = createStudioPreferences({ getItem: () => '{bad json', setItem() {} });
  assert.deepEqual(malformed.read(), defaultStudioPreferences);
});

test('restored numeric controls are finite, bounded and snapped to their actual UI steps', () => {
  assert.deepEqual(normalizeStudioPreferences({ lookahead: 0, volume: 400, reverb: -8, speed: 99 }), { ...defaultStudioPreferences, lookahead: 2, volume: 100, reverb: 0, speed: 2 });
  const value = normalizeStudioPreferences({ speed: 0.96, lookahead: 7.7, volume: NaN, reverb: Infinity });
  assert.equal(value.speed, 0.95);
  assert.equal(value.lookahead, 8);
  assert.equal(value.volume, 70);
  assert.equal(value.reverb, 25);
});

test('invalid boolean/string/color values cannot alter or inject canvas settings', () => {
  const result = normalizeStudioPreferences({ noteNames: 'false', keyNames: false, left: false, right: false, leftColor: '#AABBCC', rightColor: 'url(javascript:bad)', speed: '0.5' });
  assert.equal(result.noteNames, true);
  assert.equal(result.keyNames, false);
  assert.equal(result.left, false);
  assert.equal(result.right, false);
  assert.equal(result.leftColor, '#aabbcc');
  assert.equal(result.rightColor, defaultStudioPreferences.rightColor);
  assert.equal(result.speed, 1);
});

test('another player instance restores personal settings but never a previous score range', () => {
  const map = new Map();
  const storage = { getItem: key => map.get(key) || null, setItem: (key, value) => map.set(key, value) };
  createStudioPreferences(storage).write({ ...defaultStudioPreferences, noteNames: false, lookahead: 11, leftColor: '#112233', volume: 39, reverb: 25, speed: 0.65, loopDelay: 3, range: [12, 18], score: 15, position: 13, playing: true });
  assert.deepEqual(createStudioPreferences(storage).read(), { ...defaultStudioPreferences, noteNames: false, lookahead: 11, leftColor: '#112233', volume: 39, reverb: 25, speed: 0.65 });
  const stored = JSON.parse([...map.values()][0]);
  for (const field of ['loopDelay', 'range', 'score', 'position', 'playing']) assert.equal(field in stored, false);
});

test('denied browser storage cannot prevent opening a player or changing current preferences', () => {
  const port = createStudioPreferences({ getItem() { throw new Error('Denied'); }, setItem() { throw new Error('Quota'); } });
  assert.deepEqual(port.read(), defaultStudioPreferences);
  assert.doesNotThrow(() => port.write({ ...defaultStudioPreferences, volume: 0 }));
});

test('all player instances share account preferences and notify already-open views', () => {
  const map = new Map();
  const storage = { getItem: key => map.get(key) || null, setItem: (key, value) => map.set(key, value) };
  const main = createStudioPreferences(storage), study = createStudioPreferences(storage), preview = createStudioPreferences(storage);
  let updates = 0;
  const stop = preview.subscribe(() => updates++);
  main.write({ ...defaultStudioPreferences, speed: 1.5, volume: 44, leftColor: '#abcdef' });
  assert.equal(study.read().speed, 1.5);
  assert.equal(preview.read().volume, 44);
  assert.equal(preview.read().leftColor, '#abcdef');
  assert.equal(updates, 1);
  stop();
});


test('visual effect preferences default on, validate booleans and persist disabled choices', () => {
  const oldPreferences = normalizeStudioPreferences({ volume: 65 });
  assert.equal(oldPreferences.particles, true);
  assert.equal(oldPreferences.velocityGradients, true);
  const invalid = normalizeStudioPreferences({ particles: 'false', velocityGradients: 0 });
  assert.equal(invalid.particles, true);
  assert.equal(invalid.velocityGradients, true);
  const map = new Map();
  const port = createStudioPreferences({ getItem: key => map.get(key) || null, setItem: (key, value) => map.set(key, value) });
  port.write({ ...oldPreferences, particles: false, velocityGradients: false });
  assert.equal(port.read().particles, false);
  assert.equal(port.read().velocityGradients, false);
});
