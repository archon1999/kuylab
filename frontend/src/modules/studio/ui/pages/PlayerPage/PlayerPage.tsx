import { useActivity, PracticeNotebook } from '@modules/activity';
import { StudioPlayer } from '@modules/practice';
import { ArrowBackRounded } from '@mui/icons-material';
import { Button } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { navigate, useRoute } from '@shared/routing';
import { useEffect } from 'react';
import { useStudio, useStudyScore } from '../../../application';
import { compositionPlaybackContext, selectCompositionVariant } from '../../../domain';
import CompositionVariants from '../../shared/CompositionVariants';
import { Loading, StudioError } from '../../shared/StudioParts';
import '../../studio.css';
export default function PlayerPage() {
  const { catalog } = useStudio();
  const { params } = useRoute();
  const tr = useTranslation();
  const { recordOpen, positions, setPosition, setPlaying, lastStages, setStage } = useActivity();
  const composition = params.has('composition')
    ? catalog?.compositions.find((item) => item.id === Number(params.get('composition')))
    : catalog?.compositions[0];
  const id = composition ? `composition:${composition.id}` : null;
  const variant = selectCompositionVariant(
    composition,
    params.get('variant'),
    lastStages[`${id}:variant`],
  );
  const context = composition ? compositionPlaybackContext(composition, variant?.id) : '';
  const scoreId = variant?.score_id ?? composition?.score_id;
  const { score, loading, error, reload } = useStudyScore(scoreId);
  useEffect(() => {
    if (id && variant) setStage(`${id}:variant`, variant.id);
  }, [id, variant?.id]);
  useEffect(() => {
    if (id) recordOpen(id);
    return () => setPlaying(false);
  }, [id, recordOpen, setPlaying]);
  const onBack = () =>
    composition ? navigate('detail', { compositionSlug: composition.slug }) : navigate('library');
  if (!composition)
    return (
      <div className="studio-player-fallback">
        <Button startIcon={<ArrowBackRounded />} onClick={() => navigate('library')}>
          {tr('Kompozitsiyalar')}
        </Button>
        <StudioError message={tr('Kompozitsiya topilmadi.')} />
      </div>
    );
  return (
    <div className="studio-player-page">
      {loading && <Loading />}
      {error && (
        <div className="studio-player-fallback">
          <Button onClick={onBack}>{tr('Orqaga')}</Button>
          <StudioError message={error} retry={reload} />
        </div>
      )}
      {score && (
        <StudioPlayer
          key={String(score.id)}
          title={`${composition.title}${variant ? ' · ' + variant.title : ''}`}
          contextId={context}
          readableHolds={composition.readable_holds}
          toolbarAccessory={
            composition.variants && composition.variants.length > 1
              ? (position, pause) => (
                  <CompositionVariants
                    compact
                    variants={composition.variants!}
                    value={variant!.id}
                    onChange={(next) => {
                      if (next === variant!.id) return;
                      pause();
                      setPlaying(false);
                      navigate('practice', {
                        composition: composition.id,
                        variant: next,
                        at: Number(position.toFixed(3)),
                      });
                    }}
                  />
                )
              : undefined
          }
          notebook={(position, seek, close) => (
            <PracticeNotebook contentId={id!} position={position} onSeek={seek} onClose={close} />
          )}
          score={score}
          markers={catalog?.lessons
            .filter((item) => item.composition_id === composition.id && item.source)
            .filter(
              (item, index, array) =>
                array.findIndex(
                  (value) => value.source?.start_seconds === item.source?.start_seconds,
                ) === index,
            )
            .map((item) => ({ time: item.source!.start_seconds, label: item.title }))
            .sort((a, b) => a.time - b.time)}
          onBack={onBack}
          initialPosition={
            params.has('at')
              ? Number(params.get('at'))
              : (positions[context] ?? positions[id!] ?? 0)
          }
          onPositionChange={(seconds) => {
            setPosition(context, seconds);
            if (context !== id) setPosition(id!, seconds);
          }}
          onPlaybackChange={setPlaying}
        />
      )}
    </div>
  );
}
