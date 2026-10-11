import type { MidiInputPort, PlaybackAudioPort } from '../../domain/contracts/playback.ports.ts';

/** Browser IO lives here; constructing the adapter does not activate audio. */
export function createPlaybackAudio(): PlaybackAudioPort {
  let context: AudioContext | null = null;
  const voices = new Set<{ oscillator: OscillatorNode; gain: GainNode }>();

  function stop() {
    for (const voice of voices) {
      try {
        voice.oscillator.stop();
      } catch {
        /* A voice may already have ended. */
      }
      voice.oscillator.disconnect();
      voice.gain.disconnect();
    }
    voices.clear();
  }

  return {
    currentTime: () => context?.currentTime ?? 0,
    async resume() {
      if (!context || context.state === 'closed') {
        const constructor =
          globalThis.AudioContext ||
          (globalThis as typeof globalThis & { webkitAudioContext?: typeof AudioContext })
            .webkitAudioContext;
        if (!constructor) throw new Error('Brauzerda tovushni yoqib bo‘lmadi.');
        context = new constructor();
      }
      await context.resume();
    },
    sound(pitch, start, length, metronome = false) {
      if (
        !context ||
        context.state !== 'running' ||
        !Number.isFinite(pitch) ||
        !Number.isFinite(start) ||
        !Number.isFinite(length) ||
        length <= 0
      )
        return;
      if (metronome ? pitch <= 0 : pitch < 0 || pitch > 127) return;
      const end = start + length;
      const actualStart = Math.max(context.currentTime, start);
      if (end <= actualStart) return;
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      const voice = { oscillator, gain };
      voices.add(voice);
      oscillator.type = metronome ? 'sine' : 'triangle';
      oscillator.frequency.value = metronome ? pitch : 440 * 2 ** ((pitch - 69) / 12);
      const attackEnd = actualStart + Math.min(0.006, (end - actualStart) / 2);
      gain.gain.setValueAtTime(0.001, actualStart);
      gain.gain.linearRampToValueAtTime(metronome ? 0.04 : 0.08, attackEnd);
      gain.gain.exponentialRampToValueAtTime(0.001, end);
      oscillator.connect(gain);
      gain.connect(context.destination);
      oscillator.onended = () => {
        oscillator.disconnect();
        gain.disconnect();
        voices.delete(voice);
      };
      oscillator.start(actualStart);
      // The caller already capped this duration at its source boundary.
      // No release tail is scheduled beyond that boundary.
      oscillator.stop(end);
    },
    stop,
    async close() {
      stop();
      const previous = context;
      context = null;
      if (previous && previous.state !== 'closed') await previous.close();
    },
  };
}

/** Request access only from an explicit connect action; never request SysEx. */
export function createMidiInput(): MidiInputPort {
  let access: MIDIAccess | null = null;
  let generation = 0;
  let onNote: ((pitch: number, down: boolean, velocity: number) => void) | null = null;
  let onDevices: ((names: string[]) => void) | null = null;
  const inputs = new Map<
    MIDIInput,
    { handler: (event: MIDIMessageEvent) => void; held: Map<string, number> }
  >();

  function heldElsewhere(pitch: number) {
    return [...inputs.values()].some((input) => [...input.held.values()].includes(pitch));
  }

  function detach(input: MIDIInput) {
    const attached = inputs.get(input);
    if (!attached) return;
    if (input.onmidimessage === attached.handler) input.onmidimessage = null;
    inputs.delete(input);
    for (const pitch of new Set(attached.held.values()))
      if (!heldElsewhere(pitch)) onNote?.(pitch, false, 0);
    void input.close().catch(() => {
      /* Disconnected devices may already be closed. */
    });
  }

  function attach() {
    if (!access) return;
    const available = [...access.inputs.values()].filter((input) => input.state === 'connected');
    for (const input of inputs.keys()) if (!available.includes(input)) detach(input);
    for (const input of available)
      if (!inputs.has(input)) {
        const held = new Map<string, number>();
        const handler = (event: MIDIMessageEvent) => {
          if (!event.data || event.data.length < 3) return;
          const [status, pitch, velocity] = event.data;
          const command = status & 0xf0;
          if (command !== 0x90 && command !== 0x80) return;
          const key = `${status & 0x0f}:${pitch}`;
          const down = command === 0x90 && velocity > 0;
          if (down) {
            const mirroredVoice = heldElsewhere(pitch) && !held.has(key);
            held.set(key, pitch);
            if (!mirroredVoice) onNote?.(pitch, true, velocity);
          } else {
            held.delete(key);
            if (!heldElsewhere(pitch)) onNote?.(pitch, false, velocity);
          }
        };
        inputs.set(input, { handler, held });
        // Assigning onmidimessage opens a connected MIDIInput as specified by Web MIDI.
        input.onmidimessage = handler;
      }
    onDevices?.(available.map((input) => input.name || input.manufacturer || 'MIDI piano'));
  }

  return {
    async connect(noteCallback, deviceCallback) {
      const ticket = ++generation;
      if (!globalThis.navigator?.requestMIDIAccess)
        throw new Error('Chrome yoki Edge brauzeridan foydalaning.');
      onNote = noteCallback;
      onDevices = deviceCallback;
      const requested = access || (await navigator.requestMIDIAccess({ sysex: false }));
      if (ticket !== generation) return;
      if (!access) {
        access = requested;
        access.addEventListener('statechange', attach);
      }
      attach();
    },
    close() {
      generation++;
      if (access) access.removeEventListener('statechange', attach);
      for (const input of [...inputs.keys()]) detach(input);
      access = null;
      onNote = null;
      onDevices = null;
    },
  };
}
