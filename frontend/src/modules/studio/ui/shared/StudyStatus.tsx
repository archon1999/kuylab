import {
  CheckCircleOutlineRounded,
  ErrorOutlineRounded,
  RadioButtonCheckedRounded,
  RadioButtonUncheckedRounded,
} from '@mui/icons-material';
import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import type { StudyStatus, StudyStatusFilter as StatusFilter } from '../../domain';

export const statusPresentation = {
  not_started: { label: 'Boshlanmagan', Icon: RadioButtonUncheckedRounded },
  learning: { label: 'O‘rganyapman', Icon: RadioButtonCheckedRounded },
  struggling: { label: 'Qiynalyapman', Icon: ErrorOutlineRounded },
  mastered: { label: 'O‘zlashtirdim', Icon: CheckCircleOutlineRounded },
} as const;

export function StudyStatusBadge({ status }: { status: StudyStatus | 'not_started' }) {
  const tr = useTranslation();
  const { label, Icon } = statusPresentation[status];
  return (
    <span className="study-status-badge" data-progress={status}>
      <Icon aria-hidden="true" />
      {tr(label)}
    </span>
  );
}

export function StudyStatusFilter({
  value,
  onChange,
}: {
  value: StatusFilter;
  onChange: (status: StatusFilter) => void;
}) {
  const tr = useTranslation();
  return (
    <FormControl className="study-status-filter" size="small">
      <InputLabel id="study-status-label">{tr('O‘zlashtirish holati')}</InputLabel>
      <Select
        labelId="study-status-label"
        label={tr('O‘zlashtirish holati')}
        value={value}
        onChange={(event) => onChange(event.target.value as StatusFilter)}
      >
        <MenuItem value="">{tr('Barchasi')}</MenuItem>
        {(['not_started', 'learning', 'struggling', 'mastered'] as const).map((status) => (
          <MenuItem key={status} value={status}>
            <StudyStatusBadge status={status} />
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
