import test from 'node:test';
import assert from 'node:assert/strict';
import { PreferenceSynchronizer } from '../src/modules/profile/application/PreferenceSynchronizer.ts';

test('Rapid language/theme choices serialize writes and the final choice wins', async () => {
  const sent = []; const releases = []; let stored = {};
  const sync = new PreferenceSynchronizer(value => { sent.push(value); return new Promise(resolve => releases.push(resolve)); }, value => { stored = { ...value }; });
  const first = sync.choose({ language: 'ru' });
  sync.choose({ theme: 'dark' }); sync.choose({ language: 'en' });
  assert.deepEqual(sent, [{ language: 'ru' }]); assert.deepEqual(stored, { language: 'en', theme: 'dark' });
  releases.shift()(); await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(sent[1], { language: 'en', theme: 'dark' });
  releases.shift()(); await first;
  assert.deepEqual(sync.pending(), {}); assert.deepEqual(stored, {}); assert.equal(sync.canHydrate(), false);
});

test('A late profile GET cannot reset a choice after its PATCH completed', async () => {
  const sync = new PreferenceSynchronizer(async () => {}, () => {});
  assert.equal(sync.canHydrate(), true); await sync.choose({ language: 'en' }); assert.equal(sync.canHydrate(), false);
});

test('API failure retains the chosen preferences for reload and retries them on reconnect', async () => {
  let pending = {}; const offline = new PreferenceSynchronizer(async () => { throw new Error('offline'); }, value => { pending = { ...value }; });
  await offline.choose({ language: 'ru', theme: 'dark' }); assert.deepEqual(pending, { language: 'ru', theme: 'dark' });
  const sent = []; const reloaded = new PreferenceSynchronizer(async value => { sent.push(value); }, value => { pending = { ...value }; }, pending);
  assert.equal(reloaded.canHydrate(), false); await reloaded.flush(); assert.deepEqual(sent, [{ language: 'ru', theme: 'dark' }]); assert.deepEqual(pending, {});
});
