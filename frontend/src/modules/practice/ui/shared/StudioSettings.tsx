import { CloseRounded } from '@mui/icons-material';
import {
  FormControlLabel,
  IconButton,
  Slider,
  Switch,
  Tab,
  Tabs,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import { useId, useState } from 'react';
import type { StudioPreferences } from '../../domain/studioPreferences';
import { studioLabels } from './studioLabels';

type ToggleKey =
  | 'noteNames'
  | 'keyNames'
  | 'shadows'
  | 'particles'
  | 'velocityGradients'
  | 'focusKeys'
  | 'compactNoteLengths';
export default function StudioSettings({
  settings,
  update,
  text,
  reducedMotion,
  readableHolds,
  onClose,
  visibleKeys,
}: {
  settings: StudioPreferences;
  update: <K extends keyof StudioPreferences>(
    key: K,
    value: StudioPreferences[K],
  ) => StudioPreferences;
  text: typeof studioLabels.uz;
  reducedMotion: boolean;
  readableHolds?: boolean;
  onClose: () => void;
  visibleKeys: number;
}) {
  const [tab, setTab] = useState(0);
  const id = useId();
  const toggle = (key: ToggleKey, label: string, disabled = false) => (
    <FormControlLabel
      key={key}
      className="studio-setting-toggle"
      labelPlacement="start"
      label={label}
      control={
        <Switch
          size="small"
          checked={disabled ? false : settings[key]}
          disabled={disabled}
          onChange={(_, checked) => update(key, checked)}
        />
      }
    />
  );
  return (
    <>
      <div className="studio-settings-heading">
        <h2>{text.settings}</h2>
        <IconButton size="small" aria-label={text.close} onClick={onClose}>
          <CloseRounded />
        </IconButton>
      </div>
      <Tabs
        className="studio-settings-tabs"
        value={tab}
        onChange={(_, value: number) => setTab(value)}
        variant="fullWidth"
        aria-label={text.settings}
      >
        <Tab id={`${id}-visual-tab`} aria-controls={`${id}-visual`} label={text.view} />
        <Tab id={`${id}-sound-tab`} aria-controls={`${id}-sound`} label={text.sound} />
      </Tabs>
      <div className="studio-settings-body">
        <div
          role="tabpanel"
          id={`${id}-visual`}
          aria-labelledby={`${id}-visual-tab`}
          hidden={tab !== 0}
        >
          <fieldset>
            <legend>{text.labels}</legend>
            {toggle('noteNames', text.noteNames)}
            {toggle('keyNames', text.keyNames)}
            {readableHolds && (
              <>
                {toggle('compactNoteLengths', text.compactNoteLengths)}
                <p className="studio-settings-hint">{text.compactNoteLengthsHint}</p>
              </>
            )}
          </fieldset>
          <fieldset>
            <legend>{text.viewport}</legend>
            <div className="studio-setting-slider">
              <div className="studio-setting-slider-heading">
                <span>{text.visibleKeys}</span>
                <output>{visibleKeys}</output>
              </div>
              <Slider
                min={12}
                max={88}
                step={1}
                value={visibleKeys}
                aria-label={text.visibleKeys}
                marks={[12, 36, 61, 88].map((value) => ({ value, label: String(value) }))}
                onChange={(_, value) => update('visibleKeys', Number(value))}
              />
            </div>
          </fieldset>
          <fieldset>
            <legend>{text.effects}</legend>
            {toggle('shadows', text.shadows)}
            {toggle('velocityGradients', text.velocityGradients)}
            {toggle('particles', text.particles, reducedMotion)}
            {reducedMotion && <p className="studio-settings-hint">{text.reducedMotion}</p>}
          </fieldset>
          <label className="studio-setting-slider">
            <span className="studio-setting-slider-heading">
              <span>{text.lookahead}</span>
              <output>
                {settings.lookahead} {text.seconds}
              </output>
            </span>
            <Slider
              aria-label={text.lookahead}
              min={2}
              max={15}
              step={1}
              value={settings.lookahead}
              onChange={(_, value) => update('lookahead', value as number)}
            />
          </label>
          <fieldset className="studio-hand-fieldset">
            <legend>{text.hands}</legend>
            <div className="studio-hand-settings">
              {(['left', 'right'] as const).map((hand) => (
                <div className="studio-hand-row" key={hand}>
                  <input
                    type="color"
                    aria-label={`${text[hand]} · ${text.view}`}
                    value={settings[hand === 'left' ? 'leftColor' : 'rightColor']}
                    onChange={(event) =>
                      update(hand === 'left' ? 'leftColor' : 'rightColor', event.target.value)
                    }
                  />
                  <FormControlLabel
                    label={text[hand]}
                    labelPlacement="start"
                    control={
                      <Switch
                        size="small"
                        checked={settings[hand]}
                        onChange={(_, checked) => update(hand, checked)}
                      />
                    }
                  />
                </div>
              ))}
            </div>
          </fieldset>
        </div>
        <div
          role="tabpanel"
          id={`${id}-sound`}
          aria-labelledby={`${id}-sound-tab`}
          hidden={tab !== 1}
        >
          <fieldset>
            <legend>{text.countIn}</legend>
            <ToggleButtonGroup
              size="small"
              exclusive
              value={settings.countIn}
              onChange={(_, value) => value !== null && update('countIn', value)}
            >
              {[0, 2, 3].map((value) => (
                <ToggleButton key={value} value={value}>
                  {value === 0 ? text.off : `${value} ${text.seconds}`}
                </ToggleButton>
              ))}
            </ToggleButtonGroup>
          </fieldset>
          {(['left', 'right'] as const).map((hand) => (
            <label key={hand} className="studio-setting-slider">
              <span className="studio-setting-slider-heading">
                <span>{text[hand]}</span>
                <output>{settings[hand === 'left' ? 'leftVolume' : 'rightVolume']}%</output>
              </span>
              <Slider
                aria-label={`${text[hand]} · ${text.volume}`}
                value={settings[hand === 'left' ? 'leftVolume' : 'rightVolume']}
                min={0}
                max={100}
                onChange={(_, value) =>
                  update(hand === 'left' ? 'leftVolume' : 'rightVolume', value as number)
                }
              />
            </label>
          ))}
          <label className="studio-setting-slider">
            <span className="studio-setting-slider-heading">
              <span>{text.volume}</span>
              <output>{settings.volume}%</output>
            </span>
            <Slider
              aria-label={text.volume}
              min={0}
              max={100}
              value={settings.volume}
              onChange={(_, value) => update('volume', value as number)}
            />
          </label>
          <label className="studio-setting-slider">
            <span className="studio-setting-slider-heading">
              <span>{text.reverb}</span>
              <output>{settings.reverb}%</output>
            </span>
            <Slider
              aria-label={text.reverb}
              min={0}
              max={100}
              value={settings.reverb}
              onChange={(_, value) => update('reverb', value as number)}
            />
          </label>
        </div>
      </div>
      <details className="studio-shortcuts">
        <summary>{text.shortcuts}</summary>
        <div>
          <kbd>Space</kbd>
          <span>{text.space}</span>
        </div>
        <div>
          <kbd>← →</kbd>
          <span>{text.arrows}</span>
        </div>
        <div>
          <kbd>− +</kbd>
          <span>{text.rate}</span>
        </div>
      </details>
    </>
  );
}
