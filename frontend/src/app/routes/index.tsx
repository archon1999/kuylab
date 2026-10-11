import ErrorState from '@shared/ui/ErrorState';
import { PageSkeleton, PlayerSkeleton } from '@shared/ui/Loading';
import { useTranslation } from '@shared/i18n';
import { navigate, useRoute } from '@shared/routing';
import { lazy, Suspense } from 'react';
import RouteBoundary from './RouteBoundary';
const pages = {
  dashboard: lazy(() => import('@modules/studio/ui/pages/DashboardPage')),
  library: lazy(() => import('@modules/studio/ui/pages/LibraryPage')),
  detail: lazy(() => import('@modules/studio/ui/pages/DetailPage')),
  lesson: lazy(() => import('@modules/studio/ui/pages/StudyPage')),
  study: lazy(() => import('@modules/studio/ui/pages/StudyPage')),
  practice: lazy(() => import('@modules/studio/ui/pages/PlayerPage')),
  theory: lazy(() => import('@modules/studio/ui/pages/StudyLibraryPage')),
  exercises: lazy(() => import('@modules/studio/ui/pages/StudyLibraryPage')),
  statistics: lazy(() => import('@modules/studio/ui/pages/StatisticsPage')),
  settings: lazy(() => import('@modules/profile/ui/pages/SettingsPage')),
};
export default function Router() {
  const { page, params } = useRoute();
  const tr = useTranslation();
  if (page === 'notFound')
    return (
      <ErrorState
        code="404"
        title={tr('Sahifa topilmadi')}
        description={tr('Bu manzil o‘zgargan yoki mavjud emas.')}
        action={{ label: tr('Bosh sahifa'), onClick: () => navigate('dashboard') }}
      />
    );
  const Page = pages[page];
  return (
    <RouteBoundary
      key={params.toString()}
      fallback={
        <ErrorState
          title={tr('Sahifani ochib bo‘lmadi')}
          description={tr('Sahifani yangilab, qayta urinib ko‘ring.')}
          action={{ label: tr('Qayta urinish'), onClick: () => location.reload() }}
          secondary={{ label: tr('Bosh sahifa'), onClick: () => navigate('dashboard') }}
        />
      }
    >
      <Suspense
        fallback={
          page === 'practice' ? (
            <PlayerSkeleton />
          ) : (
            <PageSkeleton
              variant={
                page === 'settings'
                  ? 'settings'
                  : page === 'study' || page === 'lesson'
                    ? 'study'
                    : page === 'dashboard'
                      ? 'page'
                      : 'library'
              }
            />
          )
        }
      >
        <Page />
      </Suspense>
    </RouteBoundary>
  );
}
