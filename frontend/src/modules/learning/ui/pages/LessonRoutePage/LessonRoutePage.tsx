import { ScoreWorkspace, validateRequestedTempo } from '@modules/practice';
import { hasMidiSource, useRepertoire } from '@modules/repertoire';
import { Alert, Button } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { followPractice, navigate, openPractice, useRoute } from '@shared/routing';
import { SectionHeading } from '@shared/ui/StudyPrimitives';
import { useEffect, useMemo, useState } from 'react';
import { useCurriculum } from '../../../application';
import { LessonPage } from '../../shared/Curriculum';
const noop = () => {};
const asyncNoop = async () => {};
export default function LessonRoutePage() {
  const tr = useTranslation();
  const { current, mode, selectionExists } = useRepertoire();
  const { lessonId } = useRoute();
  const curriculum = useCurriculum(
    current.id,
    mode === 'online' && selectionExists && hasMidiSource(current),
  );
  const [fragmentLessonId, setFragmentLessonId] = useState<number | null>(null);
  const fragment = fragmentLessonId === lessonId;
  useEffect(() => {
    if (fragment)
      requestAnimationFrame(() =>
        document
          .querySelector('.lesson-fragment')
          ?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
      );
  }, [fragment]);
  const lesson = curriculum.data?.lessons.find((value) => value.id === lessonId);
  const lessonTempo = useMemo(
    () =>
      validateRequestedTempo(
        lesson?.exercise?.bpm || lesson?.exercise?.tempo_choice?.bpm,
        lesson?.exercise?.beat_unit || lesson?.exercise?.tempo_choice?.beat_unit,
      ),
    [lesson?.id, lesson?.exercise?.bpm],
  );
  if (!lesson)
    return (
      <>
        <SectionHeading title="Dars" />
        {curriculum.error ? (
          <Alert
            severity="warning"
            action={
              <Button onClick={() => void curriculum.refresh()}>{tr('Qayta yuklash')}</Button>
            }
          >
            {tr(curriculum.error)}
          </Alert>
        ) : (
          <p>
            {tr(
              curriculum.loading
                ? 'Dars yuklanmoqda…'
                : 'Dars topilmadi. Asar rejasidan darsni tanlang.',
            )}
          </p>
        )}
        <Button onClick={() => navigate('detail')}>{tr('Asar rejasiga')}</Button>
      </>
    );
  return (
    <>
      <LessonPage
        key={lesson.id}
        lesson={lesson}
        composition={current}
        onBack={() => navigate('detail')}
        onPractice={() => setFragmentLessonId((value) => (value === lesson.id ? null : lesson.id))}
        onSaved={curriculum.refresh}
        onTransfer={(link) => (link ? followPractice(link) : openPractice(current.id))}
      />
      {curriculum.error && (
        <Alert
          severity="warning"
          action={<Button onClick={() => void curriculum.refresh()}>{tr('Qayta yuklash')}</Button>}
        >
          {tr(curriculum.error)}
        </Alert>
      )}
      {fragment && (
        <section className="lesson-fragment">
          <ScoreWorkspace
            composition={current}
            online={mode === 'online'}
            lessonId={lesson.id}
            requestedTempo={lessonTempo}
            onScoreChange={asyncNoop}
            onSettingsChange={noop}
            onPresence={noop}
          />
        </section>
      )}
    </>
  );
}
