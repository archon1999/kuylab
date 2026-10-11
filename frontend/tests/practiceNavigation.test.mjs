import assert from 'node:assert/strict';
import test from 'node:test';

globalThis.location = new URL('http://localhost:5173/?page=lesson&composition=1&lesson=35');
globalThis.window = { addEventListener() {}, scrollTo() {} };
globalThis.history = {
  replaceState(_state,_title,path) { globalThis.location = new URL(path,location.origin); },
  pushState(_state, _title, path) {
    globalThis.location = new URL(path, location.origin);
  },
};
const { followPractice, openPractice } = await import('../src/shared/routing/index.ts');

test('legacy practice links canonicalize to the complete composition', () => {
  followPractice('/?page=practice&composition=1&score=1&start_seconds=3.6');
  assert.equal(location.pathname, '/practice/1');
  assert.equal(location.search, '');
});
test('whole-composition entry removes obsolete fragment selectors', () => {
  location.search = '?lesson=35&section=old&drill=2';
  openPractice(1);
  assert.equal(location.pathname, '/practice/1');
  assert.equal(location.search, '');
});

test('practice transfers cannot navigate to an external origin or another app page', () => {
  const before = location.href;
  followPractice('https://example.com/?page=practice&score=99');
  followPractice('/?page=settings&composition=9');
  followPractice('http://[');
  assert.equal(location.href, before);
});

test('reselecting the current page avoids duplicate browser history and a passage opens at the top', () => {
  let pushes = 0, scroll = null;
  const push = history.pushState;
  history.pushState = (...args) => { pushes++; push(...args); };
  window.scrollTo = value => { scroll = value; };
  openPractice(1);
  openPractice(1);
  assert.equal(pushes, 0);
  followPractice('/?page=practice&composition=1&start_seconds=3.6&end_seconds=7.2');
  assert.equal(pushes, 0);
  assert.equal(scroll.top, 0);
  assert.equal(scroll.behavior, 'instant');
  history.pushState = push;
});
