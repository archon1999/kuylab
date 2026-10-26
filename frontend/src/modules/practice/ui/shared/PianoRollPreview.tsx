import { useEffect, useId, useMemo, useState, type CSSProperties } from 'react';
import { PauseRounded, PlayArrowRounded, ReplayRounded } from '@mui/icons-material';
import { IconButton, Tooltip, useMediaQuery } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { pianoKeyLayout, type StudioNote } from '../../domain/studioTransport';
import { readableRollNotes } from '../../domain/readableNotes';
import './pianoRollPreview.css';

/** Silent, source-faithful visual excerpt. CSS moves one group, never the full
 * audio player. Pauses offscreen/background and plays once until explicitly replayed. */
export default function PianoRollPreview({
  notes,
  duration,
  active,
  label,
  compactHolds = false,
  onOpen,
}: {
  notes: StudioNote[];
  duration: number;
  active: boolean;
  label: string;
  compactHolds?: boolean;
  onOpen?: () => void;
}) {
  const tr = useTranslation();
  const reduced = useMediaQuery('(prefers-reduced-motion: reduce)');
  const [running, setRunning] = useState(false);
  const [started, setStarted] = useState(false);
  const [finished, setFinished] = useState(false);
  const [cycle, setCycle] = useState(0);
  const [documentVisible, setDocumentVisible] = useState(document.visibilityState === 'visible');
  useEffect(() => {
    const change = () => setDocumentVisible(document.visibilityState === 'visible');
    document.addEventListener('visibilitychange', change);
    return () => document.removeEventListener('visibilitychange', change);
  }, []);
  const id = useId().replace(/:/g, '');
  const rendered = useMemo(
    () => (compactHolds ? readableRollNotes(notes) : notes),
    [notes, compactHolds],
  );
  const keys = useMemo(() => {
    const pitches = notes.map((note) => note.pitch);
    const low = Math.max(21, Math.floor((Math.min(...pitches) - 2) / 12) * 12);
    const high = Math.min(108, Math.ceil((Math.max(...pitches) + 2) / 12) * 12 - 1);
    return pianoKeyLayout(300, low, high);
  }, [notes]);
  const byPitch = new Map(keys.map((key) => [key.pitch, key]));
  const keyboardY = 220;
  const scale = keyboardY / 4.5;
  const moving = active && running && documentVisible && !reduced && !finished;
  const keyFlashes = (white: boolean) =>
    !reduced &&
    !finished &&
    rendered.map((note) => {
      const key = byPitch.get(note.pitch);
      if (!key || key.white !== white) return null;
      return (
        <g
          key={note.id}
          className="preview-key-flash"
          style={{
            animationDelay: `${note.onset}s`,
            animationDuration: `${note.duration}s`,
            animationPlayState: moving ? 'running' : 'paused',
          }}
        >
          <rect
            x={key.x + 0.4}
            y={keyboardY + 1}
            width={key.width - 0.8}
            height={white ? 58 : 35}
            rx={white ? 1 : 1.5}
            fill={`url(#${id}-${note.hand})`}
          />
          <rect
            className="preview-key-glow"
            x={key.x - 1}
            y={keyboardY - 3}
            width={key.width + 2}
            height="6"
            rx="3"
            fill={`url(#${id}-${note.hand})`}
          />
        </g>
      );
    });
  return (
    <div className={`piano-roll-preview ${running ? 'is-playing' : 'is-paused'}`}>
      <svg viewBox="0 0 300 280" preserveAspectRatio="none" role="img" aria-label={label}>
        <defs>
          <clipPath id={`${id}-clip`}>
            <rect width="300" height={keyboardY} />
          </clipPath>
          <linearGradient id={`${id}-left`} x2="0" y2="1">
            <stop stopColor="#edb2d1" />
            <stop offset="1" stopColor="#bf729b" />
          </linearGradient>
          <linearGradient id={`${id}-right`} x2="0" y2="1">
            <stop stopColor="#afe3f4" />
            <stop offset="1" stopColor="#639bd2" />
          </linearGradient>
          <linearGradient id={`${id}-ivory`} x2="0" y2="1">
            <stop stopColor="#fffefb" />
            <stop offset=".8" stopColor="#f5f2eb" />
            <stop offset="1" stopColor="#e8e3d9" />
          </linearGradient>
          <linearGradient id={`${id}-ebony`} x2="0" y2="1">
            <stop stopColor="#35313f" />
            <stop offset=".86" stopColor="#1b1822" />
            <stop offset="1" stopColor="#0f0d15" />
          </linearGradient>
          <linearGradient id={`${id}-fade`} x2="0" y2="1">
            <stop stopColor="white" stopOpacity=".12" />
            <stop offset=".16" stopColor="white" />
          </linearGradient>
          <mask id={`${id}-atmosphere`}>
            <rect width="300" height={keyboardY} fill={`url(#${id}-fade)`} />
          </mask>
        </defs>
        <rect className="preview-roll-bg" width="300" height="280" />
        {keys
          .filter((key) => !key.white)
          .map((key) => (
            <rect
              key={key.pitch}
              className="preview-key-lane"
              x={key.x}
              width={key.width}
              height={keyboardY}
            />
          ))}
        {[44, 88, 132, 176].map((y) => (
          <line key={y} x2="300" y1={y} y2={y} className="preview-time-line" />
        ))}
        {keys
          .filter((key) => key.white && key.pitch % 12 === 0)
          .map((key) => (
            <line
              key={key.pitch}
              x1={key.x}
              x2={key.x}
              y2={keyboardY}
              className="preview-octave-line"
            />
          ))}
        <g clipPath={`url(#${id}-clip)`} mask={`url(#${id}-atmosphere)`}>
          <g
            key={cycle}
            className={!reduced && !finished ? 'preview-moving-notes' : ''}
            style={
              {
                '--preview-travel': `${duration * scale}px`,
                animationDuration: `${duration}s`,
                animationPlayState: moving ? 'running' : 'paused',
              } as CSSProperties
            }
            onAnimationEnd={() => {
              setFinished(true);
              setRunning(false);
            }}
          >
            {rendered.map((note) => {
              const key = byPitch.get(note.pitch);
              if (!key) return null;
              const height = Math.max(2, note.duration * scale);
              return (
                <rect
                  key={note.id}
                  className="preview-note"
                  x={key.x + 1}
                  y={keyboardY - note.onset * scale - height}
                  width={Math.max(1, key.width - 2)}
                  height={height}
                  rx={Math.min(5, key.width / 2)}
                  fill={`url(#${id}-${note.hand})`}
                  opacity={0.68 + (note.velocity / 127) * 0.32}
                  stroke="rgba(255,255,255,.3)"
                  strokeWidth=".45"
                />
              );
            })}
          </g>
        </g>
        <line x2="300" y1={keyboardY} y2={keyboardY} className="preview-strike-line" />
        {keys
          .filter((key) => key.white)
          .map((key) => (
            <rect
              key={key.pitch}
              className="preview-white-key"
              fill={`url(#${id}-ivory)`}
              x={key.x + 0.35}
              y={keyboardY + 1}
              width={key.width - 0.7}
              height="59"
              rx="1"
            />
          ))}
        <g key={`white:${cycle}`}>{keyFlashes(true)}</g>
        {keys
          .filter((key) => !key.white)
          .map((key) => (
            <rect
              key={key.pitch}
              className="preview-black-key"
              fill={`url(#${id}-ebony)`}
              x={key.x}
              y={keyboardY + 1}
              width={key.width}
              height="36"
              rx="1.5"
            />
          ))}
        <g key={`black:${cycle}`}>{keyFlashes(false)}</g>
      </svg>
      {(!reduced || onOpen) && (
        <Tooltip
          title={tr(
            reduced
              ? 'Playerni ochish'
              : finished
                ? 'Previewni qayta ko‘rish'
                : running
                  ? 'Previewni to‘xtatish'
                  : started
                    ? 'Previewni davom ettirish'
                    : 'Previewni boshlash',
          )}
        >
          <IconButton
            className="preview-motion-toggle"
            size="small"
            aria-label={tr(
              reduced
                ? 'Playerni ochish'
                : finished
                  ? 'Previewni qayta ko‘rish'
                  : running
                    ? 'Previewni to‘xtatish'
                    : started
                      ? 'Previewni davom ettirish'
                      : 'Previewni boshlash',
            )}
            onClick={() => {
              if (reduced) {
                onOpen?.();
                return;
              }
              setStarted(true);
              if (finished) {
                setFinished(false);
                setCycle((value) => value + 1);
                setRunning(true);
              } else setRunning((value) => !value);
            }}
          >
            {finished ? (
              <ReplayRounded fontSize="small" />
            ) : running ? (
              <PauseRounded fontSize="small" />
            ) : (
              <PlayArrowRounded fontSize="small" />
            )}
          </IconButton>
        </Tooltip>
      )}
    </div>
  );
}
