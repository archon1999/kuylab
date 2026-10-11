/* Local curated learning content only. Profile and activity APIs are never cached here. */
const shell = 'kuylab-shell-__REVISION__';
const piano = 'kuylab-piano-splendid-v2';
const development = shell === 'kuylab-shell-dev';
async function refreshShell() {
  const cache = await caches.open(shell);
  let complete = false;
  try {
    const response = await fetch('/offline-shell.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('Development shell');
    const paths = await response.json();
    if (!Array.isArray(paths) || !paths.includes('/index.html')) throw new Error('Invalid shell manifest');
    await cache.addAll(paths);
    if (paths.some(path => path.startsWith('/assets/'))) {
      await cache.put('/__shell_ready', new Response(JSON.stringify(paths)));
      complete = true;
    }
  } catch {
    // Production installs are atomic: an HTML-only shell cannot replace the last
    // usable version. Development has no built manifest; runtime modules are
    // cached separately and only that completed pass may mark it ready.
    if (development) {
      try { await cache.addAll(['/', '/index.html']); } catch { /* Preserve previous cached resources. */ }
    }
  }
  for (const client of await self.clients.matchAll()) client.postMessage({ type: 'offline-updated' });
  return complete;
}
self.addEventListener('install', event => {
  event.waitUntil(refreshShell().then(complete => {
    if (!complete && !development) throw new Error('Offline shell incomplete; keep the previous worker.');
    return self.skipWaiting();
  }));
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const complete = await (await caches.open(shell)).match('/__shell_ready');
    if (complete) for (const key of await caches.keys()) if (key.startsWith('kuylab-shell-') && key !== shell) await caches.delete(key);
    await self.clients.claim();
  })());
});
self.addEventListener('message', event => {
  if (event.data?.type === 'refresh-shell') event.waitUntil(refreshShell());
  if (event.data?.type === 'warm-runtime' && Array.isArray(event.data.paths)) event.waitUntil((async () => {
    const paths = event.data.paths.filter(path => { const url = new URL(path, self.location.origin); return url.origin === self.location.origin && !url.pathname.startsWith('/api/'); });
    if (!paths.length) return;
    try {
      const cache = await caches.open(shell);
      await cache.addAll(paths);
      const marker = await cache.match('/__shell_ready');
      let previous = [];
      try { previous = marker ? await marker.json() : []; } catch { /* Upgrade older markers. */ }
      const completePaths = [...new Set(['/index.html', ...previous, ...paths])];
      if (!(await Promise.all(completePaths.map(path => cache.match(path)))).every(Boolean)) return;
      await cache.put('/__shell_ready', new Response(JSON.stringify(completePaths)));
      for (const client of await self.clients.matchAll()) client.postMessage({ type: 'offline-updated' });
    } catch { /* The next online load can complete the cached app. */ }
  })());
});
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin || url.pathname.startsWith('/api/')) return;
  if (url.pathname.startsWith('/audio/')) {
    event.respondWith((async () => {
      const cache = await caches.open(piano);
      const cached = await cache.match(request, { ignoreSearch: true });
      if (cached) return cached;
      const response = await fetch(request);
      if (response.ok) await cache.put(request, response.clone());
      return response;
    })());
    return;
  }
  if (url.pathname === '/sw.js' || url.pathname === '/offline-shell.json') return;
  if (request.mode === 'navigate' || ['script', 'style', 'font', 'image'].includes(request.destination)) {
    event.respondWith((async () => {
      const cache = await caches.open(shell);
      try {
        const response = await fetch(request);
        if (response.ok) await cache.put(request.mode === 'navigate' ? '/index.html' : request, response.clone());
        return response;
      } catch (error) {
        const cached = await cache.match(request.mode === 'navigate' ? '/index.html' : request, { ignoreSearch: true });
        if (cached) return cached;
        throw error;
      }
    })());
  }
});
