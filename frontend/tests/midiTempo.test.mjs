import assert from 'node:assert/strict';
import test from 'node:test';
import {
  activeNotesAtQuarter,
  attacksInTempoWindow,
  audioTimelineNotes,
  clipTimeline,
  measureClickOffsets,
  normalizeTempoMap,
  playbackNoteTiming,
  quarterToSeconds,
  scaleTempoMap,
  secondsToQuarter,
  timeline,
  validateRequestedTempo,
} from '../src/modules/practice/domain/score.ts';
import {
  createMidiInput,
  createPlaybackAudio,
} from '../src/modules/practice/data-access/adapters/playback.adapter.ts';
import { createLatestScoreRequest } from '../src/modules/practice/application/latestScoreRequest.ts';
import { createTempoClock, playbackTimeLabel } from '../src/modules/practice/domain/score.ts';

const changingTempo = [
  { onset_quarters: 0, quarter_bpm: 120 },
  { onset_quarters: 4, quarter_bpm: 60 },
];
const close = (actual, expected) =>
  assert.ok(Math.abs(actual - expected) < 1e-8, `${actual} should equal ${expected}`);
function event(id, onset, duration, extra = {}) {
  return {
    id,
    part_id: 'T1',
    measure_index: Math.floor(onset / 4),
    measure_number: String(Math.floor(onset / 4) + 1),
    offset_quarters: onset % 4,
    onset_quarters: onset,
    duration_quarters: duration,
    pitch: { step: 'C', alter: 0, octave: 4, midi: 60 },
    staff: 1,
    voice: '1',
    hand: 'right',
    rest: false,
    chord: false,
    grace: false,
    ties: [],
    ...extra,
  };
}
function midiScore(events, extra = {}) {
  const total = extra.total_quarters ?? 8;
  return {
    id: 1,
    version: 1,
    title: 'fixture',
    file_format: 'midi',
    file_url: '/source.mid',
    musicxml_url: '',
    hand_overrides: extra.hand_overrides,
    parsed: {
      source_format: 'midi',
      metadata: { total_quarters: total, tempo: { quarter_bpm: 120 } },
      events,
      tempo_map: extra.tempo_map ?? changingTempo,
      playback_order: [0, 1, 0, 1],
      pedal_events: [
        { onset_quarters: 1, channel: 0, track_index: 1, controller: 64, value: 127, down: true },
      ],
      measures: [0, 1].map((index) => ({
        index,
        number: String(index + 1),
        start_quarters: index * 4,
        length_quarters: 4,
        time: null,
      })),
    },
  };
}

test('quarter seconds integration changes tempo at Q4 without changing quarter coordinates', () => {
  close(quarterToSeconds(0, changingTempo), 0);
  close(quarterToSeconds(3, changingTempo), 1.5);
  close(quarterToSeconds(4, changingTempo), 2);
  close(quarterToSeconds(5, changingTempo), 3);
  close(quarterToSeconds(8, changingTempo), 6);
});

test('compiled clocks preserve tempo boundaries and the same musical position at slower speed', () => {
  const native = createTempoClock(changingTempo);
  const slower = createTempoClock(scaleTempoMap(changingTempo, 60));
  for (const quarter of [0, 0.25, 3.9999, 4, 4.0001, 5, 17.25]) {
    close(native.quarterToSeconds(quarter), quarterToSeconds(quarter, changingTempo));
    close(native.secondsToQuarter(native.quarterToSeconds(quarter)), quarter);
  }
  const pausedQuarter = native.secondsToQuarter(3);
  close(pausedQuarter, 5);
  close(slower.quarterToSeconds(pausedQuarter), 6);
  close(slower.secondsToQuarter(6), pausedQuarter);
  const mutable = structuredClone(changingTempo);
  const snapshot = createTempoClock(mutable);
  mutable[0].quarter_bpm = 30;
  close(
    snapshot.quarterToSeconds(4),
    2,
    'Compiled clocks retain their own immutable tempo snapshot',
  );
  assert.equal(playbackTimeLabel(77.625), '01:17');
  assert.equal(playbackTimeLabel(3601), '60:01');
  assert.equal(playbackTimeLabel(NaN), '00:00');
});

test('an earlier score fetch cannot replace a newer source selection or surface its stale error', async () => {
  const scope = createLatestScoreRequest();
  const selected = [];
  let finishOld, finishNew;
  const older = scope
    .run(
      () =>
        new Promise((resolve) => {
          finishOld = resolve;
        }),
    )
    .then((score) => {
      if (score) selected.push(score.id);
    });
  const newer = scope
    .run(
      () =>
        new Promise((resolve) => {
          finishNew = resolve;
        }),
    )
    .then((score) => {
      if (score) selected.push(score.id);
    });
  finishNew({ id: 2 });
  await newer;
  finishOld({ id: 1 });
  await older;
  assert.deepEqual(selected, [2]);
  let rejectOld;
  const staleError = scope.run(
    () =>
      new Promise((_, reject) => {
        rejectOld = reject;
      }),
  );
  await scope.run(async () => ({ id: 3 }));
  rejectOld(new Error('old fetch failed'));
  assert.equal(await staleError, null);
  let finishUnmounted;
  const unmounted = scope.run(
    () =>
      new Promise((resolve) => {
        finishUnmounted = resolve;
      }),
  );
  scope.invalidate();
  finishUnmounted({ id: 4 });
  assert.equal(await unmounted, null);
  await assert.rejects(
    scope.run(async () => {
      throw new Error('current source failed');
    }),
    /current source failed/,
  );
});

test('metrical clicks use two large 6/8 pulses while MIDI tempo remains quarter based', () => {
  assert.deepEqual(measureClickOffsets({ beats: '6', beat_type: 8 }, 3), [0, 1.5]);
  assert.deepEqual(measureClickOffsets({ beats: '9', beat_type: 8 }, 4.5), [0, 1.5, 3]);
  assert.deepEqual(measureClickOffsets({ beats: '12', beat_type: 8 }, 6), [0, 1.5, 3, 4.5]);
  assert.deepEqual(measureClickOffsets({ beats: '3', beat_type: 4 }, 3), [0, 1, 2]);
  assert.deepEqual(measureClickOffsets({ beats: '3', beat_type: 8 }, 1.5), [0, 0.5, 1]);
  assert.deepEqual(measureClickOffsets({ beats: '2+3', beat_type: 8 }, 2.5), [0, 1]);
  assert.deepEqual(measureClickOffsets(null, 3), [0, 1, 2]);
  close(quarterToSeconds(1.5, [{ onset_quarters: 0, quarter_bpm: 200 }]), 0.45);
});

test('mid-window clips preserve meter phase and never click at or past their endpoint', () => {
  assert.deepEqual(measureClickOffsets({ beats: '6', beat_type: 8 }, 2, 0.5), [1]);
  assert.deepEqual(measureClickOffsets({ beats: '6', beat_type: 8 }, 0.75), [0]);
  assert.deepEqual(measureClickOffsets({ beats: '6', beat_type: 8 }, 1.5), [0]);
  const source = midiScore([event('a', 0, 1)]);
  source.parsed.measures[0].time = { beats: '4', beat_type: 4 };
  const clipped = clipTimeline(timeline(source, 0, 1, 'both'), 0.5, 3.5);
  assert.equal(clipped.occurrences[0].measure.meter_offset_quarters, 0.5);
  assert.deepEqual(
    measureClickOffsets(
      clipped.occurrences[0].measure.time,
      clipped.occurrences[0].measure.length_quarters,
      clipped.occurrences[0].measure.meter_offset_quarters,
    ),
    [0.5, 1.5, 2.5],
  );
});

test('inverse transport finds quarters on both sides and exactly at a tempo boundary', () => {
  for (const quarter of [0, 0.125, 3.9999, 4, 4.0001, 5, 8, 32.25])
    close(secondsToQuarter(quarterToSeconds(quarter, changingTempo), changingTempo), quarter);
  close(secondsToQuarter(2, changingTempo), 4);
  close(secondsToQuarter(3, changingTempo), 5);
});

test('missing MIDI tempo uses standard default120; duplicate onsets use last value without mutation', () => {
  close(quarterToSeconds(4, []), 2);
  const source = [
    { onset_quarters: 4, quarter_bpm: 60 },
    { onset_quarters: 0, quarter_bpm: 90 },
    { onset_quarters: 4, quarter_bpm: 30 },
  ];
  const before = structuredClone(source);
  assert.deepEqual(
    normalizeTempoMap(source).map((entry) => [entry.onset_quarters, entry.quarter_bpm]),
    [
      [0, 90],
      [4, 30],
    ],
  );
  close(quarterToSeconds(5, source), (4 * 60) / 90 + 2);
  assert.deepEqual(source, before);
  close(quarterToSeconds(4, [{ onset_quarters: 4, quarter_bpm: 60 }]), 2);
});

test('practice speed scales every tempo change by the same ratio', () => {
  const slower = scaleTempoMap(changingTempo, 60);
  assert.deepEqual(
    slower.map((entry) => entry.quarter_bpm),
    [60, 30],
  );
  close(quarterToSeconds(8, slower), 12);
  assert.equal(changingTempo[0].quarter_bpm, 120);
  assert.deepEqual(
    scaleTempoMap([{ onset_quarters: 0, quarter_bpm: 60 }], 120, 120).map(
      (entry) => entry.quarter_bpm,
    ),
    [60],
    'A selected slower source passage remains native at 100% global practice speed',
  );
});

test('key hold and sustain audio durations each integrate through the tempo change', () => {
  const note = { ...event('a', 3, 2), play_onset: 3, play_duration: 2, play_sound_duration: 4 };
  const timing = playbackNoteTiming(note, changingTempo);
  close(timing.onset, 1.5);
  close(timing.key_duration, 1.5);
  close(timing.sound_duration, 3.5);
});

test('MIDI timeline caps keyholds and pedal tails at exact EOT and does not invent repeats', () => {
  const source = midiScore(
    [event('a', 3, 1, { sound_duration_quarters: 20 }), event('last', 7, 2)],
    { total_quarters: 7.75 },
  );
  const result = timeline(source, 0, 1, 'both');
  close(result.length, 7.75);
  close(result.duration_seconds, 5.75);
  assert.deepEqual(
    result.notes.map((note) => note.id),
    ['a', 'last'],
  );
  close(result.notes[0].play_duration, 1);
  close(result.notes[0].play_sound_duration, 4.75);
  close(result.notes[1].play_duration, 0.75);
  close(result.occurrences[1].measure.length_quarters, 3.75);
  assert.equal(source.parsed.events[0].sound_duration_quarters, 20);
});

test('selected MIDI source rebases effective tempo and caps sustain at selected boundary', () => {
  const source = midiScore([event('a', 4, 0.5, { sound_duration_quarters: 5 }), event('b', 7, 1)]);
  const result = timeline(source, 1, 1, 'right');
  assert.deepEqual(
    result.notes.map((note) => note.play_onset),
    [0, 3],
  );
  close(result.notes[0].play_duration, 0.5);
  close(result.notes[0].play_sound_duration, 4);
  close(result.duration_seconds, 4);
  assert.deepEqual(
    result.tempo_map.map((entry) => [entry.onset_quarters, entry.quarter_bpm]),
    [[0, 60]],
  );
});

test('a held key crossing the selected start resumes with remaining duration; pedal-only tails do not become key attacks', () => {
  const source = midiScore([
    event('held', 3, 2, { sound_duration_quarters: 4 }),
    event('tail', 2, 0.5, { sound_duration_quarters: 5 }),
    event('new', 5, 1),
  ]);
  const result = timeline(source, 1, 1, 'both');
  assert.deepEqual(
    result.notes.map((note) => note.id),
    ['held', 'new'],
  );
  close(result.notes[0].play_onset, 0);
  close(result.notes[0].play_duration, 1);
  close(result.notes[0].play_sound_duration, 3);
  assert.equal(result.notes[0].resumed_at_boundary, true);
  assert.equal(result.notes[0].play_source_onset, 4);
  assert.equal(result.notes[0].play_measure_number, '2');
  assert.equal(result.notes[0].onset_quarters, 3, 'Original MIDI onset remains source evidence');
  assert.equal(
    result.sustained_at_start.length,
    1,
    'Pedal-only tail is preserved separately for audio',
  );
  const initialAudio = activeNotesAtQuarter([...result.notes, ...result.sustained_at_start], 0);
  assert.deepEqual(
    initialAudio.map((voice) => [
      voice.note.id,
      voice.key_remaining_quarters,
      voice.sound_remaining_quarters,
    ]),
    [['tail', 0, 3]],
  );
});

test('quarter-exact clipping preserves mid-window holds and rebases source tempo changes', () => {
  const source = midiScore([
    event('held', 3, 3, { sound_duration_quarters: 5 }),
    event('late', 5, 2),
  ]);
  const full = timeline(source, 0, 1, 'both');
  const clipped = clipTimeline(full, 3.5, 5.5);
  close(clipped.length, 2);
  close(clipped.duration_seconds, 1.75);
  assert.deepEqual(
    clipped.tempo_map.map((entry) => [entry.onset_quarters, entry.quarter_bpm]),
    [
      [0, 120],
      [0.5, 60],
    ],
  );
  assert.deepEqual(
    clipped.notes.map((note) => [
      note.id,
      note.play_onset,
      note.play_duration,
      note.play_sound_duration,
    ]),
    [
      ['held', 0, 2, 2],
      ['late', 1.5, 0.5, 0.5],
    ],
  );
  assert.deepEqual(
    clipped.occurrences.map((item) => [
      item.onset,
      item.measure.start_quarters,
      item.measure.length_quarters,
    ]),
    [
      [0, 3.5, 0.5],
      [0.5, 4, 1.5],
    ],
  );
  assert.equal(clipped.source_start_quarters, 3.5);
  assert.equal(clipped.notes[0].play_source_onset, 3.5);
  assert.equal(full.notes[0].play_duration, 3, 'Clipping does not mutate full source');
});

test('clipping keeps pre-start pedal resonance outside wait-mode note attacks', () => {
  const full = timeline(
    midiScore([event('tail', 1, 1, { sound_duration_quarters: 7 }), event('new', 5, 1)]),
    0,
    1,
    'both',
  );
  const clipped = clipTimeline(full, 4.5, 6.5);
  assert.deepEqual(
    clipped.notes.map((note) => note.id),
    ['new'],
  );
  assert.equal(clipped.sustained_at_start.length, 1);
  assert.deepEqual(
    activeNotesAtQuarter([...clipped.notes, ...clipped.sustained_at_start], 0).map((voice) => [
      voice.note.id,
      voice.key_remaining_quarters,
      voice.sound_remaining_quarters,
    ]),
    [['tail', 0, 2]],
  );
  assert.equal(clipped.notes[0].play_onset, 0.5);
  assert.equal(clipped.duration_seconds, 2);
});

test('a selected source restores incoming pedal resonance without adding key tasks', () => {
  const full = timeline(
    midiScore([event('tail', 1, 1, { sound_duration_quarters: 7 }), event('new', 5, 1)]),
    0,
    1,
    'both',
  );
  const clipped = clipTimeline(full, 4.5, 6.5);
  const audible = audioTimelineNotes(clipped);
  assert.deepEqual(
    clipped.notes.map((note) => note.id),
    ['new'],
  );
  assert.deepEqual(
    audible.map((note) => [note.id, note.play_onset, note.play_duration]),
    [
      ['tail', 0, 0],
      ['new', 0.5, 1],
    ],
  );
  assert.deepEqual(
    attacksInTempoWindow(audible, clipped.tempo_map, clipped.duration_seconds, 0, 0, 4.1).map(
      (item) => [item.event.id, item.when],
    ),
    [
      ['tail', 0],
      ['new', 0.5],
    ],
  );
  assert.deepEqual(
    activeNotesAtQuarter(audible, 0),
    [],
    'At the boundary the scheduler owns the first attack',
  );
  assert.deepEqual(
    activeNotesAtQuarter(audible, 1).map((voice) => [
      voice.note.id,
      voice.key_remaining_quarters,
      voice.sound_remaining_quarters,
    ]),
    [
      ['tail', 0, 1],
      ['new', 0.5, 0.5],
    ],
  );
});

test('nested clips preserve original source onsets, cap EOT and do not duplicate sustained voices', () => {
  const full = timeline(
    midiScore([event('tail', 1, 1, { sound_duration_quarters: 7 }), event('held', 3, 4)], {
      total_quarters: 7.75,
    }),
    0,
    1,
    'both',
  );
  const once = clipTimeline(full, 4, 8);
  const twice = clipTimeline(once, 1, 20);
  close(twice.length, 2.75);
  assert.equal(twice.source_start_quarters, 5);
  assert.equal(twice.notes[0].play_source_onset, 5);
  assert.equal(twice.sustained_at_start.length, 1);
  assert.equal(
    twice.sustained_at_start[0].play_onset + twice.sustained_at_start[0].play_sound_duration,
    2.75,
  );
  const empty = clipTimeline(full, 4, 3);
  assert.equal(empty.length, 0);
  assert.equal(empty.notes.length, 0);
  assert.equal(empty.sustained_at_start.length, 0);
});

test('actual pirate final hold remains playable when selecting the 87th derived beat window', () => {
  const notes = [62, 26, 38].map((midi, index) => ({
    ...event(`final-${midi}`, 255, 3.75, { sound_duration_quarters: 3.75 }),
    measure_index: 85,
    measure_number: '86',
    offset_quarters: 0,
    hand: index ? 'left' : 'right',
    part_id: index ? 'T2' : 'T1',
    pitch: { step: 'D', alter: 0, octave: Math.floor(midi / 12) - 1, midi },
  }));
  const source = midiScore(notes, {
    total_quarters: 258.75,
    tempo_map: [{ onset_quarters: 0, quarter_bpm: 200 }],
  });
  source.parsed.measures = Array.from({ length: 87 }, (_, index) => ({
    index,
    number: String(index + 1),
    start_quarters: index * 3,
    length_quarters: index === 86 ? 0.75 : 3,
    time: { beats: '6', beat_type: 8 },
  }));
  const result = timeline(source, 86, 86, 'both');
  assert.deepEqual(
    result.notes.map((note) => [
      note.pitch.midi,
      note.play_onset,
      note.play_duration,
      note.play_sound_duration,
    ]),
    [
      [62, 0, 0.75, 0.75],
      [26, 0, 0.75, 0.75],
      [38, 0, 0.75, 0.75],
    ],
  );
  close(result.duration_seconds, 0.225);
  assert.ok(
    result.notes.every(
      (note) =>
        note.resumed_at_boundary &&
        note.play_source_onset === 258 &&
        note.play_measure_number === '87',
    ),
  );
  const entire = timeline(source, 0, 86, 'both');
  assert.deepEqual(
    activeNotesAtQuarter(entire.notes, 258).map((item) => [
      item.note.pitch.midi,
      item.key_remaining_quarters,
      item.sound_remaining_quarters,
    ]),
    [
      [62, 0.75, 0.75],
      [26, 0.75, 0.75],
      [38, 0.75, 0.75],
    ],
  );
  assert.deepEqual(activeNotesAtQuarter(entire.notes, 258.75), []);
});

test('seeking resumes audio tails while leaving physically released keys inactive', () => {
  const source = midiScore([
    event('released', 1, 1, { sound_duration_quarters: 6 }),
    event('held', 4, 2),
    event('at-seek', 5, 1),
  ]);
  const result = timeline(source, 0, 1, 'both');
  assert.deepEqual(
    activeNotesAtQuarter(result.notes, 5).map((item) => [
      item.note.id,
      item.key_remaining_quarters,
      item.sound_remaining_quarters,
    ]),
    [
      ['released', 0, 2],
      ['held', 1, 1],
    ],
  );
  assert.deepEqual(activeNotesAtQuarter(result.notes, 7), []);
});

test('tempo-aware lookahead excludes attacks at EOT and never restarts the source', () => {
  const notes = [
    { id: 'first', play_onset: 0 },
    { id: 'late', play_onset: 7 },
    { id: 'outside', play_onset: 8 },
  ];
  assert.deepEqual(attacksInTempoWindow(notes, changingTempo, 6, 10, 15.95, 16.1), []);
});

test('adjacent tempo-aware scheduling windows neither duplicate boundary chord attacks nor leak beyond duration', () => {
  const notes = [
    { id: 'a', play_onset: 0 },
    { id: 'b', play_onset: 4 },
    { id: 'c', play_onset: 4 },
    { id: 'late', play_onset: 7 },
  ];
  const result = [
    [0, 2],
    [2, 4],
    [4, 6],
    [6, 8],
  ].flatMap(([from, until]) => attacksInTempoWindow(notes, changingTempo, 6, 0, from, until));
  assert.deepEqual(
    result.map((item) => [item.event.id, item.when]),
    [
      ['a', 0],
      ['b', 2],
      ['c', 2],
      ['late', 5],
    ],
  );
});

test('simultaneous MIDI notes retain independent channels, hand overrides and key lengths', () => {
  const source = midiScore(
    [
      event('a', 0, 1),
      event('b', 0, 2, { pitch: { step: 'E', alter: 0, octave: 4, midi: 64 }, chord: true }),
      event('c', 0, 0.5, { channel: 1, hand: 'left' }),
      event('drum', 0, 1, { percussion: true }),
    ],
    { hand_overrides: { b: 'left' } },
  );
  assert.deepEqual(
    timeline(source, 0, 1, 'right').notes.map((note) => [note.id, note.play_duration]),
    [['a', 1]],
  );
  assert.deepEqual(
    timeline(source, 0, 1, 'left').notes.map((note) => [note.id, note.play_duration]),
    [
      ['b', 2],
      ['c', 0.5],
    ],
  );
});

test('practice tempo validation is pure and rejects malformed URL values', () => {
  assert.deepEqual(validateRequestedTempo('40', 'quarter'), { bpm: 40, beat_unit: 'quarter' });
  for (const [value, unit] of [
    [null, 'quarter'],
    [undefined, 'quarter'],
    [[40], 'quarter'],
    ['40.5', 'quarter'],
    ['241', 'quarter'],
    ['40', 'unexpected'],
  ])
    assert.equal(validateRequestedTempo(value, unit), null);
});

test('browser audio adapter is lazy and cuts voices exactly at passed source boundaries, including late attacks', async () => {
  const previous = Object.getOwnPropertyDescriptor(globalThis, 'AudioContext');
  const contexts = [];
  class FakeAudioContext {
    currentTime = 10;
    state = 'suspended';
    destination = {};
    oscillators = [];
    ramps = [];
    constructor() {
      contexts.push(this);
    }
    async resume() {
      this.state = 'running';
    }
    async close() {
      this.state = 'closed';
    }
    createOscillator() {
      const node = {
        frequency: { value: 0 },
        type: '',
        startCalls: [],
        stopCalls: [],
        connect() {},
        disconnect() {},
        start(at) {
          this.startCalls.push(at);
        },
        stop(at) {
          this.stopCalls.push(at);
        },
        onended: null,
      };
      this.oscillators.push(node);
      return node;
    }
    createGain() {
      return {
        gain: {
          setValueAtTime: (_, at) => this.ramps.push(at),
          linearRampToValueAtTime: (_, at) => this.ramps.push(at),
          exponentialRampToValueAtTime: (_, at) => this.ramps.push(at),
        },
        connect() {},
        disconnect() {},
      };
    }
  }
  Object.defineProperty(globalThis, 'AudioContext', {
    configurable: true,
    value: FakeAudioContext,
  });
  try {
    const audio = createPlaybackAudio();
    assert.equal(contexts.length, 0);
    assert.equal(audio.currentTime(), 0);
    await audio.resume();
    const context = contexts[0];
    assert.equal(audio.currentTime(), 10);
    audio.sound(60, 10.5, 0.1);
    audio.sound(62, 9.8, 0.4);
    audio.sound(64, 9, 0.5);
    assert.equal(context.oscillators.length, 2, 'Already-ended sound is not restarted');
    close(context.oscillators[0].stopCalls[0], 10.6);
    close(context.oscillators[1].startCalls[0], 10);
    close(context.oscillators[1].stopCalls[0], 10.2, 'A late attack retains its original end');
    assert.ok(
      context.ramps.every((at) => at <= 10.6),
      'Envelope has no extra release tail',
    );
    audio.stop();
    assert.ok(context.oscillators.every((node) => node.stopCalls.at(-1) === undefined));
    await audio.close();
    assert.equal(context.state, 'closed');
  } finally {
    if (previous) Object.defineProperty(globalThis, 'AudioContext', previous);
    else delete globalThis.AudioContext;
  }
});

test('browser MIDI adapter requests only on connect and handles note releases, velocity-zero and hotplug cleanup', async () => {
  const previous = Object.getOwnPropertyDescriptor(globalThis, 'navigator');
  class Input {
    constructor(name) {
      this.name = name;
      this.state = 'connected';
      this.onmidimessage = null;
      this.closed = 0;
    }
    async close() {
      this.closed++;
    }
    send(bytes) {
      this.onmidimessage?.({ data: new Uint8Array(bytes) });
    }
  }
  class Access extends EventTarget {
    inputs = new Map();
  }
  const access = new Access();
  const first = new Input('Yamaha');
  access.inputs.set('first', first);
  let requests = 0;
  const options = [];
  const notes = [];
  const devices = [];
  Object.defineProperty(globalThis, 'navigator', {
    configurable: true,
    value: {
      requestMIDIAccess: async (option) => {
        requests++;
        options.push(option);
        return access;
      },
    },
  });
  try {
    const input = createMidiInput();
    assert.equal(requests, 0);
    await input.connect(
      (pitch, down, velocity) => notes.push([pitch, down, velocity]),
      (names) => devices.push(names),
    );
    assert.equal(requests, 1);
    assert.deepEqual(options, [{ sysex: false }]);
    assert.deepEqual(devices.at(-1), ['Yamaha']);
    first.send([0x90, 60, 90]);
    first.send([0x80, 60, 45]);
    first.send([0x90, 64, 0]);
    assert.deepEqual(notes, [
      [60, true, 90],
      [60, false, 45],
      [64, false, 0],
    ]);
    const beforeDualVoice = notes.length;
    first.send([0x90, 65, 90]);
    first.send([0x91, 65, 70]);
    assert.deepEqual(
      notes.slice(beforeDualVoice),
      [[65, true, 90]],
      'Mirrored channels represent a single physical strike',
    );
    first.send([0x80, 65, 0]);
    assert.equal(
      notes.length,
      beforeDualVoice + 1,
      'First voice release does not release the still-held key',
    );
    first.send([0x81, 65, 0]);
    assert.deepEqual(notes.at(-1), [65, false, 0]);
    const beforeReattack = notes.length;
    first.send([0x90, 65, 90]);
    first.send([0x90, 65, 95]);
    first.send([0x80, 65, 0]);
    assert.deepEqual(
      notes.slice(beforeReattack),
      [
        [65, true, 90],
        [65, true, 95],
        [65, false, 0],
      ],
      'Same-channel reattacks remain separate strikes',
    );
    first.send([0x90, 67, 90]);
    const second = new Input('Second piano');
    access.inputs.delete('first');
    access.inputs.set('second', second);
    access.dispatchEvent(new Event('statechange'));
    assert.deepEqual(notes.at(-1), [67, false, 0]);
    assert.equal(first.onmidimessage, null);
    assert.equal(first.closed, 1);
    assert.deepEqual(devices.at(-1), ['Second piano']);
    second.send([0x90, 70, 90]);
    input.close();
    assert.equal(second.onmidimessage, null);
    assert.equal(second.closed, 1);
    assert.deepEqual(notes.at(-1), [70, false, 0]);
    const count = devices.length;
    access.dispatchEvent(new Event('statechange'));
    assert.equal(devices.length, count, 'State listener is detached');
  } finally {
    if (previous) Object.defineProperty(globalThis, 'navigator', previous);
    else delete globalThis.navigator;
  }
});
