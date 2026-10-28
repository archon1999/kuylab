import test from 'node:test';
import assert from 'node:assert/strict';
import {
  keyboardRange,
  keyboardViewport,
  maximumKeyboardZoom,
  normalizeKeyboardZoom,
  normalizeVisibleKeys,
  panKeyboard,
  zoomKeyboardAt,
} from '../src/modules/practice/domain/keyboardViewport.ts';
import { pianoKeyLayout } from '../src/modules/practice/domain/studioTransport.ts';
import { normalizeStudioPreferences } from '../src/modules/practice/domain/studioPreferences.ts';

const range = keyboardRange([48, 60, 67, 84], false);

test('mobile opens readable keys while desktop retains a full keyboard by default', () => {
  const mobile = keyboardViewport(390, 0, null, range);
  assert.ok(mobile.worldWidth / 52 >= 23);
  assert.ok(mobile.zoom > 1 && mobile.zoom < 5);
  assert.equal(keyboardViewport(1280, 0, null, range).zoom, 1);
  assert.equal(keyboardViewport(390, 1, null, range).worldWidth, 390);
});

test('pan is bounded at both ends without changing the visible score range or source pitches', () => {
  const view = keyboardViewport(390, 3, 0.5, range);
  const left = keyboardViewport(390, 3, panKeyboard(view, -1e6), range);
  const right = keyboardViewport(390, 3, panKeyboard(view, 1e6), range);
  assert.equal(left.offset, 0);
  assert.equal(right.offset, right.worldWidth - right.width);
  assert.deepEqual(range.pitches, [48, 60, 67, 84]);
  assert.equal(left.low, right.low);
  assert.equal(left.high, right.high);
});

test('pinch zoom keeps the same piano position beneath a stationary or moving midpoint', () => {
  const view = keyboardViewport(390, 3, 0.55, range);
  for (const moved of [130, 165]) {
    const result = zoomKeyboardAt(view, 4, 130, moved);
    const after = keyboardViewport(390, result.zoom, result.center, range);
    assert.ok(
      Math.abs((view.offset + 130) / view.worldWidth - (after.offset + moved) / after.worldWidth) <
        1e-10,
    );
  }
});

test('panned black and white keys stay on the same pitch columns at every zoom', () => {
  for (const zoom of [1, 1.5, 3, 5]) {
    const view = keyboardViewport(390, zoom, 0.61, range);
    const keys = pianoKeyLayout(view.worldWidth, view.low, view.high);
    const key = keys.find((key) => key.pitch === 61);
    assert.equal(key.white, false);
    assert.ok(key.x - view.offset < keys.find((key) => key.pitch === 62).x - view.offset);
    assert.equal(keys.length, 88);
  }
});

test('focused ranges retain edge accidentals; empty or invalid data and zoom values stay finite', () => {
  const focused = keyboardRange([22, 107, -1, 999, NaN], true);
  assert.equal(focused.low, 21);
  assert.equal(focused.high, 108);
  for (const width of [0, -5, NaN, 390])
    for (const value of [0, 1, 5]) {
      const view = keyboardViewport(width, value, null, keyboardRange([], true));
      assert.ok(Number.isFinite(view.offset) && Number.isFinite(view.worldWidth));
    }
  assert.equal(normalizeKeyboardZoom(NaN), 0);
  assert.equal(normalizeKeyboardZoom('3'), 0);
  assert.equal(normalizeKeyboardZoom(-2), 1);
  assert.equal(normalizeKeyboardZoom(99), maximumKeyboardZoom);
  assert.equal(normalizeVisibleKeys(4), 12);
  assert.equal(normalizeVisibleKeys(100), 88);
  assert.equal(normalizeVisibleKeys(NaN), 0);
  assert.equal(normalizeStudioPreferences({ visibleKeys: 35.7 }).visibleKeys, 36);
  assert.equal(normalizeStudioPreferences({ keyboardZoom: 2 }).visibleKeys, 44);
});
