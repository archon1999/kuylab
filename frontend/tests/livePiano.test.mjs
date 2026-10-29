import test from 'node:test';
import assert from 'node:assert/strict';
import { createLivePiano } from '../src/modules/practice/application/livePiano.ts';
import { computerPianoPitch, pianoKeyboardHeight, pianoPitchAt, visiblePianoKeys } from '../src/modules/practice/domain/liveKeyboard.ts';
import { keyboardRange, keyboardViewport } from '../src/modules/practice/domain/keyboardViewport.ts';

function setup() {
  const played = [], released = [], states = [], pending = [];
  let delayed = false;
  const audio = { prepare: () => delayed ? new Promise((resolve, reject) => pending.push({ resolve, reject })) : Promise.resolve(), now: () => 10, sound(pitch, when, duration, velocity) { played.push({ pitch, when, duration, velocity }); return () => released.push(pitch); }, stop() { released.push('all'); } };
  const piano = createLivePiano(audio, state => states.push(state));
  return { piano, played, released, states, pending, delay() { delayed = true; } };
}
test('independent holds form chords and release individual voices without cutting the others', async () => {
  const t = setup();
  await Promise.all([t.piano.press('finger:1', 60), t.piano.press('finger:2', 64), t.piano.press('finger:3', 67)]);
  assert.deepEqual(t.played.map(n => n.pitch), [60, 64, 67]);
  assert.deepEqual(t.states.at(-1).pitches, [60, 64, 67]);
  t.piano.release('finger:2');
  assert.deepEqual(t.released, [64]);
  assert.deepEqual(t.states.at(-1).pitches, [60, 67]);
  t.piano.stop(); assert.deepEqual(t.states.at(-1).pitches, []);
});
test('two inputs on the same pitch hold one voice until the last input releases', async () => {
  const t=setup();
  await t.piano.press('mouse',60); await t.piano.press('KeyA',60); await t.piano.press('KeyA',60);
  assert.equal(t.played.length,1);
  t.piano.release('mouse'); assert.deepEqual(t.released,[]);
  t.piano.release('KeyA'); assert.deepEqual(t.released,[60]);
});
test('release, glissando and stop invalidate in-flight sample loads without ghost notes', async () => {
  const t=setup(); t.delay();
  const first=t.piano.press('finger',60);
  const second=t.piano.press('finger',61);
  t.pending[0].resolve(); await first; assert.deepEqual(t.played,[]);
  t.pending[1].resolve(); await second; assert.deepEqual(t.played.map(n=>n.pitch),[61]);
  const third=t.piano.press('other',64); t.piano.release('other'); t.pending[2].resolve(); await third;
  const fourth=t.piano.press('other',67); t.piano.stop(); t.pending[3].resolve(); await fourth;
  assert.deepEqual(t.played.map(n=>n.pitch),[61]);
});
test('failed notes are retryable and a late failure cannot erase a newer hold', async () => {
  const t=setup(); t.delay();
  const first=t.piano.press('finger',60); t.piano.release('finger');
  const second=t.piano.press('finger',60);
  t.pending[0].reject(new Error('old')); await first;
  assert.deepEqual(t.states.at(-1).pitches,[60]);
  t.pending[1].reject(new Error('network')); await second;
  assert.equal(t.states.at(-1).error,true);
  const retry=t.piano.press('finger',60); t.pending[2].resolve(); await retry;
  assert.equal(t.states.at(-1).error,false); assert.equal(t.played.length,1);
});
test('hit testing follows the same panned layout, black-key priority and keyboard boundary', () => {
  for(const width of [390,1200]) for(const zoom of [1,3,5]) {
    const view=keyboardViewport(width,zoom,.53,keyboardRange([],false));
    for(const key of visiblePianoKeys(view)) {
      const x=key.x+key.width/2;
      if(x<0 || x>=width) continue;
      assert.equal(pianoPitchAt(view,120,x,key.white?110:20),key.pitch);
    }
    assert.equal(pianoPitchAt(view,120,-1,20),null);
    assert.equal(pianoPitchAt(view,120,10,120),null);
  }
  assert.equal(pianoKeyboardHeight(1000),152);
  assert.equal(pianoKeyboardHeight(100),86);
  assert.equal(computerPianoPitch('KeyA'),60);
  assert.equal(computerPianoPitch('KeyW'),61);
  assert.equal(computerPianoPitch('KeyK'),72);
  assert.equal(computerPianoPitch('ArrowLeft'),null);
});
