import assert from 'node:assert/strict';
import test from 'node:test';
import { emptyPersonal } from '../src/modules/activity/domain/activity.logic.ts';
import { challengeResultKey, challengeSummary, recordChallengeAnswer, markStudyStarted } from '../src/modules/activity/domain/challengeProgress.ts';
import { mapPersonal } from '../src/modules/activity/data-access/mappers/activity.mapper.ts';
import { createStudioPreferences } from '../src/modules/practice/data-access/repository/studio-preferences.repository.impl.ts';
import { defaultStudioPreferences } from '../src/modules/practice/domain/studioPreferences.ts';
import { setAccountScope, accountStorage } from '../src/shared/lib/accountScope.ts';

const study = 'theory:triads';
const ids = ['build-major', 'build-d-major'];
test('engagement starts only untouched content and never downgrades an existing manual status', () => {
  const original = structuredClone(emptyPersonal);
  const started = markStudyStarted(original, study);
  assert.equal(original.progress[study], undefined);
  assert.equal(started.progress[study], 'learning');
  for (const status of ['learning', 'struggling', 'mastered']) {
    const state = { ...original, progress: { [study]: status } };
    assert.equal(markStudyStarted(state, study), state);
  }
});
test('every active task must be correctly answered before the shared lesson is mastered', () => {
  let state = recordChallengeAnswer(structuredClone(emptyPersonal), study, ids, ids[0], true);
  assert.equal(state.progress[study], 'learning');
  assert.deepEqual(challengeSummary(study, ids, state.challengeResults), { total: 2, correct: 1, status: 'learning' });
  state = recordChallengeAnswer(state, study, ids, ids[1], false);
  assert.equal(state.progress[study], 'struggling');
  state = recordChallengeAnswer(state, study, ids, ids[1], true);
  assert.equal(state.progress[study], 'mastered');
  state = recordChallengeAnswer(state, study, ids, ids[0], false);
  assert.equal(state.progress[study], 'struggling');
  state = recordChallengeAnswer(state, study, ids, ids[0], true);
  assert.equal(state.progress[study], 'mastered');
});
test('correcting one task cannot hide a different unresolved error', () => {
  let state = recordChallengeAnswer(structuredClone(emptyPersonal), study, ids, ids[0], false);
  state = recordChallengeAnswer(state, study, ids, ids[1], false);
  state = recordChallengeAnswer(state, study, ids, ids[0], true);
  assert.equal(state.progress[study], 'struggling');
  assert.equal(challengeSummary(study, ids, state.challengeResults).correct, 1);
});
test('retired tasks and repeated IDs do not inflate totals or block completed current tasks', () => {
  const results = { [challengeResultKey(study, 'old-task')]: 'incorrect' };
  for (const id of ids) results[challengeResultKey(study, id)] = 'correct';
  assert.deepEqual(challengeSummary(study, [...ids, ids[0]], results), { total: 2, correct: 2, status: 'mastered' });
  const state = { ...structuredClone(emptyPersonal), challengeResults: results };
  assert.equal(recordChallengeAnswer(state, study, ids, 'foreign-task', false), state);
});
test('saved results restore after reload and identical question names in other studies stay separate', () => {
  const first = recordChallengeAnswer(structuredClone(emptyPersonal), study, ids, ids[0], true);
  const second = recordChallengeAnswer(first, 'theory:inversions', ids, ids[0], false);
  const restored = mapPersonal(JSON.parse(JSON.stringify(second)));
  assert.equal(restored.challengeResults[challengeResultKey(study, ids[0])], 'correct');
  assert.equal(restored.challengeResults[challengeResultKey('theory:inversions', ids[0])], 'incorrect');
  assert.equal(challengeSummary(study, ids, restored.challengeResults).correct, 1);
  assert.deepEqual(mapPersonal({}).challengeResults, {});
});
test('malformed stored results cannot become completed tasks', () => {
  assert.deepEqual(mapPersonal({ challengeResults: { ok: 'correct', wrong: 'incorrect', '../../bad': 'correct', other: 'mastered', object: {} } }).challengeResults, { ok: 'correct', wrong: 'incorrect' });
});
test('two study players share one setting profile while composition and variant settings remain separate', () => {
  const entries = new Map();
  const storage = { getItem: key => entries.get(key) || null, setItem: (key,value) => entries.set(key,value) };
  const first = createStudioPreferences(storage, 'study:shared');
  first.write({ ...defaultStudioPreferences, speed: .65, volume: 42, keyNames: false });
  const another = createStudioPreferences(storage, 'study:shared');
  assert.equal(another.read().speed, .65);
  assert.equal(another.read().keyNames, false);
  createStudioPreferences(storage, 'composition:15:variant:hard').write({ ...defaultStudioPreferences, speed: .9 });
  assert.equal(another.read().volume, 42);
  assert.equal(createStudioPreferences(storage, 'composition:15:variant:hard').read().speed, .9);
});
test('challenge result persistence is scoped to the signed-in account', () => {
  const entries = new Map();
  globalThis.localStorage = { getItem: key => entries.get(key) || null, setItem: (key,value) => entries.set(key,value) };
  try {
    setAccountScope(751);
    accountStorage.setItem('kuylab-studio-personal-v1', JSON.stringify(recordChallengeAnswer(structuredClone(emptyPersonal), study, ids, ids[0], true)));
    setAccountScope(752);
    assert.deepEqual(mapPersonal(JSON.parse(accountStorage.getItem('kuylab-studio-personal-v1'))).challengeResults, {});
    setAccountScope(751);
    assert.equal(mapPersonal(JSON.parse(accountStorage.getItem('kuylab-studio-personal-v1'))).challengeResults[challengeResultKey(study, ids[0])], 'correct');
  } finally { setAccountScope(null); }
});
