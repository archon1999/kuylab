export type MidiDevice = { id: string; name: string; manufacturer: string };
export type MidiConnectionStatus =
  | 'idle'
  | 'connecting'
  | 'choosing'
  | 'connected'
  | 'waiting'
  | 'disconnected'
  | 'denied'
  | 'unsupported'
  | 'insecure'
  | 'error';
export type MidiConnectionState = {
  status: MidiConnectionStatus;
  devices: MidiDevice[];
  selectedId: string | null;
};
export type MidiPerformanceEvent =
  | { type: 'note'; key: string; pitch: number; velocity: number; down: boolean }
  | { type: 'pedal'; channel: number; value: number }
  | { type: 'reset'; channel?: number };
export type MidiConnectionPort = {
  initial(): MidiConnectionState;
  connect(
    event: (event: MidiPerformanceEvent) => void,
    changed: (state: MidiConnectionState) => void,
  ): Promise<void>;
  select(id: string): void;
  disconnect(): void;
};
