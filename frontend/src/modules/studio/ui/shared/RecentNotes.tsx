import { usePracticeNotes } from '@modules/activity';
import { BookmarkBorderRounded, ArrowForwardRounded } from '@mui/icons-material';
import { useTranslation } from '@shared/i18n';
import { navigate } from '@shared/routing';
import { useStudio } from '../../application';
import { allStudyItems, durationLabel } from '../../domain';
import { SectionTitle } from './StudioParts';
export default function RecentNotes() {
  const { catalog } = useStudio();
  const { notes } = usePracticeNotes();
  const tr = useTranslation();
  if (!catalog || !notes.length) return null;
  const targets = notes
    .map((note) => {
      const composition = catalog.compositions.find(
        (value) => `composition:${value.id}` === note.contentId,
      );
      const item = allStudyItems(catalog).find(
        (value) =>
          value.id === note.contentId ||
          value.stages?.some((stage) => stage.id === note.contentId) ||
          value.comparisons?.some((example) => example.id === note.contentId),
      );
      return {
        note,
        composition,
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
        {targets.map(({ note, composition, item, stage, example }) => (
          <button
            className="studio-note-link"
            key={note.id}
            onClick={() =>
              composition
                ? navigate('practice', { composition: composition.id, at: note.position })
                : navigate('study', {
                    item: item!.id,
                    stage: stage?.id || null,
                    example: example?.id || null,
                    at: note.position,
                  })
            }
          >
            <BookmarkBorderRounded />
            <span>
              <strong>
                {composition?.title || item?.title} · {durationLabel(note.position)}
              </strong>
              <small>{note.text}</small>
            </span>
            <ArrowForwardRounded />
          </button>
        ))}
      </div>
    </section>
  );
}
