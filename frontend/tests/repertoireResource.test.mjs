import assert from 'node:assert/strict';
import test from 'node:test';
import { RepertoireResource } from '../src/modules/repertoire/application/RepertoireResource.ts';
import { hasMidiSource, validateCompositionInput } from '../src/modules/repertoire/domain/index.ts';
const deferred = () => {
  let resolve;
  const promise = new Promise((yes) => {
    resolve = yes;
  });
  return { promise, resolve };
};

test('a slow repertoire read cannot erase a composition successfully added while it was pending', async () => {
  const read = deferred();
  const model = new RepertoireResource({
    list: () => read.promise,
    add: async () => ({ id: 42, title: 'New piece' }),
  });
  const loading = model.reload();
  await model.add({ title: 'New piece' });
  read.resolve([{ id: 1, title: 'Stale list' }]);
  await loading;
  assert.ok(model.getSnapshot().compositions.some((item) => item.id === 42));
  assert.equal(model.getSnapshot().mode, 'online');
});

test('the newest locale read wins and quiet refresh failures retain the usable catalog with an error', async () => {
  const reads = [deferred(), deferred()];
  let index = 0,
    fail = false;
  const model = new RepertoireResource({
    list: () => {
      if (fail) throw new Error('offline');
      return reads[index++].promise;
    },
  });
  const old = model.reload(),
    current = model.reload(true);
  reads[1].resolve([{ id: 1, title: 'Русский' }]);
  await current;
  reads[0].resolve([{ id: 1, title: 'Uzbek' }]);
  await old;
  assert.equal(model.getSnapshot().compositions[0].title, 'Русский');
  fail = true;
  await model.reload(true);
  assert.equal(model.getSnapshot().mode, 'online');
  assert.ok(model.getSnapshot().error);
});

test('real uploaded MIDI can teach without a completeness claim; wishlist/PDF/XML cannot become MIDI lessons', () => {
  assert.equal(
    hasMidiSource({ arrangement: { active_score_id: 5, active_score_format: 'midi' } }),
    true,
  );
  assert.equal(hasMidiSource({ arrangement: { full_score_verified_at: 'today' } }), false);
  assert.equal(
    hasMidiSource({ arrangement: { active_score_id: 6, active_score_format: 'musicxml' } }),
    false,
  );
});

test('new composition input validates API limits and accepts only actual HTTP(S) source URLs', () => {
  const valid = {
    title: 'Winter Sonata',
    composer: '',
    source_url: 'https://example.com/piano.mid',
    arrangement_title: '',
  };
  assert.deepEqual(validateCompositionInput(valid), {});
  assert.equal(validateCompositionInput({ ...valid, title: ' ' }).title, 'required');
  assert.equal(
    validateCompositionInput({ ...valid, composer: 'A'.repeat(161) }).composer,
    'too_long',
  );
  assert.equal(
    validateCompositionInput({ ...valid, source_url: 'javascript:alert(1)' }).source_url,
    'url',
  );
});
