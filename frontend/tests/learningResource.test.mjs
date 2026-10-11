import assert from 'node:assert/strict';
import test from 'node:test';
import { CurriculumResource } from '../src/modules/learning/application/CurriculumResource.ts';
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => {
    resolve = yes;
    reject = no;
  });
  return { promise, resolve, reject };
};

test('out-of-order composition and language reads cannot replace the current course', async () => {
  const pending = [];
  const model = new CurriculumResource({
    curriculum: () => {
      const item = deferred();
      pending.push(item);
      return item.promise;
    },
  });
  const first = model.select(1, 'uz', true);
  const second = model.select(2, 'ru', true);
  pending[1].resolve({ composition_id: 2, language: 'ru' });
  await second;
  pending[0].resolve({ composition_id: 1, language: 'uz' });
  await first;
  assert.equal(model.getSnapshot().key, '2:ru:true');
  assert.equal(model.getSnapshot().data.composition_id, 2);
});

test('a failed read ends loading and a retry restores the actual course', async () => {
  let fail = true;
  const model = new CurriculumResource({
    curriculum: async () => {
      if (fail) throw new Error('offline');
      return { composition_id: 1 };
    },
  });
  await model.select(1, 'uz', true);
  assert.equal(model.getSnapshot().loading, false);
  assert.ok(model.getSnapshot().error);
  fail = false;
  await model.refresh('1:uz:true');
  assert.equal(model.getSnapshot().data.composition_id, 1);
  assert.equal(model.getSnapshot().error, '');
});

test('a saved result from an earlier locale refreshes the current locale, never the old selection', async () => {
  const ids = [];
  const model = new CurriculumResource({
    curriculum: async (id) => {
      ids.push(id);
      return { composition_id: id };
    },
  });
  await model.select(1, 'uz', true);
  await model.select(2, 'en', true);
  await model.refresh('1:uz:true');
  assert.deepEqual(ids, [1, 2, 2]);
  assert.equal(model.getSnapshot().key, '2:en:true');
  model.cancel();
  await model.refresh('2:en:true');
  assert.deepEqual(ids, [1, 2, 2]);
});

test('a no-MIDI selection cancels pending preparation without publishing phantom lessons', async () => {
  const pending = deferred();
  let calls = 0;
  const model = new CurriculumResource({
    curriculum: () => {
      calls++;
      return pending.promise;
    },
  });
  const old = model.select(1, 'uz', true);
  await model.select(2, 'uz', false);
  pending.resolve({ composition_id: 1 });
  await old;
  assert.equal(calls, 1);
  assert.equal(model.getSnapshot().data, null);
  assert.equal(model.getSnapshot().loading, false);
});
