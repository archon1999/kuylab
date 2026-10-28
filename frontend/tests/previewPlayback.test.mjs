import assert from 'node:assert/strict';
import test from 'node:test';
import { PreviewPlayback } from '../src/modules/practice/application/previewPlayback.ts';
import { AudioFocus } from '../src/modules/practice/application/audioFocus.ts';
import { defaultStudioPreferences as defaults } from '../src/modules/practice/domain/studioPreferences.ts';

const note = (id, onset, duration, hand='right') => ({id,pitch:hand==='left'?48:72,hand,onset,duration,soundDuration:duration,velocity:83});
function fixture(t, notes=[note('a',0,1,'left'),note('b',.1,.5)], duration=2, focus=new AudioFocus()) {
  let now=10;
  const sounds=[], levels=[];
  const audio={now:()=>now,prepare:async()=>{},sound:(...args)=>sounds.push(args),
    volume:value=>levels.push(['volume',value]),reverb:value=>levels.push(['reverb',value]),
    handVolume:(hand,value)=>levels.push([hand,value]),stop(){this.stops++},close(){this.closes++},stops:0,closes:0};
  const states=[];
  const player=new PreviewPlayback(notes,duration,audio,s=>states.push(s),focus);
  t.after(()=>player.dispose());
  return {player,audio,sounds,levels,states,time:value=>now=value};
}

test('a preview stays silent until explicit play and loads only its source pitches/velocities',async t=>{
  const f=fixture(t);
  assert.equal(f.player.snapshot().playing,false); assert.equal(f.sounds.length,0);
  let requested;
  f.audio.prepare=async(pitches,_progress,notes)=>{requested={pitches,notes}};
  await f.player.toggle(defaults);
  assert.equal(f.player.snapshot().playing,true);
  assert.deepEqual(requested.pitches,[48,72]);
  assert.deepEqual(f.sounds.map(s=>[s[0],s[1],s[2],s[3],s[5]]),[[48,10,1,83,'left'],[72,10.1,.5,83,'right']]);
  assert.ok(f.levels.some(v=>v[0]==='volume'&&v[1]===.7));
});

test('pause/resume preserves position and resumes held samples without duplicate attacks',async t=>{
  const f=fixture(t,[note('held',0,2)],3);
  await f.player.toggle(defaults); f.time(10.7); f.player.pause();
  assert.ok(Math.abs(f.player.snapshot().position-.7)<1e-6);
  const before=f.sounds.length;
  f.time(30); await f.player.toggle(defaults);
  assert.equal(f.sounds.length,before+1);
  assert.ok(Math.abs(f.sounds.at(-1)[4]-.7)<1e-6);
  assert.ok(Math.abs(f.sounds.at(-1)[2]-1.3)<1e-6);
});

test('finishes once, stops tails at the excerpt boundary, and explicitly replays from zero',async t=>{
  const f=fixture(t,[note('long',0,10)],2);
  await f.player.toggle(defaults); assert.equal(f.sounds[0][2],2);
  f.time(12); f.player.tick();
  assert.equal(f.player.snapshot().playing,false); assert.equal(f.player.snapshot().finished,true);
  const count=f.sounds.length; f.time(50); f.player.tick(); assert.equal(f.sounds.length,count);
  await f.player.toggle(defaults);
  assert.equal(f.player.snapshot().position,0); assert.equal(f.player.snapshot().finished,false);
});

test('a second preview takes audio focus even while the first is preparing',async t=>{
  const focus=new AudioFocus(); const a=fixture(t,undefined,2,focus),b=fixture(t,undefined,2,focus);
  let ready; a.audio.prepare=()=>new Promise(resolve=>ready=resolve);
  const start=a.player.toggle(defaults); assert.equal(a.player.snapshot().loading,true);
  await b.player.toggle(defaults); ready(); await start;
  assert.equal(a.player.snapshot().playing,false); assert.equal(a.player.snapshot().loading,false);
  assert.equal(a.sounds.length,0); assert.equal(b.player.snapshot().playing,true);
});

test('cancel and unmount invalidate delayed audio preparation',async t=>{
  for(const action of ['pause','dispose']) {
    const f=fixture(t); let ready;
    f.audio.prepare=()=>new Promise(resolve=>ready=resolve);
    const start=f.player.toggle(defaults); f.player[action](); ready(); await start;
    assert.equal(f.sounds.length,0); assert.equal(f.player.snapshot().playing,false);
  }
});

test('audio errors remain paused and can be retried with the same source',async t=>{
  const f=fixture(t); f.audio.prepare=async()=>{throw new Error('offline')};
  await f.player.toggle(defaults); assert.equal(f.player.snapshot().error,true);
  assert.equal(f.player.snapshot().playing,false);
  f.audio.prepare=async()=>{}; await f.player.toggle(defaults);
  assert.equal(f.player.snapshot().playing,true); assert.equal(f.player.snapshot().error,false);
});

test('shared speed and hand levels apply without changing the musical excerpt',async t=>{
  const f=fixture(t,[note('a',0,1,'left'),note('b',1,1)],2);
  await f.player.toggle({...defaults,speed:2,leftVolume:25,rightVolume:80,volume:45,reverb:12});
  assert.equal(f.sounds[0][2],.5); assert.ok(f.levels.some(v=>v[0]==='left'&&v[1]===.25));
  f.time(10.4); f.player.settings({...defaults,speed:.5});
  assert.ok(Math.abs(f.player.snapshot().position-.8)<1e-6);
  assert.equal(f.player.snapshot().speed,.5);
});
