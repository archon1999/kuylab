import test from 'node:test';
import assert from 'node:assert/strict';
import { transitionColorMode } from '../src/shared/ui/colorModeTransition.ts';
import { initializeMotion, motionDurations, motionDuration, motionEasing } from '../src/shared/ui/motion.ts';

function environment(t, reduced = false) {
  const previous = ['document', 'window'].map(key => [key, Object.getOwnPropertyDescriptor(globalThis, key)]);
  const properties = new Map();
  const root = { dataset: {}, style: { setProperty: (key, value) => properties.set(key, value) } };
  const document = { documentElement: root };
  Object.defineProperty(globalThis, 'document', { configurable: true, value: document });
  Object.defineProperty(globalThis, 'window', { configurable: true, value: { matchMedia: () => ({ matches: reduced }) } });
  t.after(() => previous.forEach(([key, value]) => value ? Object.defineProperty(globalThis, key, value) : delete globalThis[key]));
  return { document, root, properties };
}

test('theme motion has one duration; unsupported and reduced-motion browsers update directly', t => {
  const { document, properties } = environment(t, true);
  initializeMotion();
  assert.equal(properties.get('--motion-duration'), `${motionDuration}ms`);
  assert.equal(properties.get('--motion-easing'), motionEasing);
  assert.deepEqual(new Set(Object.values(motionDurations)), new Set([motionDuration]));
  let value = 0;
  transitionColorMode(() => value++);
  document.startViewTransition = () => { throw new Error('Reduced motion must bypass snapshots'); };
  transitionColorMode(() => value++);
  assert.equal(value, 2);
});

test('rapid theme changes skip old snapshots; stale callbacks cannot revert the latest mode or clear its guard', async t => {
  const { document, root } = environment(t);
  const transitions = [];
  document.startViewTransition = update => {
    let finish;
    const value = { update, ready: Promise.resolve(), finished: new Promise(resolve => finish = resolve), finish: () => finish(), skipped: false, skipTransition() { this.skipped = true; } };
    transitions.push(value);
    return value;
  };
  let mode = 'light';
  transitionColorMode(() => mode = 'dark');
  transitionColorMode(() => mode = 'light');
  assert.equal(transitions[0].skipped, true);
  transitions[0].update();
  assert.equal(mode, 'light');
  transitions[1].update();
  transitions[0].finish();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(root.dataset.themeTransition, 'true');
  transitions[1].finish();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(root.dataset.themeTransition, undefined);
});
