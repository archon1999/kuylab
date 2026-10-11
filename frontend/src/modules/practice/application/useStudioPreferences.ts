import { useCallback, useRef, useState } from 'react';
import {
  normalizeStudioPreferences,
  type StudioPreferencePort,
  type StudioPreferences,
} from '../domain/studioPreferences';

export function useStudioPreferences(port: StudioPreferencePort) {
  const [preferences, setPreferences] = useState(() => port.read());
  const current = useRef(preferences);
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
