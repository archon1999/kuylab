import assert from 'node:assert/strict';
import test from 'node:test';
import { createWebMidiInput } from '../src/modules/practice/data-access/adapters/web-midi.adapter.ts';
import { createMidiPiano } from '../src/modules/practice/application/midiPiano.ts';
import { collectKeyboardAnswer, checkChallenge } from '../src/modules/studio/domain/theoryChallenges.ts';

class Device extends EventTarget {
  constructor(id, name = 'Yamaha YDP-145') { super(); this.id = id; this.name = name; this.manufacturer = 'Yamaha'; this.state = 'connected'; this.opens = 0; this.closes = 0; }
  async open() { this.opens++; return this; }
  async close() { this.closes++; return this; }
  send(...data) { const event = new Event('midimessage'); event.data = Uint8Array.from(data); this.dispatchEvent(event); }
}
class Access extends EventTarget {
  constructor(devices = []) { super(); this.inputs = new Map(devices.map(d => [d.id, d])); }
  changed() { this.dispatchEvent(new Event('statechange')); }
}
function input(devices = [new Device('yamaha')]) {
  const access = new Access(devices), states = [], events = [];
  let requests = 0;
  const port = createWebMidiInput({ secure: true, request: async () => { requests++; return access; } });
  return { access, port, states, events, devices, get requests() { return requests; }, connect: () => port.connect(e => events.push(e), s => states.push(s)) };
}
test('MIDI permission is requested only by connect; zero-velocity Note On releases and all channels preserve velocity', async () => {
  const t = input(); assert.equal(t.requests, 0); assert.equal(t.port.initial().status, 'idle');
  await t.connect(); assert.equal(t.requests, 1); assert.equal(t.states.at(-1).status, 'connected');
  t.devices[0].send(0x92, 64, 108); t.devices[0].send(0x92, 64, 0);
  assert.deepEqual(t.events, [
    { type: 'note', key: '2:64', pitch: 64, velocity: 108, down: true },
    { type: 'note', key: '2:64', pitch: 64, velocity: 0, down: false },
  ]);
  await t.connect(); assert.equal(t.requests, 1);
  assert.equal(t.devices[0].opens, 1);
  t.port.disconnect();
});
test('multiple devices require selection; changing devices resets held notes and detaches old messages', async () => {
  const a = new Device('a'), b = new Device('b'); const t = input([a,b]); await t.connect();
  assert.equal(t.states.at(-1).status, 'choosing'); assert.equal(a.opens+b.opens,0);
  a.send(0x90,60,80); assert.equal(t.events.length,0);
  t.port.select('a'); a.send(0x90,60,80); assert.equal(t.events.at(-1).pitch,60);
  t.port.select('b'); assert.equal(t.events.at(-1).type,'reset');
  const count=t.events.length; a.send(0x90,62,80); assert.equal(t.events.length,count);
  b.send(0x90,64,80); assert.equal(t.events.at(-1).pitch,64);
  t.port.disconnect();
});
test('unplugging releases all notes; reconnecting the chosen piano restores it without selecting another input', async () => {
  const t=input(); await t.connect(); const d=t.devices[0];
  d.send(0x90,60,80); d.state='disconnected'; t.access.changed();
  assert.equal(t.events.at(-1).type,'reset'); assert.equal(t.states.at(-1).status,'disconnected');
  const other=new Device('other'); t.access.inputs.set(other.id,other); t.access.changed();
  assert.equal(t.states.at(-1).selectedId,'yamaha'); assert.equal(other.opens,0);
  d.state='connected'; t.access.changed(); assert.equal(t.states.at(-1).status,'connected');
  t.port.disconnect(); const count=t.events.length; d.send(0x90,60,90); t.access.changed(); assert.equal(t.events.length,count);
});
test('waiting for USB hotplug does not require a second permission prompt', async () => {
  const t=input([]); await t.connect(); assert.equal(t.states.at(-1).status,'waiting');
  const d=new Device('added'); t.access.inputs.set(d.id,d); t.access.changed();
  assert.equal(t.states.at(-1).status,'connected'); assert.equal(t.requests,1); t.port.disconnect();
});
test('pedal, all-notes-off and controller reset are decoded; irrelevant and malformed messages are ignored', async () => {
  const t=input(); await t.connect(); const d=t.devices[0];
  d.send(0xb1,64,127); d.send(0xb1,64,0); d.send(0xb1,123,0); d.send(0xb1,121,0); d.send(0xb1,120,0);
  assert.deepEqual(t.events,[{type:'pedal',channel:1,value:127},{type:'pedal',channel:1,value:0},{type:'reset',channel:1},{type:'pedal',channel:1,value:0},{type:'reset',channel:1}]);
  const count=t.events.length; for(const bytes of [[0x90,60],[0x90,255,60],[0xf0,60,60],[0xc0,0],[0xb0,7,80]]) d.send(...bytes);
  assert.equal(t.events.length,count); t.port.disconnect();
});
test('permission denial, unsupported and insecure environments produce recoverable states', async () => {
  for(const [env,expected] of [[{secure:false},'insecure'],[{secure:true},'unsupported'],[{secure:true,request:async()=>{throw new DOMException('no','NotAllowedError');}},'denied']]) {
    const port=createWebMidiInput(env), states=[];
    await port.connect(()=>{},s=>states.push(s)); assert.equal(states.at(-1).status,expected); port.disconnect();
  }
});
test('disconnecting during permission prompt invalidates its eventual result', async () => {
  let resolve; const access=new Access([new Device('late')]); const port=createWebMidiInput({secure:true,request:()=>new Promise(r=>resolve=r)});
  const states=[]; const operation=port.connect(()=>{},s=>states.push(s)); port.disconnect(); resolve(access); await operation;
  assert.equal(states.at(-1).status,'idle'); assert.equal(access.inputs.get('late').opens,0);
});
test('a port-open failure is reported and releases the selected device', async () => {
  const d=new Device('bad'); d.open=async()=>{throw new Error('busy');}; const t=input([d]); await t.connect(); await new Promise(r=>setImmediate(r));
  assert.equal(t.states.at(-1).status,'error'); assert.equal(t.events.at(-1).type,'reset'); t.port.disconnect();
});
test('state changes after a failed open never create an automatic open/close retry loop', async () => {
  const d=new Device('busy'),t=input([d]);
  d.open=async()=>{d.opens++;throw new Error('busy');};
  d.close=async()=>{d.closes++;t.access.changed();return d;};
  await t.connect();await new Promise(r=>setImmediate(r));
  t.access.changed();t.access.changed();
  assert.equal(d.opens,1);assert.equal(t.states.at(-1).status,'error');
  d.open=async()=>{d.opens++;return d;};await t.connect();assert.equal(d.opens,2);assert.equal(t.states.at(-1).status,'connected');t.port.disconnect();
});

function performance() {
  const t=input(); const states=[], played=[], released=[]; let prepares=0;
  const audio={prepare:async()=>{prepares++;},now:()=>1,sound:(pitch,when,duration,velocity)=>{played.push({pitch,velocity});return()=>released.push(pitch);},volume(){},reverb(){},stop(){released.push('all');},close(){}};
  const controller=createMidiPiano(t.port,audio,s=>states.push(s));
  return {...t,controller,states,played,released,get prepares(){return prepares;},send:(...bytes)=>t.devices[0].send(...bytes)};
}
const flush=()=>new Promise(r=>setImmediate(r));
test('instrument sound is the default: MIDI highlights actual keys without any browser sound or sample preparation', async () => {
  const t=performance(); await t.controller.connect(); t.send(0x90,60,117); t.send(0x90,64,35);
  assert.deepEqual(t.states.at(-1).pitches,[60,64]); assert.equal(t.played.length,0); assert.equal(t.prepares,0);
  t.send(0x80,60,0); assert.deepEqual(t.states.at(-1).pitches,[64]); t.controller.close();
});
test('browser sound preserves real velocity and pedal resonance without holding visual keys', async () => {
  const t=performance(); t.controller.setSound('browser'); await t.controller.connect();
  t.send(0xb0,64,127); t.send(0x90,60,112); await flush(); t.send(0x80,60,0);
  assert.deepEqual(t.played,[{pitch:60,velocity:112}]); assert.deepEqual(t.states.at(-1).pitches,[]); assert.equal(t.states.at(-1).pedal,true);
  assert.equal(t.released.includes(60),false);
  t.send(0x90,60,42); await flush(); assert.deepEqual(t.played.at(-1),{pitch:60,velocity:42});
  t.send(0xb0,64,0); assert.equal(t.released.filter(p=>p===60).length,1); assert.deepEqual(t.states.at(-1).pitches,[60]);
  t.send(0x80,60,0); assert.equal(t.released.filter(p=>p===60).length,2); t.controller.close();
});
test('source change, device disconnect and hidden tab silence voices, clear pedal and never leave a late note', async () => {
  const t=performance(); t.controller.setSound('browser'); await t.controller.connect(); t.send(0x90,60,80);
  t.controller.setSound('instrument'); await flush(); assert.deepEqual(t.states.at(-1).pitches,[]); assert.equal(t.played.length,0);
  t.send(0xb0,64,127); t.send(0x90,64,70); t.controller.setActive(false); assert.equal(t.states.at(-1).pedal,false);
  t.send(0x90,67,80); assert.deepEqual(t.states.at(-1).pitches,[]);
  t.controller.setActive(true); t.send(0x90,67,80); assert.deepEqual(t.states.at(-1).pitches,[67]);
  t.controller.disconnect(); assert.deepEqual(t.states.at(-1).pitches,[]); t.controller.close();
});
test('sequential and simultaneous MIDI notes collect a stable answer; repeats and release do not erase it or auto-grade', async () => {
  const t=performance(); let answer=[],checks=0;
  const unsubscribe=t.controller.subscribe(event=>{ if(event.type==='note' && event.down) answer=collectKeyboardAnswer(answer,event.pitch); });
  await t.controller.connect();
  for(const pitch of [60,64,67,64]) { t.send(0x90,pitch,78); t.send(0x80,pitch,0); }
  assert.deepEqual(answer,[60,64,67]); assert.equal(checks,0);
  checks++; assert.equal(checkChallenge({mode:'keyboard',answerPitches:[60,64,67]},answer,null),true);
  answer=[]; for(const pitch of [60,64,67]) t.send(0x90,pitch,80);
  assert.deepEqual(answer,[60,64,67]); for(const pitch of [60,64,67]) t.send(0x80,pitch,0);
  assert.deepEqual(answer,[60,64,67]); unsubscribe(); answer=[]; t.send(0x90,72,80); assert.deepEqual(answer,[]); t.controller.close();
});
