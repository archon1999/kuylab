import type { Composition } from '@modules/repertoire';
import { useTranslation } from '@shared/i18n';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  activeNotesAtQuarter,
  attacksInTempoWindow,
  audioTimelineNotes,
  beatQuarters,
  clipTimeline,
  createTempoClock,
  pitchLabel,
  measureClickOffsets,
  playbackNoteTiming,
  playbackTimeLabel,
  quarterToSeconds,
  scaleTempoMap,
  secondsToQuarter,
  timeline,
  type RequestedTempo,
  type Score,
} from '../domain';
import type { ScoreSummary } from '../domain/contracts/score.repository';
import { usePracticePorts } from './index';
import { createLatestScoreRequest } from './latestScoreRequest';
export type ScoreWorkspaceProps = {
  composition: Composition;
  online: boolean;
  lessonId?: number | null;
  scoreId?: number | null;
  sectionId?: string | null;
  requestedRange?: [number, number] | null;
  requestedTempo?: RequestedTempo | null;
  requestedSeconds?: [number, number] | null;
  onScoreChange: () => Promise<void>;
  onSettingsChange: (bpm: number, hand: string) => void;
  onPresence: (present: boolean) => void;
};
export function useScoreWorkspace({
  composition,
  online,
  lessonId,
  scoreId,
  sectionId,
  requestedRange,
  requestedTempo,
  requestedSeconds,
  onScoreChange,
  onSettingsChange,
  onPresence,
}: ScoreWorkspaceProps) {
  const tr = useTranslation();
  const [scores, setScores] = useState<ScoreSummary[]>([]);
  const [score, setScore] = useState<Score | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [importOpen, setImportOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [rights, setRights] = useState(false);
  const [exact, setExact] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState('');
  const [bpm, setBpm] = useState(60);
  const [hand, setHand] = useState('both');
  const [range, setRangeState] = useState([1, 2]);
  const [focusSeconds, setFocusSeconds] = useState<[number, number] | null>(null);
  function setRange(value: number[]) {
    setFocusSeconds(null);
    setRangeState(value);
  }
  const [playing, setPlaying] = useState(false);
  const [click, setClick] = useState(false);
  const [activeQuarter, setActiveQuarter] = useState<number | null>(null);
  const [activeMeasure, setActiveMeasure] = useState('');
  const [position, setPosition] = useState(0);
  const [wait, setWait] = useState(false);
  const [waitIndex, setWaitIndex] = useState(0);
  const [matched, setMatched] = useState<number[]>([]);
  const [waitMessage, setWaitMessage] = useState('');
  const [midiStatus, setMidiStatus] = useState('Pianino ulanmagan');
  const [midiNote, setMidiNote] = useState('');
  const [connecting, setConnecting] = useState(false);
  const [sectionTitle, setSectionTitle] = useState('');
  const [sectionSaving, setSectionSaving] = useState(false);
  const [updatingScore, setUpdatingScore] = useState(false);
  const { repository, audio, midi } = usePracticePorts();
  const pausedAt = useRef(0);
  const playQuarter = useRef(0);
  const mounted = useRef(true);
  const currentArrangement = useRef(composition.arrangement?.id);
  currentArrangement.current = composition.arrangement?.id;
  const latestScoreRequest = useRef(createLatestScoreRequest()).current;
  const currentScoreId = useRef<Score['id'] | null>(null);
  currentScoreId.current = score?.id ?? null;
  const patching = useRef(false);
  const screenTimers = useRef(new Map<number, ReturnType<typeof setTimeout>>());
  const [midiHeldPitches, setMidiHeldPitches] = useState<number[]>([]);
  const [screenHeldPitches, setScreenHeldPitches] = useState<number[]>([]);
  const heldPitches = useMemo(
    () => [...new Set([...midiHeldPitches, ...screenHeldPitches])],
    [midiHeldPitches, screenHeldPitches],
  );
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      latestScoreRequest.invalidate();
      for (const timer of screenTimers.current.values()) clearTimeout(timer);
      screenTimers.current.clear();
    };
  }, [latestScoreRequest]);
  const noteHandler = useRef<(pitch: number, source: string) => void>(() => {});
  const matchedRef = useRef<number[]>([]);
  const waitIndexRef = useRef(0);
  const arrangementId = composition.arrangement?.id;
  const playbackSupported = score?.parsed.capabilities.timed_notes !== false;
  const sequence = useMemo(() => {
    if (!score) return null;
    const value = timeline(score, range[0] - 1, range[1] - 1, hand);
    if (!focusSeconds || score.file_format !== 'midi') return value;
    const nativeMap = score.parsed.tempo_map || [
      { onset_quarters: 0, quarter_bpm: score.parsed.metadata.tempo.quarter_bpm },
    ];
    return clipTimeline(
      value,
      secondsToQuarter(focusSeconds[0], nativeMap) - value.source_start_quarters,
      secondsToQuarter(focusSeconds[1], nativeMap) - value.source_start_quarters,
    );
  }, [score, range, hand, focusSeconds]);
  const tempoOverride = requestedTempo || null;
  const unit = tempoOverride?.beat_unit || score?.parsed.metadata.tempo?.beat_unit || 'quarter';
  const dots = tempoOverride ? 0 : score?.parsed.metadata.tempo?.beat_unit_dots || 0;
  const unitLength = beatQuarters(unit, dots);
  const unitLabel = `${dots ? 'nuqtali ' : ''}${({ whole: 'butun', half: 'yarim', quarter: 'chorak', eighth: 'sakkizlik', dotted_quarter: 'nuqtali chorak' } as Record<string, string>)[unit] || unit}`;
  const quarterBpm = bpm * unitLength;
  const groups = useMemo(() => {
    if (!sequence) return [];
    const map = new Map<
      string,
      {
        sourceQuarter: number;
        playQuarter: number;
        measure: string;
        pitches: number[];
      }
    >();
    for (const note of sequence.notes) {
      const key = note.play_onset.toFixed(6);
      const group = map.get(key) || {
        sourceQuarter: note.play_source_onset,
        playQuarter: note.play_onset,
        measure: String(note.play_measure_number),
        pitches: [],
      };
      if (note.pitch && !group.pitches.includes(note.pitch.midi))
        group.pitches.push(note.pitch.midi);
      map.set(key, group);
    }
    return [...map.values()];
  }, [sequence]);
  const expected = groups[waitIndex];
  const unknownStaves = useMemo(() => {
    const values = new Map<
      string,
      {
        part: string;
        staff: number;
        label: string;
        hand: string;
      }
    >();
    for (const event of score?.parsed.events || []) {
      if (!event.pitch) continue;
      const key = `${event.part_id}:${event.staff}`;
      if (!values.has(key)) {
        const name =
          score?.parsed.parts.find((part) => part.id === event.part_id)?.name || event.part_id;
        values.set(key, {
          part: event.part_id,
          staff: event.staff,
          label: `${name} · ${event.staff}-satr`,
          hand: score?.hand_overrides?.[event.id] || event.hand,
        });
      }
    }
    return [...values.values()];
  }, [score]);
  const stop = useCallback(() => {
    setPlaying(false);
    audio.stop();
  }, [audio]);
  function choose(value: Score) {
    stop();
    setWait(false);
    setScore(value);
    currentScoreId.current = value.id;
    const section = value.sections?.find((item) => item.id === sectionId);
    const explicitRange =
      !lessonId &&
      requestedRange &&
      requestedRange[0] >= 0 &&
      requestedRange[1] < value.parsed.measures.length
        ? [requestedRange[0] + 1, requestedRange[1] + 1]
        : null;
    setFocusSeconds(!lessonId ? requestedSeconds || null : null);
    setRangeState(
      section
        ? [section.start_index + 1, section.end_index + 1]
        : explicitRange || [1, value.parsed.measures.length],
    );
    setBpm(
      Math.max(20, Math.min(240, tempoOverride?.bpm || value.parsed.metadata.tempo?.bpm || 60)),
    );
    setHand('both');
    setActiveQuarter(null);
    setPosition(0);
    pausedAt.current = 0;
    playQuarter.current = 0;
    setWaitIndex(0);
    setMatched([]);
    setWaitMessage('');
  }
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError('');
    setScore(null);
    setScores([]);
    onPresence(false);
    stop();
    setWait(false);
    latestScoreRequest.invalidate();
    if (!online || !arrangementId) {
      setLoading(false);
      return;
    }
    void (async () => {
      try {
        const list = await repository.list(arrangementId);
        if (cancelled) return;
        const values = list;
        setScores(values);
        onPresence(values.length > 0);
        const target = values.find((item) => item.id === scoreId) || values[0];
        const selected =
          lessonId || target
            ? await latestScoreRequest.run(() =>
                lessonId ? repository.lesson(lessonId) : repository.get(target!.id),
              )
            : null;
        if (!cancelled && selected) choose(selected);
      } catch {
        if (!cancelled) setError('Nota ish maydoni yuklanmadi. Serverga ulanishni tekshiring.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
      latestScoreRequest.invalidate();
      stop();
    };
  }, [
    composition.id,
    arrangementId,
    online,
    lessonId,
    scoreId,
    sectionId,
    requestedRange,
    requestedTempo,
    requestedSeconds,
  ]);
  useEffect(() => {
    onSettingsChange(bpm, hand);
  }, [bpm, hand]);
  useEffect(() => {
    stop();
    setActiveQuarter(null);
    setPosition(0);
    pausedAt.current = 0;
    playQuarter.current = 0;
    setWait(false);
    setWaitIndex(0);
    waitIndexRef.current = 0;
    setMatched([]);
    matchedRef.current = [];
    setWaitMessage('');
  }, [hand, range, score?.id]);
  const tempoMap = useMemo(
    () =>
      sequence
        ? scaleTempoMap(sequence.tempo_map, quarterBpm, score?.parsed.metadata.tempo.quarter_bpm)
        : [],
    [sequence, quarterBpm],
  );
  const playbackDuration = sequence ? quarterToSeconds(sequence.length, tempoMap) : 0;
  const tempoClock = useMemo(() => createTempoClock(tempoMap), [tempoMap]);
  useEffect(() => {
    pausedAt.current = tempoClock.quarterToSeconds(playQuarter.current);
  }, [tempoClock]);
  useEffect(() => {
    if (!playing || !sequence?.length || !score) return;
    const duration = playbackDuration;
    const startedAt = audio.currentTime() + 0.06 - pausedAt.current;
    let scheduledUntil = audio.currentTime(),
      frame = 0,
      ended = false;
    const clicks = sequence.occurrences.flatMap((item) => {
      const values: {
        play_onset: number;
        accent: boolean;
      }[] = [];
      for (const offset of measureClickOffsets(
        item.measure.time,
        item.measure.length_quarters,
        item.measure.meter_offset_quarters || 0,
      ))
        values.push({
          play_onset: item.onset + offset,
          accent: offset === 0 && !(item.measure.meter_offset_quarters || 0),
        });
      return values;
    });
    const audioNotes = audioTimelineNotes(sequence);
    const resumeQuarter = secondsToQuarter(pausedAt.current, tempoMap);
    for (const voice of activeNotesAtQuarter(audioNotes, resumeQuarter)) {
      if (!voice.note.pitch) continue;
      const end = quarterToSeconds(resumeQuarter + voice.sound_remaining_quarters, tempoMap);
      audio.sound(
        voice.note.pitch.midi,
        startedAt + pausedAt.current,
        Math.max(0, end - pausedAt.current),
      );
    }
    const schedule = () => {
      if (ended) return;
      const now = audio.currentTime(),
        horizon = now + 0.12,
        from = Math.max(scheduledUntil, now - 0.01);
      for (const { event: note, when } of attacksInTempoWindow(
        audioNotes,
        tempoMap,
        duration,
        startedAt,
        from,
        horizon,
      )) {
        if (!note.pitch) continue;
        const timing = playbackNoteTiming(note, tempoMap);
        const boundary = startedAt + duration;
        const start = Math.max(now, when);
        audio.sound(
          note.pitch.midi,
          start,
          Math.max(0, Math.min(timing.sound_duration - (start - when), boundary - start)),
        );
      }
      if (click)
        for (const { event: item, when } of attacksInTempoWindow(
          clicks,
          tempoMap,
          duration,
          startedAt,
          from,
          horizon,
        )) {
          audio.sound(
            item.accent ? 1100 : 750,
            Math.max(now, when),
            Math.max(0, Math.min(0.04, startedAt + duration - Math.max(now, when))),
            true,
          );
        }
      scheduledUntil = horizon;
      if (now >= startedAt + duration) {
        ended = true;
        audio.stop();
        pausedAt.current = 0;
        setPlaying(false);
        setPosition(100);
      }
    };
    const update = () => {
      const elapsed = Math.max(0, audio.currentTime() - startedAt);
      const seconds = Math.min(duration, elapsed);
      pausedAt.current = seconds;
      const quarter = Math.min(sequence.length, secondsToQuarter(seconds, tempoMap));
      playQuarter.current = quarter;
      const occurrence = [...sequence.occurrences].reverse().find((item) => item.onset <= quarter);
      if (occurrence) {
        setActiveQuarter(occurrence.measure.start_quarters + quarter - occurrence.onset);
        setActiveMeasure(String(occurrence.measure.number));
      }
      setPosition(Math.min(100, (quarter / sequence.length) * 100));
      if (!ended) frame = requestAnimationFrame(update);
    };
    schedule();
    const scheduler = setInterval(schedule, 25);
    frame = requestAnimationFrame(update);
    return () => {
      ended = true;
      clearInterval(scheduler);
      cancelAnimationFrame(frame);
      audio.stop();
    };
  }, [playing, score, sequence, tempoMap, playbackDuration, unitLength, click, audio]);
  useEffect(() => {
    if (wait && expected) {
      setActiveQuarter(expected.sourceQuarter);
      setActiveMeasure(expected.measure);
    }
  }, [wait, expected]);
  useEffect(() => {
    noteHandler.current = (pitch, source) => {
      setMidiNote(`${pitchLabel(pitch)} · ${source}`);
      const index = waitIndexRef.current;
      const group = groups[index];
      if (!wait || !group) return;
      if (!group.pitches.includes(pitch)) {
        setWaitMessage(
          `${pitchLabel(pitch)} — bu joyda ${group.pitches.map(pitchLabel).join(' + ')} kutilmoqda`,
        );
        return;
      }
      const next = [...new Set([...matchedRef.current, pitch])];
      matchedRef.current = next;
      setMatched(next);
      if (group.pitches.every((note) => next.includes(note))) {
        setWaitMessage(
          index + 1 === groups.length
            ? 'Parcha yakunlandi. Tovush balandliklari tekshirildi.'
            : 'To‘g‘ri. Keyingi tovushlar.',
        );
        waitIndexRef.current = index + 1;
        setWaitIndex(index + 1);
        setMatched([]);
        matchedRef.current = [];
        const nextQuarter = groups[index + 1]?.playQuarter ?? sequence?.length ?? 0;
        playQuarter.current = nextQuarter;
        pausedAt.current = tempoClock.quarterToSeconds(nextQuarter);
        setPosition(sequence?.length ? (nextQuarter / sequence.length) * 100 : 0);
        if (index + 1 === groups.length) setActiveQuarter(null);
      } else
        setWaitMessage(
          `Yana: ${group.pitches
            .filter((note) => !next.includes(note))
            .map(pitchLabel)
            .join(' + ')}`,
        );
    };
  }, [wait, expected, matched, waitIndex, groups, sequence, tempoClock]);
  useEffect(
    () => () => {
      stop();
      void audio.close();
      midi.close();
    },
    [stop, audio, midi],
  );
  async function togglePlayback() {
    if (playing) {
      stop();
      return;
    }
    try {
      await audio.resume();
      if (!mounted.current) return;
      if (position >= 100) {
        pausedAt.current = 0;
        playQuarter.current = 0;
        setPosition(0);
      }
      setWait(false);
      setPlaying(true);
    } catch {
      setError('Brauzerda tovushni yoqib bo‘lmadi.');
    }
  }
  async function connectMidi() {
    setConnecting(true);
    try {
      await midi.connect(
        (pitch, down) => {
          if (!mounted.current) return;
          setMidiHeldPitches((values) =>
            down ? [...new Set([...values, pitch])] : values.filter((value) => value !== pitch),
          );
          if (down) noteHandler.current(pitch, 'MIDI');
        },
        (names) =>
          setMidiStatus(
            names.length ? names.join(', ') : 'Qurilma topilmadi. USB ulanishini tekshiring.',
          ),
      );
    } catch {
      setMidiStatus('MIDI ulanishi amalga oshmadi. Ruxsat va USB kabelni tekshiring.');
    } finally {
      setConnecting(false);
    }
  }
  async function importScore() {
    if (!file || !online || !rights) return;
    setImporting(true);
    setImportError('');
    try {
      const value = await repository.import({
        ...(arrangementId ? { arrangementId } : { compositionId: composition.id }),
        filename: file.name,
        title: file.name.replace(/\.(mid|midi)$/i, ''),
        bytes: await file.arrayBuffer(),
        rightsConfirmed: rights,
        exactVersionConfirmed: exact,
      });
      if (!mounted.current || currentArrangement.current !== arrangementId) return;
      setScores((values) => [value, ...values]);
      choose(value);
      onPresence(true);
      setImportOpen(false);
      setFile(null);
      setRights(false);
      setExact(false);
      void onScoreChange().catch(() =>
        setError('Darslar yuklanmadi. Serverga qayta ulanishni sinab ko‘ring.'),
      );
    } catch (problem) {
      setImportError(problem instanceof Error ? problem.message : 'MIDI import bo‘lmadi.');
    } finally {
      setImporting(false);
    }
  }
  async function classify(part: string, staff: number, value: string) {
    if (
      !score ||
      score.is_demo ||
      lessonId ||
      typeof score.id !== 'number' ||
      patching.current ||
      loading
    )
      return;
    patching.current = true;
    setUpdatingScore(true);
    const overrides = { ...score.hand_overrides };
    for (const event of score.parsed.events)
      if (event.part_id === part && event.staff === staff)
        overrides[event.id] = value as 'left' | 'right' | 'unknown';
    try {
      const updated = await repository.patch(score.id, { hand_overrides: overrides });
      if (!mounted.current || currentScoreId.current !== score.id) return;
      stop();
      setScore(updated);
      void onScoreChange().catch(() => {
        if (mounted.current)
          setError('Darslar yuklanmadi. Serverga qayta ulanishni sinab ko‘ring.');
      });
    } catch {
      if (mounted.current && currentScoreId.current === score.id)
        setError('Qo‘l taqsimoti saqlanmadi.');
    } finally {
      patching.current = false;
      if (mounted.current) setUpdatingScore(false);
    }
  }
  async function saveSection() {
    if (
      !score ||
      score.is_demo ||
      lessonId ||
      typeof score.id !== 'number' ||
      !sectionTitle.trim() ||
      patching.current ||
      loading
    )
      return;
    patching.current = true;
    setUpdatingScore(true);
    setSectionSaving(true);
    try {
      const sections = [
        ...(score.sections || []),
        {
          id: `section-${Date.now()}`,
          title: sectionTitle.trim(),
          start_index: range[0] - 1,
          end_index: range[1] - 1,
          notes: '',
        },
      ];
      const updated = await repository.patch(score.id, { sections });
      if (!mounted.current || currentScoreId.current !== score.id) return;
      setScore(updated);
      setSectionTitle('');
      void onScoreChange().catch(() => {
        if (mounted.current)
          setError('Darslar yuklanmadi. Serverga qayta ulanishni sinab ko‘ring.');
      });
    } catch {
      if (mounted.current && currentScoreId.current === score.id) setError('Parcha saqlanmadi.');
    } finally {
      patching.current = false;
      if (mounted.current) {
        setSectionSaving(false);
        setUpdatingScore(false);
      }
    }
  }
  const screenPitches = expected
    ? [...new Set([...expected.pitches, expected.pitches[0] - 1, expected.pitches[0] + 1])].sort(
        (a, b) => a - b,
      )
    : [];
  async function selectVersion(id: string) {
    stop();
    setWait(false);
    setLoading(true);
    setError('');
    let settledCurrent = false;
    try {
      const selected = await latestScoreRequest.run(() => repository.get(id));
      if (mounted.current && selected) {
        settledCurrent = true;
        choose(selected);
      }
    } catch {
      settledCurrent = true;
      if (mounted.current) setError('MIDI versiyasi yuklanmadi.');
    } finally {
      if (mounted.current && settledCurrent) setLoading(false);
    }
  }
  function seek(next: number) {
    stop();
    setWait(false);
    const quarter = ((sequence?.length || 0) * next) / 100;
    playQuarter.current = quarter;
    pausedAt.current = quarterToSeconds(quarter, tempoMap);
    const occurrence = [...(sequence?.occurrences || [])]
      .reverse()
      .find((item) => item.onset <= quarter);
    setActiveQuarter(
      occurrence ? occurrence.measure.start_quarters + quarter - occurrence.onset : null,
    );
    setActiveMeasure(occurrence ? String(occurrence.measure.number) : '');
    setPosition(next);
  }
  function startWait() {
    stop();
    setWait((value) => !value);
    setWaitIndex(0);
    waitIndexRef.current = 0;
    setMatched([]);
    matchedRef.current = [];
    setWaitMessage('');
    playQuarter.current = 0;
    pausedAt.current = 0;
    setPosition(0);
  }
  function pressScreen(pitch: number) {
    noteHandler.current(pitch, 'ekran');
    setScreenHeldPitches((values) => [...new Set([...values, pitch])]);
    const previous = screenTimers.current.get(pitch);
    if (previous) clearTimeout(previous);
    screenTimers.current.set(
      pitch,
      setTimeout(() => {
        screenTimers.current.delete(pitch);
        if (mounted.current)
          setScreenHeldPitches((values) => values.filter((value) => value !== pitch));
      }, 150),
    );
    void audio
      .resume()
      .then(() => {
        if (mounted.current) audio.sound(pitch, audio.currentTime(), 0.3);
      })
      .catch(() => {
        if (mounted.current) setError('Brauzerda tovushni yoqib bo‘lmadi.');
      });
  }
  const viewQuarter = wait
    ? (expected?.playQuarter ?? sequence?.length ?? 0)
    : ((sequence?.length || 0) * position) / 100;
  const sourceClock = useMemo(() => createTempoClock(sequence?.tempo_map || []), [sequence]);
  const elapsedTime = playbackTimeLabel(sourceClock.quarterToSeconds(viewQuarter));
  const totalTime = playbackTimeLabel(sequence?.duration_seconds || 0);
  const positionTimeLabel = (value: number) =>
    `${playbackTimeLabel(sourceClock.quarterToSeconds(((sequence?.length || 0) * Math.max(0, Math.min(100, value))) / 100))} / ${totalTime}`;
  return {
    tr,
    scores,
    score,
    loading,
    error,
    importOpen,
    setImportOpen,
    file,
    setFile,
    rights,
    setRights,
    exact,
    setExact,
    importing,
    importError,
    setImportError,
    bpm,
    setBpm,
    hand,
    setHand,
    range,
    setRange,
    playing,
    click,
    setClick,
    activeMeasure,
    position,
    sequence,
    tempoMap,
    wait,
    groups,
    playbackSupported,
    waitIndex,
    matched,
    expected,
    waitMessage,
    screenPitches,
    midiStatus,
    midiNote,
    connecting,
    connectMidi,
    sectionTitle,
    setSectionTitle,
    sectionSaving,
    updatingScore,
    importScore,
    classify,
    saveSection,
    togglePlayback,
    unknownStaves,
    arrangementId,
    unitLabel,
    quarterBpm,
    selectVersion,
    seek,
    startWait,
    pressScreen,
    heldPitches,
    viewQuarter,
    elapsedTime,
    totalTime,
    positionTimeLabel,
  };
}
