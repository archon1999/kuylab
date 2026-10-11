import { useEffect, useMemo, useRef } from 'react';
import { pianoKeyLayout, type StudioNote } from '../../domain/studioTransport';
import type { RollSettings } from '../../domain/studioPreferences';
import {
  allowsStrikeEffects,
  brighten,
  isContinuousStep,
  noteShading,
  StrikeParticlePool,
} from './rollVisuals';
export type { RollSettings } from '../../domain/studioPreferences';

const noteName = (pitch: number) =>
  ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B'][pitch % 12];
export default function StudioRoll({
  notes,
  position,
  playing,
  reducedMotion,
  settings,
  dark,
  label,
}: {
  notes: StudioNote[];
  position: number;
  playing: boolean;
  reducedMotion: boolean;
  settings: RollSettings;
  dark: boolean;
  label: string;
}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const frames = useMemo(
    () => notes.map((note) => ({ ...note, end: note.onset + note.duration })),
    [notes],
  );
  const current = useRef({ position, playing, reducedMotion, settings, dark });
  current.current = { position, playing, reducedMotion, settings, dark };
  useEffect(() => {
    const element = canvas.current;
    if (!element) return;
    const ctx = element.getContext('2d');
    if (!ctx) return;
    let frame = 0,
      width = 0,
      height = 0;
    let lastPosition = current.current.position;
    let lastPlaying = false;
    let lastDark = current.current.dark;
    let lastMotion = current.current.reducedMotion;
    let lastSettings: RollSettings | null = null;
    let dirty = true;
    let particlesVisible = false;
    const pitches = notes.map((note) => note.pitch);
    // White-key boundaries keep edge accidentals intact. Range stays fixed during playback.
    const low = Math.max(21, Math.floor((Math.min(60, ...pitches) - 2) / 12) * 12);
    const high = Math.min(108, Math.ceil((Math.max(72, ...pitches) + 2) / 12) * 12 - 1);
    let keys = pianoKeyLayout(0);
    let whiteKeys = keys.filter((key) => key.white);
    let blackKeys = keys.filter((key) => !key.white);
    const byPitch = new Array<(typeof keys)[number] | undefined>(128);
    const pressed = new Array<string | undefined>(128);
    let shades: ReturnType<typeof noteShading>[] = [];
    const particles = new StrikeParticlePool(144);
    const halos = new Map<string, HTMLCanvasElement>();
    let glowColors = { left: '', right: '' };
    const halo = (color: string) => {
      const cached = halos.get(color);
      if (cached) return cached;
      const sprite = document.createElement('canvas');
      sprite.width = sprite.height = 40;
      const brush = sprite.getContext('2d')!;
      const glow = brush.createRadialGradient(20, 20, 0, 20, 20, 20);
      glow.addColorStop(0, color + '80');
      glow.addColorStop(0.3, color + '40');
      glow.addColorStop(1, color + '00');
      brush.fillStyle = glow;
      brush.fillRect(0, 0, 40, 40);
      halos.set(color, sprite);
      return sprite;
    };
    const fontFamily = getComputedStyle(element).fontFamily;
    const render = (milliseconds: number) => {
      const now = milliseconds / 1000;
      const { position, playing, reducedMotion, settings, dark } = current.current;
      const effects = allowsStrikeEffects(playing, settings.particles, reducedMotion);
      const moved = position !== lastPosition;
      const continuous = isContinuousStep(lastPosition, position);
      const freshStart = playing && !lastPlaying && position < 0.05;
      if (!effects || (moved && !continuous)) particles.clear();
      const activeParticles = particles.hasActive(now);
      const changed =
        particlesVisible !== activeParticles ||
        dirty ||
        moved ||
        settings !== lastSettings ||
        dark !== lastDark ||
        playing !== lastPlaying ||
        reducedMotion !== lastMotion;
      if ((!changed && !activeParticles) || width < 1 || height < 1) {
        frame = requestAnimationFrame(render);
        return;
      }
      if (settings !== lastSettings || dark !== lastDark) {
        halos.clear();
        glowColors = {
          left: noteShading(settings.leftColor, 85, true, dark).top,
          right: noteShading(settings.rightColor, 85, true, dark).top,
        };
        shades = frames.map((note) =>
          noteShading(
            note.hand === 'left' ? settings.leftColor : settings.rightColor,
            note.velocity,
            settings.velocityGradients,
            dark,
          ),
        );
      }
      const attackFrom = freshStart ? -0.001 : lastPosition;
      lastPosition = position;
      lastPlaying = playing;
      lastDark = dark;
      lastSettings = settings;
      lastMotion = reducedMotion;
      dirty = false;
      particlesVisible = activeParticles;
      const ratio = Math.min(devicePixelRatio || 1, 2);
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      ctx.globalAlpha = 1;
      ctx.clearRect(0, 0, width, height);
      const background = ctx.createLinearGradient(0, 0, 0, height);
      background.addColorStop(0, dark ? '#231b38' : '#faf8f5');
      background.addColorStop(1, dark ? '#2b2143' : '#f4f0ea');
      ctx.fillStyle = background;
      ctx.fillRect(0, 0, width, height);
      const keyboardHeight = Math.max(86, Math.min(152, height * 0.23));
      const keyboardTop = height - keyboardHeight;
      const pixels = keyboardTop / settings.lookahead;
      pressed.fill(undefined);
      ctx.save();
      ctx.beginPath();
      ctx.rect(0, 0, width, keyboardTop);
      ctx.clip();
      for (const key of keys)
        if (key.pitch % 12 === 0) {
          ctx.fillStyle = dark ? '#f5edc908' : '#85634606';
          ctx.fillRect(key.x, 0, 1, keyboardTop);
        }
      for (let index = 0; index < frames.length; index++) {
        const note = frames[index];
        if (note.onset > position + settings.lookahead) break;
        if (!settings[note.hand]) continue;
        const key = byPitch[note.pitch];
        if (!key) continue;
        const color = note.hand === 'left' ? settings.leftColor : settings.rightColor;
        const shade = shades[index];
        if (
          effects &&
          (continuous || freshStart) &&
          note.onset > attackFrom &&
          note.onset <= position
        ) {
          particles.emit(
            key.x + key.width / 2,
            keyboardTop,
            glowColors[note.hand],
            note.velocity,
            now,
            key.width,
          );
        }
        if (note.end < position) continue;
        const bottom = keyboardTop - (note.onset - position) * pixels;
        const top = bottom - Math.max(8, note.duration * pixels);
        const x = key.x + 1.25;
        const noteWidth = Math.max(3, key.width - 2.5);
        const gradient = ctx.createLinearGradient(0, top, 0, bottom);
        gradient.addColorStop(0, shade.top);
        gradient.addColorStop(1, shade.bottom);
        ctx.globalAlpha = shade.opacity;
        ctx.fillStyle = gradient;
        if (settings.shadows) {
          ctx.shadowColor = shade.bottom + (dark ? '70' : '28');
          ctx.shadowBlur = dark ? 8 + shade.strength * 5 : 4;
          ctx.shadowOffsetY = 2;
        }
        ctx.beginPath();
        ctx.roundRect(x, top, noteWidth, Math.max(8, bottom - top), Math.min(16, noteWidth / 2));
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.shadowOffsetY = 0;
        ctx.strokeStyle = dark ? '#ffffff30' : '#ffffff70';
        ctx.lineWidth = 0.7;
        ctx.stroke();
        ctx.globalAlpha = 1;
        if (settings.noteNames && noteWidth >= 9 && bottom - top >= 18) {
          ctx.fillStyle = '#211a31';
          ctx.font = `700 ${Math.min(14, Math.max(8, noteWidth * 0.48))}px ${fontFamily}`;
          ctx.textAlign = 'center';
          // Keep the label on the falling block; the keyboard clips it at impact.
          ctx.fillText(noteName(note.pitch), x + noteWidth / 2, bottom - 7);
        }
        if (note.onset <= position && note.end > position) pressed[note.pitch] = shade.bottom;
      }
      for (const key of keys) {
        const held = pressed[key.pitch];
        if (!held) continue;
        const glow = ctx.createLinearGradient(0, keyboardTop - 36, 0, keyboardTop);
        glow.addColorStop(0, held + '00');
        glow.addColorStop(0.65, held + (dark ? '25' : '15'));
        glow.addColorStop(1, held + (dark ? '85' : '45'));
        ctx.fillStyle = glow;
        ctx.fillRect(key.x - 3, keyboardTop - 36, key.width + 6, 36);
        ctx.fillStyle = brighten(held, 0.4) + (dark ? 'b0' : '80');
        ctx.fillRect(key.x + 1, keyboardTop - 2, key.width - 2, 2);
      }
      if (effects) {
        for (const particle of particles.particles) {
          const age = now - particle.born;
          if (particle.life <= 0 || age < 0 || age >= particle.life) continue;
          const fade = 1 - age / particle.life;
          const x = particle.x + particle.vx * age;
          const y = particle.y + particle.vy * age + 18 * age * age;
          const radius = particle.radius * (0.6 + fade * 0.4);
          ctx.globalAlpha = fade * fade * (dark ? 0.8 : 0.55);
          if (settings.shadows) {
            const size = radius * 6;
            ctx.drawImage(halo(particle.color), x - size, y - size, size * 2, size * 2);
          }
          ctx.fillStyle = particle.color;
          ctx.beginPath();
          ctx.arc(x, y, radius, 0, Math.PI * 2);
          ctx.fill();
          ctx.globalAlpha *= 0.22;
          ctx.beginPath();
          ctx.arc(x, y, radius * 2.2, 0, Math.PI * 2);
          ctx.lineWidth = 0.8;
          ctx.strokeStyle = particle.color;
          ctx.stroke();
        }
      }
      ctx.globalAlpha = 1;
      ctx.restore();
      for (const key of whiteKeys) {
        const held = pressed[key.pitch];
        const gradient = ctx.createLinearGradient(0, keyboardTop, 0, height);
        gradient.addColorStop(0, held ? brighten(held, 0.18) : dark ? '#d8d0e5' : '#faf9f7');
        gradient.addColorStop(0.82, held || (dark ? '#f2edf7' : '#fffdfa'));
        gradient.addColorStop(1, held ? brighten(held, 0.05) : dark ? '#c9bfd8' : '#e6e1db');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.roundRect(key.x + 0.5, keyboardTop, key.width - 0.9, keyboardHeight - 1, [0, 0, 3, 3]);
        ctx.fill();
        ctx.fillStyle = dark ? '#18122b35' : '#00000015';
        ctx.fillRect(key.x, keyboardTop, 1, keyboardHeight);
        if (settings.keyNames) {
          ctx.fillStyle = held ? '#211a31' : dark ? '#776b88' : '#98918b';
          ctx.textAlign = 'center';
          ctx.font = `600 ${Math.min(12, Math.max(7, key.width * 0.42))}px ${fontFamily}`;
          ctx.fillText(noteName(key.pitch), key.x + key.width / 2, height - 10);
        }
      }
      for (const key of blackKeys) {
        const held = pressed[key.pitch];
        const blackHeight = keyboardHeight * 0.66;
        const gradient = ctx.createLinearGradient(key.x, 0, key.x + key.width, 0);
        gradient.addColorStop(0, held || (dark ? '#110c1d' : '#16131a'));
        gradient.addColorStop(0.5, held ? brighten(held, 0.12) : dark ? '#2c2240' : '#2b272f');
        gradient.addColorStop(1, held || (dark ? '#0c0814' : '#0b090f'));
        ctx.shadowColor = '#00000055';
        ctx.shadowBlur = settings.shadows ? 4 : 0;
        ctx.shadowOffsetY = 3;
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.roundRect(key.x, keyboardTop, key.width, blackHeight, [0, 0, 3, 3]);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.shadowOffsetY = 0;
        ctx.fillStyle = '#ffffff0c';
        ctx.fillRect(key.x + 1, keyboardTop, Math.max(1, key.width - 2), blackHeight - 7);
        if (settings.keyNames) {
          ctx.fillStyle = held ? '#211a31' : '#b4aabd';
          ctx.font = `600 ${Math.min(9, Math.max(6, key.width * 0.44))}px ${fontFamily}`;
          ctx.textAlign = 'center';
          ctx.fillText(noteName(key.pitch), key.x + key.width / 2, keyboardTop + blackHeight - 9);
        }
      }
      ctx.fillStyle = dark ? '#eba16580' : '#d3905480';
      ctx.fillRect(0, keyboardTop, width, 1.5);
      frame = requestAnimationFrame(render);
    };
    const observer = new ResizeObserver(() => {
      width = element.clientWidth;
      height = element.clientHeight;
      const ratio = Math.min(devicePixelRatio || 1, 2);
      element.width = Math.round(width * ratio);
      element.height = Math.round(height * ratio);
      keys = pianoKeyLayout(width, settings.focusKeys ? low : 21, settings.focusKeys ? high : 108);
      whiteKeys = keys.filter((key) => key.white);
      blackKeys = keys.filter((key) => !key.white);
      byPitch.fill(undefined);
      for (const key of keys) byPitch[key.pitch] = key;
      particles.clear();
      dirty = true;
    });
    observer.observe(element);
    frame = requestAnimationFrame(render);
    return () => {
      observer.disconnect();
      cancelAnimationFrame(frame);
    };
  }, [frames, settings.focusKeys]);
  return <canvas ref={canvas} className="studio-roll" role="img" aria-label={label} />;
}
