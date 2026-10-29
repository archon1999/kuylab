import { createSampledPiano } from '../src/modules/practice/data-access/adapters/sampled-piano.adapter';
import {
  StudioTransport,
  notesForWindow,
  pianoKeyLayout,
  type StudioNote,
} from '../src/modules/practice/domain/studioTransport';
import { demoNotes, demoSource } from './demo-score.mjs';

/** Standalone public composition root. No React or private account state. */
export function mountLandingDemo(host: HTMLElement) {
  const canvas = host.querySelector<HTMLCanvasElement>('canvas')!;
  const context = canvas.getContext('2d')!;
  const audio = createSampledPiano();
  const transport = new StudioTransport(demoSource.duration);
  const notes: StudioNote[] = demoNotes.map(
    ([pitch, onset, duration, velocity, hand, soundDuration], index) => ({
      id: `landing:${index}`,
      pitch,
      onset,
      duration,
      velocity,
      hand: hand === 0 ? 'left' : 'right',
      soundDuration,
    }),
  );
  const toggle = host.querySelector<HTMLButtonElement>('[data-demo-toggle]')!;
  const start = host.querySelector<HTMLButtonElement>('[data-demo-start]')!;
  const progress = host.querySelector<HTMLElement>('[data-demo-progress]')!;
  const clock = host.querySelector<HTMLElement>('[data-demo-clock]')!;
  const error = host.querySelector<HTMLElement>('[data-demo-error]')!;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let ticket = 0,
    timer: ReturnType<typeof setInterval> | undefined,
    frame = 0,
    width = 1,
    height = 1;
  let cursor = 0,
    resume = true,
    loading = false,
    muted = false;
  audio.volume(0.55);
  audio.reverb(0.2);
  const name = (pitch: number) =>
    ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B'][pitch % 12];
  const color = (note: StudioNote) => (note.hand === 'left' ? '#c978a1' : '#78b7de');
  const state = (value: string) => {
    host.dataset.state = value;
    host.setAttribute('aria-busy', String(value === 'loading'));
    toggle.disabled = start.disabled = value === 'loading';
    toggle.setAttribute('aria-label', host.dataset[value === 'playing' ? 'pause' : 'play']!);
    start.setAttribute('aria-label', host.dataset[value === 'ended' ? 'completed' : 'play']!);
    error.hidden = value !== 'error';
  };
  function draw() {
    const position = transport.snapshot(audio.outputTime?.() ?? audio.now()).position;
    const keyboard = Math.max(58, Math.min(84, width * 0.15));
    const top = height - keyboard,
      pixels = top / 5;
    const keys = pianoKeyLayout(width, width < 480 ? 40 : 36, width < 480 ? 81 : 84);
    const layout = new Map(keys.map((key) => [key.pitch, key]));
    const active = new Map<number, StudioNote>();
    context.setTransform(
      Math.min(devicePixelRatio || 1, 2),
      0,
      0,
      Math.min(devicePixelRatio || 1, 2),
      0,
      0,
    );
    context.clearRect(0, 0, width, height);
    context.fillStyle = '#241c37';
    context.fillRect(0, 0, width, height);
    for (const key of keys.filter((key) => key.white)) {
      context.fillStyle = '#ffffff03';
      context.fillRect(key.x, 0, key.width * 0.5, top);
      context.fillStyle = '#ffffff06';
      context.fillRect(key.x, 0, 0.5, top);
    }
    context.save();
    context.beginPath();
    context.rect(0, 0, width, top);
    context.clip();
    for (const note of notes) {
      if (note.onset > position + 5 || note.onset + note.duration < position) continue;
      const key = layout.get(note.pitch);
      if (!key) continue;
      const bottom = top - (note.onset - position) * pixels;
      const y = bottom - Math.max(7, note.duration * pixels),
        w = Math.max(4, key.width - 3);
      const gradient = context.createLinearGradient(0, y, 0, bottom);
      gradient.addColorStop(0, note.hand === 'left' ? '#f4add1' : '#a1e9f5');
      gradient.addColorStop(1, color(note));
      context.globalAlpha = Math.min(1, 0.68 + note.velocity / 360);
      context.fillStyle = gradient;
      context.shadowBlur = 7;
      context.shadowColor = color(note) + '35';
      context.beginPath();
      context.roundRect(key.x + 1.5, y, w, Math.max(7, bottom - y), Math.min(10, w / 2));
      context.fill();
      context.shadowBlur = 0;
      context.globalAlpha = 1;
      if (w >= 15 && bottom - y >= 18) {
        context.font = '700 11px Alan, InterCyr, sans-serif';
        context.textAlign = 'center';
        context.fillStyle = '#241c37';
        context.fillText(name(note.pitch), key.x + key.width / 2, bottom - 6);
      }
      if (note.onset <= position && note.onset + note.duration > position)
        active.set(note.pitch, note);
    }
    for (const [pitch, note] of active) {
      const key = layout.get(pitch)!;
      const glow = context.createRadialGradient(
        key.x + key.width / 2,
        top,
        0,
        key.x + key.width / 2,
        top,
        28,
      );
      glow.addColorStop(0, color(note) + '80');
      glow.addColorStop(1, color(note) + '00');
      context.fillStyle = glow;
      context.fillRect(key.x - 20, top - 42, key.width + 40, 45);
      const age = position - note.onset;
      if (transport.playing && !motion.matches && age < 0.45) {
        context.globalAlpha = (1 - age / 0.45) * 0.65;
        context.fillStyle = '#e1ddfa';
        context.beginPath();
        context.arc(key.x + key.width / 2, top - age * 45, 1.7, 0, Math.PI * 2);
        context.fill();
        context.globalAlpha = 1;
      }
    }
    context.restore();
    for (const white of [true, false])
      for (const key of keys.filter((key) => key.white === white)) {
        const note = active.get(key.pitch);
        context.fillStyle = note ? color(note) : white ? '#f5f1ec' : '#15101f';
        context.beginPath();
        context.roundRect(
          key.x + 0.5,
          top,
          key.width - 1,
          white ? keyboard - 1 : keyboard * 0.64,
          [0, 0, 2, 2],
        );
        context.fill();
        if (white && key.width > 13) {
          context.fillStyle = note ? '#241c37' : '#867f87';
          context.font = '600 9px Alan, sans-serif';
          context.textAlign = 'center';
          context.fillText(name(key.pitch), key.x + key.width / 2, height - 7);
        }
      }
    context.fillStyle = '#dba57e';
    context.fillRect(0, top, width, 1.4);
    progress.style.transform = `scaleX(${position / demoSource.duration})`;
    clock.textContent = `0:${String(Math.floor(position)).padStart(2, '0')}`;
  }
  const stopTimers = () => {
    clearInterval(timer);
    cancelAnimationFrame(frame);
    timer = undefined;
    frame = 0;
  };
  const render = () => {
    draw();
    if (transport.playing) frame = requestAnimationFrame(render);
  };
  const pause = () => {
    ticket++;
    loading = false;
    transport.pause(audio.outputTime?.() ?? audio.now());
    audio.stop();
    stopTimers();
    state(transport.snapshot(audio.now()).position > 0.01 ? 'paused' : 'idle');
    draw();
  };
  const schedule = () => {
    const now = audio.now();
    if (transport.snapshot(audio.outputTime?.() ?? now).ended) {
      transport.pause(now);
      stopTimers();
      state('ended');
      draw();
      return;
    }
    for (const window of transport.windows(Math.max(cursor, now), now + 0.15)) {
      window.resume ||= resume;
      resume = false;
      for (const sound of notesForWindow(notes, window))
        audio.sound(
          sound.note.pitch,
          sound.when,
          sound.duration,
          sound.note.velocity,
          sound.offset,
          sound.note.hand,
        );
    }
    cursor = now + 0.15;
  };
  const play = async () => {
    if (transport.playing || loading || document.hidden) return;
    const current = ++ticket;
    loading = true;
    state('loading');
    try {
      await audio.prepare(
        notes.map((note) => note.pitch),
        undefined,
        notes,
      );
      if (current !== ticket) return;
      const bounds = host.getBoundingClientRect();
      if (document.hidden || bounds.bottom <= 0 || bounds.top >= innerHeight) {
        pause();
        return;
      }
      loading = false;
      audio.stop();
      cursor = audio.now() + 0.025;
      resume = true;
      transport.play(cursor);
      state('playing');
      schedule();
      timer = setInterval(schedule, 25);
      render();
    } catch {
      if (current === ticket) {
        loading = false;
        audio.stop();
        state('error');
      }
    }
  };
  new ResizeObserver(() => {
    width = canvas.clientWidth;
    height = canvas.clientHeight;
    const ratio = Math.min(devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    draw();
  }).observe(canvas);
  host.dataset.canvas = 'ready';
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) pause();
  });
  if ('IntersectionObserver' in window)
    new IntersectionObserver(
      (entries) => {
        if (!entries[0].isIntersecting && (transport.playing || loading)) pause();
      },
      { threshold: 0.08 },
    ).observe(host);
  // Close resources on navigation; the adapter can reopen when returning from the back/forward cache.
  window.addEventListener('pagehide', () => {
    pause();
    audio.close();
  });
  return {
    play,
    pause,
    toggle: () => (transport.playing || loading ? pause() : play()),
    speed(value: number) {
      if (![0.5, 0.75, 1].includes(value)) return;
      transport.setSpeed(value, audio.outputTime?.() ?? audio.now());
      audio.stop();
      cursor = audio.now();
      resume = true;
      host
        .querySelectorAll<HTMLButtonElement>('[data-demo-speed]')
        .forEach((button) =>
          button.setAttribute('aria-pressed', String(Number(button.dataset.demoSpeed) === value)),
        );
      draw();
    },
    mute() {
      muted = !muted;
      audio.volume(muted ? 0 : 0.55);
      const button = host.querySelector<HTMLButtonElement>('[data-demo-mute]')!;
      button.setAttribute('aria-pressed', String(muted));
      button.setAttribute('aria-label', host.dataset[muted ? 'unmute' : 'mute']!);
    },
  };
}
