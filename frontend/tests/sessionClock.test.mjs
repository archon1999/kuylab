import assert from 'node:assert/strict';
import test from 'node:test';
import { SessionClock, MAX_SESSION_SECONDS } from '../src/modules/practice/application/SessionClock.ts';
import { mergeSessionHistory } from '../src/modules/practice/application/SessionHistory.ts';

test('background throttling cannot turn ten minutes of practice into one timer tick', () => {
  let now = 0;
  const clock = new SessionClock(() => now);
  clock.start(); now = 600_000;
  assert.equal(clock.seconds(), 600);
});

test('paused time is excluded and subsecond practice survives pause/resume', () => {
  let now = 0;
  const clock = new SessionClock(() => now);
  clock.start(); now = 600; assert.equal(clock.pause(), 0);
  now = 100_000; assert.equal(clock.seconds(), 0);
  clock.start(); now += 600; assert.equal(clock.pause(), 1);
});

test('repeated starts do not restart the clock and reset starts a fresh interval', () => {
  let now = 0;
  const clock = new SessionClock(() => now);
  clock.start(); now = 5_000; clock.start(); now = 10_000;
  assert.equal(clock.seconds(), 10);
  clock.reset(); now += 2_000;
  assert.equal(clock.seconds(), 2);
  clock.pause(); clock.reset(); now += 10_000;
  assert.equal(clock.seconds(), 0);
});

test('a forgotten timer remains within the API four-hour limit', () => {
  let now = 0;
  const clock = new SessionClock(() => now);
  clock.start(); now = 24 * 60 * 60 * 1000;
  assert.equal(clock.seconds(), MAX_SESSION_SECONDS);
  assert.equal(clock.pause(), MAX_SESSION_SECONDS);
});

test('a delayed history response preserves a newly saved session and deduplicates its acknowledgement', () => {
  const old = { id: 1, duration_seconds: 60 };
  const saved = { id: 2, duration_seconds: 120 };
  assert.deepEqual(mergeSessionHistory([old], [saved]), [saved, old]);
  assert.deepEqual(mergeSessionHistory([saved, old], [saved]), [saved, old]);
  assert.deepEqual(mergeSessionHistory([old], []), [old]);
});
