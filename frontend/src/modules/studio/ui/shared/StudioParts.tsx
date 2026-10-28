import ErrorState from '@shared/ui/ErrorState';
import { useActivity } from '@modules/activity';
import {
  ArrowForwardRounded,
  FavoriteBorderRounded,
  FavoriteRounded,
  MusicNoteRounded,
  PlayArrowRounded,
} from '@mui/icons-material';
import { Button, IconButton, Tooltip } from '@mui/material';
import { usePreferences, useTranslation } from '@shared/i18n';
import { followRouteLink, navigate, routePath } from '@shared/routing';
import { useStudio } from '../../application';
import { StudyStatusBadge } from './StudyStatus';
import CompositionPreview from './CompositionPreview';
import DifficultyStars from './DifficultyStars';
import '../compositionLibrary.css';
import {
  durationLabel,
  studyCountLabel,
  studyProgress,
  allStudyItems,
  libraryVariant,
  compositionAttribution,
  studyMatchesPerformance,
  type Composition,
  type StudyItem,
} from '../../domain';

export function Heading({
  eyebrow,
  title,
  action,
}: {
  eyebrow?: string;
  title: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="studio-heading">
      <div>
        {eyebrow && <p className="studio-eyebrow">{eyebrow}</p>}
        <h1>{title}</h1>
      </div>
      {action}
    </div>
  );
}
export function SectionTitle({ title, action }: { title: string; action?: React.ReactNode }) {
  return (
    <div className="studio-section-title">
      <h2>{title}</h2>
      {action}
    </div>
  );
}
export function Favorite({ id }: { id: string }) {
  const tr = useTranslation();
  const { favorites, toggleFavorite } = useActivity();
  const selected = favorites.includes(id);
  return (
    <Tooltip title={tr(selected ? 'Sevimlilardan olib tashlash' : 'Sevimlilarga qo‘shish')}>
      <IconButton
        aria-label={tr(selected ? 'Sevimlilardan olib tashlash' : 'Sevimlilarga qo‘shish')}
        aria-pressed={selected}
        onClick={() => toggleFavorite(id)}
        className={`studio-favorite ${selected ? 'selected' : ''}`}
      >
        {selected ? <FavoriteRounded /> : <FavoriteBorderRounded />}
      </IconButton>
    </Tooltip>
  );
}
export function StudioError({ message, retry }: { message: string; retry?: () => void }) {
  const tr = useTranslation();
  return (
    <ErrorState
      title={message}
      action={
        retry
          ? { label: tr('Qayta urinish'), onClick: retry }
          : { label: tr('Bosh sahifa'), onClick: () => navigate('dashboard') }
      }
    />
  );
}
export { PlayerSkeleton as Loading } from '@shared/ui/Loading';
export function openComposition(composition: Composition) {
  navigate('practice', { composition: composition.id, score: composition.score_id, item: null });
}
export function StudyCard({ item, number }: { item: StudyItem; number?: number }) {
  const tr = useTranslation();
  const { catalog } = useStudio();
  const { progress } = useActivity();
  const learned = studyProgress(item, progress);
  const category = catalog?.categories.find((value) => value.id === item.category)?.label;
  const level = { easy: 'Oson', intermediate: 'O‘rta', advanced: 'Murakkab' };
  return (
    <article className="studio-study-card" data-progress={learned.state || 'not_started'}>
      <div className="studio-card-top">
        <span className="studio-card-category">
          {number
            ? String(number).padStart(2, '0')
            : category || tr(item.kind === 'theory' ? 'Nazariya' : 'Mashq')}
          {number && category ? ` · ${category}` : ''}
        </span>
        <Favorite id={item.id} />
      </div>
      <a
        href={`/study/${encodeURIComponent(item.id)}`}
        className="studio-study-link"
        onClick={followRouteLink}
      >
        <h3>{item.title}</h3>
        <p>{item.subtitle}</p>
      </a>
      {(learned.total > 0 || learned.state) && (
        <div className="study-card-progress">
          <span>
            {learned.total
              ? tr('{0}/{1} bosqich o‘zlashtirilgan', [learned.completed, learned.total])
              : ''}
          </span>
          {learned.state && <StudyStatusBadge status={learned.state} />}
        </div>
      )}
      <div className="studio-card-bottom">
        <span>
          {item.level
            ? tr(level[item.level])
            : tr(
                item.kind === 'journey'
                  ? 'To‘liq ijroga tayyorgarlik'
                  : item.kind === 'lesson'
                    ? 'Kompozitsiya darsi'
                    : 'Amaliy nazariya',
              )}
          <span className="studio-dot">·</span>
          {item.minutes} {tr('daq.')}
        </span>
        <ArrowForwardRounded aria-hidden="true" />
      </div>
    </article>
  );
}
export function CompositionCard({
  composition,
  difficulty = 0,
}: {
  composition: Composition;
  difficulty?: number;
}) {
  const tr = useTranslation();
  const { language } = usePreferences();
  const variant = libraryVariant(composition, difficulty);
  const { catalog } = useStudio();
  const lessonCount =
    catalog?.lessons.filter((item) => studyMatchesPerformance(item, composition, variant?.id))
      .length || 0;
  const attribution = compositionAttribution(composition);
  return (
    <article className="studio-composition-card">
      <CompositionPreview composition={composition} variant={variant?.id} />
      <div className="studio-composition-content">
        <div className="studio-card-top">
          <span className="studio-card-category">{attribution.category}</span>
          <Favorite id={`composition:${composition.id}`} />
        </div>
        <h2>{composition.title}</h2>
        {attribution.composer && <p>{attribution.composer}</p>}
        <div className="composition-difficulty-row">
          <DifficultyStars value={variant?.difficulty || composition.difficulty} />
          {variant && <span className="composition-current-variant">{variant.title}</span>}
        </div>
        <div className="studio-composition-meta">
          <span>{durationLabel(variant?.duration_seconds || composition.duration_seconds)}</span>
          {!!lessonCount && <span>{studyCountLabel(lessonCount, 'lesson', language)}</span>}
          {!!composition.variants?.length && (
            <span>{composition.variants.map((variant) => variant.title).join(' / ')}</span>
          )}
        </div>
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
          <Button
            component="a"
            href={routePath('detail', { compositionSlug: composition.slug })}
            onClick={followRouteLink}
          >
            {tr(composition.lesson_ids.length ? 'Darslar' : 'Batafsil')}
          </Button>
        </div>
      </div>
    </article>
  );
}
export function ContentRow({ id }: { id: string }) {
  const { catalog } = useStudio();
  const tr = useTranslation();
  const composition = catalog?.compositions.find((value) => `composition:${value.id}` === id);
  const item = catalog && allStudyItems(catalog).find((value) => value.id === id);
  if (!composition && !item) return null;
  return (
    <div className="studio-content-row">
      <button
        onClick={() =>
          composition
            ? openComposition(composition)
            : navigate('study', { item: item!.id, composition: item!.composition_id ?? null })
        }
      >
        <span className="studio-row-icon">
          <MusicNoteRounded />
        </span>
        <span>
          <strong>{composition?.title || item?.title}</strong>
          <small>
            {composition?.subtitle ||
              tr(
                item?.kind === 'theory'
                  ? 'Nazariya'
                  : item?.kind === 'journey'
                    ? 'To‘liq ijroga tayyorgarlik'
                    : item?.kind === 'lesson'
                      ? 'Kompozitsiya darsi'
                      : 'Umumiy mashq',
              )}
          </small>
        </span>
        <ArrowForwardRounded />
      </button>
      <Favorite id={id} />
    </div>
  );
}
