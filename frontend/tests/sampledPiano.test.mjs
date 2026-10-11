import assert from 'node:assert/strict';
import test from 'node:test';
import {
  createSampledPiano,
  PIANO_SAMPLE_FILES,
} from '../src/modules/practice/data-access/adapters/sampled-piano.adapter.ts';

function fakeAudio() {
  const nodes = [],
    fetched = [],
    contexts = [];
  const parameter = () => ({
    value: 0,
    calls: [],
    setValueAtTime(...args) {
      this.calls.push(['set', ...args]);
    },
    linearRampToValueAtTime(...args) {
      this.calls.push(['ramp', ...args]);
    },
    setTargetAtTime(...args) {
      this.calls.push(['target', ...args]);
    },
    cancelAndHoldAtTime(...args) {
      this.calls.push(['hold', ...args]);
    },
  });
  const graph = (kind) => {
    const node = {
      kind,
      connections: [],
      gain: parameter(),
      connect(to) {
        this.connections.push(to);
      },
      disconnect() {
        this.disconnected = true;
      },
    };
    nodes.push(node);
    return node;
  };
  class Context {
    state = 'suspended';
    currentTime = 10;
    sampleRate = 2000;
    destination = {};
    audioWorklet = { addModule: async () => {} };
    constructor() {
      contexts.push(this);
    }
    async resume() {
      this.state = 'running';
    }
    async close() {
      this.state = 'closed';
    }
    createGain() {
      return graph('gain');
    }
    createConvolver() {
      return graph('convolver');
    }
    createBiquadFilter() {
      const node = graph('filter');
      node.frequency = parameter();
      node.Q = parameter();
      return node;
    }
    createDynamicsCompressor() {
      const node = graph('compressor');
      for (const name of ['threshold', 'knee', 'ratio', 'attack', 'release'])
        node[name] = parameter();
      return node;
    }
    createBuffer(channels, length) {
      const data = Array.from({ length: channels }, () => new Float32Array(length));
      return { getChannelData: (index) => data[index] };
    }
    async decodeAudioData() {
      const data = Float32Array.from({ length: 40000 }, (_, index) => 0.25 * Math.sin(index * 0.7));
      return { duration: 20, sampleRate: 2000, numberOfChannels: 2, getChannelData: () => data };
    }
    createBufferSource() {
      const node = graph('sample');
      node.playbackRate = parameter();
      node.start = (...args) => {
        node.started = args;
      };
      node.stop = (...args) => {
        node.stopped = args;
      };
      return node;
    }
  }
  const originalWorklet = globalThis.AudioWorkletNode;
  globalThis.AudioWorkletNode = class {
    constructor() { const node = graph('room'); node.port = {messages: [], postMessage(value) { this.messages.push(value); }, close() {this.closed = true;} }; return node; }
  };
  const originalAudio = globalThis.AudioContext,
    originalFetch = globalThis.fetch;
  globalThis.AudioContext = Context;
  globalThis.fetch = async (path) => {
    fetched.push(path);
    return { ok: true, arrayBuffer: async () => new ArrayBuffer(32) };
  };
  return {
    nodes,
    fetched,
    contexts,
    restore() {
      globalThis.AudioWorkletNode = originalWorklet;
      globalThis.AudioContext = originalAudio;
      globalThis.fetch = originalFetch;
    },
  };
}

test('recorded piano loads four local velocity layers at the nearest anchor, once', async () => {
  const environment = fakeAudio();
  try {
    const piano = createSampledPiano();
    await piano.prepare([60, 61, 60]);
    await piano.prepare([60]);
    assert.deepEqual(
      environment.fetched.sort(),
      [
        '/audio/splendid/pp-c3.ogg',
        '/audio/splendid/mp-c3.ogg',
        '/audio/splendid/mf-c3.ogg',
        '/audio/splendid/ff-c3.ogg',
      ].sort(),
    );
    piano.sound(61, 11, 2, 45);
    const source = environment.nodes.find((node) => node.kind === 'sample');
    assert.ok(source.buffer);
    assert.equal(source.playbackRate.value, 2 ** (1 / 12));
    assert.deepEqual(source.started, [11, 0]);
    assert.deepEqual(source.stopped, [13.5]);
    piano.close();
  } finally {
    environment.restore();
  }
});

test('seek resumes a sample at its decay offset and stop cancels all scheduled voices', async () => {
  const environment = fakeAudio();
  try {
    const piano = createSampledPiano();
    await piano.prepare([60]);
    piano.sound(60, 11, 4, 90, 2);
    piano.sound(60, 12, 1, 120);
    const sources = environment.nodes.filter((node) => node.kind === 'sample');
    assert.deepEqual(sources[0].started, [11, 2]);
    piano.stop();
    assert.ok(sources.every((source) => source.disconnected));
    assert.ok(sources.every((source) => source.stopped.length === 0));
    piano.close();
  } finally {
    environment.restore();
  }
});

test('volume zero and reverb zero change the actual audio graph, not just labels', async () => {
  const environment = fakeAudio();
  try {
    const piano = createSampledPiano();
    piano.volume(0);
    piano.reverb(0);
    await piano.prepare([60]);
    const gains = environment.nodes.filter((node) => node.kind === 'gain');
    assert.equal(gains[0].gain.value, 0);
    assert.equal(gains[4].gain.value, 10 ** (-1.71 / 20));
    assert.equal(gains[3].gain.value, 0);
    piano.volume(0.5);
    piano.reverb(0.8);
    assert.equal(gains[0].gain.calls.at(-1)[1], (50 / 127) ** 2);
    assert.equal(gains[3].gain.calls.at(-1)[1], 0.8);
    piano.close();
  } finally {
    environment.restore();
  }
});

test('a failed sample fetch remains retryable and cannot silently create a synthetic tone', async () => {
  const environment = fakeAudio();
  try {
    const piano = createSampledPiano();
    globalThis.fetch = async () => ({ ok: false });
    await assert.rejects(piano.prepare([60]));
    assert.equal(environment.nodes.filter((node) => node.kind === 'sample').length, 0);
    globalThis.fetch = async () => ({ ok: true, arrayBuffer: async () => new ArrayBuffer(20) });
    await piano.prepare([60]);
    piano.sound(60, 11, 1, 90);
    assert.equal(environment.nodes.filter((node) => node.kind === 'sample').length, 1);
    piano.close();
  } finally {
    environment.restore();
  }
});

test('the exported sample list covers exactly the local 88-key sampler bank', () => {
  assert.equal(PIANO_SAMPLE_FILES.length, 226);
  assert.equal(new Set(PIANO_SAMPLE_FILES).size, 226);
  assert.ok(PIANO_SAMPLE_FILES.includes('/audio/splendid/pp-b-1.ogg'));
  assert.ok(PIANO_SAMPLE_FILES.includes('/audio/splendid/mf-c7.ogg'));
});

test('note-off preserves the full held note then adds a half-second acoustic release', async () => {
  const environment = fakeAudio();
  try {
    const piano = createSampledPiano();
    await piano.prepare([60]);
    piano.sound(60, 11, 2, 80);
    const source = environment.nodes.find(node => node.kind === 'sample');
    assert.deepEqual(source.started, [11, 0]);
    assert.deepEqual(source.stopped, [13.5]);
    const envelope = source.connections[0].gain.calls;
    assert.deepEqual(envelope.at(-2), ['set', (80 / 127) ** 2, 13]);
    assert.deepEqual(envelope.at(-1), ['ramp', 0, 13.5]);
    piano.close();
  } finally { environment.restore(); }
});

test('expired samples are silent after a long seek rather than retriggering their final millisecond', async () => {
  const environment = fakeAudio();
  try {
    const piano = createSampledPiano();
    await piano.prepare([60]);
    piano.sound(60, 11, 2, 80, 25);
    piano.sound(60, 11, 2, 0);
    piano.sound(60, NaN, 2, 80);
    assert.equal(environment.nodes.filter((node) => node.kind === 'sample').length, 0);
    piano.close();
  } finally {
    environment.restore();
  }
});

test('pause fades an audible waveform briefly, cancels future attacks immediately and cleans every voice', async () => {
  const environment = fakeAudio();
  try {
    const piano = createSampledPiano();
    await piano.prepare([60]);
    piano.sound(60, 10, 2, 80);
    piano.sound(60, 12, 2, 80);
    environment.contexts[0].currentTime = 10.2;
    piano.stop();
    const sources = environment.nodes.filter((node) => node.kind === 'sample');
    assert.deepEqual(sources[0].stopped, [10.206]);
    assert.deepEqual(sources[1].stopped, []);
    assert.equal(sources[1].disconnected, true);
    await new Promise((resolve) => setTimeout(resolve, 30));
    assert.ok(sources.every((source) => source.disconnected));
    piano.close();
  } finally {
    environment.restore();
  }
});

test('Ivory-style dynamics preserve the dry path and use a stereo worklet send', async () => {
  const environment = fakeAudio();
  try {
    const piano = createSampledPiano();
    await piano.prepare([60]);
    const compressor = environment.nodes.find(node => node.kind === 'compressor');
    assert.equal(compressor.threshold.value, -3);
    assert.equal(compressor.ratio.value, 20);
    assert.equal(compressor.attack.value, 0.002);
    const room = environment.nodes.find(node => node.kind === 'room');
    const gains = environment.nodes.filter(node => node.kind === 'gain');
    assert.ok(gains[0].connections.includes(compressor));
    assert.ok(gains[0].connections.includes(gains[3]));
    assert.ok(gains[3].connections.includes(room));
    assert.ok(room.connections.includes(compressor));
    piano.sound(60, 11, 1, 25);
    const filter = environment.nodes.find(node => node.kind === 'filter');
    assert.equal(filter.frequency.value, 1000, 'PPP uses the reference warm low-pass zone');
    piano.stop();
    assert.ok(room.port.messages.includes('reset'));
    piano.close();
    assert.ok(room.port.messages.includes('dispose'));
    assert.equal(room.disconnected, true);
  } finally { environment.restore(); }
});

test('preload decodes only required velocity regions without resuming audio', async () => {
  const env = fakeAudio();
  try {
    const piano = createSampledPiano();
    const progress = [];
    await piano.preload([{pitch:60,velocity:75},{pitch:60,velocity:75}], value => progress.push(value));
    assert.equal(env.contexts[0].state,'suspended');
    assert.equal(env.fetched.length,1);
    assert.equal(progress.at(-1),1);
    await piano.prepare([60],undefined,[{pitch:60,velocity:75}]);
    assert.equal(env.contexts[0].state,'running');
    assert.equal(env.fetched.length,1);
    piano.close();
  } finally {env.restore();}
});
test('hand gains mute independently without changing sample velocity', async () => {
  const env = fakeAudio();
  try {
    const piano = createSampledPiano();
    piano.handVolume('left',0);
    await piano.prepare([60]);
    const gains = env.nodes.filter(node => node.kind === 'gain');
    assert.equal(gains[1].gain.value,0);
    assert.equal(gains[2].gain.value,1);
    piano.sound(60,10,.5,75,0,'left');
    piano.sound(60,10,.5,75,0,'right');
    const voices = env.nodes.filter(node => node.kind === 'gain').slice(-2);
    assert.equal(voices[0].connections[0],gains[1]);
    assert.equal(voices[1].connections[0],gains[2]);
    assert.deepEqual(voices[0].gain.calls,voices[1].gain.calls);
    piano.handVolume('right',.4);
    assert.equal(gains[2].gain.calls.at(-1)[1],.4);
    assert.equal(piano.outputTime(),10);
    piano.close();
  } finally {env.restore();}
});
