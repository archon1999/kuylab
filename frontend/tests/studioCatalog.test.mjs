import assert from 'node:assert/strict';
import test from 'node:test';
import { emptyFilter, filterStudyItems, durationLabel, selectStudyStage } from '../src/modules/studio/domain/index.ts';
import { formatStudioDate } from '../src/modules/studio/domain/dateLabels.ts';

const items = [
  { id: 'left-easy', title: 'Chap qo‘l ritmi', subtitle: 'Tayanchni saqlash', intro: 'Sekin va ravon', category: 'rhythm', goals: ['coordination'], level: 'easy' },
  { id: 'left-advanced', title: 'Chap qo‘l sakrashlari', subtitle: 'Aniq tushish', intro: 'Masofani his qiling', category: 'jumps', goals: ['accuracy'], level: 'advanced' },
  { id: 'right-easy', title: 'O‘ng qo‘l ritmi', subtitle: 'Puls', intro: 'Ritmni eshiting', category: 'rhythm', goals: ['coordination', 'accuracy'], level: 'easy' },
];
test('studio search combines user-selected goal, type, level, search and favorites', () => {
  const result = filterStudyItems(items, { ...emptyFilter, query: ' RITM ', category: 'rhythm', goal: 'accuracy', level: 'easy', favoritesOnly: true }, ['right-easy', 'left-advanced']);
  assert.deepEqual(result.map(item => item.id), ['right-easy']);
});
test('clearing studio filters restores the full curated catalog without mutating it', () => {
  const before = structuredClone(items);
  assert.equal(filterStudyItems(items, { ...emptyFilter, query: 'missing' }, []).length, 0);
  assert.deepEqual(filterStudyItems(items, emptyFilter, []), items);
  assert.deepEqual(items, before);
});
test('favorites can safely contain content removed from a prior catalog', () => {
  assert.deepEqual(filterStudyItems(items, { ...emptyFilter, favoritesOnly: true }, ['old-pirate']), []);
});
test('display duration preserves the actual source length and pads seconds', () => {
  assert.equal(durationLabel(214.604), '3:34');
  assert.equal(durationLabel(65), '1:05');
  assert.equal(durationLabel(-4), '0:00');
});
test('Uzbek recent-visit and chart dates use actual month and weekday names without Intl locale data', () => {
  const native = Date.prototype.toLocaleDateString;
  Date.prototype.toLocaleDateString = () => { throw new Error('Unavailable locale'); };
  try {
    assert.equal(formatStudioDate('2026-10-11T12:00:00', 'uz'), '11-oktabr');
    assert.equal(formatStudioDate('2026-09-14T12:00:00', 'uz'), '14-sentabr');
    assert.equal(formatStudioDate('2026-10-11T12:00:00', 'uz', true), 'Yak');
    assert.equal(formatStudioDate('2026-09-14T12:00:00', 'uz', true), 'Dush');
  } finally { Date.prototype.toLocaleDateString = native; }
});
test('English and Russian statistics preserve their native date formatting', () => {
  const input = '2026-10-11T12:00:00';
  for (const [language, locale] of [['en', 'en-GB'], ['ru', 'ru-RU']]) {
    assert.equal(formatStudioDate(input, language), new Date(input).toLocaleDateString(locale, { day: 'numeric', month: 'short' }));
    assert.equal(formatStudioDate(input, language, true), new Date(input).toLocaleDateString(locale, { weekday: 'short' }));
  }
});
test('invalid historical dates do not display fabricated month names', () => {
  assert.equal(formatStudioDate('bad-date', 'uz'), '—');
});
test('lesson links select their own stage and never inherit another lesson stage', () => {
  const lesson = { stages: [{ id: 'lesson:still:left:stage:1', score_id: 100 }, { id: 'lesson:still:left:stage:2', score_id: 101 }] };
  assert.equal(selectStudyStage(lesson, null).score_id, 100);
  assert.equal(selectStudyStage(lesson, 'lesson:still:left:stage:2').score_id, 101);
  assert.equal(selectStudyStage(lesson, 'lesson:still:right:stage:2').score_id, 100);
  assert.equal(selectStudyStage({ score_id: 80 }, null), undefined);
});
