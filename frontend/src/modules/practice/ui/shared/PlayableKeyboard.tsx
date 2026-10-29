import { useEffect, useRef, useState, type PointerEvent } from 'react';
import type { KeyboardViewport } from '../../domain/keyboardViewport';
import {
  computerPianoPitch,
  pianoPitchAt,
  pianoPitchName,
  visiblePianoKeys,
} from '../../domain/liveKeyboard';
import { useTranslation } from '@shared/i18n';
import type { useLivePiano } from '../../application/useLivePiano';
import './playableKeyboard.css';

export default function PlayableKeyboard({
  view,
  height,
  piano,
}: {
  view: KeyboardViewport;
  height: number;
  piano: ReturnType<typeof useLivePiano>;
}) {
  const tr = useTranslation();
  const host = useRef<HTMLDivElement>(null);
  const pointers = useRef(new Set<number>());
  const accessibleReleases = useRef(new Map<string, ReturnType<typeof setTimeout>>());
  const [focusedPitch, setFocusedPitch] = useState(60);
  const keys = visiblePianoKeys(view);
  const tabPitch = keys.some((key) => key.pitch === focusedPitch)
    ? focusedPitch
    : keys[Math.floor(keys.length / 2)]?.pitch;
  const movePointer = (event: PointerEvent<HTMLDivElement>) => {
    const box = event.currentTarget.getBoundingClientRect();
    const pitch = pianoPitchAt(view, height, event.clientX - box.left, event.clientY - box.top);
    const input = `pointer:${event.pointerId}`;
    if (pitch === null) piano.release(input);
    else piano.press(input, pitch);
  };
  const finish = (event: PointerEvent<HTMLDivElement>) => {
    pointers.current.delete(event.pointerId);
    piano.release(`pointer:${event.pointerId}`);
  };
  useEffect(
    () => () => {
      pointers.current.clear();
      for (const timer of accessibleReleases.current.values()) clearTimeout(timer);
      accessibleReleases.current.clear();
    },
    [],
  );
  return (
    <div
      ref={host}
      className="playable-keyboard"
      style={{ height }}
      role="group"
      aria-label={tr('Pianino chalish')}
      onPointerDown={(event) => {
        if (event.button !== 0) return;
        event.stopPropagation();
        event.preventDefault();
        event.currentTarget.setPointerCapture(event.pointerId);
        pointers.current.add(event.pointerId);
        (event.target as HTMLElement).closest('button')?.focus({ preventScroll: true });
        movePointer(event);
      }}
      onPointerMove={(event) => {
        if (!pointers.current.has(event.pointerId)) return;
        event.stopPropagation();
        event.preventDefault();
        movePointer(event);
      }}
      onPointerUp={finish}
      onPointerCancel={finish}
      onLostPointerCapture={finish}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) piano.stop();
      }}
      onKeyDown={(event) => {
        if (event.altKey || event.ctrlKey || event.metaKey) return;
        const pitch = computerPianoPitch(event.code);
        if (pitch !== null) {
          event.preventDefault();
          event.stopPropagation();
          if (!event.repeat) piano.press(`computer:${event.code}`, pitch);
        } else if (event.code === 'Space' || event.code === 'Enter') {
          event.preventDefault();
          event.stopPropagation();
          if (!event.repeat)
            piano.press(
              `computer:${event.code}`,
              Number((event.target as HTMLElement).dataset.pitch),
            );
        } else if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) {
          event.preventDefault();
          event.stopPropagation();
          const current = Number((event.target as HTMLElement).dataset.pitch);
          const next =
            event.key === 'Home'
              ? keys[0].pitch
              : event.key === 'End'
                ? keys.at(-1)!.pitch
                : Math.max(
                    keys[0].pitch,
                    Math.min(keys.at(-1)!.pitch, current + (event.key === 'ArrowRight' ? 1 : -1)),
                  );
          setFocusedPitch(next);
          host.current
            ?.querySelector<HTMLButtonElement>(`[data-pitch="${next}"]`)
            ?.focus({ preventScroll: true });
        } else if (event.key === 'Escape') {
          event.stopPropagation();
          piano.stop();
        }
      }}
      onKeyUp={(event) => {
        if (computerPianoPitch(event.code) !== null || ['Space', 'Enter'].includes(event.code)) {
          event.preventDefault();
          event.stopPropagation();
          piano.release(`computer:${event.code}`);
        }
      }}
    >
      {keys.map((key) => (
        <button
          key={key.pitch}
          type="button"
          data-pitch={key.pitch}
          className={key.white ? 'playable-key white' : 'playable-key black'}
          style={{ left: key.x, width: key.width, height: key.white ? '100%' : '66%' }}
          aria-label={pianoPitchName(key.pitch)}
          aria-pressed={piano.pitches.includes(key.pitch)}
          tabIndex={key.pitch === tabPitch ? 0 : -1}
          onFocus={() => setFocusedPitch(key.pitch)}
          onClick={(event) => {
            // Assistive activation may send a click without pointer/key events.
            if (event.detail !== 0) return;
            const input = `accessible:${key.pitch}`;
            clearTimeout(accessibleReleases.current.get(input));
            piano.press(input, key.pitch);
            accessibleReleases.current.set(
              input,
              setTimeout(() => {
                piano.release(input);
                accessibleReleases.current.delete(input);
              }, 600),
            );
          }}
        />
      ))}
    </div>
  );
}
