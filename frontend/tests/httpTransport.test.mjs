import assert from 'node:assert/strict';
import test from 'node:test';
import { requestJson } from '../src/shared/api/transport.ts';

test('successful JSON reads pass language and empty responses support writes', async t => {
  const calls = [];
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    calls.push({ url, options });
    return options.method === 'DELETE'
      ? new Response(null, { status: 204 })
      : Response.json({ id: 1 });
  });
  assert.deepEqual(await requestJson('scores/1/', 'GET', undefined, 'ru'), { id: 1 });
  assert.equal(calls[0].url, '/api/scores/1/');
  assert.equal(calls[0].options.headers['Accept-Language'], 'ru');
  assert.equal(calls[0].options.headers['Content-Type'], undefined);
  assert.equal(await requestJson('section/1/', 'DELETE'), undefined);
});

test('multipart upload leaves its boundary to fetch and does not JSON-stringify bytes', async t => {
  const body = new FormData();
  body.append('file', new Blob(['MThd']), 'piano.mid');
  t.mock.method(globalThis, 'fetch', async (_url, options) => {
    assert.equal(options.body, body);
    assert.equal(options.headers['Content-Type'], undefined);
    return Response.json({ id: 2 });
  });
  assert.deepEqual(await requestJson('scores/', 'POST', body), { id: 2 });
});

test('nested validation errors survive while non-JSON pages never become error text', async t => {
  t.mock.method(globalThis, 'fetch', async () => Response.json(
    { title: ['Required'], non_field_errors: ['Invalid source'] }, { status: 400 },
  ));
  await assert.rejects(requestJson('scores/', 'POST', {}), /title: Required Invalid source/);
  globalThis.fetch = async () => new Response('<html>debug data</html>', { status: 502 });
  await assert.rejects(requestJson('scores/'), { message: 'Server javobi noto‘g‘ri.' });
});

test('offline errors are actionable', async t => {
  t.mock.method(globalThis, 'fetch', async () => { throw new TypeError('Failed to fetch'); });
  await assert.rejects(requestJson('overview/'), /Server bilan bog‘lanib bo‘lmadi/);
});

test('stalled GET is aborted and a timed-out write is not automatically retried', async t => {
  let calls = 0;
  t.mock.method(globalThis, 'fetch', (_url, { signal }) => new Promise((_resolve, reject) => {
    calls++;
    signal.addEventListener('abort', () => reject(signal.reason));
  }));
  await assert.rejects(requestJson('overview/', 'GET', undefined, 'uz', 5), /uzoq davom etdi/);
  await assert.rejects(requestJson('sessions/', 'POST', {}, 'uz', 5), /Takror saqlashdan oldin/);
  assert.equal(calls, 2);
});

test('deadline also covers a body that stalls after response headers', async t => {
  t.mock.method(globalThis, 'fetch', async (_url, { signal }) => ({
    status: 200, ok: true,
    json: () => new Promise((_resolve, reject) => signal.addEventListener('abort', () => reject(signal.reason))),
  }));
  await assert.rejects(requestJson('scores/1/', 'GET', undefined, 'uz', 5), /uzoq davom etdi/);
});
