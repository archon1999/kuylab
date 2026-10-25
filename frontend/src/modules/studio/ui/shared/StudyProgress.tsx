import { useActivity } from '@modules/activity';
import { ToggleButton, ToggleButtonGroup } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { statusPresentation } from './StudyStatus';
export default function StudyProgress({
  id,
  staged,
  atEnd = false,
  automatic = false,
}: {
  id: string;
  staged: boolean;
  atEnd?: boolean;
  automatic?: boolean;
}) {
  const tr = useTranslation();
  const { progress, setProgress } = useActivity();
  return (
    <section
      className="study-progress-panel"
      data-study-progress
      aria-label={tr(
        atEnd ? 'Dars yakunidagi holat' : staged ? 'Joriy bosqich holati' : 'O‘zlashtirish holati',
      )}
    >
      <div>
        <small>
          {tr(
            atEnd
              ? 'Dars yakunidagi holat'
              : staged
                ? 'Joriy bosqich holati'
                : 'O‘zlashtirish holati',
          )}
        </small>
        <ToggleButtonGroup
          className="study-progress"
          size="small"
          exclusive
          value={progress[id] || null}
          onChange={(_, value) => setProgress(id, value)}
          aria-label={tr('O‘zlashtirish holati')}
        >
          {(['learning', 'struggling', 'mastered'] as const).map((status) => {
            const { label, Icon } = statusPresentation[status];
            return (
              <ToggleButton key={status} value={status} data-progress={status}>
                <Icon aria-hidden="true" />
                {tr(label)}
              </ToggleButton>
            );
          })}
        </ToggleButtonGroup>
        {automatic && atEnd && (
          <p className="study-progress-caption">
            {tr(
              'Holat javoblaringizga qarab yangilanadi. Uni qo‘lda ham o‘zgartirishingiz mumkin.',
            )}
          </p>
        )}
      </div>
    </section>
  );
}
