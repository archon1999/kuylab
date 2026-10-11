import { pianoToPreset } from 'smplr';
import type { StudioAudioPort } from '../../domain/contracts/studio-audio.port';

const preset = pianoToPreset({
  baseUrl: '/audio/splendid',
  detune: 0,
  decayTime: 0.5,
  formats: ['ogg'],
});
const pathFor = (sample: string) =>
  `/audio/splendid/${sample.toLowerCase().replaceAll(' ', '-').replaceAll('#', 's')}.ogg`;
export const PIANO_SAMPLE_FILES = [
  ...new Set(
    preset.groups.flatMap((group) => group.regions.map((region) => pathFor(region.sample))),
  ),
];
// A bounded decoded cache makes changing lesson stages inexpensive.
const decoded = new Map<string, AudioBuffer>();
let decodedBytes = 0;
const CACHE_LIMIT = 48 * 1024 * 1024;
function remember(key: string, buffer: AudioBuffer) {
  if (decoded.has(key)) return;
  const bytes = buffer.length * buffer.numberOfChannels * 4;
  if (!Number.isFinite(bytes) || bytes > CACHE_LIMIT) return;
  while (decodedBytes + bytes > CACHE_LIMIT && decoded.size) {
    const oldest = decoded.keys().next().value!;
    const old = decoded.get(oldest)!;
    decodedBytes -= old.length * old.numberOfChannels * 4;
    decoded.delete(oldest);
  }
  decoded.set(key, buffer);
  decodedBytes += bytes;
}
const RELEASE = 0.5;
const OUTPUT_GAIN = 10 ** (-1.71 / 20);
const midiGain = (value: number) => (Math.max(0, Math.min(127, value)) / 127) ** 2;
function regionFor(pitch: number, velocity: number) {
  const group = preset.groups.find(
    (group) => velocity >= group.velRange![0] && velocity <= group.velRange![1],
  )!;
  return {
    region: group.regions.find(
      (region) => pitch >= region.keyRange![0] && pitch <= region.keyRange![1],
    )!,
    cutoff: group.lpfCutoffHz,
  };
}
type Voice = {
  source: AudioBufferSourceNode;
  gain: GainNode;
  filter?: BiquadFilterNode;
  start: number;
  end: number;
  cleanupTimer?: ReturnType<typeof setTimeout>;
};
/** Also accepts native OfflineAudioContext for reproducible audio verification. */
export type PianoAudioContext = AudioContext | OfflineAudioContext;

/** Splendid Steinway recordings and Dattorro stereo room, as observed in Ivory.
 * Native scheduling retains KuyLab's seek offsets and explicit pause cleanup.
 */
export function createSampledPiano(
  createContext: () => PianoAudioContext = () => new AudioContext({ latencyHint: 'interactive' }),
): StudioAudioPort {
  let context: PianoAudioContext | null = null;
  let master: GainNode | null = null;
  const hands: Partial<Record<'left' | 'right', GainNode>> = {};
  const handLevels = { left: 1, right: 1 };
  let wet: GainNode | null = null;
  let output: GainNode | null = null;
  let compressor: DynamicsCompressorNode | null = null;
  let room: AudioWorkletNode | null = null;
  let roomReady: Promise<void> | null = null;
  let gainValue = 0.7,
    reverbValue = 0.25,
    closed = false;
  const buffers = new Map<string, AudioBuffer>();
  const loading = new Map<string, Promise<void>>();
  const voices = new Set<Voice>();
  const requests = new Set<AbortController>();

  function initialize() {
    if (context) return context;
    closed = false;
    const ctx = (context = createContext());
    master = ctx.createGain();
    for (const hand of ['left', 'right'] as const) {
      const node = (hands[hand] = ctx.createGain());
      node.gain.value = handLevels[hand];
      node.connect(master);
    }
    master.gain.value = midiGain(gainValue * 100);
    wet = ctx.createGain();
    wet.gain.value = reverbValue;
    compressor = ctx.createDynamicsCompressor();
    compressor.threshold.value = -3;
    compressor.knee.value = 0;
    compressor.ratio.value = 20;
    compressor.attack.value = 0.002;
    compressor.release.value = 0.2;
    output = ctx.createGain();
    output.gain.value = OUTPUT_GAIN;
    master.connect(compressor);
    // The room is post-volume, so muting also silences its input and output.
    master.connect(wet);
    compressor.connect(output);
    output.connect(ctx.destination);
    return ctx;
  }
  function prepareRoom(ctx: PianoAudioContext) {
    if (roomReady) return roomReady;
    roomReady = ctx.audioWorklet
      .addModule('/audio/dattorro.worklet.js')
      .then(() => {
        if (closed || context !== ctx) return;
        room = new AudioWorkletNode(ctx as AudioContext, 'DattorroReverb', {
          outputChannelCount: [2],
        });
        wet!.connect(room);
        room.connect(compressor!);
      })
      .catch((error) => {
        roomReady = null;
        throw error;
      });
    return roomReady;
  }
  async function load(sample: string, ctx: PianoAudioContext) {
    if (buffers.has(sample)) return;
    const cacheKey = `${ctx.sampleRate}:${sample}`;
    const cached = decoded.get(cacheKey);
    if (cached) {
      buffers.set(sample, cached);
      return;
    }
    if (loading.has(sample)) return loading.get(sample);
    const operation = (async () => {
      const abort = new AbortController();
      requests.add(abort);
      const timeout = setTimeout(() => abort.abort(), 30000);
      try {
        const response = await fetch(pathFor(sample), { signal: abort.signal });
        if (!response.ok) throw new Error('piano-sample');
        const bytes = await response.arrayBuffer();
        const buffer = await ctx.decodeAudioData(bytes).catch((cause: unknown) => {
          throw new Error(`piano-sample-decode: ${sample}`, { cause });
        });
        if (!closed && context === ctx) {
          buffers.set(sample, buffer);
          remember(cacheKey, buffer);
        }
      } finally {
        clearTimeout(timeout);
        requests.delete(abort);
      }
    })();
    loading.set(sample, operation);
    try {
      await operation;
    } finally {
      if (loading.get(sample) === operation) loading.delete(sample);
    }
  }
  function disposeVoice(voice: Voice) {
    if (voice.cleanupTimer) clearTimeout(voice.cleanupTimer);
    voice.source.onended = null;
    voice.source.disconnect();
    voice.gain.disconnect();
    voice.filter?.disconnect();
    voices.delete(voice);
  }
  function stop() {
    const now = context?.currentTime || 0;
    for (const voice of voices) {
      try {
        if (!closed && context?.state === 'running' && voice.start <= now && voice.end > now) {
          voice.gain.gain.cancelAndHoldAtTime(now);
          voice.gain.gain.linearRampToValueAtTime(0, now + 0.006);
          voice.source.stop(now + 0.006);
          if (voice.cleanupTimer) clearTimeout(voice.cleanupTimer);
          voice.cleanupTimer = setTimeout(() => disposeVoice(voice), 20);
          continue;
        }
        voice.source.stop();
      } catch {
        /* A naturally ended source is already stopped. */
      }
      disposeVoice(voice);
    }
    room?.port.postMessage('reset');
  }
  async function prepareSamples(
    pitches: number[],
    progress?: (fraction: number) => void,
    notes?: { pitch: number; velocity: number }[],
    resume = true,
  ) {
    const ctx = initialize();
    if (resume && 'close' in ctx) await ctx.resume();
    const samples = notes
      ? [
          ...new Set(
            notes
              .filter((n) => n.pitch >= 21 && n.pitch <= 108 && n.velocity > 0)
              .map(
                (n) =>
                  regionFor(n.pitch, Math.max(1, Math.min(127, Math.round(n.velocity)))).region
                    .sample,
              ),
          ),
        ]
      : [
          ...new Set(
            pitches
              .filter((pitch) => Number.isInteger(pitch) && pitch >= 21 && pitch <= 108)
              .flatMap((pitch) =>
                [30, 55, 75, 92, 115].map((velocity) => regionFor(pitch, velocity).region.sample),
              ),
          ),
        ];
    // Bounded decoding avoids a burst of hundreds of simultaneous requests.
    const queue = [...samples];
    let completed = 0;
    progress?.(0);
    await Promise.all([
      prepareRoom(ctx),
      ...Array.from({ length: 6 }, async () => {
        for (let sample = queue.shift(); sample; sample = queue.shift()) {
          await load(sample, ctx);
          progress?.(++completed / samples.length);
        }
      }),
    ]);
    if (closed || context !== ctx) throw new Error('piano-closed');
    if (resume && 'close' in ctx) await ctx.resume();
  }
  return {
    prepare: (pitches, progress, notes) => prepareSamples(pitches, progress, notes),
    preload: (notes, progress) => prepareSamples([], progress, notes, false),
    handVolume(hand, value) {
      if (!Number.isFinite(value)) return;
      handLevels[hand] = Math.max(0, Math.min(1, value));
      hands[hand]?.gain.setTargetAtTime(handLevels[hand], context!.currentTime, 0.015);
    },
    now: () => context?.currentTime || 0,
    outputTime() {
      if (!context) return 0;
      if ('getOutputTimestamp' in context && context.state === 'running') {
        const stamp = context.getOutputTimestamp();
        if (stamp.contextTime && stamp.performanceTime)
          return Math.max(
            0,
            Math.min(
              context.currentTime,
              stamp.contextTime + (performance.now() - stamp.performanceTime) / 1000,
            ),
          );
      }
      return Math.max(
        0,
        context.currentTime - ('outputLatency' in context ? context.outputLatency || 0 : 0),
      );
    },
    sound(pitch, when, duration, velocity, offset = 0, hand = 'right') {
      if (
        !context ||
        (context.state !== 'running' && 'close' in context) ||
        !master ||
        duration <= 0 ||
        ![pitch, when, duration, velocity, offset].every(Number.isFinite) ||
        !Number.isInteger(pitch) ||
        pitch < 21 ||
        pitch > 108 ||
        velocity <= 0
      )
        return;
      const { region, cutoff } = regionFor(pitch, Math.max(1, Math.min(127, Math.round(velocity))));
      const buffer = buffers.get(region.sample);
      if (!buffer) return;
      const rate = 2 ** ((pitch - region.pitch!) / 12);
      const start = Math.max(context.currentTime, when);
      const skipped = Math.max(0, context.currentTime - when);
      const sampleOffset = (Math.max(0, offset) + skipped) * rate;
      const noteOff = when + duration;
      if (sampleOffset >= buffer.duration || noteOff <= start) return;
      const end = Math.min(noteOff + RELEASE, start + (buffer.duration - sampleOffset) / rate);
      const source = context.createBufferSource();
      const gain = context.createGain();
      source.buffer = buffer;
      source.playbackRate.value = rate;
      const level = midiGain(velocity);
      const attackEnd = Math.min(start + (offset > 0 || skipped > 0 ? 0.008 : 0.001), noteOff);
      gain.gain.setValueAtTime(0, start);
      gain.gain.linearRampToValueAtTime(level, attackEnd);
      gain.gain.setValueAtTime(level, Math.max(attackEnd, Math.min(noteOff, end)));
      gain.gain.linearRampToValueAtTime(0, end);
      let filter: BiquadFilterNode | undefined;
      if (cutoff) {
        filter = context.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.value = cutoff;
        source.connect(filter);
        filter.connect(gain);
      } else source.connect(gain);
      gain.connect(hands[hand] || master);
      const voice: Voice = { source, gain, filter, start, end };
      voices.add(voice);
      source.onended = () => disposeVoice(voice);
      source.start(start, sampleOffset);
      source.stop(end);
    },
    volume(value) {
      if (!Number.isFinite(value)) return;
      gainValue = Math.max(0, Math.min(1, value));
      if (master && context)
        master.gain.setTargetAtTime(midiGain(gainValue * 100), context.currentTime, 0.015);
      // Clear a previously audible room tail on mute as well.
      if (gainValue === 0) room?.port.postMessage('reset');
    },
    reverb(value) {
      if (!Number.isFinite(value)) return;
      reverbValue = Math.max(0, Math.min(1, value));
      if (wet && context) wet.gain.setTargetAtTime(reverbValue, context.currentTime, 0.02);
      if (reverbValue === 0) room?.port.postMessage('reset');
    },
    stop,
    close() {
      closed = true;
      for (const request of requests) request.abort();
      stop();
      room?.port.postMessage('dispose');
      room?.port.close();
      for (const node of [master, wet, output, compressor, room, hands.left, hands.right])
        node?.disconnect();
      if (context && 'close' in context && context.state !== 'closed') void context.close();
      context = null;
      master = wet = output = null;
      compressor = null;
      room = null;
      roomReady = null;
      buffers.clear();
      loading.clear();
    },
  };
}
