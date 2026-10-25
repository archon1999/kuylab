import BrandMark from '@shared/ui/BrandMark';
import { Alert, CircularProgress, Drawer, IconButton, Tooltip, useMediaQuery } from '@mui/material';
import {
  AddCircleOutlineRounded,
  RemoveCircleOutlineRounded,
  ChevronLeftRounded,
  DarkModeOutlined,
  FullscreenExitRounded,
  FullscreenRounded,
  LightModeOutlined,
  PauseCircleOutlineRounded,
  PlayCircleOutlineRounded,
  RestartAltRounded,
  SettingsOutlined,
  BookmarkBorderRounded,
} from '@mui/icons-material';
import { useEffect, useMemo, useRef, useState } from 'react';
import { readableRollNotes } from '../../domain/readableNotes';
import { usePreferences, useTranslation } from '@shared/i18n';
import type { StudioAudioPort } from '../../domain/contracts/studio-audio.port';
import { useStudioPlayer, type StudioPlayerProps } from '../../application/useStudioPlayer';
import { useStudioPreferences } from '../../application/useStudioPreferences';
import type { StudioPreferencePort } from '../../domain/studioPreferences';
import StudioRoll from './StudioRoll';
import StudioTimeline from './StudioTimeline';
import StudioSettings from './StudioSettings';
import { studioLabels } from './studioLabels';
import '../studioPlayer.css';

export default function StudioPlayerView(
  props: StudioPlayerProps & { audio: StudioAudioPort; preferences: StudioPreferencePort },
) {
  const { language, mode, toggleMode } = usePreferences();
  const tr = useTranslation();
  const text = studioLabels[language];
  const title = props.title || props.score.title;
  const { preferences: settings, update } = useStudioPreferences(props.preferences);
  const transport = useStudioPlayer(props, props.audio, settings);
  const rollNotes = useMemo(
    () =>
      props.readableHolds && settings.compactNoteLengths
        ? readableRollNotes(transport.timeline.notes)
        : transport.timeline.notes,
    [props.readableHolds, settings.compactNoteLengths, transport.timeline.notes],
  );
  const player = {
    ...transport,
    changeSpeed(value: number) {
      transport.changeSpeed(update('speed', value).speed);
    },
  };
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [notebookOpen, setNotebookOpen] = useState(false);
  const notePosition = useRef(0);
  useEffect(() => {
    if (transport.speed !== settings.speed) transport.changeSpeed(settings.speed);
  }, [settings.speed]);
  const reducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)');
  const { volume, reverb, leftVolume, rightVolume } = settings;
  const [full, setFull] = useState(false);
  const element = useRef<HTMLElement>(null);
  const current = useRef(player);
  current.current = player;
  useEffect(() => {
    props.audio.volume(volume / 100);
    props.audio.reverb(reverb / 100);
    props.audio.handVolume?.('left', leftVolume / 100);
    props.audio.handVolume?.('right', rightVolume / 100);
  }, [props.audio, volume, reverb, leftVolume, rightVolume]);
  useEffect(() => {
    const keydown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      if (
        settingsOpen ||
        event.altKey ||
        event.ctrlKey ||
        event.metaKey ||
        target.closest(
          'input,textarea,select,[contenteditable="true"],[role="dialog"],[role="slider"],[role="combobox"],[role="listbox"]',
        )
      )
        return;
      const p = current.current;
      if (event.code === 'Space') {
        if (target.closest('button,a')) return;
        event.preventDefault();
        if (!event.repeat) void p.toggle();
      } else if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        event.preventDefault();
        p.seek(p.position + (event.key === 'ArrowRight' ? 5 : -5));
      } else if (event.key === '-' || event.key === '_') {
        event.preventDefault();
        p.changeSpeed(p.speed - 0.05);
      } else if (event.key === '+' || event.key === '=') {
        event.preventDefault();
        p.changeSpeed(p.speed + 0.05);
      } else if (event.key === 'Home') {
        event.preventDefault();
        p.seek(0);
      }
    };
    document.addEventListener('keydown', keydown);
    return () => document.removeEventListener('keydown', keydown);
  }, [settingsOpen]);
  useEffect(() => {
    const changed = () => setFull(document.fullscreenElement === element.current);
    document.addEventListener('fullscreenchange', changed);
    return () => document.removeEventListener('fullscreenchange', changed);
  }, []);
  const fullscreen = async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await element.current?.requestFullscreen();
    } catch {
      /* Embedded browsers can disallow full screen; regular player remains available. */
    }
  };
  return (
    <section
      ref={element}
      className={`studio-player ${props.compact ? 'studio-player-compact' : ''}`}
      data-color-mode={mode}
      aria-label={title}
    >
      <div className="studio-toolbar">
        {props.onBack && (
          <button className="studio-back-brand" onClick={props.onBack} aria-label={text.back}>
            <BrandMark />
            <span>
              <ChevronLeftRounded aria-hidden="true" />
              {text.back}
            </span>
          </button>
        )}
        <Tooltip title={`${player.playing ? text.pause : text.play} · Space`}>
          <span>
            <IconButton
              className="studio-play"
              aria-label={player.playing ? text.pause : text.play}
              onClick={() => void player.toggle()}
              aria-busy={player.loading}
            >
              {player.loading ? (
                <CircularProgress size={28} />
              ) : player.playing ? (
                <PauseCircleOutlineRounded />
              ) : (
                <PlayCircleOutlineRounded />
              )}
            </IconButton>
          </span>
        </Tooltip>
        <StudioTimeline
          duration={player.timeline.duration}
          position={player.position}
          onSeek={player.seek}
          label={text.seek}
          sectionsLabel={text.sections}
          markers={props.markers}
        />
        <div className="studio-speed">
          <IconButton
            size="small"
            aria-label={text.slower}
            onClick={() => player.changeSpeed(player.speed - 0.05)}
            disabled={player.speed <= 0.2}
          >
            <RemoveCircleOutlineRounded className="studio-circle-sign" />
          </IconButton>
          <div>
            <span>{text.speed}</span>
            <b>{Math.round(player.speed * 100)}%</b>
          </div>
          <IconButton
            size="small"
            aria-label={text.faster}
            onClick={() => player.changeSpeed(player.speed + 0.05)}
            disabled={player.speed >= 2}
          >
            <AddCircleOutlineRounded className="studio-circle-sign" />
          </IconButton>
        </div>
        {props.toolbarAccessory?.(player.position, player.pause)}
        <Tooltip title={text.reset}>
          <IconButton
            className="studio-secondary"
            aria-label={text.reset}
            onClick={() => player.seek(0)}
          >
            <RestartAltRounded />
          </IconButton>
        </Tooltip>
        {props.notebook && (
          <Tooltip title={tr('Qaydlar')}>
            <IconButton
              className="studio-notebook-button"
              aria-label={tr('Qaydlar')}
              onClick={() => {
                notePosition.current = player.position;
                if (player.playing) void player.toggle();
                setSettingsOpen(false);
                setNotebookOpen(true);
              }}
              aria-expanded={notebookOpen}
            >
              <BookmarkBorderRounded />
            </IconButton>
          </Tooltip>
        )}
        <Tooltip title={text.settings}>
          <IconButton
            className="studio-settings-button"
            aria-label={text.settings}
            onClick={() => setSettingsOpen(true)}
            aria-expanded={settingsOpen}
          >
            <SettingsOutlined />
          </IconButton>
        </Tooltip>
        <Tooltip title={full ? text.exitFull : text.full}>
          <IconButton
            className="studio-secondary"
            aria-label={full ? text.exitFull : text.full}
            onClick={() => void fullscreen()}
          >
            {full ? <FullscreenExitRounded /> : <FullscreenRounded />}
          </IconButton>
        </Tooltip>
        {!props.compact && (
          <IconButton
            className="studio-theme"
            aria-label={tr(mode === 'dark' ? 'Yorug‘ rejim' : 'Qorong‘i rejim')}
            onClick={toggleMode}
          >
            {mode === 'dark' ? <LightModeOutlined /> : <DarkModeOutlined />}
          </IconButton>
        )}
      </div>
      <div className="studio-roll-frame">
        <StudioRoll
          notes={rollNotes}
          position={player.position}
          playing={player.playing}
          reducedMotion={reducedMotion}
          settings={settings}
          dark={mode === 'dark'}
          label={text.keyboard}
        />
        {!player.playing && !player.loading && player.position < 0.2 && (
          <div className="studio-piece-label">
            <span>{title}</span>
          </div>
        )}
        {player.loading && (
          <div className="studio-player-status" role="status">
            <BrandMark />
            <span>
              {player.countdown || `${text.loading} ${Math.round(player.loadProgress * 100)}%`}
            </span>
          </div>
        )}
        {player.error && (
          <Alert className="studio-player-error" severity="error" onClose={player.clearError}>
            {text.error}
          </Alert>
        )}
      </div>
      <Drawer
        anchor="right"
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        container={full ? element.current : undefined}
        slotProps={{
          paper: {
            className: `studio-settings-panel ${mode === 'dark' ? 'is-dark' : ''}`,
            role: 'dialog',
            'aria-label': text.settings,
          },
        }}
      >
        <StudioSettings
          settings={settings}
          update={update}
          text={text}
          reducedMotion={reducedMotion}
          onClose={() => setSettingsOpen(false)}
          readableHolds={props.readableHolds}
        />
      </Drawer>
      {props.notebook && (
        <Drawer
          anchor="right"
          open={notebookOpen}
          onClose={() => setNotebookOpen(false)}
          container={full ? element.current : undefined}
          slotProps={{ paper: { role: 'dialog', 'aria-label': tr('Qaydlar') } }}
        >
          {props.notebook(notePosition.current, player.seek, () => setNotebookOpen(false))}
        </Drawer>
      )}
    </section>
  );
}
