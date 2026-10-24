import assert from 'node:assert/strict';
import test from 'node:test';
import vm from 'node:vm';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../scripts/studio-sw.js', import.meta.url), 'utf8');
function worker({ revision = 'new', fails = false, paths = ['/', '/studio.html', '/assets/app-new.js'], network = async () => new Response(JSON.stringify(paths)) } = {}) {
  const stores = new Map(), listeners = new Map();
  let skipped = false, claimed = false;
  const origin = 'https://piano.example';
  function key(input) { return new URL(typeof input === 'string' ? input : input.url, origin).href; }
  const caches = {
    async open(name) {
      if (!stores.has(name)) stores.set(name, new Map());
      const store = stores.get(name);
      return {
        async put(path, response) { store.set(key(path), response.clone()); },
        async match(path) { return store.get(key(path))?.clone(); },
        async addAll(paths) { if (fails) throw new Error('Offline during precache'); for (const path of paths) store.set(key(path), new Response(path)); },
      };
    },
    async keys() { return [...stores.keys()]; },
    async delete(name) { return stores.delete(name); },
  };
  const self = {
    location: { origin },
    addEventListener(name, listener) { listeners.set(name, listener); },
    async skipWaiting() { skipped = true; },
    clients: { async matchAll() { return []; }, async claim() { claimed = true; } },
  };
  vm.runInNewContext(source.replace('__REVISION__', revision), { self, caches, fetch: (...args) => network(...args), Response, URL });
  return {
    stores, caches,
    get skipped() { return skipped; }, get claimed() { return claimed; },
    async dispatch(type, data) { let promise; listeners.get(type)({ data, waitUntil(value) { promise = value; } }); return promise; },
    async navigate(path) { let promise; listeners.get('fetch')({ request: { url: origin + path, method: 'GET', mode: 'navigate' }, respondWith(value) { promise = value; } }); return promise; },
  };
}

test('an incomplete new shell cannot install, skip waiting, or remove the previous ready version', async () => {
  const w = worker({ fails: true });
  const previous = await w.caches.open('kuylab-shell-previous');
  await previous.put('/__shell_ready', new Response('ready'));
  await previous.put('/studio.html', new Response('working old HTML'));
  await previous.put('/assets/app-old.js', new Response('working old bundle'));
  await assert.rejects(w.dispatch('install'), /Offline shell incomplete/);
  assert.equal(w.skipped, false);
  assert.equal(w.claimed, false);
  assert.equal(await (await previous.match('/studio.html')).text(), 'working old HTML');
  assert.ok(await previous.match('/assets/app-old.js'));
  assert.ok(await previous.match('/__shell_ready'));
  assert.equal(await (await w.caches.open('kuylab-shell-new')).match('/__shell_ready'), undefined);
});

test('public page navigation cannot poison the app HTML used by an offline deep link', async () => {
  let offline = false;
  const w = worker({ network: async (request) => { if (offline) throw new Error('Offline'); return new Response(request.url.endsWith('/studio') ? 'private app' : 'public guide'); } });
  assert.equal(await (await w.navigate('/studio')).text(), 'private app');
  assert.equal(await (await w.navigate('/')).text(), 'public guide');
  assert.equal(await (await w.navigate('/musiqa-nazariyasi/')).text(), 'public guide');
  offline = true;
  assert.equal(await (await w.navigate('/practice/8')).text(), 'private app');
  assert.equal(await (await w.navigate('/')).text(), 'public guide');
  assert.equal(await (await w.navigate('/musiqa-nazariyasi/')).text(), 'public guide');
  await assert.rejects(w.navigate('/never-cached/'), /Offline/);
});

test('only a complete new shell activates and then retires the previous version', async () => {
  const w = worker();
  await (await w.caches.open('kuylab-shell-previous')).put('/__shell_ready', new Response('ready'));
  await w.caches.open('kuylab-content-v1');
  await w.caches.open('kuylab-piano-v1');
  await w.dispatch('install');
  assert.equal(w.skipped, true);
  const current = await w.caches.open('kuylab-shell-new');
  assert.deepEqual(await (await current.match('/__shell_ready')).json(), ['/', '/studio.html', '/assets/app-new.js']);
  assert.ok(await current.match('/assets/app-new.js'));
  await w.dispatch('activate');
  assert.equal(w.claimed, true);
  assert.equal(w.stores.has('kuylab-shell-previous'), false);
  assert.equal(w.stores.has('kuylab-content-v1'), true);
  assert.equal(w.stores.has('kuylab-piano-v1'), true);
});

test('HTML alone is never a complete production shell', async () => {
  const w = worker({ paths: ['/', '/studio.html'] });
  await assert.rejects(w.dispatch('install'), /Offline shell incomplete/);
  assert.equal(w.skipped, false);
  assert.equal(await (await w.caches.open('kuylab-shell-new')).match('/__shell_ready'), undefined);
});

test('development bootstrap keeps previous caches until runtime modules have been cached', async () => {
  const w = worker({ revision: 'dev', paths: ['/', '/studio.html'] });
  const old = await w.caches.open('kuylab-shell-previous');
  await old.put('/__shell_ready', new Response('ready'));
  await w.dispatch('install');
  await w.dispatch('activate');
  assert.equal(w.skipped, true);
  assert.equal(w.stores.has('kuylab-shell-previous'), true);
  assert.equal(await (await w.caches.open('kuylab-shell-dev')).match('/__shell_ready'), undefined);
  await w.dispatch('message', { type: 'warm-runtime', paths: ['https://piano.example/src/main.tsx'] });
  assert.ok(await (await w.caches.open('kuylab-shell-dev')).match('/__shell_ready'));
});
