import test from 'node:test';
import assert from 'node:assert/strict';
import { AudioFocus } from '../src/modules/practice/application/audioFocus.ts';
import { createStudioPreferences } from '../src/modules/practice/data-access/repository/studio-preferences.repository.impl.ts';
import { defaultStudioPreferences } from '../src/modules/practice/domain/studioPreferences.ts';
import { studyProgress } from '../src/modules/studio/domain/studio.logic.ts';
import { checkChallenge } from '../src/modules/studio/domain/theoryChallenges.ts';
import { parseRoute,routePath } from '../src/shared/routing/paths.ts';
import { setAccountScope } from '../src/shared/lib/accountScope.ts';

test('leaving a player flushes scoped preferences immediately and never flushes them as another account', async t => {
  const previous = Object.getOwnPropertyDescriptor(globalThis, 'localStorage');
  const map = new Map();
  Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: {
    getItem: key => map.get(key) || null, setItem: (key, value) => map.set(key, value),
  } });
  t.after(() => {
    setAccountScope(null);
    if (previous) Object.defineProperty(globalThis, 'localStorage', previous);
    else delete globalThis.localStorage;
  });
  const calls = [];
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    calls.push({ url, options });
    return Response.json({});
  });
  setAccountScope(101);
  const preferences = createStudioPreferences(undefined, 'composition:8');
  preferences.write({ ...defaultStudioPreferences, speed: .7 });
  preferences.dispose();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, '/api/auth/player-preferences/?context=composition%3A8');
  assert.equal(JSON.parse(calls[0].options.body).speed, .7);
  preferences.write({ ...defaultStudioPreferences, speed: .8 });
  setAccountScope(102);
  preferences.dispose();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(calls.length, 1);
  assert.equal(createStudioPreferences(undefined, 'composition:8').read().speed, 1);
});

test('a new audition pauses the old player; a stale owner cannot release the new one',()=>{
  const focus=new AudioFocus(), a=Symbol(), b=Symbol(), c=Symbol(); let old=0,current=0;
  focus.claim(a,()=>old++);focus.claim(b,()=>current++);assert.equal(old,1);
  focus.release(a);focus.claim(c,()=>{});assert.equal(current,1);
  focus.release(c);focus.claim(a,()=>old++);assert.equal(old,1);
});
test('each composition and lesson stage restores its own player state and inherits only the global default',()=>{
  const map=new Map();const storage={getItem:key=>map.get(key)||null,setItem:(key,value)=>map.set(key,value)};
  createStudioPreferences(storage).write({...defaultStudioPreferences,volume:45});
  createStudioPreferences(storage,'composition:8').write({...defaultStudioPreferences,speed:.7,left:false});
  createStudioPreferences(storage,'lesson:still:opening-listen:stage:1').write({...defaultStudioPreferences,speed:.9,right:false});
  assert.equal(createStudioPreferences(storage,'composition:8').read().speed,.7);
  assert.equal(createStudioPreferences(storage,'composition:8').read().left,false);
  assert.equal(createStudioPreferences(storage,'lesson:still:opening-listen:stage:1').read().right,false);
  assert.equal(createStudioPreferences(storage,'theory:triads').read().volume,45);
  assert.equal(createStudioPreferences(storage,'theory:triads').read().speed,1);
});
test('stage progress preserves the old lesson report without declaring unpractised stages mastered',()=>{
  const item={id:'lesson:one',stages:[{id:'stage:1'},{id:'stage:2'},{id:'stage:3'}]};
  assert.deepEqual(studyProgress(item,{'lesson:one':'mastered'}),{state:'mastered',completed:0,total:3});
  assert.deepEqual(studyProgress(item,{'lesson:one':'mastered','stage:1':'mastered'}),{state:'learning',completed:1,total:3});
  assert.equal(studyProgress(item,{'stage:1':'mastered','stage:2':'struggling'}).state,'struggling');
  assert.equal(studyProgress(item,{'stage:1':'mastered','stage:2':'mastered','stage:3':'mastered'}).state,'mastered');
});
test('keyboard checks accept a chord in any click order and require the intended octave',()=>{
  const task={mode:'keyboard',answerPitches:[60,64,67]};
  assert.equal(checkChallenge(task,[67,60,64,64],null),true);
  assert.equal(checkChallenge(task,[60,64,79],null),false);
  assert.equal(checkChallenge(task,[],null),false);
  assert.equal(checkChallenge({mode:'choice',answerChoice:'0'},[],'0'),true);
});
test('timestamp note links survive a clean URL round trip and discard invalid seeks',()=>{
  for(const [page,params] of [['practice',{composition:8,at:112.5}],['study',{item:'lesson:still:opening-listen',stage:'lesson:still:opening-listen:stage:1',at:0}]]){
    const url=new URL(routePath(page,params),'https://kuylab.uz');const route=parseRoute(url.pathname,url.search);
    assert.equal(route.page,page);assert.equal(Number(route.params.get('at')),params.at);
  }
  for(const value of ['-5','Infinity','NaN','99999',''])assert.equal(parseRoute('/practice/8','?t='+value).params.has('at'),false);
});
