import { useEffect, useState, useSyncExternalStore } from 'react';
import { usePreferences } from '@shared/i18n';
import { isOfflineReady, offlineChanged, subscribeOffline, warmPiano } from './cache';

export function useOfflineReady(scoreId?: number | string) {
  const { language } = usePreferences();
  const [ready, setReady] = useState(false);
  useEffect(() => {
    let disposed = false;
    const check = () =>
      void isOfflineReady(scoreId, language).then((value) => {
        if (!disposed) setReady(value);
      });
    setReady(false);
    check();
    const unsubscribe = subscribeOffline(check);
    navigator.serviceWorker?.addEventListener('controllerchange', check);
    return () => {
      disposed = true;
      unsubscribe();
      navigator.serviceWorker?.removeEventListener('controllerchange', check);
    };
  }, [scoreId, language]);
  return ready;
}
export function useOnlineStatus() {
  return useSyncExternalStore(
    (listener) => {
      window.addEventListener('online', listener);
      window.addEventListener('offline', listener);
      return () => {
        window.removeEventListener('online', listener);
        window.removeEventListener('offline', listener);
      };
    },
    () => navigator.onLine,
  );
}
export function registerOffline() {
  if (!('serviceWorker' in navigator)) return;
  void navigator.serviceWorker
    .register('/sw.js', { scope: '/' })
    .then((registration) => {
      const warm = () => {
        registration.active?.postMessage({ type: 'refresh-shell' });
        const paths = performance
          .getEntriesByType('resource')
          .map((entry) => new URL(entry.name))
          .filter(
            (url) =>
              url.origin === location.origin &&
              !url.pathname.startsWith('/api/') &&
              /\.(?:tsx?|jsx?|mjs|css|woff2?)(?:$|\?)/.test(url.pathname),
          )
          .map((url) => url.href);
        registration.active?.postMessage({ type: 'warm-runtime', paths });
        void warmPiano();
      };
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        offlineChanged();
        warm();
      });
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data?.type === 'offline-updated') offlineChanged();
      });
      window.addEventListener('online', warm);
      warm();
    })
    .catch(() => undefined);
}
