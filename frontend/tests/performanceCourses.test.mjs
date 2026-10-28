import assert from 'node:assert/strict';
import test from 'node:test';
import { studyMatchesPerformance, compositionPositionKeys, compositionResumePosition, selectCompositionVariant } from '../src/modules/studio/domain/studio.logic.ts';

const piece = {
  id: 10, playback_revision: 'primary-sha', default_variant_id: 'primary',
  variants: [
    { id: 'primary', playback_revision: 'primary-sha' },
    { id: 'alternative', playback_revision: 'alternative-sha' },
  ],
};
const lesson = { composition_id: 10, source: { start_seconds: 33, playback_revision: 'primary-sha', composition_variant_id: 'primary' } };

test('lessons and timeline markers follow only the reviewed recording', () => {
  assert.equal(studyMatchesPerformance(lesson, piece, 'primary'), true);
  assert.equal(studyMatchesPerformance(lesson, piece), true);
  assert.equal(studyMatchesPerformance(lesson, piece, 'alternative'), false);
  assert.equal(studyMatchesPerformance(lesson, { ...piece, id: 11 }, 'primary'), false);
  assert.equal(studyMatchesPerformance({ ...lesson, source: { ...lesson.source, playback_revision: 'retired' } }, piece, 'primary'), false);
  assert.equal(studyMatchesPerformance({ composition_id: 10 }, piece, 'primary'), false);
});

test('retained lesson editions and aligned package variants keep their existing courses', () => {
  const legacy = { id: 10, default_variant_id: 'original', variants: [{ id: 'original' }, { id: 'new', playback_revision: 'new-sha' }] };
  const originalLesson = { composition_id: 10, source: { start_seconds: 12 } };
  assert.equal(studyMatchesPerformance(originalLesson, legacy, 'original'), true);
  assert.equal(studyMatchesPerformance(originalLesson, legacy, 'new'), false);
  assert.equal(studyMatchesPerformance(originalLesson, { id: 10, variants: [{ id: 'easy' }, { id: 'hard' }] }, 'easy'), true);
  assert.equal(studyMatchesPerformance(originalLesson, { id: 10, variants: [{ id: 'easy' }, { id: 'hard' }] }, 'hard'), true);
  assert.equal(studyMatchesPerformance(originalLesson, { id: 10, playback_revision: 'replacement-sha' }), false);
});

test('lesson jump and dashboard resume use the exact source position, independently per recording', () => {
  const positions = { 'composition:10': 90, 'composition:10:source:alternative-sha': 55 };
  for (const key of compositionPositionKeys(piece, lesson.source.composition_variant_id)) positions[key] = lesson.source.start_seconds;
  assert.equal(positions['composition:10'], 90);
  assert.equal(positions['composition:10:source:alternative-sha'], 55);
  assert.equal(compositionResumePosition(piece, positions, 'primary'), 33);
  assert.equal(compositionResumePosition(piece, positions, 'alternative'), 55);
  const remembered = selectCompositionVariant(piece, null, 'alternative');
  assert.equal(compositionResumePosition(piece, positions, remembered.id), 55);
  assert.equal(compositionResumePosition(piece, { 'composition:10': 90 }, 'primary'), 0);
});
