import { StarRounded } from '@mui/icons-material';
import { useTranslation } from '@shared/i18n';

export default function DifficultyStars({ value }: { value: number | undefined }) {
  const tr = useTranslation();
  if (!value) return null;
  const rating = Math.min(5, Math.max(1, Math.round(value)));
  return (
    <span
      className="composition-difficulty"
      role="img"
      aria-label={tr('Qiyinchilik: {0}/5', [rating])}
      title={tr('Qiyinchilik: {0}/5', [rating])}
    >
      <span aria-hidden="true">
        {Array.from({ length: 5 }, (_, index) => (
          <StarRounded key={index} className={index < rating ? 'is-filled' : ''} />
        ))}
      </span>
      <small aria-hidden="true">{rating}/5</small>
    </span>
  );
}
