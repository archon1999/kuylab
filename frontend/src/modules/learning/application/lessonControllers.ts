import { useEffect, useRef, useState } from 'react';
import type { Curriculum, Lesson, QuizResult } from '../domain';
import { useLearningRepository } from './learning-provider';
export function useDiagnosticController(
  compositionId: number,
  data: Curriculum | null,
  open: boolean,
  onClose: () => void,
  onSaved: () => Promise<void>,
) {
  const repository = useLearningRepository();
  const pending = useRef(false);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    if (open) {
      setAnswers({});
      setError('');
    }
  }, [open, compositionId]);
  const questions = data?.diagnostic.questions || [];
  async function save() {
    if (pending.current) return;
    pending.current = true;
    setSaving(true);
    setError('');
    try {
      await repository.diagnostic(compositionId, answers);
      await onSaved();
      onClose();
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Javoblar saqlanmadi. Barcha savollarni javoblab, yana urinib ko‘ring.',
      );
    } finally {
      pending.current = false;
      setSaving(false);
    }
  }
  return { answers, setAnswers, saving, error, questions, save };
}
export function useLessonController(lesson: Lesson, onSaved: () => Promise<void>) {
  const repository = useLearningRepository();
  const pending = useRef(false);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [repetitions, setRepetitions] = useState(lesson.progress.successful_repetitions || 0);
  const [comfort, setComfort] = useState(lesson.progress.comfort || 3);
  const [reflection, setReflection] = useState('');
  const [saved, setSaved] = useState(false);
  const [reportBpm, setReportBpm] = useState(
    String(lesson.exercise?.bpm || lesson.exercise?.tempo_choice?.bpm || 60),
  );
  const reportUnit =
    lesson.exercise?.beat_unit || lesson.exercise?.tempo_choice?.beat_unit || 'quarter';
  const reportUnitLabel =
    (
      {
        quarter: 'chorak',
        dotted_quarter: 'nuqtali chorak',
        half: 'yarim',
        eighth: 'sakkizlik',
        whole: 'butun',
      } as Record<string, string>
    )[reportUnit] || reportUnit;
  const reportBpmValid =
    Number.isInteger(Number(reportBpm)) && Number(reportBpm) >= 20 && Number(reportBpm) <= 240;
  useEffect(() => {
    setAnswers({});
    setResult(null);
    setError('');
    setRepetitions(lesson.progress.successful_repetitions || 0);
    setComfort(lesson.progress.comfort || 3);
    setReflection('');
    setSaved(false);
    setReportBpm(String(lesson.exercise?.bpm || lesson.exercise?.tempo_choice?.bpm || 60));
  }, [lesson.id]);
  async function submitQuiz() {
    if (pending.current) return;
    pending.current = true;
    setBusy(true);
    setError('');
    try {
      setResult(await repository.quiz(lesson.id, answers));
      await onSaved();
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Javoblarni tekshirib bo‘lmadi. Yana urinib ko‘ring.',
      );
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }
  async function submitPractice() {
    if (pending.current || !reportBpmValid) return;
    pending.current = true;
    setBusy(true);
    setError('');
    try {
      await repository.practice(lesson.id, {
        successful_repetitions: repetitions,
        comfort,
        bpm: Number(reportBpm),
        reflection,
      });
      await onSaved();
      setSaved(true);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : 'Mashq natijasi saqlanmadi. Yana urinib ko‘ring.',
      );
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }
  return {
    answers,
    setAnswers,
    result,
    setResult,
    busy,
    error,
    repetitions,
    setRepetitions,
    comfort,
    setComfort,
    reflection,
    setReflection,
    saved,
    setSaved,
    reportBpm,
    setReportBpm,
    reportUnitLabel,
    reportBpmValid,
    submitQuiz,
    submitPractice,
  };
}
