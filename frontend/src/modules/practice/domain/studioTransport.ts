import { createTempoClock, type Score } from './score.ts';
import type {
  StudioNote,
  StudioTimeline,
  PlaybackWindow,
} from './entities/studio-transport.types.ts';
export type {
  StudioNote,
  StudioTimeline,
  PlaybackWindow,
} from './entities/studio-transport.types.ts';

export function studioTimeline(score: Score): StudioTimeline {
  const clock = createTempoClock(
    score.parsed.tempo_map?.length
      ? score.parsed.tempo_map
      : [{ onset_quarters: 0, quarter_bpm: score.parsed.metadata.tempo.quarter_bpm }],
  );
  const notes = score.parsed.events
    .filter((event) => event.pitch && !event.rest && !event.percussion)
    .map((event) => {
      const onset = event.onset_seconds ?? clock.quarterToSeconds(event.onset_quarters);
      const duration =
        event.duration_seconds ??
        clock.quarterToSeconds(event.onset_quarters + event.duration_quarters) - onset;
      return {
        id: event.id,
        pitch: event.pitch!.midi,
        hand: event.hand === 'left' ? ('left' as const) : ('right' as const),
        onset,
        duration,
        soundDuration:
          event.sound_duration_seconds ??
          clock.quarterToSeconds(
            event.onset_quarters + (event.sound_duration_quarters ?? event.duration_quarters),
          ) - onset,
        velocity: event.velocity ?? 85,
      };
    })
    .filter(
      (note) =>
        note.pitch >= 21 &&
        note.pitch <= 108 &&
        Number.isFinite(note.onset) &&
        Number.isFinite(note.duration) &&
        note.duration > 0,
    )
    .sort((a, b) => a.onset - b.onset);
  return {
    notes,
    duration: Math.max(
      score.parsed.metadata.duration_seconds || 0,
      ...notes.map((note) => note.onset + note.soundDuration),
      0.01,
    ),
  };
}

export class StudioTransport {
  duration: number;
  speed = 1;
  playing = false;
  private anchorPosition = 0;
  private anchorTime = 0;
  constructor(duration: number, initialPosition = 0) {
    this.duration = Math.max(0.01, Number.isFinite(duration) ? duration : 0.01);
    this.anchorPosition = this.clamp(initialPosition);
  }
  private clamp(value: number) {
    return Math.max(0, Math.min(this.duration, Number.isFinite(value) ? value : 0));
  }
  snapshot(now: number) {
    if (!this.playing) return { position: this.anchorPosition, ended: false };
    const position = this.anchorPosition + Math.max(0, now - this.anchorTime) * this.speed;
    return { position: Math.min(position, this.duration), ended: position >= this.duration };
  }
  play(now: number) {
    if (this.anchorPosition >= this.duration - 0.001) this.anchorPosition = 0;
    this.anchorTime = now;
    this.playing = true;
  }
  pause(now: number) {
    this.anchorPosition = this.snapshot(now).position;
    this.anchorTime = now;
    this.playing = false;
  }
  seek(position: number, now: number) {
    this.anchorPosition = this.clamp(position);
    this.anchorTime = now;
  }
  setSpeed(speed: number, now: number) {
    this.seek(this.snapshot(now).position, now);
    this.speed = Math.max(0.2, Math.min(2, Number.isFinite(speed) ? speed : 1));
  }
  /** Half-open scheduling windows stop at the source's final release. */
  windows(from: number, until: number): PlaybackWindow[] {
    if (!this.playing || until <= from) return [];
    const wallEnd = this.anchorTime + (this.duration - this.anchorPosition) / this.speed;
    const begin = Math.max(this.anchorTime, from);
    const end = Math.min(wallEnd, until);
    if (end <= begin + 1e-9) return [];
    return [
      {
        sourceFrom: this.anchorPosition + (begin - this.anchorTime) * this.speed,
        sourceTo: this.anchorPosition + (end - this.anchorTime) * this.speed,
        wallFrom: begin,
        speed: this.speed,
        resume: Math.abs(begin - this.anchorTime) < 1e-8,
        sourceEnd: this.duration,
      },
    ];
  }
}

export function notesForWindow(notes: StudioNote[], window: PlaybackWindow) {
  return notes.flatMap((note) => {
    const resume =
      window.resume &&
      note.onset < window.sourceFrom - 1e-8 &&
      note.onset + note.soundDuration > window.sourceFrom;
    if (!resume && (note.onset < window.sourceFrom - 1e-8 || note.onset >= window.sourceTo - 1e-8))
      return [];
    const start = Math.max(note.onset, window.sourceFrom);
    const end = Math.min(note.onset + note.soundDuration, window.sourceEnd);
    return end > start
      ? [
          {
            note,
            when: window.wallFrom + (start - window.sourceFrom) / window.speed,
            duration: (end - start) / window.speed,
            offset: Math.max(0, start - note.onset),
            speed: window.speed,
          },
        ]
      : [];
  });
}

export const pianoKeys = Array.from({ length: 88 }, (_, index) => index + 21);

export function pianoKeyLayout(width: number, low = 21, high = 108) {
  const visible = pianoKeys.filter((pitch) => pitch >= low && pitch <= high);
  const whiteCount = visible.filter((pitch) => [0, 2, 4, 5, 7, 9, 11].includes(pitch % 12)).length;
  const whiteWidth = width / Math.max(1, whiteCount);
  let count = 0;
  return visible.map((pitch) => {
    const white = [0, 2, 4, 5, 7, 9, 11].includes(pitch % 12);
    return {
      pitch,
      white,
      x: white ? count++ * whiteWidth : count * whiteWidth - whiteWidth * 0.31,
      width: white ? whiteWidth : whiteWidth * 0.62,
    };
  });
}
