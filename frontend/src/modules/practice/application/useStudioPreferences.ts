import { useCallback, useEffect, useRef, useState } from 'react';
import {
  normalizeStudioPreferences,
  type StudioPreferencePort,
  type StudioPreferences,
} from '../domain/studioPreferences';

export function useStudioPreferences(port: StudioPreferencePort, hydrateRemote = true) {
  const [preferences, setPreferences] = useState(() => port.read());
  const current = useRef(preferences);
  useEffect(() => {
    let live = true;
    const hydrate = () =>
      void port.load?.().then((value) => {
        if (live) {
          current.current = value;
          setPreferences(value);
        }
      });
    const initial = port.read();
    current.current = initial;
    setPreferences(initial);
    const unsubscribe = port.subscribe?.(() => {
      current.current = port.read();
      setPreferences(current.current);
    });
    if (hydrateRemote) hydrate();
    if (hydrateRemote) window.addEventListener('online', hydrate);
    return () => {
      live = false;
      window.removeEventListener('online', hydrate);
      unsubscribe?.();
      port.dispose?.();
    };
  }, [port, hydrateRemote]);
  const update = useCallback(
    <K extends keyof StudioPreferences>(key: K, value: StudioPreferences[K]) => {
      const next = normalizeStudioPreferences({ ...current.current, [key]: value });
      current.current = next;
      port.write(next);
      setPreferences(next);
      return next;
    },
    [port],
  );
  return { preferences, update };
}
