import { useCallback, useEffect, useRef, useState } from 'react';
import type { StudioAudioPort } from '../domain/contracts/studio-audio.port';
import { audioFocus } from './audioFocus';
export type AuditionNote = { pitch: number; onset: number; duration: number; velocity: number };
export function useAudition(audio: StudioAudioPort) {
  const owner = useRef(Symbol('audition'));
  const generation = useRef(0);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);
  const stop = useCallback(() => {
    generation.current++;
    clearTimeout(timer.current);
    audio.stop();
    setBusy(false);
    audioFocus.release(owner.current);
  }, [audio]);
  useEffect(
    () => () => {
      generation.current++;
      clearTimeout(timer.current);
      audioFocus.release(owner.current);
      audio.close();
    },
    [audio],
  );
  const play = useCallback(
    async (notes: AuditionNote[]) => {
      if (!notes.length) return;
      stop();
      audioFocus.claim(owner.current, stop);
      const ticket = ++generation.current;
      setBusy(true);
      setError(false);
      try {
        await audio.prepare(
          notes.map((note) => note.pitch),
          undefined,
          notes,
        );
        if (ticket !== generation.current) return;
        audio.volume(0.7);
        audio.reverb(0.12);
        const start = audio.now() + 0.03;
        for (const note of notes)
          audio.sound(note.pitch, start + note.onset, note.duration, note.velocity);
        timer.current = setTimeout(
          () => {
            setBusy(false);
            audioFocus.release(owner.current);
          },
          (Math.max(...notes.map((note) => note.onset + note.duration)) + 0.6) * 1000,
        );
      } catch {
        if (ticket === generation.current) {
          setBusy(false);
          setError(true);
          audioFocus.release(owner.current);
        }
      }
    },
    [audio, stop],
  );
  return { play, stop, busy, error };
}
