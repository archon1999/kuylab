import assert from 'node:assert/strict';
import test from 'node:test';
import { selectCompositionVariant, compositionPlaybackContext } from '../src/modules/studio/domain/studio.logic.ts';
import { mapStudioCatalog } from '../src/modules/studio/data-access/mappers/studio.mapper.ts';
import { parseRoute, routePath } from '../src/shared/routing/paths.ts';

const piece = {
  id: 8, default_variant_id: 'easy', score_id: 80, lesson_ids: ['lesson:all-in:chord-shapes'],
  variants: [{ id: 'easy', title: 'Easy', description: 'Simpler LH', score_id: 80, duration_seconds: 287.8 },
             { id: 'hard', title: 'Hard', description: 'Complete LH', score_id: 81, duration_seconds: 287.8 }],
};

test('explicit variant wins over remembered choice; defaults and foreign choices are safe', () => {
  assert.equal(selectCompositionVariant(piece, 'hard', 'easy').score_id, 81);
  assert.equal(selectCompositionVariant(piece, null, 'hard').score_id, 81);
  assert.equal(selectCompositionVariant(piece, 'removed', 'removed').score_id, 80);
  assert.equal(selectCompositionVariant({ ...piece, default_variant_id: 'removed' }).score_id, 80);
  assert.equal(selectCompositionVariant({ id: 1, score_id: 5 }), undefined);
  assert.equal(selectCompositionVariant(undefined, 'easy'), undefined);
});

test('playback settings and positions separate variants while old composition contexts stay stable', () => {
  assert.equal(compositionPlaybackContext(piece, 'easy'), 'composition:8:variant:easy');
  assert.equal(compositionPlaybackContext(piece, 'hard'), 'composition:8:variant:hard');
  assert.equal(compositionPlaybackContext({ id: 1, score_id: 5 }, 'hard'), 'composition:1');
  assert.equal(compositionPlaybackContext(piece, 'unknown'), 'composition:8');
});

test('clean variant deep links retain a precise timestamp, including browser back and refresh', () => {
  for (const variant of ['easy', 'hard']) {
    const url = routePath('practice', { composition: 8, variant, at: 67.040048 });
    const parsed = parseRoute(...url.split('?').map((v, i) => i ? '?' + v : v));
    assert.equal(url, `/practice/8/variants/${variant}?t=67.040048`);
    assert.equal(parsed.page, 'practice');
    assert.equal(parsed.params.get('variant'), variant);
    assert.equal(parsed.params.get('at'), '67.040048');
    assert.equal(routePath(parsed.page, parsed.params), url);
  }
  for (const path of ['/practice/8/variants', '/practice/8/variants/hard/extra', '/practice/8/other/hard'])
    assert.equal(parseRoute(path).page, 'notFound');
  assert.equal(routePath('practice', { composition: 1 }), '/practice/1');
  assert.equal(routePath('detail', { composition: 8, variant: 'hard' }), '/compositions/8');
});

test('catalog mapping clones variant metadata and keeps a single shared lesson list', () => {
  const dto = { revision: 'v9', compositions: [piece], lessons: [], exercises: [], theory: [], categories: [], goals: [] };
  const mapped = mapStudioCatalog(dto);
  assert.equal(mapped.compositions.length, 1);
  assert.deepEqual(mapped.compositions[0].variants, piece.variants);
  mapped.compositions[0].variants[0].title = 'Changed';
  mapped.compositions[0].lesson_ids.push('new');
  assert.equal(piece.variants[0].title, 'Easy');
  assert.equal(piece.lesson_ids.length, 1);
});
