export interface PlaybackAudioPort {
  currentTime(): number;
  resume(): Promise<void>;
  sound(pitch: number, start: number, length: number, metronome?: boolean): void;
  stop(): void;
  close(): Promise<void>;
}

export interface MidiInputPort {
  connect(
    onNote: (pitch: number, down: boolean, velocity: number) => void,
    onDevices: (names: string[]) => void,
  ): Promise<void>;
  close(): void;
}
