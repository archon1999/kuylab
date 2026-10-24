import EmptyState from '@shared/ui/EmptyState';
import { useActivity } from '@modules/activity';
import { ArrowBackRounded, PlayArrowRounded } from '@mui/icons-material';
import { Button } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { navigate, useRoute } from '@shared/routing';
import { useEffect, useState } from 'react';
import { useStudio } from '../../../application';
import { filterByStudyStatus, type StudyStatusFilter as StatusFilter } from '../../../domain';
import { StudyStatusFilter } from '../../shared/StudyStatus';
import {
  Favorite,
  Heading,
  SectionTitle,
  StudyCard,
  StudioError,
  openComposition,
} from '../../shared/StudioParts';
import '../../studio.css';
export default function DetailPage() {
  const { params } = useRoute();
  const { catalog } = useStudio();
  const tr = useTranslation();
  const { recordOpen, progress } = useActivity();
  const [status, setStatus] = useState<StatusFilter>('');
  const composition = params.has('composition')
    ? catalog?.compositions.find((item) => item.id === Number(params.get('composition')))
    : catalog?.compositions[0];
  useEffect(() => {
    if (composition) recordOpen(`composition:${composition.id}`);
  }, [composition?.id, recordOpen]);
  if (!composition) return <StudioError message={tr('Kompozitsiya topilmadi.')} />;
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
        eyebrow={composition.subtitle}
        title={composition.title}
        action={<Favorite id={`composition:${composition.id}`} />}
      />
      <div className="studio-detail-intro">
        <p>{composition.composer}</p>
        <div className="studio-actions">
          <Button
            variant="contained"
            startIcon={<PlayArrowRounded />}
            onClick={() => openComposition(composition)}
          >
            {tr('Playerni ochish')}
          </Button>
          {!!catalog?.journeys?.length && (
            <Button component="a" href="#whole-performance">
              {tr('To‘liq ijroga tayyorgarlik')}
            </Button>
          )}
        </div>
      </div>
      <div className="studio-lesson-filter">
        <span>{tr('Darslarni holat bo‘yicha ko‘rsatish')}</span>
        <StudyStatusFilter value={status} onChange={setStatus} />
      </div>
      <section>
        <SectionTitle title={tr('Kompozitsiya darslari')} />
        {!lessons.length && (
          <EmptyState
            kind="lessons"
            title={tr('Bu kompozitsiya uchun hali darslar yo‘q')}
            action={{ label: tr('Playerni ochish'), onClick: () => openComposition(composition) }}
          />
        )}
        {!!lessons.length && !shownLessons.length && (
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
