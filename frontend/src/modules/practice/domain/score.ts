import type {
  Hand,
  TempoMapEntry,
  ScoreTempo,
  ScoreMeter,
  MidiControlEvent,
  ScoreEvent,
  ScoreMeasure,
  Score,
  PlaybackNote,
  PlaybackSequence,
  RequestedTempo,
  TempoClock,
} from './entities/score.types.ts';
export type {
  Hand,
  TempoMapEntry,
  ScoreTempo,
  ScoreMeter,
  MidiControlEvent,
  ScoreEvent,
  ScoreMeasure,
  Score,
  PlaybackNote,
  PlaybackSequence,
  RequestedTempo,
  TempoClock,
} from './entities/score.types.ts';

export function validateRequestedTempo(value: unknown, unit: unknown): RequestedTempo | null {
  if ((typeof value !== 'number' && typeof value !== 'string') || typeof unit !== 'string')
    return null;
  const bpm = Number(value);
  return Number.isInteger(bpm) &&
    bpm >= 20 &&
    bpm <= 240 &&
    ['whole', 'half', 'quarter', 'eighth', '16th', '32nd', 'dotted_quarter'].includes(unit)
    ? { bpm, beat_unit: unit }
    : null;
}

/** Tempo is quarter-note based, independent of meter or the UI pulse unit. */
export function normalizeTempoMap(tempoMap: readonly TempoMapEntry[] = []): TempoMapEntry[] {
  const byOnset = new Map<number, TempoMapEntry>();
  byOnset.set(0, { onset_quarters: 0, quarter_bpm: 120 });
  for (const entry of tempoMap) {
    if (
      Number.isFinite(entry.onset_quarters) &&
      entry.onset_quarters >= 0 &&
      Number.isFinite(entry.quarter_bpm) &&
      entry.quarter_bpm > 0
    )
      byOnset.set(entry.onset_quarters, { ...entry });
  }
  return [...byOnset.values()]
    .sort((a, b) => a.onset_quarters - b.onset_quarters)
    .filter(
      (entry, index, entries) => !index || entry.quarter_bpm !== entries[index - 1].quarter_bpm,
    );
}

export function quarterToSeconds(quarter: number, tempoMap: readonly TempoMapEntry[] = []): number {
  if (!Number.isFinite(quarter) || quarter <= 0) return 0;
  const entries = normalizeTempoMap(tempoMap);
  let seconds = 0;
  for (let index = 0; index < entries.length; index++) {
    const entry = entries[index];
    const end = Math.min(quarter, entries[index + 1]?.onset_quarters ?? quarter);
    if (end > entry.onset_quarters)
      seconds += ((end - entry.onset_quarters) * 60) / entry.quarter_bpm;
    if (end >= quarter) break;
  }
  return seconds;
}

/** Compile an immutable tempo snapshot once for rendering and transport clocks. */
export function createTempoClock(tempoMap: readonly TempoMapEntry[] = []): TempoClock {
  const entries = normalizeTempoMap(tempoMap);
  const seconds = [0];
  for (let index = 1; index < entries.length; index++)
    seconds.push(
      seconds[index - 1] +
        ((entries[index].onset_quarters - entries[index - 1].onset_quarters) * 60) /
          entries[index - 1].quarter_bpm,
    );
  const find = (value: number, get: (index: number) => number) => {
    let low = 0,
      high = entries.length;
    while (low < high) {
      const middle = (low + high) >>> 1;
      if (get(middle) <= value) low = middle + 1;
      else high = middle;
    }
    return Math.max(0, low - 1);
  };
  return {
    quarterToSeconds(quarter) {
      if (!Number.isFinite(quarter) || quarter <= 0) return 0;
      const index = find(quarter, (index) => entries[index].onset_quarters);
      return (
        seconds[index] +
        ((quarter - entries[index].onset_quarters) * 60) / entries[index].quarter_bpm
      );
    },
    secondsToQuarter(value) {
      if (!Number.isFinite(value) || value <= 0) return 0;
      const index = find(value, (index) => seconds[index]);
      return (
        entries[index].onset_quarters + ((value - seconds[index]) * entries[index].quarter_bpm) / 60
      );
    },
  };
}

export function playbackTimeLabel(seconds: number): string {
  const total = Number.isFinite(seconds) ? Math.max(0, Math.floor(seconds)) : 0;
  return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;
}

export function secondsToQuarter(seconds: number, tempoMap: readonly TempoMapEntry[] = []): number {
  if (!Number.isFinite(seconds) || seconds <= 0) return 0;
  const entries = normalizeTempoMap(tempoMap);
  let elapsed = 0;
  for (let index = 0; index < entries.length; index++) {
    const entry = entries[index];
    const next = entries[index + 1];
    const segmentSeconds = next
      ? ((next.onset_quarters - entry.onset_quarters) * 60) / entry.quarter_bpm
      : Infinity;
    if (seconds <= elapsed + segmentSeconds)
      return entry.onset_quarters + ((seconds - elapsed) * entry.quarter_bpm) / 60;
    elapsed += segmentSeconds;
  }
  return 0;
}

function tempoAt(quarter: number, tempoMap: readonly TempoMapEntry[]): number {
  let bpm = 120;
  for (const entry of tempoMap) {
    if (entry.onset_quarters > quarter) break;
    bpm = entry.quarter_bpm;
  }
  return bpm;
}

export function scaleTempoMap(
  tempoMap: readonly TempoMapEntry[],
  quarterBpm: number,
  sourceQuarterBpm?: number,
): TempoMapEntry[] {
  const entries = normalizeTempoMap(tempoMap);
  if (!Number.isFinite(quarterBpm) || quarterBpm <= 0) return entries;
  const basis =
    sourceQuarterBpm !== undefined && Number.isFinite(sourceQuarterBpm) && sourceQuarterBpm > 0
      ? sourceQuarterBpm
      : entries[0].quarter_bpm;
  const factor = quarterBpm / basis;
  return entries.map((entry) => ({
    onset_quarters: entry.onset_quarters,
    quarter_bpm: entry.quarter_bpm * factor,
  }));
}

function attacksAtTimesInWindow<T>(
  events: readonly T[],
  onsetSeconds: (event: T) => number,
  duration: number,
  startedAt: number,
  from: number,
  until: number,
): { event: T; when: number }[] {
  if (!events.length || !Number.isFinite(duration) || duration <= 0 || until <= from) return [];
  const result: { event: T; when: number }[] = [];
  let low = 0;
  let high = events.length;
  while (low < high) {
    const middle = Math.floor((low + high) / 2);
    if (startedAt + onsetSeconds(events[middle]) < from - 1e-9) low = middle + 1;
    else high = middle;
  }
  for (let index = low; index < events.length; index++) {
    const offset = onsetSeconds(events[index]);
    if (offset >= duration - 1e-9) break;
    const when = startedAt + offset;
    if (when >= until - 1e-9) break;
    if (offset >= 0 && when >= from - 1e-9) result.push({ event: events[index], when });
  }
  return result;
}

export function attacksInWindow<T extends { play_onset: number }>(
  events: readonly T[],
  secondsPerQuarter: number,
  duration: number,
  startedAt: number,
  from: number,
  until: number,
): { event: T; when: number }[] {
  return attacksAtTimesInWindow(
    events,
    (event) => event.play_onset * secondsPerQuarter,
    duration,
    startedAt,
    from,
    until,
  );
}

export function attacksInTempoWindow<T extends { play_onset: number }>(
  events: readonly T[],
  tempoMap: readonly TempoMapEntry[],
  duration: number,
  startedAt: number,
  from: number,
  until: number,
): { event: T; when: number }[] {
  const clock = createTempoClock(tempoMap);
  return attacksAtTimesInWindow(
    events,
    (event) => clock.quarterToSeconds(event.play_onset),
    duration,
    startedAt,
    from,
    until,
  );
}

export function playbackNoteTiming(note: PlaybackNote, tempoMap: readonly TempoMapEntry[]) {
  const onset = quarterToSeconds(note.play_onset, tempoMap);
  return {
    onset,
    key_duration: quarterToSeconds(note.play_onset + note.play_duration, tempoMap) - onset,
    sound_duration: quarterToSeconds(note.play_onset + note.play_sound_duration, tempoMap) - onset,
  };
}

/** Resume audible voices after seeking without treating pedal tails as held keys. */
export function activeNotesAtQuarter(notes: readonly PlaybackNote[], quarter: number) {
  if (!Number.isFinite(quarter) || quarter < 0) return [];
  return notes
    .filter(
      (note) =>
        note.play_onset < quarter - 1e-9 &&
        note.play_onset + note.play_sound_duration > quarter + 1e-9,
    )
    .map((note) => ({
      note,
      key_remaining_quarters: Math.max(0, note.play_onset + note.play_duration - quarter),
      sound_remaining_quarters: note.play_onset + note.play_sound_duration - quarter,
    }));
}

/** The selected source restores incoming pedal resonance without adding piano key tasks. */
export function audioTimelineNotes(sequence: PlaybackSequence): PlaybackNote[] {
  const tails = sequence.sustained_at_start.map((note) => ({
    ...note,
    play_onset: 0,
    play_duration: 0,
    play_sound_duration: Math.max(
      0,
      Math.min(sequence.length, note.play_onset + note.play_sound_duration),
    ),
  }));
  return [...sequence.notes, ...tails].sort((a, b) => a.play_onset - b.play_onset);
}

export function pitchLabel(midi: number) {
  return `${['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B'][midi % 12]}${Math.floor(midi / 12) - 1}`;
}

export function beatQuarters(unit: string, dots = 0) {
  const base: Record<string, number> = {
    whole: 4,
    half: 2,
    quarter: 1,
    eighth: 0.5,
    '16th': 0.25,
    '32nd': 0.125,
    dotted_quarter: 1.5,
  };
  let value = base[unit] || 1;
  let addition = value;
  for (let i = 0; i < dots; i++) {
    addition /= 2;
    value += addition;
  }
  return value;
}

/** Metrical clicks are independent of the tempo's quarter-note BPM unit. */
export function measureClickOffsets(
  time: ScoreMeter | null | undefined,
  length: number,
  meterOffset = 0,
): number[] {
  if (!Number.isFinite(length) || length <= 0) return [];
  const offset = Number.isFinite(meterOffset) && meterOffset > 0 ? meterOffset : 0;
  const groups = time?.beats?.split('+').map((value) => Number(value.trim())) || [];
  const valid =
    groups.length > 0 &&
    groups.every((value) => Number.isInteger(value) && value > 0 && value <= 64) &&
    Number.isInteger(time?.beat_type) &&
    (time?.beat_type || 0) > 0;
  const denominatorUnit = valid ? 4 / time!.beat_type : 1;
  const barLength = valid ? groups.reduce((sum, value) => sum + value, 0) * denominatorUnit : 4;
  const pulseOffsets: number[] = [];
  if (valid && groups.length > 1) {
    let cursor = 0;
    for (const group of groups) {
      pulseOffsets.push(cursor);
      cursor += group * denominatorUnit;
    }
  } else {
    const compound = valid && groups[0] > 3 && groups[0] % 3 === 0;
    const pulseLength = compound ? 3 * denominatorUnit : denominatorUnit;
    for (let cursor = 0; cursor < barLength - 1e-9; cursor += pulseLength)
      pulseOffsets.push(cursor);
  }
  const result: number[] = [];
  for (
    let cycle = Math.floor(offset / barLength);
    cycle * barLength < offset + length - 1e-9;
    cycle++
  )
    for (const pulse of pulseOffsets) {
      const candidate = cycle * barLength + pulse - offset;
      if (candidate >= -1e-9 && candidate < length - 1e-9) result.push(Math.max(0, candidate));
    }
  return result;
}

/** Key holds drive the piano roll. Pedal tails only extend audible duration. */
export function timeline(score: Score, from: number, to: number, hand: string): PlaybackSequence {
  const measures = score.parsed.measures;
  const isMidi = score.file_format === 'midi' || score.parsed.source_format === 'midi';
  const full = from === 0 && to === measures.length - 1;
  const indices =
    full && !isMidi && score.parsed.playback_order?.length
      ? score.parsed.playback_order
      : Array.from({ length: Math.max(0, to - from + 1) }, (_, i) => from + i);
  const notes: PlaybackNote[] = [];
  const occurrences: { measure: ScoreMeasure; onset: number }[] = [];
  const playbackTempos: TempoMapEntry[] = [];
  const sourceTempos = normalizeTempoMap(
    score.parsed.tempo_map?.length
      ? score.parsed.tempo_map
      : [
          { onset_quarters: 0, quarter_bpm: score.parsed.metadata?.tempo?.quarter_bpm || 120 },
          ...measures.flatMap((measure) =>
            (measure.tempos || []).map((tempo) => ({
              onset_quarters: measure.start_quarters + tempo.offset_quarters,
              quarter_bpm: tempo.quarter_bpm,
            })),
          ),
        ],
  );
  const endQuarter =
    isMidi && Number.isFinite(score.parsed.metadata?.total_quarters)
      ? score.parsed.metadata.total_quarters!
      : Infinity;
  const selectedStart = measures[from]?.start_quarters ?? 0;
  let length = 0;
  const openTies = new Map<string, PlaybackNote>();
  for (const index of indices) {
    const measure = measures[index];
    if (!measure) continue;
    const measureLength = Math.max(
      0,
      Math.min(measure.length_quarters, endQuarter - measure.start_quarters),
    );
    if (!measureLength) continue;
    occurrences.push({
      measure:
        measureLength === measure.length_quarters
          ? measure
          : { ...measure, length_quarters: measureLength },
      onset: length,
    });
    playbackTempos.push({
      onset_quarters: length,
      quarter_bpm: tempoAt(measure.start_quarters, sourceTempos),
    });
    for (const tempo of sourceTempos)
      if (
        tempo.onset_quarters > measure.start_quarters &&
        tempo.onset_quarters < measure.start_quarters + measureLength
      )
        playbackTempos.push({
          onset_quarters: length + tempo.onset_quarters - measure.start_quarters,
          quarter_bpm: tempo.quarter_bpm,
        });
    const candidates = score.parsed.events.filter(
      (event) =>
        event.measure_index === index ||
        (isMidi &&
          index === from &&
          event.onset_quarters < selectedStart &&
          event.onset_quarters + event.duration_quarters > selectedStart),
    );
    for (const event of candidates) {
      const eventHand = score.hand_overrides?.[event.id] || event.hand;
      if (
        !event.pitch ||
        event.rest ||
        event.grace ||
        event.cue ||
        event.percussion ||
        (hand !== 'both' && eventHand !== hand)
      )
        continue;
      const key = `${event.part_id}-${event.staff}-${event.voice}-${event.pitch.midi}`;
      const previous = openTies.get(key);
      const resumeOffset = isMidi ? Math.max(0, selectedStart - event.onset_quarters) : 0;
      const onset = isMidi
        ? length + Math.max(0, event.onset_quarters - measure.start_quarters)
        : length + event.offset_quarters;
      if (onset >= length + measureLength - 1e-9) continue;
      const keyDuration = Math.max(0, event.duration_quarters - resumeOffset);
      const soundDuration = Math.max(
        0,
        (event.sound_duration_quarters ?? event.duration_quarters) - resumeOffset,
      );
      if (
        event.ties.includes('stop') &&
        previous &&
        Math.abs(previous.play_onset + previous.play_duration - onset) < 0.02
      ) {
        previous.play_duration += keyDuration;
        previous.play_sound_duration += soundDuration;
        if (!event.ties.includes('start')) openTies.delete(key);
      } else {
        const note: PlaybackNote = {
          ...event,
          hand: eventHand,
          play_onset: onset,
          play_duration: keyDuration,
          play_sound_duration: soundDuration,
          play_source_onset: event.onset_quarters + resumeOffset,
          play_measure_index: index,
          play_measure_number: measure.number,
          ...(resumeOffset > 0 ? { resumed_at_boundary: true } : {}),
        };
        notes.push(note);
        if (event.ties.includes('start')) openTies.set(key, note);
        else openTies.delete(key);
      }
    }
    length += measureLength;
  }
  for (const note of notes) {
    note.play_duration = Math.min(note.play_duration, Math.max(0, length - note.play_onset));
    note.play_sound_duration = Math.min(
      note.play_sound_duration,
      Math.max(0, length - note.play_onset),
    );
  }
  const sustained_at_start: PlaybackNote[] = [];
  if (isMidi && length > 0)
    for (const event of score.parsed.events) {
      const eventHand = score.hand_overrides?.[event.id] || event.hand;
      const soundDuration = event.sound_duration_quarters ?? event.duration_quarters;
      if (
        !event.pitch ||
        event.rest ||
        event.grace ||
        event.cue ||
        event.percussion ||
        (hand !== 'both' && eventHand !== hand)
      )
        continue;
      if (
        event.onset_quarters >= selectedStart ||
        event.onset_quarters + event.duration_quarters > selectedStart ||
        event.onset_quarters + soundDuration <= selectedStart
      )
        continue;
      const onset = event.onset_quarters - selectedStart;
      sustained_at_start.push({
        ...event,
        hand: eventHand,
        play_onset: onset,
        play_duration: event.duration_quarters,
        play_sound_duration: Math.min(soundDuration, length - onset),
        play_source_onset: selectedStart,
        play_measure_index: from,
        play_measure_number: measures[from]?.number || event.measure_number,
        resumed_at_boundary: true,
      });
    }
  return {
    notes: notes.sort((a, b) => a.play_onset - b.play_onset),
    sustained_at_start,
    occurrences,
    length,
    tempo_map: normalizeTempoMap(playbackTempos),
    duration_seconds: quarterToSeconds(length, playbackTempos),
    source_start_quarters: selectedStart,
  };
}

/** Inclusive start/exclusive end in this sequence's quarter coordinates. */
export function clipTimeline(
  sequence: PlaybackSequence,
  startQ: number,
  endQ: number,
): PlaybackSequence {
  const start = Number.isFinite(startQ) ? Math.max(0, Math.min(sequence.length, startQ)) : 0;
  const end = Number.isFinite(endQ) ? Math.max(start, Math.min(sequence.length, endQ)) : start;
  const length = end - start;
  const sourceTempos = normalizeTempoMap(sequence.tempo_map);
  const tempo_map = normalizeTempoMap([
    { onset_quarters: 0, quarter_bpm: tempoAt(start, sourceTempos) },
    ...sourceTempos
      .filter((entry) => entry.onset_quarters > start && entry.onset_quarters < end)
      .map((entry) => ({
        onset_quarters: entry.onset_quarters - start,
        quarter_bpm: entry.quarter_bpm,
      })),
  ]);
  const occurrences = sequence.occurrences.flatMap((occurrence) => {
    const left = Math.max(start, occurrence.onset);
    const right = Math.min(end, occurrence.onset + occurrence.measure.length_quarters);
    return right > left
      ? [
          {
            onset: left - start,
            measure: {
              ...occurrence.measure,
              start_quarters: occurrence.measure.start_quarters + left - occurrence.onset,
              length_quarters: right - left,
              meter_offset_quarters:
                (occurrence.measure.meter_offset_quarters || 0) + left - occurrence.onset,
            },
          },
        ]
      : [];
  });
  const source_start_quarters =
    occurrences[0]?.measure.start_quarters ?? sequence.source_start_quarters + start;
  const notes: PlaybackNote[] = [];
  const sustained_at_start: PlaybackNote[] = [];
  if (length > 0)
    for (const original of [...sequence.sustained_at_start, ...sequence.notes]) {
      const keyEnd = original.play_onset + original.play_duration;
      const soundEnd = original.play_onset + original.play_sound_duration;
      if (original.play_onset >= end || (soundEnd <= start && keyEnd <= start)) continue;
      if (original.play_onset < start && keyEnd <= start) {
        if (soundEnd > start)
          sustained_at_start.push({
            ...original,
            play_onset: original.play_onset - start,
            play_sound_duration: Math.min(soundEnd, end) - original.play_onset,
            play_source_onset: source_start_quarters,
            play_measure_index: occurrences[0]?.measure.index ?? original.play_measure_index,
            play_measure_number: occurrences[0]?.measure.number ?? original.play_measure_number,
            resumed_at_boundary: true,
          });
        continue;
      }
      const clippedStart = Math.max(start, original.play_onset);
      const skipped = clippedStart - original.play_onset;
      notes.push({
        ...original,
        play_onset: clippedStart - start,
        play_duration: Math.max(0, Math.min(keyEnd, end) - clippedStart),
        play_sound_duration: Math.max(0, Math.min(soundEnd, end) - clippedStart),
        play_source_onset: original.play_source_onset + skipped,
        ...(skipped > 0
          ? {
              play_measure_index: occurrences[0]?.measure.index ?? original.play_measure_index,
              play_measure_number: occurrences[0]?.measure.number ?? original.play_measure_number,
              resumed_at_boundary: true,
            }
          : {}),
      });
    }
  return {
    notes: notes.sort((a, b) => a.play_onset - b.play_onset),
    sustained_at_start,
    occurrences,
    length,
    tempo_map,
    duration_seconds: quarterToSeconds(length, tempo_map),
    source_start_quarters,
  };
}
