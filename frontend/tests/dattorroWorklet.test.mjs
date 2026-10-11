import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

function processor() {
  let Processor;
  const scope = {sampleRate:44100, Float32Array, Int16Array, AudioWorkletProcessor: class { port = {close() {}}; }, registerProcessor(_name, value) {Processor = value;}};
  vm.runInNewContext(readFileSync(new URL('../public/audio/dattorro.worklet.js', import.meta.url),'utf8'),scope);
  const instance = new Processor();
  const parameters = Object.fromEntries(Processor.parameterDescriptors.map(p=>[p.name,new Float32Array([p.defaultValue])]));
  const block = (impulse=false) => {
    const input = [new Float32Array(128),new Float32Array(128)];
    if (impulse) input[0][0]=input[1][0]=1;
    const output = [new Float32Array(128),new Float32Array(128)];
    const active = instance.process([input],[output],parameters);
    return {output,active};
  };
  return {instance,block};
}
test('Dattorro generates a finite stereo tail and reset removes all old energy', () => {
  const {instance,block} = processor();
  block(true);
  let energy=0, stereoDifference=0;
  for(let i=0;i<200;i++) {
    const {output}=block();
    for(let j=0;j<128;j++) {
      assert.ok(Number.isFinite(output[0][j]) && Number.isFinite(output[1][j]));
      energy+=output[0][j]**2+output[1][j]**2;
      stereoDifference+=Math.abs(output[0][j]-output[1][j]);
    }
  }
  assert.ok(energy>0 && stereoDifference>0);
  instance.port.onmessage({data:'reset'});
  for(let i=0;i<200;i++) assert.ok(block().output.every(channel=>channel.every(value=>value===0)));
  block(true);
  assert.equal(block().active,true,'reset leaves the room usable');
  instance.port.onmessage({data:'dispose'});
  assert.equal(block().active,false,'disposed worklet stops processing');
});
