import { usePracticeNotes } from '@modules/activity';
import { BookmarkBorderRounded, ArrowForwardRounded } from '@mui/icons-material';
import { useTranslation } from '@shared/i18n';
import { followRouteLink, routePath } from '@shared/routing';
import { useStudio } from '../../application';
import { allStudyItems, compositionNoteTarget, durationLabel } from '../../domain';
import { SectionTitle } from './StudioParts';
export default function RecentNotes() {
  const { catalog } = useStudio();
  const { notes } = usePracticeNotes();
  const tr = useTranslation();
  if (!catalog || !notes.length) return null;
  const targets = notes
    .map((note) => {
      const performance = compositionNoteTarget(catalog.compositions, note.contentId);
      const item = allStudyItems(catalog).find(
        (value) =>
          value.id === note.contentId ||
          value.stages?.some((stage) => stage.id === note.contentId) ||
          value.comparisons?.some((example) => example.id === note.contentId),
      );
      return {
        note,
        composition: performance?.composition,
        performance,
        item,
        stage: item?.stages?.find((value) => value.id === note.contentId),
        example: item?.comparisons?.find((value) => value.id === note.contentId),
      };
    })
    .filter((target) => target.composition || target.item)
    .slice(0, 3);
  if (!targets.length) return null;
  return (
    <section>
      <SectionTitle title={tr('Oxirgi qaydlar')} />
      <div className="studio-list-surface">
        {targets.map(({ note, composition, performance, item, stage, example }) => (
          <a
            className="studio-note-link"
            key={note.id}
            href={
              composition
                ? performance?.currentSource
                  ? routePath('practice', {
                      composition: composition.id,
                      variant: performance.variant?.id || null,
                      at: note.position,
                    })
                  : routePath('detail', { compositionSlug: composition.slug })
                : routePath('study', {
                    item: item!.id,
                    stage: stage?.id || null,
                    example: example?.id || null,
                    at: note.position,
                  })
            }
            onClick={followRouteLink}
          >
            <BookmarkBorderRounded />
            <span>
              <strong>
                {composition?.title || item?.title}
                {performance?.variant && ` · ${performance.variant.title}`}
                {performance && !performance.currentSource && ` · ${tr('Oldingi ijro')}`} ·{' '}
                {durationLabel(note.position)}
              </strong>
              <small>{note.text}</small>
            </span>
            <ArrowForwardRounded />
          </a>
        ))}
      </div>
    </section>
  );
}
