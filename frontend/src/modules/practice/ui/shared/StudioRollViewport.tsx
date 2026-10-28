import { useEffect, useId, useMemo, useRef, useState, type PointerEvent } from 'react';
import {
  keyboardRange,
  keyboardViewport,
  normalizeKeyboardZoom,
  panKeyboard,
  zoomKeyboardAt,
  type KeyboardViewport,
} from '../../domain/keyboardViewport';
import type { StudioPreferences } from '../../domain/studioPreferences';
import type { StudioNote } from '../../domain/studioTransport';
import StudioRoll from './StudioRoll';
import { studioLabels } from './studioLabels';

type Point = { x: number; y: number };
type Gesture = { view: KeyboardViewport; point: Point; distance: number };

export default function StudioRollViewport({
  settings,
  onZoom,
  onVisibleKeysChange,
  text,
  ...roll
}: {
  notes: StudioNote[];
  position: number;
  playing: boolean;
  reducedMotion: boolean;
  settings: StudioPreferences;
  dark: boolean;
  label: string;
  text: typeof studioLabels.uz;
  onZoom: (zoom: number) => void;
  onVisibleKeysChange: (count: number) => void;
}) {
  const host = useRef<HTMLDivElement>(null);
  const hint = useId();
  const [width, setWidth] = useState(1);
  const [center, setCenter] = useState<number | null>(null);
  const range = useMemo(
    () =>
      keyboardRange(
        roll.notes.map((note) => note.pitch),
        false,
      ),
    [roll.notes],
  );
  const view = useMemo(
    () =>
      keyboardViewport(width, settings.visibleKeys ? 88 / settings.visibleKeys : 0, center, range),
    [width, settings.visibleKeys, center, range],
  );
  const current = useRef({ view, onZoom, range });
  current.current = { view, onZoom, range };
  const pointers = useRef(new Map<number, Point>());
  const gesture = useRef<Gesture | null>(null);
  const point = (event: PointerEvent<HTMLDivElement>) => {
    const box = event.currentTarget.getBoundingClientRect();
    return { x: event.clientX - box.left, y: event.clientY - box.top };
  };
  const rebase = () => {
    const [a, b] = [...pointers.current.values()];
    gesture.current = a
      ? {
          view: current.current.view,
          point: b ? { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 } : a,
          distance: b ? Math.max(1, Math.hypot(a.x - b.x, a.y - b.y)) : 0,
        }
      : null;
  };
  const moveCenter = (next: number) => {
    const live = current.current;
    live.view = keyboardViewport(live.view.width, live.view.zoom, next, live.range);
    setCenter(next);
  };
  const zoomAt = (base: KeyboardViewport, next: number, anchor: number, moved = anchor) => {
    const count = Math.max(12, Math.round(88 / (normalizeKeyboardZoom(next) || 1)));
    const value = zoomKeyboardAt(base, 88 / count, anchor, moved);
    const live = current.current;
    live.view = keyboardViewport(base.width, value.zoom, value.center, live.range);
    setCenter(value.center);
    current.current.onZoom(value.zoom);
  };
  const finishPointer = (event: PointerEvent<HTMLDivElement>) => {
    pointers.current.delete(event.pointerId);
    rebase();
  };
  useEffect(() => setCenter(null), [range]);
  useEffect(
    () => onVisibleKeysChange(Math.round(88 / view.zoom)),
    [view.zoom, onVisibleKeysChange],
  );
  useEffect(() => {
    const element = host.current;
    if (!element) return;
    const observer = new ResizeObserver(() => setWidth(element.clientWidth));
    observer.observe(element);
    const wheel = (event: WheelEvent) => {
      const live = current.current.view;
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault();
        const anchor = event.clientX - element.getBoundingClientRect().left;
        zoomAt(live, live.zoom * Math.exp(-event.deltaY * 0.006), anchor);
      } else if (live.zoom > 1) {
        const delta = Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY;
        const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? live.width : 1;
        const next = panKeyboard(live, delta * unit);
        if (next !== live.center) {
          event.preventDefault();
          moveCenter(next);
        }
      }
    };
    element.addEventListener('wheel', wheel, { passive: false });
    return () => {
      observer.disconnect();
      element.removeEventListener('wheel', wheel);
      pointers.current.clear();
      gesture.current = null;
    };
  }, []);
  return (
    <div className="studio-roll-view">
      <div
        ref={host}
        className="studio-roll-viewport"
        role="region"
        aria-label={text.viewport}
        aria-description={`${text.visibleKeys}: ${Math.round(88 / view.zoom)}`}
        aria-describedby={hint}
        tabIndex={0}
        onPointerDown={(event) => {
          if (event.button !== 0 || pointers.current.size >= 2) return;
          event.currentTarget.setPointerCapture(event.pointerId);
          pointers.current.set(event.pointerId, point(event));
          rebase();
        }}
        onPointerMove={(event) => {
          if (!pointers.current.has(event.pointerId) || !gesture.current) return;
          event.preventDefault();
          pointers.current.set(event.pointerId, point(event));
          const [a, b] = [...pointers.current.values()];
          const start = gesture.current;
          if (b && start.distance) {
            const distance = Math.hypot(a.x - b.x, a.y - b.y);
            zoomAt(
              start.view,
              start.view.zoom * (distance / start.distance),
              start.point.x,
              (a.x + b.x) / 2,
            );
          } else moveCenter(panKeyboard(start.view, start.point.x - a.x));
        }}
        onPointerUp={finishPointer}
        onPointerCancel={finishPointer}
        onLostPointerCapture={finishPointer}
        onKeyDown={(event) => {
          if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
            event.preventDefault();
            event.stopPropagation();
            moveCenter(panKeyboard(view, event.key === 'ArrowRight' ? 72 : -72));
          } else if (['+', '=', '-', '_'].includes(event.key)) {
            event.preventDefault();
            event.stopPropagation();
            zoomAt(
              view,
              view.zoom + (['+', '='].includes(event.key) ? 0.25 : -0.25),
              view.width / 2,
            );
          }
        }}
      >
        <StudioRoll {...roll} settings={settings} viewport={view} />
      </div>
      <span id={hint} className="studio-viewport-hint">
        {text.panHint}
      </span>
    </div>
  );
}
