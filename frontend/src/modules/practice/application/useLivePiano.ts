import { useEffect, useMemo, useRef, useState } from 'react';
import type { StudioAudioPort } from '../domain/contracts/studio-audio.port';
import type { StudioPreferences } from '../domain/studioPreferences';
import { createLivePiano, type LivePianoState } from './livePiano';
import { audioFocus } from './audioFocus';

export function useLivePiano(audio: StudioAudioPort, settings: StudioPreferences) {
  const [state, setState] = useState<LivePianoState>({ pitches: [], loading: false, error: false });
  const piano = useMemo(() => createLivePiano(audio, setState), [audio]);
  const owner = useRef(Symbol('live-piano'));
  useEffect(() => {
    audio.volume(settings.volume / 100);
    audio.reverb(settings.reverb / 100);
  }, [audio, settings.volume, settings.reverb]);
  useEffect(() => {
    // A single velocity layer across the range warms the small local sample set.
    void audio
      .preload?.(Array.from({ length: 88 }, (_, i) => ({ pitch: i + 21, velocity: 88 })))
      .catch(() => undefined);
    const stop = () => {
      piano.stop();
      audioFocus.release(owner.current);
    };
    const hidden = () => {
      if (document.hidden) stop();
    };
    window.addEventListener('blur', stop);
    document.addEventListener('visibilitychange', hidden);
    return () => {
      window.removeEventListener('blur', stop);
      document.removeEventListener('visibilitychange', hidden);
      stop();
      audio.close();
    };
  }, [audio, piano]);
  return {
    ...state,
    press(input: string, pitch: number) {
      audioFocus.claim(owner.current, piano.stop);
      void piano.press(input, pitch);
    },
    release: piano.release,
    stop: piano.stop,
  };
}
