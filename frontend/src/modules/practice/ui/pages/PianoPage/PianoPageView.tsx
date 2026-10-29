import { useState } from 'react';
import { Button, Drawer, useMediaQuery } from '@mui/material';
import { PianoRounded, SettingsOutlined } from '@mui/icons-material';
import { usePreferences, useTranslation } from '@shared/i18n';
import type { StudioPreferencePort } from '../../../domain/studioPreferences';
import { useStudioPreferences } from '../../../application/useStudioPreferences';
import StudioRollViewport from '../../shared/StudioRollViewport';
import StudioSettings from '../../shared/StudioSettings';
import { studioLabels } from '../../shared/studioLabels';
import '../../studioPlayer.css';
import './pianoPage.css';

const notes: [] = [];
export default function PianoPageView({ preferences }: { preferences: StudioPreferencePort }) {
  const tr = useTranslation();
  const { language, mode } = usePreferences();
  const { preferences: settings, update } = useStudioPreferences(preferences);
  const [open, setOpen] = useState(false);
  const [visibleKeys, setVisibleKeys] = useState(88);
  const reducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)');
  const text = studioLabels[language];
  return (
    <div className="free-piano-page">
      <div className="free-piano-heading">
        <div>
          <h1>{tr('Pianino')}</h1>
          <p>{tr('Klavishlarni bosib chaling. Bir nechta tovushni birga ushlash mumkin.')}</p>
        </div>
        <Button startIcon={<SettingsOutlined />} variant="outlined" onClick={() => setOpen(true)}>
          {tr('Sozlamalar')}
        </Button>
      </div>
      <section
        className="studio-player free-piano-instrument"
        data-color-mode={mode}
        aria-label={tr('Pianino chalish')}
      >
        <StudioRollViewport
          notes={notes}
          position={0}
          playing={false}
          reducedMotion={reducedMotion}
          settings={settings}
          dark={mode === 'dark'}
          label={text.keyboard}
          text={text}
          onZoom={(zoom) => update('visibleKeys', Math.round(88 / zoom))}
          onVisibleKeysChange={setVisibleKeys}
          keyboardSize={160}
        />
        <div className="free-piano-emblem" aria-hidden="true">
          <PianoRounded />
          <span>{tr('Royal')}</span>
        </div>
      </section>
      <div className="free-piano-shortcuts">
        <span>{tr('Kompyuter klaviaturasi')}</span>
        <kbd>A W S E D F T G Y H U J K</kbd>
        <span>C4 — C5</span>
      </div>
      <Drawer
        anchor="right"
        open={open}
        onClose={() => setOpen(false)}
        slotProps={{
          paper: { className: 'studio-settings', role: 'dialog', 'aria-label': text.settings },
        }}
      >
        <StudioSettings
          settings={settings}
          update={update}
          text={text}
          reducedMotion={reducedMotion}
          onClose={() => setOpen(false)}
          visibleKeys={visibleKeys}
          freePiano
        />
      </Drawer>
    </div>
  );
}
