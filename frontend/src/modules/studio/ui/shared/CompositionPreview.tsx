import { useRef } from 'react';
import { MusicNoteRounded, RefreshRounded } from '@mui/icons-material';
import { IconButton, Skeleton, Tooltip } from '@mui/material';
import { PianoRollPreview } from '@modules/practice';
import { useTranslation } from '@shared/i18n';
import { useCompositionPreview } from '../../application/useCompositionPreview';
import type { Composition } from '../../domain';

export default function CompositionPreview({
  composition,
  variant,
}: {
  composition: Composition;
  variant?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const tr = useTranslation();
  const { preview, error, visible, reload } = useCompositionPreview(composition.id, variant, ref);
  return (
    <div
      ref={ref}
      className="studio-composition-art composition-preview"
      aria-busy={!preview && !error}
    >
      {preview ? (
        <>
          <PianoRollPreview
            key={preview.score_id}
            notes={preview.notes}
            duration={preview.duration_seconds}
            active={visible}
            compactHolds={composition.readable_holds}
            label={tr('{0}: asardan tushayotgan notalar', [composition.title])}
          />
        </>
      ) : error ? (
        <div className="composition-preview-state" role="status">
          <MusicNoteRounded />
          <small>{tr('Previewni yuklab bo‘lmadi.')}</small>
          <Tooltip title={tr('Qayta urinish')}>
            <IconButton aria-label={tr('Previewni qayta yuklash')} onClick={reload}>
              <RefreshRounded />
            </IconButton>
          </Tooltip>
        </div>
      ) : (
        <div
          className="composition-preview-state"
          role="status"
          aria-label={tr('Preview yuklanmoqda')}
        >
          <div className="composition-preview-skeleton" aria-hidden="true">
            <Skeleton variant="rounded" width={13} height={75} />
            <Skeleton variant="rounded" width={13} height={112} />
            <Skeleton variant="rounded" width={13} height={55} />
          </div>
        </div>
      )}
    </div>
  );
}
