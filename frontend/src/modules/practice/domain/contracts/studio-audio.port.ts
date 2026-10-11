export type StudioAudioPort = {
  prepare(
    pitches: number[],
    progress?: (fraction: number) => void,
    notes?: { pitch: number; velocity: number }[],
  ): Promise<void>;
  preload?(
    notes: { pitch: number; velocity: number }[],
    progress?: (fraction: number) => void,
  ): Promise<void>;
  handVolume?(hand: 'left' | 'right', value: number): void;
  now(): number;
  outputTime?(): number;
  sound(
    pitch: number,
    when: number,
    duration: number,
    velocity: number,
    offset?: number,
    hand?: 'left' | 'right',
  ): void;
  volume(value: number): void;
  reverb(value: number): void;
  stop(): void;
  close(): void;
};
