import { hasMidiSource } from '../../../domain';
import { CurriculumOverview, DiagnosticDialog, useCurriculum } from '@modules/learning';
import {
  ArrowBackRounded,
  ArrowForwardRounded,
  PianoRounded,
  PlayArrowRounded,
} from '@mui/icons-material';
import { Alert, Button } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { followPractice, navigate, openPractice } from '@shared/routing';
import { SectionHeading } from '@shared/ui/StudyPrimitives';
import { useState } from 'react';
import { useRepertoire } from '../../../application';
import ReferenceVideo from '../../shared/ReferenceVideo';
export default function DetailPage() {
  const tr = useTranslation();
  const { current, mode, selectionExists } = useRepertoire();
  const hasSource = hasMidiSource(current);
  const curriculum = useCurriculum(current.id, mode === 'online' && selectionExists && hasSource);
  const [diagnostic, setDiagnostic] = useState(false);
  return (
    <>
      <Button
        className="back-link"
        color="inherit"
        startIcon={<ArrowBackRounded />}
        onClick={() => navigate('library')}
      >
        {tr('Kompozitsiyalarga qaytish')}
      </Button>
      <SectionHeading
        title={current.title}
        description={current.composer}
        action={
          <Button
            variant="contained"
            startIcon={<PlayArrowRounded />}
            onClick={() => openPractice(current.id)}
          >
            {tr(hasSource ? 'Boshlash' : 'MIDI qo‘shish')}
          </Button>
        }
      />
      <section className="source-panel panel">
        <div className="source-panel-icon">
          <PianoRounded />
        </div>
        <div>
          <span className="eyebrow">{tr('ANIQ ARANJIROVKA')}</span>
          <h3>{current.arrangement_label || tr('Variant hali tanlanmagan')}</h3>
          <p>
            {!hasSource
              ? tr('MIDI kerak')
              : curriculum.data?.score_binding
                ? tr('Darslar shu MIDI’dagi aniq parchalardan olingan.')
                : curriculum.loading
                  ? tr('Dars yuklanmoqda…')
                  : curriculum.data?.source_notice}
          </p>
          {current.source_url && (
            <a
              className="text-link"
              href={current.source_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              {tr('Manbani ochish')}
              <ArrowForwardRounded sx={{ fontSize: 15 }} />
            </a>
          )}
        </div>
      </section>
      <ReferenceVideo arrangement={current.arrangement} />
      {hasSource && curriculum.data && (
        <CurriculumOverview
          data={curriculum.data}
          onLesson={(id) => navigate('lesson', { composition: current.id, lesson: id })}
          onDiagnostic={() => setDiagnostic(true)}
          onTransfer={(link) => (link ? followPractice(link) : openPractice(current.id))}
        />
      )}
      <DiagnosticDialog
        compositionId={current.id}
        data={curriculum.data}
        open={diagnostic}
        onClose={() => setDiagnostic(false)}
        onSaved={curriculum.refresh}
      />
      {curriculum.loading && !curriculum.data && <p role="status">{tr('Dars yuklanmoqda…')}</p>}
      {curriculum.error && (
        <Alert
          severity="warning"
          action={<Button onClick={() => void curriculum.refresh()}>{tr('Qayta yuklash')}</Button>}
        >
          {tr(curriculum.error)}
        </Alert>
      )}
    </>
  );
}
