import { accountId, accountStorage, scopedKey } from '../../../../shared/lib/accountScope.ts';
import { requestJson } from '../../../../shared/api/transport.ts';
import {
  normalizeStudioPreferences,
  type StudioPreferencePort,
} from '../../domain/studioPreferences.ts';

const key = 'kuylab-studio-player-preferences-v1';
const listeners = new Map<string, Set<() => void>>();
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
  const notificationKey = scopedKey(storageKey);
  const notify = () => listeners.get(notificationKey)?.forEach((listener) => listener());
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
    subscribe(listener) {
      const group = listeners.get(notificationKey) || new Set<() => void>();
      group.add(listener);
      listeners.set(notificationKey, group);
      const changed = (event: StorageEvent) => {
        if ((!event.key || event.key === notificationKey) && accountId() === owner) listener();
      };
      if (!storage && typeof window !== 'undefined') window.addEventListener('storage', changed);
      return () => {
        group.delete(listener);
        if (!group.size) listeners.delete(notificationKey);
        if (!storage && typeof window !== 'undefined')
          window.removeEventListener('storage', changed);
      };
    },
    async load() {
      const ticket = revision;
      if (storage) return read();
      try {
        await sync();
        const previous = getStorage().getItem(storageKey);
        const remote = await requestJson<Record<string, unknown>>(endpoint);
        if (
          ticket === revision &&
          accountId() === owner &&
          previous === getStorage().getItem(storageKey) &&
          !accountStorage.getItem(pendingKey) &&
          Object.keys(remote).length
        ) {
          getStorage().setItem(storageKey, JSON.stringify(normalizeStudioPreferences(remote)));
          notify();
        }
      } catch {
        /* Preserve this context's local settings until connectivity returns. */
      }
      return read();
    },
    write(value) {
      if (!storage && accountId() !== owner) return;
      revision++;
      try {
        const encoded = JSON.stringify(normalizeStudioPreferences(value));
        getStorage().setItem(storageKey, encoded);
        notify();
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
