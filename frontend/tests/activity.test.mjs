import test from 'node:test';
import assert from 'node:assert/strict';
import { ActivityClock, activityStats, mergeVisits, tashkentDate } from '../src/modules/activity/domain/index.ts';
const base = Date.parse('2026-10-11T10:00:00Z');
const visit = () => ({id:'one', startedAt:new Date(base).toISOString(),seconds:0,contentSeconds:{},daySeconds:{}});
test('five-minute qualification includes the first five minutes and ignores shorter visits', () => {
  const clock = new ActivityClock(visit(),0);
  clock.advance(0,base,true,'composition:1');
  clock.advance(299000,base+299000,true,'composition:1');
  assert.equal(mergeVisits([clock.session]).length,0);
  clock.advance(300000,base+300000,true,'composition:1');
  assert.equal(activityStats([clock.session],base).totalSeconds,300);
  assert.equal(clock.session.contentSeconds['composition:1'],300);
});
test('hidden paused time is excluded; hidden playback is supplied as active', () => {
  const clock = new ActivityClock(visit(),0);
  clock.advance(0,base,true,null);
  clock.advance(120000,base+120000,false,null);
  clock.advance(300000,base+300000,true,'exercise:rhythm');
  clock.advance(480000,base+480000,true,'exercise:rhythm');
  assert.equal(clock.session.seconds,300);
  assert.equal(clock.session.contentSeconds['exercise:rhythm'],180);
});
test('duplicate and delayed cumulative sync cannot double or reduce the total', () => {
  const a = {...visit(), seconds:300, daySeconds:{'2026-10-11':300}};
  const b = {...a,seconds:350,daySeconds:{'2026-10-11':350}};
  assert.equal(activityStats(mergeVisits([b],[a],[b]),base).totalSeconds,350);
});
test('local midnight splits a qualified visit into correct Tashkent dates', () => {
  const start = Date.parse('2026-10-11T18:58:00Z');
  const clock = new ActivityClock({...visit(),startedAt:new Date(start).toISOString()},0);
  clock.advance(0,start,true,null);
  clock.advance(300000,start+300000,true,null);
  assert.deepEqual(clock.session.daySeconds,{'2026-10-11':120,'2026-10-12':180});
  assert.equal(tashkentDate(start+300000),'2026-10-12');
});
test('current-week statistics use Monday as the local week boundary', () => {
  const rows = [{...visit(),seconds:900,daySeconds:{'2026-10-04':300,'2026-10-05':300,'2026-10-11':300}}];
  assert.equal(activityStats(rows,base).weekSeconds,600);
  assert.equal(activityStats(rows,base).activeDays,3);
});
