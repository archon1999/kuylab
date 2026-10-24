const contentCache = 'kuylab-content-v1';
const audioCache = 'kuylab-piano-splendid-v2';
const listeners = new Set<() => void>();
let warming: Promise<void> | null = null;
export const offlineChanged = () => {
  for (const listener of listeners) listener();
};
export function subscribeOffline(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}
export function cacheableContent(path: string) {
  return path === 'studio/catalog/' || /^scores\/\d+\/$/.test(path);
}
function cacheKey(path: string, language: string) {
  return new URL('/__kuylab_offline/' + language + '/' + path, location.origin).href;
}
export async function saveContent(path: string, language: string, value: unknown) {
  if (!cacheableContent(path) || !('caches' in globalThis)) return;
  try {
    const cache = await caches.open(contentCache);
    await cache.put(
      cacheKey(path, language),
      new Response(JSON.stringify(value), { headers: { 'Content-Type': 'application/json' } }),
    );
    offlineChanged();
    void warmPiano();
  } catch {
    /* Storage denied/full: no Offline ready claim is made. */
  }
}
export async function readContent<T>(path: string, language: string): Promise<T | undefined> {
  if (!cacheableContent(path) || !('caches' in globalThis)) return undefined;
  try {
    const response = await (await caches.open(contentCache)).match(cacheKey(path, language));
    return response ? ((await response.json()) as T) : undefined;
  } catch {
    return undefined;
  }
}
export async function warmPiano() {
  if (!('caches' in globalThis)) return;
  if (warming) return warming;
  warming = (async () => {
    try {
      const cache = await caches.open(audioCache);
      const response = await fetch('/audio/splendid/manifest.json');
      if (!response.ok) return;
      const manifest = (await response.clone().json()) as {
        files: { path: string; sha256: string }[];
      };
      if (!Array.isArray(manifest.files) || !manifest.files.length) return;
      await cache.put('/audio/splendid/manifest.json', response);
      const queue = [...manifest.files];
      const failed: string[] = [];
      const valid = async (source: Response, expected: string) => {
        if (!source.ok) return false;
        const bytes = await source.clone().arrayBuffer();
        const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))]
          .map((v) => v.toString(16).padStart(2, '0'))
          .join('');
        return Boolean(expected) && hash === expected;
      };
      await Promise.all(
        Array.from({ length: 4 }, async () => {
          for (let file = queue.shift(); file; file = queue.shift()) {
            try {
              const cached = await cache.match(file.path);
              if (cached && (await valid(cached, file.sha256))) continue;
              if (cached) await cache.delete(file.path);
              const source = await fetch(file.path);
              if (!(await valid(source, file.sha256))) throw new Error('Sample integrity mismatch');
              await cache.put(file.path, source);
            } catch {
              await cache.delete(file.path);
              failed.push(file.path);
            }
          }
        }),
      );
      if (!failed.length)
        await cache.put(
          '/__piano_ready',
          new Response(JSON.stringify(manifest.files.map((file) => file.path))),
        );
      else await cache.delete('/__piano_ready');
      offlineChanged();
    } catch {
      /* A future successful content load retries incomplete samples. */
    }
  })().finally(() => {
    warming = null;
  });
  return warming;
}
export async function isOfflineReady(id: string | number | undefined, language: string) {
  if (id === undefined || !('caches' in globalThis) || !navigator.serviceWorker?.controller)
    return false;
  try {
    const score = await readContent('scores/' + id + '/', language);
    const catalog = await readContent('studio/catalog/', language);
    if (!score || !catalog) return false;
    const shells = (await caches.keys()).filter((key) => key.startsWith('kuylab-shell-'));
    const shellReady = await Promise.all(
      shells.map(async (key) => {
        const cache = await caches.open(key);
        const marker = await cache.match('/__shell_ready');
        if (!marker) return false;
        try {
          const paths = (await marker.json()) as string[];
          return (
            Array.isArray(paths) &&
            paths.includes('/studio.html') &&
            (await Promise.all(paths.map((path) => cache.match(path).then(Boolean)))).every(Boolean)
          );
        } catch {
          return false;
        }
      }),
    );
    if (!shellReady.some(Boolean)) return false;
    const audio = await caches.open(audioCache);
    const ready = await audio.match('/__piano_ready');
    if (!ready) return false;
    const paths = (await ready.json()) as string[];
    // Do not rely only on a marker if the browser evicts part of its storage.
    const present = await Promise.all(paths.map((path) => audio.match(path).then(Boolean)));
    return present.length > 0 && present.every(Boolean);
  } catch {
    return false;
  }
}
