import type { StudioPreferences, RollSettings } from './entities/studio-preferences.types.ts';
export type { StudioPreferences, RollSettings } from './entities/studio-preferences.types.ts';
export type { StudioPreferencePort } from './contracts/studio-preferences.repository.ts';

export const defaultStudioPreferences: Readonly<StudioPreferences> = {
  noteNames: true,
  keyNames: true,
  shadows: true,
  particles: true,
  velocityGradients: true,
  left: true,
  right: true,
  leftColor: '#bf6e95',
  rightColor: '#5f95ce',
  lookahead: 6,
  volume: 70,
  reverb: 25,
  speed: 1,
  leftVolume: 100,
  rightVolume: 100,
  countIn: 0,
  focusKeys: false,
  compactNoteLengths: true,
};

/** Persist only personal settings; score identity and position cannot leak into this record. */
export function normalizeStudioPreferences(value: unknown): StudioPreferences {
  const raw =
    value && typeof value === 'object' && !Array.isArray(value)
      ? (value as Record<string, unknown>)
      : {};
  const bool = (
    key:
      | 'noteNames'
      | 'keyNames'
      | 'shadows'
      | 'particles'
      | 'velocityGradients'
      | 'left'
      | 'right'
      | 'focusKeys'
      | 'compactNoteLengths',
  ) => (typeof raw[key] === 'boolean' ? raw[key] : defaultStudioPreferences[key]);
  const color = (key: 'leftColor' | 'rightColor') =>
    typeof raw[key] === 'string' && /^#[\da-f]{6}$/i.test(raw[key])
      ? raw[key].toLowerCase()
      : defaultStudioPreferences[key];
  const number = (
    key: 'lookahead' | 'volume' | 'reverb' | 'speed' | 'leftVolume' | 'rightVolume' | 'countIn',
    minimum: number,
    maximum: number,
    step: number,
  ) => {
    const current = raw[key];
    if (typeof current !== 'number' || !Number.isFinite(current))
      return defaultStudioPreferences[key];
    return Math.round(Math.max(minimum, Math.min(maximum, current)) / step) * step;
  };
  return {
    leftVolume: number('leftVolume', 0, 100, 1),
    rightVolume: number('rightVolume', 0, 100, 1),
    countIn: [2, 3].includes(Number(raw.countIn)) ? Number(raw.countIn) : 0,
    focusKeys: bool('focusKeys'),
    compactNoteLengths: bool('compactNoteLengths'),
    noteNames: bool('noteNames'),
    keyNames: bool('keyNames'),
    shadows: bool('shadows'),
    particles: bool('particles'),
    velocityGradients: bool('velocityGradients'),
    left: bool('left'),
    right: bool('right'),
    leftColor: color('leftColor'),
    rightColor: color('rightColor'),
    lookahead: number('lookahead', 2, 15, 1),
    volume: number('volume', 0, 100, 1),
    reverb: number('reverb', 0, 100, 1),
    speed: Number(number('speed', 0.2, 2, 0.05).toFixed(2)),
  };
}
