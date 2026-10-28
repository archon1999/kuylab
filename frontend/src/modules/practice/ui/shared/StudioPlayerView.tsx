import BrandMark from '@shared/ui/BrandMark';
import {
  Alert,
  Button,
  CircularProgress,
  Drawer,
  IconButton,
  Menu,
  MenuItem,
  Popover,
  Slider,
  Tooltip,
  useMediaQuery,
} from '@mui/material';
import {
  AddCircleOutlineRounded,
  RemoveCircleOutlineRounded,
  ChevronLeftRounded,
  DarkModeOutlined,
  FullscreenExitRounded,
  FullscreenRounded,
  LightModeOutlined,
  KeyboardArrowDownRounded,
  PauseRounded,
  PlayArrowRounded,
  RestartAltRounded,
  SettingsOutlined,
  BookmarkBorderRounded,
  MoreHorizRounded,
} from '@mui/icons-material';
import { useEffect, useMemo, useRef, useState } from 'react';
import { readableRollNotes } from '../../domain/readableNotes';
import { usePreferences, useTranslation } from '@shared/i18n';
import type { StudioAudioPort } from '../../domain/contracts/studio-audio.port';
import { useStudioPlayer, type StudioPlayerProps } from '../../application/useStudioPlayer';
import { useStudioPreferences } from '../../application/useStudioPreferences';
import type { StudioPreferencePort } from '../../domain/studioPreferences';
import StudioRollViewport from './StudioRollViewport';
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
  const [speedAnchor, setSpeedAnchor] = useState<HTMLElement | null>(null);
  const [moreAnchor, setMoreAnchor] = useState<HTMLElement | null>(null);
  const [visibleKeys, setVisibleKeys] = useState(88);
  const notePosition = useRef(0);
  useEffect(() => {
    if (transport.speed !== settings.speed) transport.changeSpeed(settings.speed);
  }, [settings.speed]);
  const reducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)');
  const mobile = useMediaQuery('(max-width: 680px)');
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
        speedAnchor ||
        moreAnchor ||
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
  }, [settingsOpen, speedAnchor, moreAnchor]);
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
  const openNotebook = () => {
    notePosition.current = player.position;
    player.pause();
    setSettingsOpen(false);
    setMoreAnchor(null);
    setNotebookOpen(true);
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
          <span className="studio-play-wrap">
            <IconButton
              className="studio-play"
              aria-label={player.playing ? text.pause : text.play}
              onClick={() => void player.toggle()}
              aria-busy={player.loading}
            >
              {player.loading ? (
                <CircularProgress size={28} />
              ) : player.playing ? (
                <PauseRounded />
              ) : (
                <PlayArrowRounded />
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
        <button
          className="studio-mobile-speed"
          aria-label={`${text.speed}: ${Math.round(player.speed * 100)}%`}
          aria-haspopup="dialog"
          aria-expanded={!!speedAnchor}
          onClick={(event) => setSpeedAnchor(event.currentTarget)}
        >
          <span>{text.speed}</span>
          <b>{Math.round(player.speed * 100)}%</b>
          <KeyboardArrowDownRounded aria-hidden="true" />
        </button>
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
              onClick={openNotebook}
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
        <IconButton
          className="studio-more-button"
          aria-label={text.more}
          aria-haspopup="menu"
          aria-expanded={!!moreAnchor}
          onClick={(event) => setMoreAnchor(event.currentTarget)}
        >
          <MoreHorizRounded />
        </IconButton>
      </div>
      <div className="studio-roll-frame">
        <StudioRollViewport
          notes={rollNotes}
          position={player.position}
          playing={player.playing}
          reducedMotion={reducedMotion}
          settings={settings}
          dark={mode === 'dark'}
          label={text.keyboard}
          text={text}
          onZoom={(zoom) => update('visibleKeys', Math.round(88 / zoom))}
          onVisibleKeysChange={setVisibleKeys}
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
      <Popover
        open={!!speedAnchor}
        anchorEl={speedAnchor}
        onClose={() => setSpeedAnchor(null)}
        container={() => element.current || document.body}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        slotProps={{
          paper: { className: 'studio-speed-popover', role: 'dialog', 'aria-label': text.speed },
        }}
      >
        <div className="studio-speed-popover-heading">
          <strong>{text.speed}</strong>
          <output>{Math.round(player.speed * 100)}%</output>
        </div>
        <Slider
          min={20}
          max={200}
          step={5}
          value={Math.round(player.speed * 100)}
          aria-label={text.speed}
          onChange={(_, value) => player.changeSpeed(Number(value) / 100)}
        />
        <div className="studio-speed-presets">
          {[0.5, 0.75, 1, 1.5].map((speed) => (
            <Button
              key={speed}
              aria-pressed={player.speed === speed}
              onClick={() => {
                player.changeSpeed(speed);
                setSpeedAnchor(null);
              }}
            >
              {Math.round(speed * 100)}%
            </Button>
          ))}
        </div>
      </Popover>
      <Menu
        open={!!moreAnchor}
        anchorEl={moreAnchor}
        onClose={() => setMoreAnchor(null)}
        container={() => element.current || document.body}
        slotProps={{ paper: { className: 'studio-actions-menu' } }}
      >
        {mobile && props.notebook && (
          <MenuItem onClick={openNotebook}>
            <BookmarkBorderRounded />
            {tr('Qaydlar')}
          </MenuItem>
        )}
        <MenuItem
          onClick={() => {
            player.seek(0);
            setMoreAnchor(null);
          }}
        >
          <RestartAltRounded />
          {text.reset}
        </MenuItem>
        <MenuItem
          onClick={() => {
            void fullscreen();
            setMoreAnchor(null);
          }}
        >
          <FullscreenRounded />
          {full ? text.exitFull : text.full}
        </MenuItem>
        {mobile && !props.compact && (
          <MenuItem
            onClick={() => {
              toggleMode();
              setMoreAnchor(null);
            }}
          >
            {mode === 'dark' ? <LightModeOutlined /> : <DarkModeOutlined />}
            {tr(mode === 'dark' ? 'Yorug‘ rejim' : 'Qorong‘i rejim')}
          </MenuItem>
        )}
      </Menu>
      <Drawer
        anchor={mobile ? 'bottom' : 'right'}
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
          visibleKeys={visibleKeys}
        />
      </Drawer>
      {props.notebook && (
        <Drawer
          anchor={mobile ? 'bottom' : 'right'}
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
