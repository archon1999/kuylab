import assert from 'node:assert/strict';
import test from 'node:test';
import {
  mapProfileSnapshot,
  profilePayload,
} from '../src/modules/profile/data-access/mappers/profile.mapper.ts';
import { mapStudioCatalog } from '../src/modules/studio/data-access/mappers/studio.mapper.ts';
import { mapPersonal } from '../src/modules/activity/data-access/mappers/activity.mapper.ts';
import { mapSession } from '../src/modules/practice/data-access/mappers/session.mapper.ts';

test('profile mapping keeps legacy API field names out of profile edits and round-trips preferences', () => {
  const profile = mapProfileSnapshot({
    display_name: 'Naz ar',
    instrument_model: 'Yamaha YDP-145',
    keys: 88,
    level: 'intermediate',
    practice_minutes: 35,
    goal: 'Still',
    language: 'ru',
    theme: 'dark',
  });
  assert.equal(profile.keyboard_keys, 88);
  assert.equal(profile.daily_minutes, 35);
  assert.equal(profile.goals, 'Still');
  assert.equal(profile.language, 'ru');
  assert.equal(profile.theme, 'dark');
  assert.deepEqual(profilePayload(profile), {
    display_name: 'Naz ar',
    instrument_model: 'Yamaha YDP-145',
    keys: 88,
    level: 'intermediate',
    practice_minutes: 35,
    goal: 'Still',
  });
});

test('catalog mapping preserves all lesson stages and their original source timing without sharing mutable cached arrays', () => {
  const lesson = {
    id: 'lesson:still:left',
    kind: 'lesson',
    title: 'Chap qo‘l',
    subtitle: 'Tayanch',
    category: 'coordination',
    goals: ['left-hand'],
    level: 'easy',
    minutes: 5,
    score_id: 100,
    intro: 'Sekin boshlang.',
    explanation: [{ title: 'Tayanch', text: 'Tovushni eshiting.' }],
    steps: [{ title: '1', instruction: 'Chaling.' }],
    source: { start_seconds: 16, end_seconds: 32, transformation: 'left' },
    stages: [
      {
        id: 'left:stage:1',
        score_id: 100,
        title: 'Oson',
        instruction: 'Tayanchlar',
        source_speed_percent: 60,
      },
      {
        id: 'left:stage:2',
        score_id: 101,
        title: 'Ulash',
        instruction: 'Birlashtiring',
        source_speed_percent: 80,
      },
      {
        id: 'left:stage:3',
        score_id: 102,
        title: 'Original',
        instruction: 'To‘liq',
        source_speed_percent: 100,
      },
    ],
  };
  const dto = {
    revision: 'v2',
    compositions: [
      {
        id: 8,
        slug: 'still',
        title: 'Still',
        subtitle: 'Winter Sonata',
        composer: '',
        score_id: 2,
        duration_seconds: 214.604,
        lesson_ids: [lesson.id],
      },
    ],
    lessons: [lesson],
    exercises: [],
    theory: [],
    categories: [],
    goals: [],
  };
  const catalog = mapStudioCatalog(dto);
  assert.deepEqual(catalog.lessons[0].stages, lesson.stages);
  assert.equal(catalog.compositions[0].duration_seconds, 214.604);
  assert.equal(catalog.lessons[0].source.start_seconds, 16);
  catalog.lessons[0].stages[0].score_id = 999;
  catalog.lessons[0].explanation[0].text = 'Changed';
  catalog.compositions[0].lesson_ids.push('other');
  assert.equal(dto.lessons[0].stages[0].score_id, 100);
  assert.equal(dto.lessons[0].explanation[0].text, 'Tovushni eshiting.');
  assert.equal(dto.compositions[0].lesson_ids.length, 1);
});

test('activity normalization preserves valid old positions while discarding corrupted local entries', () => {
  const state = mapPersonal({
    favorites: ['composition:8', '<invalid>'],
    recents: [
      { id: 'composition:8', openedAt: '2026-10-11T12:00:00Z' },
      { id: 'bad', openedAt: 'not-date' },
    ],
    positions: { 'composition:8': 62, negative: -1, missing: NaN },
  });
  assert.deepEqual(state.favorites, ['composition:8']);
  assert.equal(state.recents.length, 1);
  assert.deepEqual(state.positions, { 'composition:8': 62 });
});

test('legacy session mapping preserves seconds and only falls back to minutes when absent', () => {
  assert.equal(mapSession({ id: 2, composition: 8, minutes: 5, comfort: 4 }).duration_seconds, 300);
  assert.equal(
    mapSession({ id: 2, composition: 8, duration_seconds: 45, minutes: 5 }).duration_seconds,
    45,
  );
});
