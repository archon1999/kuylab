import { MenuItem, Select, ToggleButton, ToggleButtonGroup, Tooltip } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import type { CompositionVariant } from '../../domain';

export default function CompositionVariants({
  variants,
  value,
  onChange,
  compact = false,
}: {
  variants: CompositionVariant[];
  value: string;
  onChange: (id: string) => void;
  compact?: boolean;
}) {
  const tr = useTranslation();
  const dropdown =
    variants.length > 2 || (compact && variants.some((item) => item.title.length > 18));
  return (
    <div className={`composition-variants ${compact ? 'composition-variants-compact' : ''}`}>
      {!compact && <span>{tr('Ijro varianti')}</span>}
      {dropdown ? (
        <Select
          className="composition-variant-select"
          size="small"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          inputProps={{ 'aria-label': tr('Ijro varianti') }}
          renderValue={(id) => variants.find((item) => item.id === id)?.title || ''}
          MenuProps={{
            slotProps: {
              paper: { className: 'composition-variant-menu' },
            },
          }}
        >
          {variants.map((variant) => (
            <MenuItem key={variant.id} value={variant.id}>
              <span className="composition-variant-option">
                <strong>{variant.title}</strong>
                {variant.description && <small>{variant.description}</small>}
              </span>
            </MenuItem>
          ))}
        </Select>
      ) : (
        <ToggleButtonGroup
          exclusive
          size="small"
          value={value}
          onChange={(_, id: string | null) => id && onChange(id)}
          aria-label={tr('Ijro varianti')}
        >
          {variants.map((variant) => (
            <Tooltip key={variant.id} title={variant.description}>
              <ToggleButton
                value={variant.id}
                aria-label={`${variant.title} · ${variant.description}`}
              >
                {variant.title}
              </ToggleButton>
            </Tooltip>
          ))}
        </ToggleButtonGroup>
      )}
    </div>
  );
}
