import type { StudioAudioPort } from '../domain/contracts/studio-audio.port.ts';

export type LivePianoState = { pitches: number[]; loading: boolean; error: boolean };

/** Each input owns a key hold. Releasing a pending load must never play a late note. */
export function createLivePiano(audio: StudioAudioPort, changed: (state: LivePianoState) => void) {
  const inputs = new Map<string, number>();
  const voices = new Map<number, { release?: () => void; pending: boolean }>();
  const sustained = new Set<{ release?: () => void; pending: boolean }>();
  let pedalDown = false;
  let error = false;
  const publish = () =>
    changed({
      pitches: [...new Set(inputs.values())],
      loading: [...voices.values()].some((v) => v.pending),
      error,
    });
  const release = (input: string) => {
    const pitch = inputs.get(input);
    if (pitch === undefined) return;
    inputs.delete(input);
    if (![...inputs.values()].includes(pitch)) {
      const voice = voices.get(pitch);
      if (voice && pedalDown && !voice.pending) {
        sustained.add(voice);
        // Bound retained release handles even during very long pedal holds.
        if (sustained.size > 256) {
          const oldest = sustained.values().next().value!;
          oldest.release?.();
          sustained.delete(oldest);
        }
      } else voice?.release?.();
      voices.delete(pitch);
    }
    publish();
  };
  const press = async (input: string, pitch: number, velocity = 88) => {
    if (!Number.isInteger(pitch) || pitch < 21 || pitch > 108) return;
    if (inputs.get(input) === pitch) return;
    release(input);
    inputs.set(input, pitch);
    if (voices.has(pitch)) return;
    error = false;
    const voice: { release?: () => void; pending: boolean } = { pending: true };
    voices.set(pitch, voice);
    publish();
    try {
      await audio.prepare([pitch], undefined, [{ pitch, velocity }]);
      if (voices.get(pitch) !== voice) return;
      voice.pending = false;
      voice.release = audio.sound(pitch, audio.now(), 120, velocity) || undefined;
      publish();
    } catch {
      if (voices.get(pitch) !== voice) return;
      voices.delete(pitch);
      for (const [key, value] of inputs) if (value === pitch) inputs.delete(key);
      error = true;
      publish();
    }
  };
  const stop = () => {
    inputs.clear();
    voices.clear();
    sustained.clear();
    pedalDown = false;
    audio.stop();
    publish();
  };
  const pedal = (down: boolean) => {
    pedalDown = down;
    if (!down) {
      for (const voice of sustained) voice.release?.();
      sustained.clear();
    }
  };
  return { press, release, pedal, stop };
}
