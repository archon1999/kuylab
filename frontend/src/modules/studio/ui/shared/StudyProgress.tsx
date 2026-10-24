import { useEffect, useState } from 'react';
import { useActivity } from '@modules/activity';
import { TextField, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { useTranslation } from '@shared/i18n';
export default function StudyProgress({ id, staged }: { id: string; staged: boolean }) {
  const tr = useTranslation();
  const { progress, setProgress, comfortableSpeeds, setComfortableSpeed } = useActivity();
  const saved = comfortableSpeeds[id];
  const [draft, setDraft] = useState(saved ? String(saved) : '');
  useEffect(() => setDraft(saved ? String(saved) : ''), [id, saved]);
  const valid =
    draft === '' ||
    (Number.isInteger(Number(draft)) && Number(draft) >= 20 && Number(draft) <= 200);
  return (
    <section
      className="study-progress-panel"
      aria-label={tr(staged ? 'Joriy bosqich holati' : 'O‘zlashtirish holati')}
    >
      <div>
        <small>{tr(staged ? 'Joriy bosqich holati' : 'O‘zlashtirish holati')}</small>
        <ToggleButtonGroup
          className="study-progress"
          size="small"
          exclusive
          value={progress[id] || null}
          onChange={(_, value) => setProgress(id, value)}
          aria-label={tr('O‘zlashtirish holati')}
        >
          <ToggleButton value="learning">{tr('O‘rganyapman')}</ToggleButton>
          <ToggleButton value="struggling">{tr('Qiynalyapman')}</ToggleButton>
          <ToggleButton value="mastered">{tr('O‘zlashtirdim')}</ToggleButton>
        </ToggleButtonGroup>
      </div>
      <TextField
        size="small"
        type="number"
        label={tr('Qulay tezligim (%)')}
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        onBlur={() => {
          if (valid) setComfortableSpeed(id, draft ? Number(draft) : null);
        }}
        error={!valid}
        helperText={tr(
          valid
            ? 'O‘zingiz ravon chalgan tezlik. Namuna = 100%.'
            : '20–200 orasida butun son kiriting.',
        )}
        slotProps={{ htmlInput: { min: 20, max: 200, step: 5 } }}
      />
    </section>
  );
}
