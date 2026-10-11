import assert from 'node:assert/strict';
import test from 'node:test';
import {
  ProfileResource,
  serializeProfileWrites,
} from '../src/modules/profile/application/ProfileResource.ts';
import { defaultProfile, validateProfile } from '../src/modules/profile/domain/index.ts';
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => {
    resolve = yes;
    reject = no;
  });
  return { promise, resolve, reject };
};
const flush = () => new Promise((resolve) => setImmediate(resolve));
const snapshot = (name) => ({
  ...defaultProfile,
  display_name: name,
  language: 'uz',
  theme: 'light',
});

test('profile fields and language/theme changes never write the same record concurrently', async () => {
  const first = deferred(),
    calls = [];
  const port = serializeProfileWrites({
    get: async () => snapshot('Server'),
    save: (value) => {
      calls.push(['profile', value.display_name]);
      return first.promise;
    },
    savePreferences: async (value) => {
      calls.push(['preferences', value]);
    },
  });
  const saving = port.save(snapshot('New name'));
  const preferences = port.savePreferences({ language: 'en', theme: 'dark' });
  await flush();
  assert.deepEqual(calls, [['profile', 'New name']]);
  first.resolve(snapshot('New name'));
  await saving;
  await preferences;
  assert.deepEqual(calls[1], ['preferences', { language: 'en', theme: 'dark' }]);
});

test('a failed profile save cannot block a later preference write', async () => {
  let written = false;
  const port = serializeProfileWrites({
    get: async () => snapshot('Server'),
    save: async () => {
      throw new Error('save failed');
    },
    savePreferences: async () => {
      written = true;
    },
  });
  await assert.rejects(port.save(defaultProfile));
  await port.savePreferences({ language: 'ru' });
  assert.equal(written, true);
});

test('a late profile GET cannot undo a successful profile save or persist its stale fields', async () => {
  const reads = [deferred(), deferred()];
  let index = 0;
  const persisted = [],
    hydrated = [];
  const model = new ProfileResource(
    { get: () => reads[index++].promise, save: async (value) => value },
    defaultProfile,
    (value) => persisted.push(value.display_name),
    (value) => hydrated.push(value.display_name),
  );
  const initial = model.reload();
  reads[0].resolve(snapshot('Initial'));
  await initial;
  const late = model.reload();
  await model.save(snapshot('User edited'));
  reads[1].resolve(snapshot('Stale'));
  await late;
  assert.equal(model.getSnapshot().profile.display_name, 'User edited');
  assert.deepEqual(persisted, ['Initial', 'User edited']);
  assert.deepEqual(hydrated, ['Initial']);
});

test('the latest retry decides profile connectivity and older failed reads cannot mark it offline', async () => {
  const reads = [deferred(), deferred()];
  let index = 0;
  const model = new ProfileResource(
    { get: () => reads[index++].promise },
    defaultProfile,
    () => {},
    () => {},
  );
  const old = model.reload(),
    current = model.reload();
  reads[1].resolve(snapshot('Current'));
  await current;
  reads[0].reject(new Error('old timeout'));
  await old;
  assert.equal(model.getSnapshot().online, true);
  assert.equal(model.getSnapshot().loading, false);
  assert.equal(model.getSnapshot().profile.display_name, 'Current');
});

test('profile validation accepts API limits and catches blank/control/oversize fields before writes', () => {
  assert.deepEqual(
    validateProfile({
      ...defaultProfile,
      display_name: 'A'.repeat(80),
      instrument_model: 'B'.repeat(120),
      goals: 'C'.repeat(240),
      daily_minutes: 180,
    }),
    {},
  );
  assert.equal(validateProfile({ ...defaultProfile, display_name: '  ' }).display_name, 'required');
  assert.equal(
    validateProfile({ ...defaultProfile, display_name: 'Name\n' }).display_name,
    'control',
  );
  assert.equal(validateProfile({ ...defaultProfile, goals: 'C'.repeat(241) }).goals, 'too_long');
  assert.equal(validateProfile({ ...defaultProfile, daily_minutes: 4 }).daily_minutes, 'range');
});
