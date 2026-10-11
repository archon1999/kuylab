import { useSessions } from '@modules/practice';
import { useProfile } from '@modules/profile';
import { hasMidiSource, useRepertoire } from '@modules/repertoire';
import {
  ArrowForwardRounded,
  PianoRounded,
  PlayArrowRounded,
  TimerOutlined,
} from '@mui/icons-material';
import { Alert, Button } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { followPractice, navigate, openPractice } from '@shared/routing';
import { Keyboard, SectionHeading } from '@shared/ui/StudyPrimitives';
import { useState } from 'react';
import { useCurriculum } from '../../../application';
import { AdaptivePlan, DiagnosticDialog } from '../../shared/Curriculum';
export default function DashboardPage() {
  const tr = useTranslation();
  const { current, compositions, mode, selectionExists } = useRepertoire();
  const { profile } = useProfile();
  const { sessions } = useSessions();
  const hasSource = hasMidiSource(current);
  const curriculum = useCurriculum(current.id, mode === 'online' && selectionExists && hasSource);
  const [diagnostic, setDiagnostic] = useState(false);
  const totalMinutes = Math.round(
    sessions.reduce((total, session) => total + session.duration_seconds, 0) / 60,
  );
  return (
    <>
      <SectionHeading
        eyebrow="MUSIQA SIZDAN BOSHLANADI"
        title="Bugungi mashq"
        action={
          <div className="daily-goal">
            <TimerOutlined sx={{ fontSize: 20 }} />
            <span>
              {tr('Kunlik maqsad')}
              <strong>
                {profile.daily_minutes} {tr('daqiqa')}
              </strong>
            </span>
          </div>
        }
      />
      <section className="hero-card">
        <div className="hero-content">
          <span className="hero-label">{tr('Hozir o‘rganayotgan asaringiz')}</span>
          <h2>{current.title}</h2>
          <p className="composer">{current.composer}</p>
          <div className="hero-actions">
            <Button
              variant="contained"
              startIcon={<PlayArrowRounded />}
              onClick={() => openPractice(current.id)}
            >
              {tr(hasSource ? 'Boshlash' : 'MIDI qo‘shish')}
            </Button>
            <Button
              color="inherit"
              endIcon={<ArrowForwardRounded />}
              onClick={() => navigate('detail', { composition: current.id })}
            >
              {tr('Darslar')}
            </Button>
          </div>
          <div className="source-note">
            <i />
            {tr(
              current.source_status === 'full_midi_ready'
                ? 'To‘liq MIDI tayyor'
                : current.source_status === 'midi_uploaded'
                  ? 'MIDI tayyor'
                  : 'MIDI kerak',
            )}
          </div>
        </div>
        <div className="hero-instrument">
          <div className="instrument-label">
            <PianoRounded />
            <span>{profile.instrument_model}</span>
          </div>
          <Keyboard compact />
          <span className="instrument-sub">
            {profile.keyboard_keys} {tr('klavish')}
          </span>
        </div>
      </section>
      <div className="dashboard-grid">
        {!hasSource ? (
          <section className="panel" style={{ padding: 24 }}>
            <p>{tr('MIDI kerak')}</p>
            <Button onClick={() => openPractice(current.id)}>{tr('MIDI qo‘shish')}</Button>
          </section>
        ) : curriculum.data ? (
          <AdaptivePlan
            data={curriculum.data}
            onLesson={(id) => navigate('lesson', { lesson: id, composition: current.id })}
            onDiagnostic={() => setDiagnostic(true)}
            onTransfer={(link) => (link ? followPractice(link) : openPractice(current.id))}
          />
        ) : curriculum.error ? (
          <Alert
            severity="warning"
            action={
              <Button onClick={() => void curriculum.refresh()}>{tr('Qayta yuklash')}</Button>
            }
          >
            {tr(curriculum.error)}
          </Alert>
        ) : (
          <p className="learning-caption" role="status">
            {tr(curriculum.loading ? 'Dars yuklanmoqda…' : 'Lokal serverga ulaning.')}
          </p>
        )}
        <aside className="dashboard-aside">
          <div className="session-summary panel">
            <span className="summary-label">{tr('Mashq daftari')}</span>
            <h3>{sessions.length ? tr('{0} ta qayd', [sessions.length]) : tr('Hali qayd yo‘q')}</h3>
            <div className="summary-number">
              {totalMinutes}
              <span>{tr('daqiqa mashq')}</span>
            </div>
            <button className="text-link" onClick={() => openPractice(current.id)}>
              {tr('Mashq xonasiga')}
              <ArrowForwardRounded sx={{ fontSize: 17 }} />
            </button>
          </div>
        </aside>
      </div>
      {sessions.length > 0 && (
        <section className="history-panel panel">
          <h3>{tr('Oxirgi mashqlar')}</h3>
          {sessions.slice(0, 3).map((session, index) => (
            <div className="history-row" key={session.id || index}>
              <span className="history-icon">
                <PianoRounded />
              </span>
              <div>
                <strong>
                  {compositions.find((item) => item.id === session.composition)?.title}
                </strong>
                <span>{session.notes || tr('Kuzatuv yozilmagan')}</span>
              </div>
              <span>
                {Math.floor(session.duration_seconds / 60)}:
                {String(session.duration_seconds % 60).padStart(2, '0')}
              </span>
            </div>
          ))}
        </section>
      )}
      {curriculum.data && curriculum.error && (
        <Alert
          severity="warning"
          action={<Button onClick={() => void curriculum.refresh()}>{tr('Qayta yuklash')}</Button>}
        >
          {tr(curriculum.error)}
        </Alert>
      )}
      <DiagnosticDialog
        compositionId={current.id}
        data={curriculum.data}
        open={diagnostic}
        onClose={() => setDiagnostic(false)}
        onSaved={curriculum.refresh}
      />
    </>
  );
}
