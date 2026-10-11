import { usePreferences, useTranslation } from '@shared/i18n';
import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { createTempoClock, pitchLabel, type PlaybackNote, type TempoMapEntry } from '../../domain';

const whitePitch = (pitch: number) => [0, 2, 4, 5, 7, 9, 11].includes(pitch % 12);
function keyLayout(width: number) {
  const whites = Array.from({ length: 88 }, (_, index) => index + 21).filter(whitePitch);
  const size = width / whites.length;
  let count = 0;
  const keys = Array.from({ length: 88 }, (_, index) => {
    const pitch = index + 21;
    const white = whitePitch(pitch);
    const x = white ? count++ * size : count * size - size * 0.31;
    return { pitch, white, x, width: white ? size : size * 0.62 };
  });
  return { keys, size };
}
export default function Synthesia({
  notes,
  quarter,
  tempoMap,
  heldPitches = [],
  onKey,
}: {
  notes: PlaybackNote[];
  quarter: number;
  tempoMap: TempoMapEntry[];
  heldPitches?: number[];
  onKey: (pitch: number) => void;
}) {
  const tr = useTranslation();
  const { mode } = usePreferences();
  const canvas = useRef<HTMLCanvasElement>(null);
  const [selectedPitch, setSelectedPitch] = useState(60);
  const helpId = useId();
  const tempoClock = useMemo(() => createTempoClock(tempoMap), [tempoMap]);
  const timedNotes = useMemo(
    () =>
      notes.map((note) => ({
        note,
        start: tempoClock.quarterToSeconds(note.play_onset),
        duration:
          tempoClock.quarterToSeconds(note.play_onset + note.play_duration) -
          tempoClock.quarterToSeconds(note.play_onset),
      })),
    [notes, tempoClock],
  );
  useEffect(() => {
    const element = canvas.current;
    if (!element) return;
    let frame = 0;
    const render = () => {
      const width = element.clientWidth;
      const height = element.clientHeight;
      const ratio = Math.min(devicePixelRatio || 1, 2);
      element.width = Math.round(width * ratio);
      element.height = Math.round(height * ratio);
      const ctx = element.getContext('2d');
      if (!ctx) return;
      ctx.scale(ratio, ratio);
      const dark = mode === 'dark';
      ctx.fillStyle = dark ? '#181e26' : '#f9f7f2';
      ctx.fillRect(0, 0, width, height);
      const keyboardHeight = 88;
      const keyboardTop = height - keyboardHeight;
      const speed = keyboardTop / 5.5;
      const layout = keyLayout(width);
      const byPitch = new Map(layout.keys.map((key) => [key.pitch, key]));
      for (const key of layout.keys.filter((key) => key.white)) {
        ctx.strokeStyle = dark ? '#222c36' : '#eeeae2';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(key.x, 0);
        ctx.lineTo(key.x, keyboardTop);
        ctx.stroke();
      }
      const pressed = new Map<number, string>(heldPitches.map((pitch) => [pitch, '#9aba9c']));
      const current = tempoClock.quarterToSeconds(quarter);
      for (const timed of timedNotes) {
        const note = timed.note;
        if (!note.pitch) continue;
        const start = timed.start - current;
        const duration = timed.duration;
        if (start > 5.6 || start + duration < 0) continue;
        const key = byPitch.get(note.pitch.midi);
        if (!key) continue;
        const color = note.hand === 'left' ? '#c39367' : '#809bac';
        if (start <= 0 && start + duration > 0) pressed.set(note.pitch.midi, color);
        const bottom = keyboardTop - start * speed;
        const top = bottom - Math.max(7, duration * speed);
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.9;
        ctx.beginPath();
        ctx.roundRect(
          key.x + 1,
          Math.max(0, top),
          Math.max(2, key.width - 2),
          Math.max(0, Math.min(keyboardTop, bottom) - Math.max(0, top)),
          3,
        );
        ctx.fill();
        ctx.globalAlpha = 1;
      }
      for (const key of layout.keys.filter((key) => key.white)) {
        ctx.fillStyle = pressed.get(key.pitch) || '#fff';
        ctx.fillRect(key.x, keyboardTop, key.width - 0.7, keyboardHeight);
        ctx.strokeStyle = '#d5d3ce';
        ctx.strokeRect(key.x, keyboardTop, key.width, keyboardHeight);
        if (key.pitch % 12 === 0) {
          ctx.fillStyle = '#8b8e90';
          ctx.font = '9px Segoe UI';
          ctx.textAlign = 'center';
          ctx.fillText(`C${Math.floor(key.pitch / 12) - 1}`, key.x + key.width / 2, height - 10);
        }
      }
      for (const key of layout.keys.filter((key) => !key.white)) {
        ctx.fillStyle = pressed.get(key.pitch) || '#34383d';
        ctx.beginPath();
        ctx.roundRect(key.x, keyboardTop, key.width, keyboardHeight * 0.63, [0, 0, 3, 3]);
        ctx.fill();
      }
      if (element === document.activeElement) {
        const selected = byPitch.get(selectedPitch);
        if (selected) {
          ctx.strokeStyle = dark ? '#c7d4dd' : '#52738a';
          ctx.lineWidth = 2;
          ctx.strokeRect(
            selected.x + 1,
            keyboardTop + 2,
            Math.max(1, selected.width - 3),
            (selected.white ? keyboardHeight : keyboardHeight * 0.63) - 4,
          );
        }
      }
      ctx.strokeStyle = dark ? '#a47148' : '#bb906c';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, keyboardTop);
      ctx.lineTo(width, keyboardTop);
      ctx.stroke();
    };
    const observer = new ResizeObserver(() => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(render);
    });
    observer.observe(element);
    render();
    return () => {
      observer.disconnect();
      cancelAnimationFrame(frame);
    };
  }, [timedNotes, quarter, tempoClock, heldPitches, mode, selectedPitch]);
  return (
    <div className="synthesia">
      <canvas
        ref={canvas}
        aria-label={tr('Pianino · 88 klavish')}
        tabIndex={0}
        role="slider"
        aria-valuemin={21}
        aria-valuemax={108}
        aria-valuenow={selectedPitch}
        aria-valuetext={pitchLabel(selectedPitch)}
        aria-describedby={helpId}
        aria-keyshortcuts="ArrowLeft ArrowRight ArrowUp ArrowDown Enter Space"
        onKeyDown={(event) => {
          const steps: Record<string, number> = {
            ArrowLeft: -1,
            ArrowRight: 1,
            ArrowUp: 12,
            ArrowDown: -12,
          };
          if (steps[event.key]) {
            event.preventDefault();
            setSelectedPitch((value) => Math.max(21, Math.min(108, value + steps[event.key])));
          } else if (event.key === 'Home' || event.key === 'End') {
            event.preventDefault();
            setSelectedPitch(event.key === 'Home' ? 21 : 108);
          } else if ((event.key === 'Enter' || event.key === ' ') && !event.repeat) {
            event.preventDefault();
            onKey(selectedPitch);
          }
        }}
        onPointerDown={(event) => {
          const element = canvas.current;
          if (!element) return;
          const box = element.getBoundingClientRect();
          const x = event.clientX - box.left;
          const y = event.clientY - box.top;
          const keyboardTop = box.height - 88;
          if (y < keyboardTop) return;
          const { keys } = keyLayout(box.width);
          const black =
            y < keyboardTop + 88 * 0.63
              ? keys.find((key) => !key.white && x >= key.x && x < key.x + key.width)
              : undefined;
          const key = black || keys.find((key) => key.white && x >= key.x && x < key.x + key.width);
          if (key) {
            setSelectedPitch(key.pitch);
            onKey(key.pitch);
          }
        }}
      />
      <span
        id={helpId}
        style={{
          position: 'absolute',
          width: 1,
          height: 1,
          padding: 0,
          margin: -1,
          overflow: 'hidden',
          clip: 'rect(0,0,0,0)',
          whiteSpace: 'nowrap',
          border: 0,
        }}
      >
        {tr('Strelkalar bilan nota tanlang. Enter yoki Space bilan chaling.')}
      </span>
      <div className="synthesia-legend">
        <span>
          <i className="left" />
          {tr('Chap qo‘l')}
        </span>
        <span>
          <i className="right" />
          {tr('O‘ng qo‘l')}
        </span>
      </div>
    </div>
  );
}
