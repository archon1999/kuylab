import EmptyState from '@shared/ui/EmptyState';
import { useTranslation } from '@shared/i18n';
import { useStudio } from '../../../application';
import { CompositionCard, Heading } from '../../shared/StudioParts';
import '../../studio.css';
export default function LibraryPage() {
  const { catalog } = useStudio();
  const tr = useTranslation();
  return (
    <div className="studio-page">
      <Heading title={tr('Kompozitsiyalar')} />
      {!catalog?.compositions.length && (
        <EmptyState
          kind="library"
          title={tr('Hozircha kompozitsiyalar yo‘q')}
          description={tr('Tayyor kompozitsiyalar shu yerda ko‘rinadi.')}
        />
      )}
      <div className="studio-compositions">
        {catalog?.compositions.map((composition) => (
          <CompositionCard key={composition.id} composition={composition} />
        ))}
      </div>
    </div>
  );
}
