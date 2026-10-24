import EmptyState from '@shared/ui/EmptyState';
import BrandMark from '@shared/ui/BrandMark';
import { useActivity } from '@modules/activity';
import { useProfile } from '@modules/profile';
import {
  ArrowForwardRounded,
  AutoStoriesOutlined,
  PianoRounded,
  PlayArrowRounded,
} from '@mui/icons-material';
import { Button } from '@mui/material';
import { usePreferences, useTranslation } from '@shared/i18n';
import { navigate } from '@shared/routing';
import { useStudio } from '../../../application';
import { durationLabel, studyCountLabel } from '../../../domain';
import {
  ContentRow,
  Heading,
  SectionTitle,
  StudyCard,
  openComposition,
} from '../../shared/StudioParts';
import '../../studio.css';
import RecentNotes from '../../shared/RecentNotes';
import { StudyStatusBadge } from '../../shared/StudyStatus';
export default function DashboardPage() {
  const tr = useTranslation();
  const { language } = usePreferences();
  const { catalog } = useStudio();
  const { profile } = useProfile();
  const { recents, favorites, stats, positions, lastStages, progress } = useActivity();
  if (!catalog) return null;
  const currentId = recents.find((item) => item.id.startsWith('composition:'))?.id;
  const composition =
    catalog.compositions.find((value) => `composition:${value.id}` === currentId) ||
    catalog.compositions[0];
  const validIds = new Set([
    ...catalog.compositions.map((value) => `composition:${value.id}`),
    ...catalog.lessons.map((value) => value.id),
    ...catalog.exercises.map((value) => value.id),
    ...catalog.theory.map((value) => value.id),
    ...(catalog.journeys || []).map((value) => value.id),
  ]);
  const recent = recents.filter((value) => validIds.has(value.id)).slice(0, 4);
  const lastStudy = [
    ...catalog.lessons,
    ...catalog.exercises,
    ...catalog.theory,
    ...(catalog.journeys || []),
  ].find((item) => item.id === recent[0]?.id);
  const lastStage = lastStudy?.stages?.find((stage) => stage.id === lastStages[lastStudy.id]);
  const lastProgress = lastStudy && progress[lastStage?.id || lastStudy.id];
  const saved = favorites.filter((value) => validIds.has(value)).slice(0, 4);
  return (
    <div className="studio-page studio-dashboard">
      <Heading title={tr('Salom, {0}', [profile.display_name])} />
      {composition && (
        <section className="studio-hero">
          <div>
            <p className="studio-eyebrow">
              {tr(
                positions[`composition:${composition.id}`]
                  ? 'Davom etish'
                  : 'Bugun pianino chalamiz',
              )}
            </p>
            <h2>{composition.title}</h2>
            <p className="studio-hero-caption">
              {durationLabel(composition.duration_seconds)} ·{' '}
              {studyCountLabel(composition.lesson_ids.length, 'lesson', language)}
            </p>
            <div className="studio-actions">
              <Button
                variant="contained"
                startIcon={<PlayArrowRounded />}
                onClick={() => openComposition(composition)}
              >
                {tr(positions[`composition:${composition.id}`] ? 'Davom etish' : 'Playerni ochish')}
              </Button>
              <Button onClick={() => navigate('detail', { composition: composition.id })}>
                {tr('Darslar')}
                <ArrowForwardRounded sx={{ ml: 1, fontSize: 18 }} />
              </Button>
            </div>
          </div>
          <div className="studio-hero-art" aria-hidden="true">
            <BrandMark />
          </div>
        </section>
      )}
      {lastStudy && (
        <section className="studio-resume">
          <div>
            <small>{tr('Davom etish')}</small>
            <h2>{lastStudy.title}</h2>
            {(lastStage || lastProgress) && (
              <div className="studio-resume-meta">
                {lastStage && <span>{lastStage.title}</span>}
                {lastProgress && <StudyStatusBadge status={lastProgress} />}
              </div>
            )}
          </div>
          <Button
            onClick={() => navigate('study', { item: lastStudy.id, stage: lastStage?.id || null })}
            endIcon={<ArrowForwardRounded />}
          >
            {tr('Davom etish')}
          </Button>
        </section>
      )}
      <div className="studio-week-strip">
        <div>
          <span>{tr('Shu hafta')}</span>
          <strong>
            {Math.floor(stats.weekSeconds / 60)} <small>{tr('daq.')}</small>
          </strong>
          <span>{tr('saytda o‘tkazilgan vaqt')}</span>
        </div>
        <div>
          <span>{tr('Oxirgi faollik')}</span>
          <strong className="studio-last-activity">
            {recent[0] ? <ContentName id={recent[0].id} /> : tr('Hali faollik yo‘q')}
          </strong>
        </div>
        <Button onClick={() => navigate('statistics')} endIcon={<ArrowForwardRounded />}>
          {tr('Statistika')}
        </Button>
      </div>
      <div className="studio-dashboard-columns">
        <section>
          <SectionTitle title={tr('Sevimlilar')} />
          <div className="studio-list-surface">
            {saved.length ? (
              saved.map((id) => <ContentRow key={id} id={id} />)
            ) : (
              <EmptyState
                kind="favorites"
                title={tr('Hozircha sevimlilar yo‘q')}
                description={tr('Yoqtirgan asar yoki mashqingizdagi yurakchani bosing.')}
                action={{
                  label: tr('Kompozitsiyalarni ko‘rish'),
                  onClick: () => navigate('library'),
                }}
              />
            )}
          </div>
        </section>
        <section>
          <SectionTitle title={tr('Oxirgi ochilganlar')} />
          <div className="studio-list-surface">
            {recent.length ? (
              recent.map((item) => <ContentRow key={item.id} id={item.id} />)
            ) : (
              <EmptyState
                kind="recent"
                title={tr('Birinchi kuy sizni kutmoqda')}
                description={tr('Ochgan kompozitsiya va mashqlaringiz shu yerda ko‘rinadi.')}
                action={{ label: tr('Mashqlarni ko‘rish'), onClick: () => navigate('exercises') }}
              />
            )}
          </div>
        </section>
      </div>
      <div className="studio-paths">
        <button onClick={() => navigate('exercises')}>
          <PianoRounded />
          <span>
            <strong>{tr('Mashqlar')}</strong>
            <small>
              {studyCountLabel(catalog.exercises.length, 'exercise', language)} · {tr('Uch daraja')}
            </small>
          </span>
          <ArrowForwardRounded />
        </button>
        <button onClick={() => navigate('theory')}>
          <AutoStoriesOutlined />
          <span>
            <strong>{tr('Amaliy nazariya')}</strong>
            <small>
              {studyCountLabel(catalog.theory.length, 'theory', language)} ·{' '}
              {tr('Ko‘ring, eshiting, sinab ko‘ring')}
            </small>
          </span>
          <ArrowForwardRounded />
        </button>
      </div>
      <RecentNotes />
      {catalog.theory[0] && (
        <section>
          <SectionTitle
            title={tr('Nazariyadan bir mavzu')}
            action={<Button onClick={() => navigate('theory')}>{tr('Barcha mavzular')}</Button>}
          />
          <div className="studio-featured-theory">
            <StudyCard item={catalog.theory[0]} />
          </div>
        </section>
      )}
    </div>
  );
}
function ContentName({ id }: { id: string }) {
  const { catalog } = useStudio();
  return (
    catalog?.compositions.find((item) => `composition:${item.id}` === id)?.title ||
    [
      ...(catalog?.lessons || []),
      ...(catalog?.exercises || []),
      ...(catalog?.theory || []),
      ...(catalog?.journeys || []),
    ].find((item) => item.id === id)?.title ||
    ''
  );
}
