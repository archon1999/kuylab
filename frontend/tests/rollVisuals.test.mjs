import test from 'node:test';
import assert from 'node:assert/strict';
import { velocityStrength, noteShading, allowsStrikeEffects, isContinuousStep, StrikeParticlePool } from '../src/modules/practice/ui/shared/rollVisuals.ts';

test('velocity shading is bounded and stronger notes have stronger visual emphasis', () => {
  assert.equal(velocityStrength(-10), 0);
  assert.equal(velocityStrength(400), 1);
  assert.equal(velocityStrength(NaN), 85 / 127);
  const soft = noteShading('#5f95ce', 20, true);
  const strong = noteShading('#5f95ce', 120, true);
  assert.ok(strong.opacity > soft.opacity);
  assert.ok(strong.strength > soft.strength);
  assert.notEqual(strong.top, soft.top);
  assert.deepEqual(noteShading('#5f95ce', 20, false), noteShading('#5f95ce', 120, false));
});

test('paused, disabled or reduced-motion playback cannot emit particles; seeks are not strikes', () => {
  assert.equal(allowsStrikeEffects(true, true, false), true);
  assert.equal(allowsStrikeEffects(false, true, false), false);
  assert.equal(allowsStrikeEffects(true, false, false), false);
  assert.equal(allowsStrikeEffects(true, true, true), false);
  assert.equal(isContinuousStep(4, 4.025), true);
  assert.equal(isContinuousStep(4, 4), false);
  assert.equal(isContinuousStep(4, 3), false);
  assert.equal(isContinuousStep(4, 9), false);
});

test('dense chords reuse a bounded particle pool and particles expire without growing memory', () => {
  const pool = new StrikeParticlePool(144);
  const entries = [...pool.particles];
  for (let i = 0; i < 1000; i++) pool.emit(300, 400, '#a5c7f0', 127, 10, 20);
  assert.equal(pool.particles.length, 144);
  assert.ok(pool.particles.every((particle, index) => particle === entries[index]));
  assert.equal(pool.hasActive(10.2), true);
  assert.equal(pool.hasActive(12), false);
  pool.emit(300, 400, '#a5c7f0', 64, 20, 20);
  pool.clear();
  assert.equal(pool.hasActive(20.1), false);
  assert.equal(new StrikeParticlePool(10000).particles.length, 192);
});
