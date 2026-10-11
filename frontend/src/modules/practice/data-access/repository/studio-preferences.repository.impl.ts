import { accountStorage } from '../../../../shared/lib/accountScope.ts';
import { requestJson } from '../../../../shared/api/transport.ts';
import {
  normalizeStudioPreferences,
  type StudioPreferencePort,
} from '../../domain/studioPreferences.ts';

const key = 'kuylab-studio-player-preferences-v1';
type PreferenceStorage = {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
};
/** Storage access stays behind a port, including the blocked-storage fallback. */
export function createStudioPreferences(storage?: PreferenceStorage): StudioPreferencePort {
  const getStorage = () => storage || accountStorage;
  let pending: ReturnType<typeof setTimeout> | undefined;
  const sync = () => {
    if (storage) return;
    let value: string | null;
    try {
      value = accountStorage.getItem('player-preferences-pending');
    } catch {
      return;
    }
    if (!value) return;
    void requestJson('auth/player-preferences/', 'PATCH', JSON.parse(value))
      .then(() => {
        if (accountStorage.getItem('player-preferences-pending') === value)
          accountStorage.setItem('player-preferences-pending', '');
      })
      .catch(() => undefined);
  };
  if (!storage) sync();
  return {
    read() {
      try {
        return normalizeStudioPreferences(JSON.parse(getStorage().getItem(key) || 'null'));
      } catch {
        return normalizeStudioPreferences(null);
      }
    },
    write(value) {
      try {
        const encoded = JSON.stringify(normalizeStudioPreferences(value));
        getStorage().setItem(key, encoded);
        if (!storage) {
          accountStorage.setItem('player-preferences-pending', encoded);
          clearTimeout(pending);
          pending = setTimeout(sync, 500);
        }
      } catch {
        /* Current page preferences still work if the browser disallows storage. */
      }
    },
  };
}
