import { pianoKeyLayout } from './studioTransport.ts';

export const maximumKeyboardZoom = 88 / 12;
const clamp = (value: number, low: number, high: number) => Math.max(low, Math.min(high, value));

/** Zero selects a readable, responsive default; manual zoom is shared across players. */
export function normalizeKeyboardZoom(value: unknown) {
  if (typeof value !== 'number' || !Number.isFinite(value) || value === 0) return 0;
  return clamp(value, 1, maximumKeyboardZoom);
}

export function normalizeVisibleKeys(value: unknown) {
  if (typeof value !== 'number' || !Number.isFinite(value) || value === 0) return 0;
  return Math.round(clamp(value, 12, 88));
}

export function keyboardRange(pitches: number[], focused: boolean) {
  const valid = pitches.filter((pitch) => Number.isInteger(pitch) && pitch >= 21 && pitch <= 108);
  return {
    low: focused ? Math.max(21, Math.floor((Math.min(60, ...valid) - 2) / 12) * 12) : 21,
    high: focused ? Math.min(108, Math.ceil((Math.max(72, ...valid) + 2) / 12) * 12 - 1) : 108,
    pitches: valid,
  };
}

export function keyboardViewport(
  width: number,
  requestedZoom: number,
  center: number | null,
  range: ReturnType<typeof keyboardRange>,
) {
  width = Number.isFinite(width) ? Math.max(1, width) : 1;
  const unitKeys = pianoKeyLayout(1, range.low, range.high);
  const whiteCount = unitKeys.filter((key) => key.white).length;
  const autoZoom = width <= 680 ? clamp((whiteCount * 23) / width, 1, maximumKeyboardZoom) : 1;
  const zoom = normalizeKeyboardZoom(requestedZoom) || autoZoom;
  const sourceKeys = unitKeys.filter((key) => range.pitches.includes(key.pitch));
  const openingCenter = sourceKeys.length
    ? (Math.min(...sourceKeys.map((key) => key.x)) +
        Math.max(...sourceKeys.map((key) => key.x + key.width))) /
      2
    : 0.5;
  const worldWidth = width * zoom;
  const offset = clamp(
    (center !== null && Number.isFinite(center) ? center : openingCenter) * worldWidth - width / 2,
    0,
    worldWidth - width,
  );
  return {
    width,
    worldWidth,
    zoom,
    offset,
    center: (offset + width / 2) / worldWidth,
    pan: worldWidth > width ? offset / (worldWidth - width) : 0.5,
    low: range.low,
    high: range.high,
  };
}

export type KeyboardViewport = ReturnType<typeof keyboardViewport>;

/** Keep the pitch beneath the pinch midpoint in place while fingers move apart. */
export function zoomKeyboardAt(
  view: KeyboardViewport,
  zoom: number,
  anchor: number,
  moved = anchor,
) {
  zoom = normalizeKeyboardZoom(zoom) || 1;
  const worldWidth = view.width * zoom;
  const point = (view.offset + anchor) / view.worldWidth;
  const offset = clamp(point * worldWidth - moved, 0, worldWidth - view.width);
  return { zoom, center: (offset + view.width / 2) / worldWidth };
}

export function panKeyboard(view: KeyboardViewport, distance: number) {
  const offset = clamp(view.offset + distance, 0, view.worldWidth - view.width);
  return (offset + view.width / 2) / view.worldWidth;
}
