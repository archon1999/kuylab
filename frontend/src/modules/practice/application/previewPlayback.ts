import type { StudioAudioPort } from '../domain/contracts/studio-audio.port.ts';
import type { StudioPreferences } from '../domain/studioPreferences.ts';
import { StudioTransport, notesForWindow, type StudioNote } from '../domain/studioTransport.ts';
import { audioFocus, type AudioFocus } from './audioFocus.ts';

export type PreviewState = {
  playing: boolean;
  loading: boolean;
  finished: boolean;
  error: boolean;
  position: number;
  cycle: number;
  speed: number;
  progress: number;
};

/** Audio-clock preview with cancellable preparation and one shared audio owner.
 * The view animates one SVG group between these anchored state changes. */
export class PreviewPlayback {
  readonly transport: StudioTransport;
  private owner = Symbol('composition-preview');
  private generation = 0;
  private cursor = 0;
  private resumeVoices = true;
  private closeTimer: ReturnType<typeof setTimeout> | undefined;
  private notes: StudioNote[];
  private audio: StudioAudioPort;
  private changed: (state: PreviewState) => void;
  private focus: AudioFocus;
  private state: PreviewState = {
    playing: false,
    loading: false,
    finished: false,
    error: false,
    position: 0,
    cycle: 0,
    speed: 1,
    progress: 0,
  };
  constructor(
    notes: StudioNote[],
    duration: number,
    audio: StudioAudioPort,
    changed: (state: PreviewState) => void,
    focus: AudioFocus = audioFocus,
  ) {
    this.notes = notes;
    this.audio = audio;
    this.changed = changed;
    this.focus = focus;
    this.transport = new StudioTransport(duration);
  }
  snapshot() {
    return { ...this.state };
  }
  private update(value: Partial<PreviewState>) {
    this.state = { ...this.state, ...value };
    this.changed(this.snapshot());
  }
  pause = () => {
    this.generation++;
    this.transport.pause(this.audio.now());
    const position = this.transport.snapshot(this.audio.now()).position;
    this.audio.stop();
    clearTimeout(this.closeTimer);
    this.closeTimer = setTimeout(() => this.audio.close(), 25);
    this.focus.release(this.owner);
    this.update({ playing: false, loading: false, position, cycle: this.state.cycle + 1 });
  };
  settings(value: StudioPreferences) {
    this.audio.volume(value.volume / 100);
    this.audio.reverb(value.reverb / 100);
    this.audio.handVolume?.('left', value.leftVolume / 100);
    this.audio.handVolume?.('right', value.rightVolume / 100);
    if (this.transport.speed !== value.speed) {
      this.transport.setSpeed(value.speed, this.audio.now());
      if (this.state.playing) {
        this.audio.stop();
        this.cursor = this.audio.now();
        this.resumeVoices = true;
      }
      this.update({
        speed: this.transport.speed,
        position: this.transport.snapshot(this.audio.now()).position,
        cycle: this.state.cycle + 1,
      });
    }
  }
  async toggle(settings: StudioPreferences) {
    if (this.state.playing || this.state.loading) {
      this.pause();
      return;
    }
    this.focus.claim(this.owner, this.pause);
    clearTimeout(this.closeTimer);
    const ticket = ++this.generation;
    this.settings(settings);
    this.update({ loading: true, error: false, progress: 0 });
    try {
      await this.audio.prepare(
        this.notes.map((note) => note.pitch),
        (progress) => {
          if (ticket === this.generation) this.update({ progress });
        },
        this.notes,
      );
      if (ticket !== this.generation) return;
      this.audio.stop();
      this.cursor = this.audio.now();
      this.resumeVoices = true;
      this.transport.play(this.cursor);
      this.update({
        playing: true,
        loading: false,
        finished: false,
        position: this.transport.snapshot(this.cursor).position,
        cycle: this.state.cycle + 1,
      });
      this.tick();
    } catch {
      if (ticket !== this.generation) return;
      this.pause();
      this.update({ error: true });
    }
  }
  tick() {
    if (!this.state.playing) return;
    const now = this.audio.now();
    if (this.transport.snapshot(now).ended) {
      this.pause();
      this.update({ finished: true });
      return;
    }
    const until = now + 0.15;
    const throttled = now > this.cursor + 0.03;
    for (const window of this.transport.windows(Math.max(this.cursor, now), until)) {
      if (this.resumeVoices || throttled) window.resume = true;
      this.resumeVoices = false;
      for (const sound of notesForWindow(this.notes, window)) {
        this.audio.sound(
          sound.note.pitch,
          sound.when,
          sound.duration,
          sound.note.velocity,
          sound.offset,
          sound.note.hand,
        );
      }
    }
    this.cursor = until;
  }
  dispose() {
    this.generation++;
    clearTimeout(this.closeTimer);
    this.focus.release(this.owner);
    this.audio.close();
  }
}
