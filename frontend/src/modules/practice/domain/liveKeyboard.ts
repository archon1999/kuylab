import { pianoKeyLayout } from './studioTransport.ts';
import type { KeyboardViewport } from './keyboardViewport.ts';

export const pianoKeyboardHeight = (height: number) => Math.max(86, Math.min(152, height * 0.23));
export const pianoPitchName = (pitch: number) =>
  ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B'][pitch % 12] +
  (Math.floor(pitch / 12) - 1);

export function visiblePianoKeys(view: KeyboardViewport) {
  return pianoKeyLayout(view.worldWidth, view.low, view.high)
    .map((key) => ({ ...key, x: key.x - view.offset }))
    .filter((key) => key.x + key.width > 0 && key.x < view.width);
}
export function pianoPitchAt(view: KeyboardViewport, height: number, x: number, y: number) {
  if (x < 0 || x >= view.width || y < 0 || y >= height) return null;
  const keys = visiblePianoKeys(view);
  const black =
    y < height * 0.66 && keys.find((key) => !key.white && x >= key.x && x < key.x + key.width);
  return (
    (black || keys.find((key) => key.white && x >= key.x && x < key.x + key.width))?.pitch ?? null
  );
}
const computerKeys = [
  'KeyA',
  'KeyW',
  'KeyS',
  'KeyE',
  'KeyD',
  'KeyF',
  'KeyT',
  'KeyG',
  'KeyY',
  'KeyH',
  'KeyU',
  'KeyJ',
  'KeyK',
  'KeyO',
  'KeyL',
  'KeyP',
  'Semicolon',
];
export function computerPianoPitch(code: string, base = 60) {
  const index = computerKeys.indexOf(code);
  return index < 0 ? null : base + index;
}
