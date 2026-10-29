import type {
  MidiConnectionPort,
  MidiConnectionState,
  MidiPerformanceEvent,
} from '../../domain/contracts/midi-connection.port.ts';

type Environment = {
  secure: boolean;
  request?: () => Promise<MIDIAccess>;
};

/** One explicitly selected input. Never request SysEx or write to a MIDI output. */
export function createWebMidiInput(environment?: Environment): MidiConnectionPort {
  const env = environment || {
    secure: globalThis.isSecureContext,
    request:
      typeof globalThis.navigator?.requestMIDIAccess === 'function'
        ? () => navigator.requestMIDIAccess({ sysex: false })
        : undefined,
  };
  let state: MidiConnectionState = {
    status: !env.secure ? 'insecure' : env.request ? 'idle' : 'unsupported',
    devices: [],
    selectedId: null,
  };
  let access: MIDIAccess | null = null;
  let input: MIDIInput | null = null;
  let generation = 0;
  let selected = false;
  let failedId: string | null = null;
  let receive: ((event: MidiPerformanceEvent) => void) | null = null;
  let notify: ((state: MidiConnectionState) => void) | null = null;
  const publish = (patch: Partial<MidiConnectionState>) => {
    state = { ...state, ...patch };
    notify?.(state);
  };
  const message = (event: MIDIMessageEvent) => {
    const data = event.data;
    if (!data || data.length < 3 || data[0] < 0x80 || data[0] >= 0xf0) return;
    const [status, number, value] = data;
    if (number > 127 || value > 127) return;
    const command = status & 0xf0;
    const channel = status & 0x0f;
    if (command === 0x90 || command === 0x80)
      receive?.({
        type: 'note',
        key: `${channel}:${number}`,
        pitch: number,
        velocity: value,
        down: command === 0x90 && value > 0,
      });
    else if (command === 0xb0) {
      if (number === 64) receive?.({ type: 'pedal', channel, value });
      else if (number === 120 || number === 123) receive?.({ type: 'reset', channel });
      else if (number === 121) receive?.({ type: 'pedal', channel, value: 0 });
    }
  };
  const detach = () => {
    if (!input) return;
    const previous = input;
    input = null;
    previous.removeEventListener('midimessage', message);
    receive?.({ type: 'reset' });
    void previous.close().catch(() => undefined);
  };
  const refresh = () => {
    if (!access) return;
    const available = [...access.inputs.values()].filter((port) => port.state === 'connected');
    const devices = available.map((port) => ({
      id: port.id,
      name: port.name || port.manufacturer || 'MIDI piano',
      manufacturer: port.manufacturer || '',
    }));
    let id = state.selectedId;
    if (!selected && !id && available.length === 1) {
      id = available[0].id;
      selected = true;
    }
    if (failedId && !available.some((port) => port.id === failedId)) failedId = null;
    const next = id === failedId ? null : available.find((port) => port.id === id) || null;
    if (input !== next) {
      detach();
      input = next;
      if (input) {
        input.addEventListener('midimessage', message);
        const port = input;
        void port.open().catch(() => {
          if (input === port) {
            failedId = port.id;
            detach();
            publish({ status: 'error' });
          }
        });
      }
    }
    publish({
      devices,
      selectedId: id,
      status:
        id && id === failedId
          ? 'error'
          : next
            ? 'connected'
            : id
              ? 'disconnected'
              : devices.length
                ? 'choosing'
                : 'waiting',
    });
  };
  return {
    initial: () => state,
    async connect(event, changed) {
      receive = event;
      notify = changed;
      if (!env.secure || !env.request) {
        publish({ status: !env.secure ? 'insecure' : 'unsupported' });
        return;
      }
      const ticket = ++generation;
      failedId = null;
      publish({ status: 'connecting' });
      try {
        const requested = access || (await env.request());
        if (ticket !== generation) return;
        if (!access) {
          access = requested;
          access.addEventListener('statechange', refresh);
        }
        refresh();
      } catch (error) {
        if (ticket !== generation) return;
        detach();
        const name = error instanceof Error ? error.name : '';
        publish({
          status: ['NotAllowedError', 'SecurityError'].includes(name) ? 'denied' : 'error',
        });
      }
    },
    select(id) {
      if (!access?.inputs.has(id)) return;
      selected = true;
      failedId = null;
      state = { ...state, selectedId: id };
      refresh();
    },
    disconnect() {
      generation++;
      access?.removeEventListener('statechange', refresh);
      detach();
      access = null;
      publish({
        devices: [],
        status: !env.secure ? 'insecure' : env.request ? 'idle' : 'unsupported',
      });
      receive = notify = null;
    },
  };
}
