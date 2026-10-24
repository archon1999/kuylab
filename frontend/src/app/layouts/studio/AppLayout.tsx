import { useErrorScreen } from '@shared/ui/errorScreen';
import ErrorState from '@shared/ui/ErrorState';
import { useActivity } from '@modules/activity';
import { useProfile } from '@modules/profile';
import { allStudyItems, useStudio } from '@modules/studio';
import { CloseRounded, PianoRounded } from '@mui/icons-material';
import { Button, Drawer, IconButton, useMediaQuery } from '@mui/material';
import { PageSkeleton, PlayerSkeleton } from '@shared/ui/Loading';
import { useTranslation } from '@shared/i18n';
import { useOnlineStatus } from '@shared/offline';
import { navigate, useRoute, type Page } from '@shared/routing';
import { useEffect, useRef, useState } from 'react';
import Router from '../../routes';
import AppHeader from './AppHeader';
import MenuContent from './MenuContent';
import '../../styles/studioShell.css';
export default function AppLayout() {
  const tr = useTranslation();
  const mainRef = useRef<HTMLElement>(null);
  const { page, params } = useRoute();
  const { profile } = useProfile();
  const { catalog, loading, error, reload } = useStudio();
  const { setContent } = useActivity();
  const online = useOnlineStatus();
  const [open, setOpen] = useState(false);
  const mobile = useMediaQuery('(max-width: 680px)');
  const focused = page === 'practice';
  const pageError = useErrorScreen();
  const standaloneError = page === 'notFound' || pageError;
  const itemId = params.get('item');
  const compositionId = params.get('composition');
  useEffect(() => {
    mainRef.current?.scrollTo({ top: 0 });
  }, [page, itemId, compositionId]);
  const studyItem =
    page === 'study' && catalog
      ? allStudyItems(catalog).find((item) => item.id === params.get('item'))
      : null;
  const navigationPage = studyItem
    ? ['lesson', 'journey'].includes(studyItem.kind)
      ? 'library'
      : studyItem.kind === 'exercise'
        ? 'exercises'
        : 'theory'
    : page;
  useEffect(() => {
    setOpen(false);
    if (!['practice', 'study', 'detail'].includes(page)) setContent(null);
  }, [page, mobile, setContent]);
  useEffect(() => {
    const titles: Record<Page, string> = {
      dashboard: 'Bosh sahifa',
      library: 'Kompozitsiyalar',
      detail: 'Kompozitsiyalar',
      lesson: 'Darslar',
      practice: 'Player',
      theory: 'Nazariya',
      settings: 'Sozlamalar',
      exercises: 'Mashqlar',
      study: 'Dars',
      statistics: 'Statistika',
      notFound: 'Sahifa topilmadi',
    };
    const composition =
      catalog?.compositions.find((value) => value.id === Number(compositionId)) ??
      (!compositionId ? catalog?.compositions[0] : undefined);
    const stage =
      studyItem?.stages?.find((value) => value.id === params.get('stage')) ||
      studyItem?.comparisons?.find((value) => value.id === params.get('example'));
    const detail = studyItem
      ? [studyItem.title, stage?.title].filter(Boolean).join(' · ')
      : page === 'practice' || page === 'detail'
        ? composition?.title
        : null;
    document.title = `${detail ? detail + ' — ' : ''}${tr(titles[page])} · KuyLab`;
  }, [page, tr, catalog, compositionId, studyItem, params.toString()]);
  const navigation = (
    <>
      <MenuContent
        page={navigationPage}
        onNavigate={(value) => {
          setOpen(false);
          navigate(value);
        }}
      />
      <div className="instrument-card">
        <PianoRounded />
        <div>
          <strong>{profile.instrument_model}</strong>
          <span>
            {profile.keyboard_keys} {tr('klavish')}
          </span>
        </div>
      </div>
    </>
  );
  const content =
    page === 'settings' || page === 'notFound' ? (
      <Router />
    ) : !catalog && loading ? (
      focused ? (
        <PlayerSkeleton />
      ) : (
        <PageSkeleton
          variant={
            page === 'dashboard'
              ? 'page'
              : page === 'statistics'
                ? 'statistics'
                : page === 'study'
                  ? 'study'
                  : 'library'
          }
        />
      )
    ) : !catalog ? (
      <ErrorState
        title={tr('Kontentni ochib bo‘lmadi.')}
        description={tr('Studiyaga ulanish vaqtincha uzildi. Yana bir bor urinib ko‘ring.')}
        action={{ label: tr('Qayta urinish'), onClick: () => void reload() }}
        secondary={{ label: tr('Bosh sahifa'), onClick: () => navigate('dashboard') }}
      />
    ) : (
      <Router />
    );
  return (
    <div
      className={standaloneError ? 'error-layout' : `app-shell ${focused ? 'focused-studio' : ''}`}
    >
      {!standaloneError && (
        <a className="skip-link" href="#main-content">
          {tr('Asosiy qismga o‘tish')}
        </a>
      )}
      {!focused && !standaloneError && (
        <>
          <AppHeader
            profile={profile}
            menuOpen={open}
            onMenu={() => setOpen((value) => !value)}
            onHome={() => navigate('dashboard')}
            onSettings={() => navigate('settings')}
          />
          {mobile ? (
            <Drawer
              open={open}
              onClose={() => setOpen(false)}
              sx={{ zIndex: 1300 }}
              slotProps={{
                paper: {
                  className: 'sidebar open mobile-sidebar',
                  role: 'dialog',
                  'aria-modal': true,
                  'aria-label': tr('Asosiy menyu'),
                },
              }}
            >
              <div className="mobile-sidebar-heading">
                <span>KuyLab</span>
                <IconButton aria-label={tr('Menyuni yopish')} onClick={() => setOpen(false)}>
                  <CloseRounded />
                </IconButton>
              </div>
              {navigation}
            </Drawer>
          ) : (
            <aside className="sidebar">{navigation}</aside>
          )}
        </>
      )}
      <main
        key="content"
        ref={mainRef}
        className={standaloneError ? 'error-layout-content' : 'main-content'}
        id="main-content"
        tabIndex={-1}
      >
        {!online && !focused && !standaloneError && (
          <div className="studio-offline-notice" role="status">
            {tr('Offline rejim · saqlangan kontent ochiladi')}
          </div>
        )}
        {error && catalog && !focused && !standaloneError && (
          <div className="studio-offline-notice" role="status">
            <span>{error}</span>
            <Button onClick={() => void reload()}>{tr('Qayta urinish')}</Button>
          </div>
        )}
        <div className={standaloneError ? 'error-layout-body' : 'page-body'}>{content}</div>
      </main>
    </div>
  );
}
