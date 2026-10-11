import { Skeleton } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import BrandMark from './BrandMark';
import './loading.css';

export function PageSkeleton({
  variant = 'page',
}: {
  variant?: 'page' | 'library' | 'study' | 'settings' | 'statistics';
}) {
  const tr = useTranslation();
  return (
    <div
      className={`page-skeleton page-skeleton-${variant}`}
      role="status"
      aria-label={tr('Yuklanmoqda…')}
      aria-busy="true"
    >
      <span className="sr-only">{tr('Yuklanmoqda…')}</span>
      <div aria-hidden="true">
        <Skeleton width={110} height={18} />
        <Skeleton width="48%" height={58} />
      </div>
      {variant === 'settings' ? (
        <div className="skeleton-form" aria-hidden="true">
          {Array.from({ length: 6 }, (_, i) => (
            <Skeleton key={i} variant="rounded" height={54} />
          ))}
        </div>
      ) : variant === 'study' ? (
        <>
          <Skeleton width="85%" height={28} />
          <PlayerSkeleton compact />
        </>
      ) : (
        <>
          {variant === 'page' && <Skeleton variant="rounded" height={252} />}
          <div className="skeleton-grid" aria-hidden="true">
            {Array.from({ length: variant === 'statistics' ? 3 : 6 }, (_, i) => (
              <div className="skeleton-card" key={i}>
                <Skeleton width={65} />
                <Skeleton width="72%" height={34} />
                <Skeleton width="90%" />
                <Skeleton width="60%" />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export function PlayerSkeleton({ compact = false }: { compact?: boolean }) {
  const tr = useTranslation();
  return (
    <div
      className={`player-skeleton ${compact ? 'compact' : ''}`}
      role="status"
      aria-label={tr('MIDI yuklanmoqda…')}
      aria-busy="true"
    >
      <span className="sr-only">{tr('MIDI yuklanmoqda…')}</span>
      <div className="skeleton-transport" aria-hidden="true">
        <BrandMark />
        <Skeleton variant="circular" width={34} height={34} />
        <Skeleton width="55%" height={16} />
        <Skeleton width={95} height={38} />
      </div>
      <div className="skeleton-roll" aria-hidden="true">
        <BrandMark />
        <span className="loading-track">
          <i />
        </span>
      </div>
      <div className="skeleton-keys" aria-hidden="true">
        {Array.from({ length: 28 }, (_, i) => (
          <i key={i} />
        ))}
      </div>
    </div>
  );
}
