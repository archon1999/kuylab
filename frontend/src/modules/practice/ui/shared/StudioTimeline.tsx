import { CheckRounded, KeyboardArrowDownRounded } from '@mui/icons-material';
import { MenuItem, Select } from '@mui/material';
import { useRef, useState } from 'react';
import { playbackTimeLabel } from '../../domain';

const timerLabel = (seconds: number) => playbackTimeLabel(seconds).replace(/^0(?=\d:)/, '');

export default function StudioTimeline({
  duration,
  position,
  onSeek,
  label,
  sectionsLabel,
  markers = [],
}: {
  markers?: { time: number; label: string }[];
  duration: number;
  position: number;
  onSeek: (value: number) => void;
  label: string;
  sectionsLabel: string;
}) {
  const [hover, setHover] = useState<number | null>(null);
  const track = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);
  const currentSection = markers.reduce(
    (current, marker, index) => (marker.time <= position ? index : current),
    0,
  );
  const at = (clientX: number) => {
    const box = track.current!.getBoundingClientRect();
    return Math.max(0, Math.min(duration, ((clientX - box.left) / box.width) * duration));
  };
  return (
    <div className="studio-time">
      <div className="studio-time-labels">
        <span>{timerLabel(position)}</span>
        <span>{timerLabel(duration)}</span>
      </div>
      <div
        ref={track}
        className="studio-time-hit"
        role="slider"
        aria-label={label}
        aria-valuemin={0}
        aria-valuemax={Math.ceil(duration)}
        aria-valuenow={Math.floor(position)}
        aria-valuetext={playbackTimeLabel(position)}
        tabIndex={0}
        onPointerDown={(event) => {
          if (event.button !== 0) return;
          event.currentTarget.setPointerCapture(event.pointerId);
          dragging.current = true;
          onSeek(at(event.clientX));
        }}
        onPointerLeave={() => setHover(null)}
        onPointerMove={(event) => {
          setHover(at(event.clientX));
          if (dragging.current) onSeek(at(event.clientX));
        }}
        onPointerUp={(event) => {
          if (!dragging.current) return;
          onSeek(at(event.clientX));
          dragging.current = false;
        }}
        onPointerCancel={() => {
          dragging.current = false;
        }}
        onLostPointerCapture={() => {
          dragging.current = false;
        }}
        onKeyDown={(event) => {
          const keys: Record<string, number> = {
            ArrowLeft: position - 5,
            ArrowRight: position + 5,
            Home: 0,
            End: duration,
            PageUp: position + duration / 10,
            PageDown: position - duration / 10,
          };
          if (event.key in keys) {
            event.preventDefault();
            event.stopPropagation();
            onSeek(keys[event.key]);
          }
        }}
      >
        {hover !== null && (
          <span className="studio-time-tooltip" style={{ left: `${(hover / duration) * 100}%` }}>
            {timerLabel(hover)}
          </span>
        )}
        <div className="studio-time-rail">
          {markers.map((marker, index) => (
            <i
              className="studio-time-marker"
              key={index}
              style={{ left: `${Math.max(0, Math.min(100, (marker.time / duration) * 100))}%` }}
            />
          ))}
          <div className="studio-time-fill" style={{ width: `${(position / duration) * 100}%` }} />
        </div>
      </div>
      {markers.length > 0 && (
        <Select
          className="studio-section-select"
          variant="standard"
          disableUnderline
          fullWidth
          autoWidth
          value={currentSection}
          inputProps={{ 'aria-label': sectionsLabel }}
          IconComponent={KeyboardArrowDownRounded}
          onChange={(event) => onSeek(markers[Number(event.target.value)].time)}
          renderValue={() => (
            <span className="studio-section-value">
              <span className="studio-section-time">
                {timerLabel(markers[currentSection].time)}
              </span>
              <span className="studio-marker-select-label">{markers[currentSection].label}</span>
            </span>
          )}
          MenuProps={{
            container: () => track.current?.closest<HTMLElement>('.studio-player') ?? document.body,
            anchorOrigin: { vertical: 'bottom', horizontal: 'left' },
            transformOrigin: { vertical: 'top', horizontal: 'left' },
            slotProps: {
              paper: { className: 'studio-section-menu' },
              list: { 'aria-label': sectionsLabel },
            },
          }}
        >
          {markers.map((marker, index) => (
            <MenuItem
              key={marker.time}
              value={index}
              className="studio-section-option"
              onClick={() => {
                if (index === currentSection) onSeek(marker.time);
              }}
            >
              <span className="studio-section-time">{timerLabel(marker.time)}</span>
              <span className="studio-marker-select-label">{marker.label}</span>
              <CheckRounded className="studio-section-check" aria-hidden="true" />
            </MenuItem>
          ))}
        </Select>
      )}
    </div>
  );
}
