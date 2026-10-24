import { Skeleton } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import BrandMark from './BrandMark';
import './loading.css';

export function StudioSplash({ label }: { label: string }) {
  return (
    <div className="studio-splash" role="status" aria-label={label} aria-busy="true">
      <div className="studio-splash-brand loading-visual" aria-hidden="true">
        <BrandMark />
        <span>KuyLab</span>
        <span className="loading-track">
          <i />
        </span>
      </div>
    </div>
  );
}

function CardGrid() {
  return (
    <div className="skeleton-grid">
      {Array.from({ length: 6 }, (_, i) => (
        <div className="skeleton-card" key={i}>
          <Skeleton width={75} height={12} />
          <Skeleton width="76%" height={24} />
          <Skeleton width="90%" height={12} />
          <Skeleton width="58%" height={12} />
          <Skeleton width="42%" height={10} />
        </div>
      ))}
    </div>
  );
}

function SummaryRow() {
  return (
    <div className="skeleton-summary">
      {Array.from({ length: 3 }, (_, i) => (
        <div key={i}>
          <Skeleton width={90} height={12} />
          <Skeleton width={70} height={30} />
        </div>
      ))}
    </div>
  );
}

export function PageSkeleton({
  variant = 'page',
}: {
  variant?: 'page' | 'library' | 'collection' | 'detail' | 'study' | 'settings' | 'statistics';
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
      <div className="skeleton-content loading-visual" aria-hidden="true">
        {(variant === 'detail' || variant === 'study') && (
          <Skeleton className="skeleton-back" width={120} height={14} />
        )}
        <Skeleton className="skeleton-title" width="min(380px, 72%)" height={38} />
        {variant === 'settings' ? (
          <div className="skeleton-settings">
            <Skeleton width={145} height={20} />
            <div className="skeleton-form">
              {Array.from({ length: 6 }, (_, i) => (
                <Skeleton key={i} height={54} />
              ))}
            </div>
          </div>
        ) : variant === 'study' ? (
          <>
            <div className="skeleton-stage-options">
              {[0, 1, 2].map((i) => (
                <Skeleton key={i} width={150} height={40} />
              ))}
            </div>
            <PlayerSkeleton compact />
          </>
        ) : variant === 'library' ? (
          <div className="skeleton-compositions">
            {[0, 1, 2].map((i) => (
              <div className="skeleton-composition" key={i}>
                <div className="skeleton-composition-art">
                  <BrandMark />
                </div>
                <div className="skeleton-composition-copy">
                  <Skeleton width="38%" height={12} />
                  <Skeleton width="70%" height={30} />
                  <Skeleton width={100} height={12} />
                  <Skeleton width={150} height={40} />
                </div>
              </div>
            ))}
          </div>
        ) : variant === 'page' ? (
          <>
            <div className="skeleton-hero">
              <div>
                <Skeleton width={125} height={12} />
                <Skeleton width="78%" height={32} />
                <Skeleton width={90} height={12} />
                <Skeleton width={155} height={42} />
              </div>
              <BrandMark />
            </div>
            <SummaryRow />
            <div className="skeleton-columns">
              {[0, 1].map((i) => (
                <div className="skeleton-list" key={i}>
                  <Skeleton width={160} height={22} />
                  <Skeleton width="80%" height={14} />
                  <Skeleton width="65%" height={14} />
                </div>
              ))}
            </div>
          </>
        ) : variant === 'statistics' ? (
          <>
            <SummaryRow />
            <div className="skeleton-chart">
              <Skeleton width={180} height={20} />
              <div className="skeleton-chart-lines">
                {[0, 1, 2, 3].map((i) => (
                  <Skeleton key={i} width="100%" height={1} />
                ))}
              </div>
            </div>
          </>
        ) : (
          <>
            {variant === 'collection' && (
              <div className="skeleton-filters">
                {[0, 1, 2, 3].map((i) => (
                  <Skeleton key={i} height={52} />
                ))}
              </div>
            )}
            {variant === 'detail' && <Skeleton width={155} height={42} />}
            <CardGrid />
          </>
        )}
      </div>
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
      <div className="skeleton-transport loading-visual" aria-hidden="true">
        <BrandMark />
        <Skeleton variant="circular" width={34} height={34} />
        <Skeleton width="55%" height={16} />
        <Skeleton width={95} height={38} />
      </div>
      <div className="skeleton-roll loading-visual" aria-hidden="true">
        <BrandMark />
        <span className="loading-track">
          <i />
        </span>
      </div>
      <div className="skeleton-keys loading-visual" aria-hidden="true">
        {Array.from({ length: 28 }, (_, i) => (
          <i key={i} />
        ))}
      </div>
    </div>
  );
}
