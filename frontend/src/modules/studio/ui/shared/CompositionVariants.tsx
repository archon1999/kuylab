import { ToggleButton, ToggleButtonGroup, Tooltip } from '@mui/material';
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
  return (
    <div className={`composition-variants ${compact ? 'composition-variants-compact' : ''}`}>
      {!compact && <span>{tr('Ijro varianti')}</span>}
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
    </div>
  );
}
