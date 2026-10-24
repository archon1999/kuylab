import { accountId, accountStorage } from '../../../../shared/lib/accountScope.ts';
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
export function createStudioPreferences(
  storage?: PreferenceStorage,
  contextId?: string,
): StudioPreferencePort {
  const getStorage = () => storage || accountStorage;
  const context = contextId && /^[a-zA-Z0-9:_-]{1,100}$/.test(contextId) ? contextId : undefined;
  const storageKey = context ? key + ':' + context : key;
  const pendingKey = 'player-preferences-pending' + (context ? ':' + context : '');
  const endpoint =
    'auth/player-preferences/' + (context ? '?context=' + encodeURIComponent(context) : '');
  const owner = accountId();
  let revision = 0;
  let pending: ReturnType<typeof setTimeout> | undefined;
  const sync = async () => {
    if (storage || accountId() !== owner) return;
    let value: string | null;
    try {
      value = accountStorage.getItem(pendingKey);
    } catch {
      return;
    }
    if (!value) return;
    await requestJson(endpoint, 'PATCH', JSON.parse(value))
      .then(() => {
        if (accountId() === owner && accountStorage.getItem(pendingKey) === value)
          accountStorage.setItem(pendingKey, '');
      })
      .catch(() => undefined);
  };
  const read = () => {
    try {
      return normalizeStudioPreferences(
        JSON.parse(getStorage().getItem(storageKey) || getStorage().getItem(key) || 'null'),
      );
    } catch {
      return normalizeStudioPreferences(null);
    }
  };
  return {
    read,
    async load() {
      const ticket = revision;
      if (storage) return read();
      try {
        await sync();
        const remote = await requestJson<Record<string, unknown>>(endpoint);
        if (
          ticket === revision &&
          accountId() === owner &&
          !accountStorage.getItem(pendingKey) &&
          Object.keys(remote).length
        )
          getStorage().setItem(storageKey, JSON.stringify(normalizeStudioPreferences(remote)));
      } catch {
        /* Preserve this context's local settings until connectivity returns. */
      }
      return read();
    },
    write(value) {
      revision++;
      try {
        const encoded = JSON.stringify(normalizeStudioPreferences(value));
        getStorage().setItem(storageKey, encoded);
        if (!storage) {
          accountStorage.setItem(pendingKey, encoded);
          clearTimeout(pending);
          pending = setTimeout(sync, 500);
        }
      } catch {
        /* Current page preferences still work if the browser disallows storage. */
      }
    },
    dispose() {
      clearTimeout(pending);
      void sync();
    },
  };
}
