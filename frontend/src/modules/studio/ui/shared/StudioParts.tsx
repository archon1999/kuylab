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
import { useTranslation } from '@shared/i18n';
import { navigate } from '@shared/routing';
import { useStudio } from '../../application';
import { durationLabel, type Composition, type StudyItem } from '../../domain';

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
  const category = catalog?.categories.find((value) => value.id === item.category)?.label;
  const level = { easy: 'Oson', intermediate: 'O‘rta', advanced: 'Murakkab' };
  return (
    <article className="studio-study-card">
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
        onClick={(event) => {
          event.preventDefault();
          navigate('study', { item: item.id, composition: item.composition_id ?? null });
        }}
      >
        <h3>{item.title}</h3>
        <p>{item.subtitle}</p>
      </a>
      <div className="studio-card-bottom">
        <span>
          {item.level
            ? tr(level[item.level])
            : tr(item.kind === 'lesson' ? 'Kompozitsiya darsi' : 'Amaliy nazariya')}
          <span className="studio-dot">·</span>
          {item.minutes} {tr('daq.')}
        </span>
        <ArrowForwardRounded aria-hidden="true" />
      </div>
    </article>
  );
}
export function CompositionCard({ composition }: { composition: Composition }) {
  const tr = useTranslation();
  return (
    <article className="studio-composition-card">
      <div className="studio-composition-art" aria-hidden="true">
        <MusicNoteRounded />
        <span>Still</span>
        <div className="studio-art-keys">
          {Array.from({ length: 14 }, (_, index) => (
            <i key={index} />
          ))}
        </div>
      </div>
      <div className="studio-composition-content">
        <div className="studio-card-top">
          <span className="studio-card-category">{composition.subtitle}</span>
          <Favorite id={`composition:${composition.id}`} />
        </div>
        <h2>{composition.title}</h2>
        <p>{composition.composer}</p>
        <div className="studio-composition-meta">
          <span>{durationLabel(composition.duration_seconds)}</span>
          <span>
            {composition.lesson_ids.length} {tr('dars')}
          </span>
        </div>
        <div className="studio-actions">
          <Button
            variant="contained"
            startIcon={<PlayArrowRounded />}
            onClick={() => openComposition(composition)}
          >
            {tr('Playerni ochish')}
          </Button>
          <Button onClick={() => navigate('detail', { composition: composition.id })}>
            {tr('Darslar')}
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
  const item =
    catalog &&
    [...catalog.lessons, ...catalog.exercises, ...catalog.theory].find((value) => value.id === id);
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
