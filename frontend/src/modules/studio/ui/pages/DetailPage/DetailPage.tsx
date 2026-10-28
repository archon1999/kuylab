import EmptyState from '@shared/ui/EmptyState';
import { useActivity } from '@modules/activity';
import { ArrowBackRounded, PianoOutlined, PlayArrowRounded } from '@mui/icons-material';
import { Button } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { followRouteLink, navigate, replaceRoute, routePath, useRoute } from '@shared/routing';
import { useEffect, useState } from 'react';
import { useStudio } from '../../../application';
import {
  filterByStudyStatus,
  selectCompositionVariant,
  compositionAttribution,
  type StudyStatusFilter as StatusFilter,
} from '../../../domain';
import CompositionVariants from '../../shared/CompositionVariants';
import DifficultyStars from '../../shared/DifficultyStars';
import { StudyStatusFilter } from '../../shared/StudyStatus';
import { Favorite, Heading, SectionTitle, StudyCard, StudioError } from '../../shared/StudioParts';
import '../../studio.css';
export default function DetailPage() {
  const { params } = useRoute();
  const { catalog } = useStudio();
  const tr = useTranslation();
  const { recordOpen, progress, lastStages, setStage } = useActivity();
  const [requestedVariant, setRequestedVariant] = useState<string | null>(null);
  const [status, setStatus] = useState<StatusFilter>('');
  const composition = params.has('compositionSlug')
    ? catalog?.compositions.find((item) => item.slug === params.get('compositionSlug'))
    : params.has('composition')
      ? catalog?.compositions.find((item) => item.id === Number(params.get('composition')))
      : catalog?.compositions[0];
  useEffect(() => {
    if (composition) recordOpen(`composition:${composition.id}`);
  }, [composition?.id, recordOpen]);
  useEffect(() => {
    if (composition && !params.has('compositionSlug'))
      replaceRoute('detail', { compositionSlug: composition.slug });
  }, [composition?.slug, params.has('compositionSlug')]);
  if (!composition) return <StudioError message={tr('Kompozitsiya topilmadi.')} />;
  const attribution = compositionAttribution(composition);
  const variant = selectCompositionVariant(
    composition,
    requestedVariant,
    lastStages[`composition:${composition.id}:variant`],
  );
  const lessons = catalog?.lessons.filter((item) => composition.lesson_ids.includes(item.id)) || [];
  const journeys =
    catalog?.journeys?.filter((item) => item.composition_id === composition.id) || [];
  const shownLessons = filterByStudyStatus(lessons, status, progress);
  const shownJourneys = filterByStudyStatus(journeys, status, progress);
  return (
    <div className="studio-page">
      <Button
        className="studio-back"
        startIcon={<ArrowBackRounded />}
        onClick={() => navigate('library')}
      >
        {tr('Kompozitsiyalar')}
      </Button>
      <Heading
        eyebrow={attribution.category || composition.subtitle}
        title={composition.title}
        action={<Favorite id={`composition:${composition.id}`} />}
      />
      <div className="studio-detail-intro">
        <DifficultyStars value={variant?.difficulty || composition.difficulty} />
        {attribution.composer && <p>{attribution.composer}</p>}
        {composition.variants && variant && (
          <div className="composition-variant-intro">
            <CompositionVariants
              variants={composition.variants}
              value={variant.id}
              onChange={(next) => {
                setRequestedVariant(next);
                setStage(`composition:${composition.id}:variant`, next);
              }}
            />
            <p>{variant.description}</p>
            {!!lessons.length && !composition.variants.some((value) => value.playback_revision) && (
              <small>{tr('Darslar barcha ijro variantlari uchun umumiy.')}</small>
            )}
          </div>
        )}
        <div className="studio-actions">
          <Button
            component="a"
            href={routePath('practice', {
              composition: composition.id,
              variant: variant?.id || null,
            })}
            variant="contained"
            startIcon={<PlayArrowRounded />}
            onClick={followRouteLink}
          >
            {tr('Playerni ochish')}
          </Button>
          {!!journeys.length && (
            <Button component="a" href="#whole-performance">
              {tr('To‘liq ijroga tayyorgarlik')}
            </Button>
          )}
        </div>
      </div>
      {!!(lessons.length || journeys.length) && (
        <div className="studio-lesson-filter">
          <span>{tr('Darslarni holat bo‘yicha ko‘rsatish')}</span>
          <StudyStatusFilter value={status} onChange={setStatus} />
        </div>
      )}
      {lessons.length ? (
        <section>
          <SectionTitle title={tr('Kompozitsiya darslari')} />
          {!shownLessons.length && (
            <EmptyState
              compact
              kind="search"
              title={tr('Bu holatda darslar yo‘q')}
              action={{ label: tr('Barcha darslar'), onClick: () => setStatus('') }}
            />
          )}
          <div className="studio-card-grid">
            {shownLessons.map((item) => (
              <StudyCard
                key={item.id}
                item={item}
                number={lessons.findIndex((value) => value.id === item.id) + 1}
              />
            ))}
          </div>
        </section>
      ) : (
        <div className="composition-course-note" role="note">
          <PianoOutlined aria-hidden="true" />
          <div>
            <h2>{tr('Playerda o‘rganish')}</h2>
            <p>{tr('Bu kompozitsiya uchun alohida darslar hali tayyorlanmagan.')}</p>
          </div>
        </div>
      )}
      {!!journeys.length && (
        <section id="whole-performance" style={{ scrollMarginTop: 24 }}>
          <SectionTitle title={tr('To‘liq ijroga tayyorgarlik')} />
          <div className="studio-card-grid">
            {shownJourneys.map((item) => (
              <StudyCard key={item.id} item={item} />
            ))}
          </div>
          {!shownJourneys.length && (
            <EmptyState
              compact
              kind="search"
              title={tr('Bu holatda darslar yo‘q')}
              action={{ label: tr('Barcha darslar'), onClick: () => setStatus('') }}
            />
          )}
        </section>
      )}
    </div>
  );
}
