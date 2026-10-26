import { useId, useMemo, type CSSProperties } from 'react';
import { PauseRounded, PlayArrowRounded, ReplayRounded } from '@mui/icons-material';
import { CircularProgress, IconButton, Tooltip, useMediaQuery } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { pianoKeyLayout, type StudioNote } from '../../domain/studioTransport';
import { readableRollNotes } from '../../domain/readableNotes';
import type { PreviewState } from '../../application/previewPlayback';
import type { StudioPreferences } from '../../domain/studioPreferences';
import './pianoRollPreview.css';

/** Source-faithful excerpt. One CSS group follows the audio clock's anchors. */
export default function PianoRollPreview({
  notes,
  duration,
  active,
  label,
  compactHolds = false,
  playback,
  settings,
  onToggle,
}: {
  notes: StudioNote[];
  duration: number;
  active: boolean;
  label: string;
  compactHolds?: boolean;
  playback: PreviewState;
  settings: StudioPreferences;
  onToggle: () => void;
}) {
  const tr = useTranslation();
  const reduced = useMediaQuery('(prefers-reduced-motion: reduce)');
  const { playing: running, finished, cycle, position, speed, loading, error } = playback;
  const started = position > 0;
  const id = useId().replace(/:/g, '');
  const rendered = useMemo(
    () =>
      (compactHolds && settings.compactNoteLengths ? readableRollNotes(notes) : notes).filter(
        (note) => settings[note.hand],
      ),
    [notes, compactHolds, settings.compactNoteLengths, settings.left, settings.right],
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
  const moving = active && running && !reduced && !finished;
  const labelText = tr(
    loading
      ? 'Preview ovozini yuklashni bekor qilish'
      : error
        ? 'Preview ovozini qayta yuklash'
        : finished
          ? 'Previewni qayta ko‘rish'
          : running
            ? 'Previewni to‘xtatish'
            : started
              ? 'Previewni davom ettirish'
              : 'Previewni boshlash',
  );
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
            animationDelay: `${(note.onset - position) / speed}s`,
            animationDuration: `${note.duration / speed}s`,
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
            <stop stopColor={`color-mix(in srgb, ${settings.leftColor} 65%, white)`} />
            <stop offset="1" stopColor={settings.leftColor} />
          </linearGradient>
          <linearGradient id={`${id}-right`} x2="0" y2="1">
            <stop stopColor={`color-mix(in srgb, ${settings.rightColor} 60%, #b8f5ff)`} />
            <stop offset="1" stopColor={settings.rightColor} />
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
                animationDuration: `${duration / speed}s`,
                animationDelay: `${-position / speed}s`,
                animationPlayState: moving ? 'running' : 'paused',
              } as CSSProperties
            }
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
                  style={{ filter: settings.shadows ? undefined : 'none' }}
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
      <Tooltip title={labelText}>
        <IconButton
          className="preview-motion-toggle"
          size="small"
          aria-label={labelText}
          aria-busy={loading}
          onClick={onToggle}
        >
          {loading ? (
            <CircularProgress size={24} color="inherit" />
          ) : finished ? (
            <ReplayRounded fontSize="small" />
          ) : running ? (
            <PauseRounded fontSize="small" />
          ) : (
            <PlayArrowRounded fontSize="small" />
          )}
        </IconButton>
      </Tooltip>
      {error && (
        <small className="preview-audio-error" role="status">
          {tr('Preview ovozini yuklab bo‘lmadi. Qayta urining.')}
        </small>
      )}
    </div>
  );
}
