export type Hand = 'left' | 'right' | 'unknown';

export type TempoMapEntry = {
  onset_quarters: number;
  quarter_bpm: number;
  onset_seconds?: number;
  onset_ticks?: number;
  microseconds_per_quarter?: number;
  bpm?: number;
  beat_unit?: string;
  explicit?: boolean;
};

export type ScoreTempo = {
  quarter_bpm: number;
  beat_unit: string;
  bpm: number;
  beat_unit_dots: number;
  explicit?: boolean;
};

export type ScoreMeter = {
  beats: string;
  beat_type: number;
  provenance?: string;
  length_quarters?: number;
};

export type MidiControlEvent = {
  onset_quarters: number;
  onset_seconds?: number;
  onset_ticks?: number;
  channel: number;
  track_index: number;
  port?: number;
  controller: number;
  value: number;
  down?: boolean;
  reset_controllers?: boolean;
};

export type ScoreEvent = {
  id: string;
  part_id: string;
  measure_index: number;
  measure_number: string;
  offset_quarters: number;
  onset_quarters: number;
  duration_quarters: number;
  pitch: {
    step: string;
    alter: number;
    octave: number;
    midi: number;
    spelling_basis?: string;
  } | null;
  staff: number;
  voice: string;
  hand: Hand;
  rest: boolean;
  chord: boolean;
  grace: boolean;
  ties: string[];
  cue?: boolean;
  onset_seconds?: number;
  duration_seconds?: number;
  sound_duration_quarters?: number;
  sound_duration_seconds?: number;
  source_onset_quarters?: number;
  source_onset_seconds?: number;
  start_ticks?: number;
  end_ticks?: number;
  sound_end_ticks?: number;
  velocity?: number;
  channel?: number;
  track_index?: number;
  port?: number;
  percussion?: boolean;
  hand_evidence?: string;
  end_reason?: string;
  provenance?: string;
};

export type ScoreMeasure = {
  index: number;
  number: string;
  start_quarters: number;
  length_quarters: number;
  meter_offset_quarters?: number;
  time: ScoreMeter | null;
  tempos?: {
    offset_quarters: number;
    quarter_bpm: number;
    beat_unit?: string;
    bpm?: number;
    beat_unit_dots?: number;
  }[];
  start_seconds?: number;
  end_seconds?: number;
  provenance?: string;
};

export type Score = {
  id: number | string;
  version: number;
  arrangement_id?: number;
  arrangement_label?: string;
  title: string;
  is_demo?: boolean;
  exact_version_confirmed?: boolean;
  musicxml_url: string;
  file_format?: 'musicxml' | 'midi';
  file_url?: string;
  source_url?: string;
  source_provenance?: Record<string, unknown>;
  completeness_verified_at?: string | null;
  original_filename?: string;
  content_sha256?: string;
  rights_note?: string;
  rights_basis?: string;
  rights_confirmed_at?: string;
  created_at?: string;
  hand_overrides?: Record<string, Hand>;
  sections?: { id: string; title: string; start_index: number; end_index: number; notes: string }[];
  parsed: {
    metadata: {
      title: string;
      composer: string;
      part_count: number;
      measure_count: number;
      event_count: number;
      time: ScoreMeter | null;
      tempo: ScoreTempo;
      total_quarters?: number;
      duration_seconds?: number;
      file_end_ticks?: number;
      ticks_per_beat?: number;
      source_format?: string;
      notation_available?: boolean;
      window_basis?: string;
      key?: unknown;
    };
    events: ScoreEvent[];
    measures: ScoreMeasure[];
    playback_order: number[];
    warnings: string[];
    capabilities: Record<string, unknown>;
    parts: {
      id: string;
      name: string;
      staff_count: number;
      hand?: Hand;
      hand_evidence?: string;
      channels?: number[];
      programs?: Record<string, number>;
    }[];
    source_format?: 'musicxml' | 'midi';
    tempo_map?: TempoMapEntry[];
    pedal_events?: MidiControlEvent[];
    control_events?: MidiControlEvent[];
    fragment?: {
      source_score_id: number;
      start_seconds: number;
      end_seconds: number;
      start_quarters: number;
      end_quarters: number;
      event_ids: string[];
    };
  };
};

export type PlaybackNote = ScoreEvent & {
  play_onset: number;
  play_duration: number;
  play_sound_duration: number;
  play_source_onset: number;
  play_measure_index: number;
  play_measure_number: string;
  resumed_at_boundary?: boolean;
};

export type PlaybackSequence = {
  notes: PlaybackNote[];
  sustained_at_start: PlaybackNote[];
  occurrences: { measure: ScoreMeasure; onset: number }[];
  length: number;
  tempo_map: TempoMapEntry[];
  duration_seconds: number;
  source_start_quarters: number;
};

export type RequestedTempo = { bpm: number; beat_unit: string };

export type TempoClock = {
  quarterToSeconds(quarter: number): number;
  secondsToQuarter(seconds: number): number;
};
