import type { Composition } from '@modules/repertoire';
import {
  ArrowBackRounded,
  ArrowForwardRounded,
  CheckRounded,
  PianoRounded,
} from '@mui/icons-material';
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  Radio,
  RadioGroup,
  Slider,
  TextField,
} from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { useDiagnosticController, useLessonController } from '../../application/lessonControllers';
import type { Curriculum, Lesson, Question, QuizResult } from '../../domain';
export function AdaptivePlan({
  data,
  onLesson,
  onDiagnostic,
  onTransfer,
}: {
  data: Curriculum;
  onLesson: (id: number) => void;
  onDiagnostic: () => void;
  onTransfer: (link?: string) => void;
}) {
  const tr = useTranslation();
  return (
    <section className="learning-plan panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">{tr('SIZNING O‘QUV YO‘LINGIZ')}</span>
          <h3>
            {tr('Bugungi ')}
            {data.adaptive_plan.minutes} {tr(' daqiqa')}
          </h3>
        </div>
        <Button size="small" color="inherit" onClick={onDiagnostic}>
          {data.diagnostic.latest_attempt ? tr('Qayta tekshirish') : tr('Darajamni tekshirish')}
        </Button>
      </div>
      <div className="adaptive-list">
        {data.adaptive_plan.items.map((item, i) => {
          const content = (
            <>
              <span className="learning-index">{String(i + 1).padStart(2, '0')}</span>
              <span>
                <strong>{tr(item.title)}</strong>
                <small title={tr(item.reason)}>
                  {item.kind === 'transfer'
                    ? tr('Bugungi tushunchani tanlangan ijroda sinab ko‘ring.')
                    : item.reason}
                </small>
              </span>
              <span className="learning-time">
                {item.minutes} {tr(' daq')}
              </span>
              {(item.lesson_id || (item.kind === 'transfer' && item.practice_link)) && (
                <ArrowForwardRounded sx={{ fontSize: 17 }} />
              )}
            </>
          );
          return item.lesson_id || (item.kind === 'transfer' && item.practice_link) ? (
            <button
              key={`${item.lesson_id}-${i}`}
              onClick={() =>
                item.kind === 'transfer'
                  ? onTransfer(item.practice_link)
                  : onLesson(item.lesson_id!)
              }
            >
              {content}
            </button>
          ) : (
            <div className="adaptive-static" key={`${item.kind}-${i}`}>
              {content}
            </div>
          );
        })}
      </div>
      <p className="learning-caption">
        {data.adaptive_plan.basis === 'source_pending'
          ? tr('Avval siz yoqtirgan aniq variantni tanlaymiz.')
          : tr('Javoblaringiz va oxirgi mashq qaydlaringiz asosidagi reja.')}
      </p>
    </section>
  );
}

export function CurriculumOverview({
  data,
  onLesson,
  onDiagnostic,
  onTransfer,
}: {
  data: Curriculum;
  onLesson: (id: number) => void;
  onDiagnostic: () => void;
  onTransfer: (link?: string) => void;
}) {
  const tr = useTranslation();
  return (
    <div className="curriculum-overview">
      <AdaptivePlan
        data={data}
        onLesson={onLesson}
        onDiagnostic={onDiagnostic}
        onTransfer={onTransfer}
      />
      <div className="skill-strip">
        {data.skills.map((skill) => (
          <div key={skill.id}>
            <span>{tr(skill.label)}</span>
            <strong>{skill.score === null ? '—' : `${Math.round(skill.score)}%`}</strong>
            <small>
              {skill.evidence === 'not_assessed'
                ? tr('Hali tekshirilmagan')
                : skill.knowledge_score !== null && skill.self_reported_score !== null
                  ? tr('Javob va shaxsiy kuzatuv')
                  : skill.knowledge_score !== null
                    ? tr('Nazariy javoblar')
                    : tr('Shaxsiy kuzatuv')}
            </small>
          </div>
        ))}
      </div>
      <div className="panel-heading detail-plan-heading">
        <h3>{tr('Asar bilan bog‘liq darslar')}</h3>
        <span className="muted">
          {data.lessons.length} {tr(' dars')}
        </span>
      </div>
      <div className="curriculum-lessons">
        {data.lessons.map((lesson, index) => (
          <button
            className="curriculum-lesson panel"
            key={lesson.id}
            onClick={() => onLesson(lesson.id)}
          >
            <span className="learning-index">
              {lesson.progress.quiz_passed && lesson.progress.drill_completed ? (
                <CheckRounded sx={{ fontSize: 18 }} />
              ) : (
                String(index + 1).padStart(2, '0')
              )}
            </span>
            <span>
              <small>
                {lesson.minutes} {tr(' daqiqa')}
              </small>
              <strong>{tr(lesson.title)}</strong>
              <span>{tr(lesson.summary)}</span>
            </span>
            <ArrowForwardRounded sx={{ fontSize: 18 }} />
          </button>
        ))}
      </div>
    </div>
  );
}

function Questions({
  questions,
  answers,
  onAnswer,
  disabled = false,
  feedback,
}: {
  questions: Question[];
  answers: Record<string, string>;
  onAnswer: (id: string, answer: string) => void;
  disabled?: boolean;
  feedback?: QuizResult['feedback'];
}) {
  const tr = useTranslation();
  return (
    <div className="lesson-questions">
      {questions.map((question, i) => {
        const result = feedback?.find((item) => item.id === question.id);
        return (
          <div className="lesson-question" key={question.id}>
            <h4 id={`question-${question.id}`}>
              {i + 1}. {question.prompt || question.title}
            </h4>
            {question.kind === 'self_report' && (
              <p className="learning-caption">
                {tr('Shaxsiy kuzatuv — pianino ijrosi avtomatik tekshirilmaydi.')}
              </p>
            )}
            <RadioGroup
              aria-labelledby={`question-${question.id}`}
              value={answers[question.id] || ''}
              onChange={(event) => onAnswer(question.id, event.target.value)}
            >
              {question.choices.map((choice) => (
                <FormControlLabel
                  key={choice.id}
                  value={choice.id}
                  disabled={disabled}
                  control={<Radio size="small" />}
                  label={tr(choice.label)}
                />
              ))}
            </RadioGroup>
            {result && (
              <div
                className={`quiz-feedback ${result.correct ? 'correct' : 'incorrect'}`}
                role="status"
              >
                <strong>{result.correct ? tr('To‘g‘ri') : tr('Yana bir ko‘rib chiqing')}</strong>
                <p>{tr(result.explanation)}</p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export function DiagnosticDialog({
  compositionId,
  data,
  open,
  onClose,
  onSaved,
}: {
  compositionId: number;
  data: Curriculum | null;
  open: boolean;
  onClose: () => void;
  onSaved: () => Promise<void>;
}) {
  const tr = useTranslation();
  const { answers, setAnswers, saving, error, questions, save } = useDiagnosticController(
    compositionId,
    data,
    open,
    onClose,
    onSaved,
  );
  return (
    <Dialog open={open} onClose={() => !saving && onClose()} maxWidth="sm" fullWidth>
      <DialogTitle>{tr('Qayerdan boshlaymiz?')}</DialogTitle>
      <DialogContent>
        <p className="dialog-intro">
          {tr(
            'Bilimingiz va qo‘lingizning tayyorgarligini alohida ko‘ramiz. Javoblar bugungi dars tartibini o‘zgartiradi.',
          )}
        </p>
        <Questions
          questions={questions}
          answers={answers}
          onAnswer={(id, answer) => setAnswers((value) => ({ ...value, [id]: answer }))}
          disabled={saving}
        />
        {error && <Alert severity="error">{tr(error)}</Alert>}
      </DialogContent>
      <DialogActions>
        <Button color="inherit" disabled={saving} onClick={onClose}>
          {tr('Qaytish')}
        </Button>
        <Button
          variant="contained"
          disabled={
            saving || !questions.length || questions.some((question) => !answers[question.id])
          }
          onClick={() => void save()}
        >
          {tr(saving ? 'Saqlanmoqda…' : 'Rejani moslashtirish')}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export function LessonPage({
  lesson,
  composition,
  onBack,
  onPractice,
  onSaved,
  onTransfer,
}: {
  lesson: Lesson;
  composition: Composition;
  onBack: () => void;
  onPractice: () => void;
  onSaved: () => Promise<void>;
  onTransfer: (link?: string) => void;
}) {
  const tr = useTranslation();
  const {
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
  } = useLessonController(lesson, onSaved);
  return (
    <>
      <Button
        className="back-link"
        color="inherit"
        startIcon={<ArrowBackRounded />}
        onClick={onBack}
      >
        {tr('Asar rejasiga qaytish')}
      </Button>
      <div className="section-heading">
        <div>
          <div className="eyebrow">
            {tr(composition.title)} · {lesson.minutes} {tr(' DAQIQA')}
          </div>
          <h1>{tr(lesson.title)}</h1>
          <p>{tr(lesson.summary)}</p>
        </div>
      </div>
      <div className="lesson-layout">
        <article className="lesson-reading panel">
          <details className="lesson-source">
            <summary>{tr('Dars manbasi')}</summary>
            <p className="lesson-context">{tr(lesson.context)}</p>
            {!!lesson.sources?.length && (
              <div className="lesson-source-links">
                {lesson.sources.map((source) => (
                  <a key={source.url} href={source.url} target="_blank" rel="noopener noreferrer">
                    {tr(source.title)}
                  </a>
                ))}
              </div>
            )}
          </details>
          {lesson.explanation.map((item, i) => (
            <section key={i}>
              <h2>{tr(item.title)}</h2>
              <p>{tr(item.text)}</p>
            </section>
          ))}
          {lesson.quiz.questions.length > 0 && (
            <section className="lesson-check">
              <div className="eyebrow">{tr('TUSHUNGANINGIZNI TEKSHIRING')}</div>
              <Questions
                questions={lesson.quiz.questions}
                answers={answers}
                onAnswer={(id, answer) => {
                  setAnswers((value) => ({ ...value, [id]: answer }));
                  setResult(null);
                }}
                disabled={busy}
                feedback={result?.feedback}
              />
              {result && (
                <p className="quiz-score" role="status">
                  {result.score}% ·{' '}
                  {result.passed
                    ? tr('Nazariy qism o‘zlashtirildi')
                    : tr('Izohlarni o‘qib, yana javob bering')}
                </p>
              )}
              <Button
                variant="contained"
                disabled={busy || lesson.quiz.questions.some((q) => !answers[q.id])}
                onClick={() => void submitQuiz()}
              >
                {busy
                  ? 'Tekshirilmoqda…'
                  : result
                    ? tr('Yana tekshirish')
                    : tr('Javoblarni tekshirish')}
              </Button>
            </section>
          )}
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {tr(error)}
            </Alert>
          )}
        </article>
        <aside className="lesson-drill panel">
          <span className="eyebrow">{tr('PIANINO OLDIDA')}</span>
          <h2>{lesson.exercise?.label || tr('Kichik amaliy qadam')}</h2>
          {lesson.exercise?.original && (
            <p className="learning-caption">
              {tr('Original tayyorgarlik mashqi. Asar notalari ko‘chirilmagan.')}
            </p>
          )}
          {lesson.exercise?.notes && (
            <div className="drill-notes">
              {Array.isArray(lesson.exercise.notes)
                ? lesson.exercise.notes.join(' · ')
                : lesson.exercise.notes}
            </div>
          )}
          {lesson.exercise?.counting && (
            <p className="drill-counting">
              {Array.isArray(lesson.exercise.counting)
                ? lesson.exercise.counting.join(' · ')
                : lesson.exercise.counting}
            </p>
          )}
          <ol>
            {lesson.steps.map((step, i) => (
              <li key={i}>
                <strong>{tr(step.title)}</strong>
                <p>{step.instruction}</p>
              </li>
            ))}
          </ol>
          <p className="drill-criterion">{tr(lesson.success_criterion)}</p>
          {(lesson.exercise?.score_url ||
            (lesson.exercise?.original === false && lesson.practice_link)) && (
            <Button variant="outlined" startIcon={<PianoRounded />} onClick={onPractice}>
              {lesson.exercise?.original === false
                ? tr('Asar parchasini mashq qilish')
                : tr('Dars mashqini chalish')}
            </Button>
          )}
          <div className="lesson-transfer">
            <h3>{tr('Asarga qayting')}</h3>
            <p>{lesson.transfer || tr('Tushunchani tanlangan ijroda kuzating.')}</p>
            <Button
              size="small"
              endIcon={<ArrowForwardRounded />}
              onClick={() => onTransfer(lesson.practice_link)}
            >
              {lesson.practice_link ? tr('Tanlangan parchaga') : tr('Ijro va nota manbasiga')}
            </Button>
          </div>
          <div className="practice-report">
            <h3>{tr('Qanday o‘tdi?')}</h3>
            <TextField
              size="small"
              type="number"
              label={tr('Qaysi tempda chaldingiz? · {0} BPM', [tr(reportUnitLabel)])}
              disabled={busy}
              value={reportBpm}
              onChange={(event) => {
                setReportBpm(event.target.value);
                setSaved(false);
              }}
              slotProps={{ htmlInput: { min: 20, max: 240, step: 1 } }}
              error={!reportBpmValid}
              helperText={tr('Dars tavsiyasi bilan boshlandi. Amalda chalgan tempingizni yozing.')}
              sx={{ mb: 2 }}
            />
            <span className="control-label">
              {tr('BARQAROR TAKROR · ')}
              {repetitions}/3
            </span>
            <Slider
              disabled={busy}
              min={0}
              max={3}
              step={1}
              marks
              value={repetitions}
              onChange={(_, value) => {
                setRepetitions(value as number);
                setSaved(false);
              }}
              aria-label={tr('Barqaror takrorlar soni')}
            />
            <span className="control-label">
              {tr('QULAYLIK · ')}
              {comfort}/5
            </span>
            <Slider
              disabled={busy}
              min={1}
              max={5}
              step={1}
              marks
              value={comfort}
              onChange={(_, value) => {
                setComfort(value as number);
                setSaved(false);
              }}
              aria-label={tr('Mashqdagi qulaylik')}
            />
            <TextField
              label={tr('Bitta kuzatuv (ixtiyoriy)')}
              disabled={busy}
              slotProps={{ htmlInput: { maxLength: 2000 } }}
              size="small"
              multiline
              minRows={2}
              value={reflection}
              onChange={(e) => {
                setReflection(e.target.value);
                setSaved(false);
              }}
            />
            <p className="learning-caption">
              {tr('Siz qayd etgan natija. Temp va takrorlash tavsiyasiga ta’sir qiladi.')}
            </p>
            <Button
              variant="contained"
              disabled={busy || !reportBpmValid}
              onClick={() => void submitPractice()}
            >
              {saved ? tr('Natija saqlandi') : tr('Mashq natijasini saqlash')}
            </Button>
            {saved && (
              <p className="learning-caption" role="status">
                {tr('Keyingi mashq rejasi yangilandi.')}
              </p>
            )}
          </div>
        </aside>
      </div>
    </>
  );
}
