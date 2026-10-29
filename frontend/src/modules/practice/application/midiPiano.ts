import type {
  MidiConnectionPort,
  MidiConnectionState,
  MidiPerformanceEvent,
} from '../domain/contracts/midi-connection.port.ts';
import type { StudioAudioPort } from '../domain/contracts/studio-audio.port.ts';
import { createLivePiano } from './livePiano.ts';

export type MidiSound = 'instrument' | 'browser';
export type MidiPianoState = {
  connection: MidiConnectionState;
  pitches: number[];
  pedal: boolean;
  loading: boolean;
  audioError: boolean;
};
export const initialMidiPianoState = (port: MidiConnectionPort): MidiPianoState => ({
  connection: port.initial(),
  pitches: [],
  pedal: false,
  loading: false,
  audioError: false,
});

/** MIDI input is additive to playback: it must never claim exclusive audio focus. */
export function createMidiPiano(
  port: MidiConnectionPort,
  audio: StudioAudioPort,
  changed: (state: MidiPianoState) => void,
) {
  let state = initialMidiPianoState(port);
  let source: MidiSound = 'instrument';
  let active = true;
  let warming = 0;
  let preparing = false;
  let liveLoading = false;
  const held = new Map<string, number>();
  const pedals = new Map<number, boolean>();
  const listeners = new Set<(event: MidiPerformanceEvent) => void>();
  const publish = (patch: Partial<MidiPianoState> = {}) => {
    state = { ...state, ...patch };
    changed(state);
  };
  const piano = createLivePiano(audio, (value) => {
    liveLoading = value.loading;
    publish({ loading: preparing || liveLoading, audioError: value.error });
  });
  const reset = () => {
    held.clear();
    pedals.clear();
    piano.stop();
    publish({ pitches: [], pedal: false });
  };
  const receive = (event: MidiPerformanceEvent) => {
    if (event.type === 'reset') {
      if (event.channel === undefined) reset();
      else {
        for (const key of held.keys())
          if (key.startsWith(`${event.channel}:`)) {
            held.delete(key);
            piano.release(key);
          }
        pedals.delete(event.channel);
        const pedal = [...pedals.values()].some(Boolean);
        piano.pedal(pedal);
        publish({ pitches: [...new Set(held.values())], pedal });
      }
      return;
    }
    if (!active) return;
    if (event.type === 'note') {
      if (event.pitch < 21 || event.pitch > 108) return;
      if (event.down) {
        // Repeated Note On must restrike, but it is still one held physical key.
        if (held.has(event.key)) piano.release(event.key);
        held.set(event.key, event.pitch);
        if (source === 'browser') void piano.press(event.key, event.pitch, event.velocity);
      } else {
        held.delete(event.key);
        piano.release(event.key);
      }
      publish({ pitches: [...new Set(held.values())] });
    } else {
      pedals.set(event.channel, event.value >= 64);
      const pedal = [...pedals.values()].some(Boolean);
      if (source === 'browser') piano.pedal(pedal);
      publish({ pedal });
    }
    for (const listener of listeners) listener(event);
  };
  const warm = async () => {
    if (source !== 'browser') return;
    const ticket = ++warming;
    preparing = true;
    publish({ loading: true });
    try {
      // Resume in the connect/source click gesture before waiting for browser permission.
      await audio.prepare([], undefined, []);
      if (ticket !== warming) return;
      publish({ audioError: false });
      await audio.preload?.(
        Array.from({ length: 88 * 5 }, (_, i) => ({
          pitch: 21 + (i % 88),
          velocity: [30, 55, 75, 92, 115][Math.floor(i / 88)],
        })),
      );
    } catch {
      if (ticket === warming) publish({ audioError: true });
    } finally {
      if (ticket === warming) {
        preparing = false;
        publish({ loading: liveLoading });
      }
    }
  };
  return {
    connect() {
      void warm();
      return port.connect(receive, (connection) => publish({ connection }));
    },
    select(id: string) {
      port.select(id);
    },
    disconnect() {
      warming++;
      preparing = false;
      port.disconnect();
      reset();
    },
    setSound(value: MidiSound) {
      if (source === value) return;
      source = value;
      warming++;
      preparing = false;
      reset();
      if (state.connection.status === 'connected') void warm();
    },
    setLevels(volume: number, reverb: number) {
      audio.volume(volume / 100);
      audio.reverb(reverb / 100);
    },
    setActive(value: boolean) {
      active = value;
      if (!active) reset();
    },
    subscribe(listener: (event: MidiPerformanceEvent) => void) {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },
    stop: reset,
    close() {
      warming++;
      preparing = false;
      port.disconnect();
      reset();
      listeners.clear();
      audio.close();
    },
  };
}
