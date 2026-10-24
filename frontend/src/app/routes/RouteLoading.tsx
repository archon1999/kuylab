import { PageSkeleton, PlayerSkeleton } from '@shared/ui/Loading';
import type { Page } from '@shared/routing';

export default function RouteLoading({ page }: { page: Page }) {
  if (page === 'practice') return <PlayerSkeleton />;
  return (
    <PageSkeleton
      variant={
        page === 'settings'
          ? 'settings'
          : page === 'statistics'
            ? 'statistics'
            : page === 'study' || page === 'lesson'
              ? 'study'
              : page === 'library'
                ? 'library'
                : page === 'detail'
                  ? 'detail'
                  : page === 'theory' || page === 'exercises'
                    ? 'collection'
                    : 'page'
      }
    />
  );
}
