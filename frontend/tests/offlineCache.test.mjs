import assert from 'node:assert/strict';
import test from 'node:test';
import { createHash } from 'node:crypto';
import { warmPiano, isOfflineReady } from '../src/shared/offline/cache.ts';

test('piano warming repairs poisoned cache entries and never marks corrupt samples ready', async () => {
  const oldCaches = globalThis.caches, oldFetch = globalThis.fetch;
  const store = new Map();
  const path = '/audio/splendid/test.mp3';
  const bytes = 'known sampled piano bytes';
  const manifest = { files: [{ path, sha256: createHash('sha256').update(bytes).digest('hex') }] };
  const cache = {
    async match(key) { return store.get(key)?.clone(); },
    async put(key, value) { store.set(key, value.clone()); },
    async delete(key) { return store.delete(key); },
  };
  let corruptRemote = false, downloads = 0;
  globalThis.caches = { async open() { return cache; } };
  globalThis.fetch = async (url) => {
    if (url.endsWith('manifest.json')) return new Response(JSON.stringify(manifest));
    downloads++;
    const response = new Response(corruptRemote ? '<html>fallback page</html>' : bytes);
    // Model the service worker caching a successful response before integrity checks.
    await cache.put(url, response);
    return response;
  };
  try {
    await cache.put(path, new Response('old corrupt body'));
    await warmPiano();
    assert.equal(downloads, 1);
    assert.equal(await (await cache.match(path)).text(), bytes);
    assert.deepEqual(await (await cache.match('/__piano_ready')).json(), [path]);
    await warmPiano();
    assert.equal(downloads, 1, 'valid cached sample does not download again');

    corruptRemote = true;
    await cache.put(path, new Response('poisoned cached 200 response'));
    await warmPiano();
    assert.equal(await cache.match(path), undefined, 'failed body removed even when worker cached it');
    assert.equal(await cache.match('/__piano_ready'), undefined);
    await warmPiano();
    assert.equal(await cache.match('/__piano_ready'), undefined, 'retry cannot accept prior bad data');
    corruptRemote = false;
    await warmPiano();
    assert.ok(await cache.match('/__piano_ready'), 'connection recovery completes bank');
  } finally {
    globalThis.caches = oldCaches;
    globalThis.fetch = oldFetch;
  }
});

test('offline badge disappears when a required application bundle or sample is evicted', async () => {
  const original = Object.fromEntries(['caches','navigator','location'].map(key => [key, Object.getOwnPropertyDescriptor(globalThis,key)]));
  const stores = new Map();
  const origin = 'https://piano.example';
  const key = path => new URL(path, origin).href;
  const caches = {
    async keys() { return [...stores.keys()]; },
    async open(name) {
      if (!stores.has(name)) stores.set(name,new Map());
      const store = stores.get(name);
      return {
        async match(path) { return store.get(key(path))?.clone(); },
        async put(path,value) { store.set(key(path),value.clone()); },
        async delete(path) { store.delete(key(path)); },
      };
    },
  };
  Object.defineProperty(globalThis,'caches',{value:caches,configurable:true,writable:true});
  Object.defineProperty(globalThis,'navigator',{value:{serviceWorker:{controller:{}}},configurable:true});
  Object.defineProperty(globalThis,'location',{value:{origin},configurable:true});
  try {
    const content = await caches.open('kuylab-content-v1');
    await content.put('/__kuylab_offline/uz/scores/1/',new Response('{}'));
    await content.put('/__kuylab_offline/uz/studio/catalog/',new Response('{}'));
    const shell = await caches.open('kuylab-shell-test');
    await shell.put('/__shell_ready',new Response(JSON.stringify(['/index.html','/assets/app.js'])));
    await shell.put('/index.html',new Response('app'));
    await shell.put('/assets/app.js',new Response('bundle'));
    const audio = await caches.open('kuylab-piano-splendid-v2');
    await audio.put('/__piano_ready',new Response(JSON.stringify(['/audio/piano.mp3'])));
    await audio.put('/audio/piano.mp3',new Response('sample'));
    assert.equal(await isOfflineReady(1,'uz'),true);
    await shell.delete('/assets/app.js');
    assert.equal(await isOfflineReady(1,'uz'),false);
    await shell.put('/assets/app.js',new Response('bundle'));
    await audio.delete('/audio/piano.mp3');
    assert.equal(await isOfflineReady(1,'uz'),false);
    assert.equal(await isOfflineReady(1,'en'),false,'uncached language is not advertised');
  } finally {
    for (const [name,descriptor] of Object.entries(original)) {
      if (descriptor) Object.defineProperty(globalThis,name,descriptor);
      else delete globalThis[name];
    }
  }
});
