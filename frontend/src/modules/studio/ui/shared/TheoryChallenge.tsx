import { useEffect, useRef, useState } from 'react';
import { usePianoAudition } from '@modules/practice';
import { useActivity, challengeResultKey, challengeSummary } from '@modules/activity';
import { Alert, Button, Chip, ToggleButton, ToggleButtonGroup } from '@mui/material';
import {
  HearingRounded,
  MenuBookRounded,
  PlayArrowRounded,
  StopRounded,
  CheckCircleOutlineRounded,
  ErrorOutlineRounded,
} from '@mui/icons-material';
import { useTranslation } from '@shared/i18n';
import { checkChallenge, type TheoryChallenge as Challenge } from '../../domain/theoryChallenges';
const keyName = (pitch: number) =>
  ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B'][pitch % 12] +
  (Math.floor(pitch / 12) - 1);
export default function TheoryChallenge({
  studyId,
  challenges,
}: {
  studyId: string;
  challenges: Challenge[];
}) {
  const tr = useTranslation();
  const { challengeResults, recordChallengeResult } = useActivity();
  const questionIds = challenges.map((question) => question.id);
  const summary = challengeSummary(studyId, questionIds, challengeResults);
  const [index, setIndex] = useState(() =>
    Math.max(
      0,
      challenges.findIndex(
        (question) => challengeResults[challengeResultKey(studyId, question.id)] !== 'correct',
      ),
    ),
  );
  const [pitches, setPitches] = useState<number[]>([]);
  const [choice, setChoice] = useState<string | null>(null);
  const [checked, setChecked] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const piano = usePianoAudition();
  const question = challenges[index] || challenges[0];
  const section = useRef<HTMLElement>(null);
  const previousQuestion = useRef(question.id);
  useEffect(() => {
    piano.stop();
    setPitches([]);
    setChoice(null);
    setChecked(false);
    setRevealed(false);
    if (previousQuestion.current !== question.id) {
      section.current?.scrollIntoView({
        block: 'start',
        behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches
          ? 'instant'
          : 'smooth',
      });
      previousQuestion.current = question.id;
    }
  }, [question.id, piano.stop]);
  const correct = checkChallenge(question, pitches, choice);
  const highest = Math.max(72, ...(question.answerPitches || []));
  const lastKey = 60 + Math.ceil((highest - 60) / 12) * 12;
  const keys = Array.from({ length: lastKey - 59 }, (_, i) => 60 + i);
  const white = keys.filter((pitch) => ![1, 3, 6, 8, 10].includes(pitch % 12));
  const press = (pitch: number) => {
    setPitches((value) =>
      value.includes(pitch) ? value.filter((note) => note !== pitch) : [...value, pitch],
    );
    setChecked(false);
    setRevealed(false);
    void piano.play([{ pitch, onset: 0, duration: 0.65, velocity: 78 }]);
  };
  return (
    <section ref={section} className="theory-challenge" aria-label={tr('O‘zingiz sinab ko‘ring')}>
      <div className="theory-challenge-heading">
        <HearingRounded />
        <h2>{tr('O‘zingiz sinab ko‘ring')}</h2>
        <span>
          {index + 1}/{challenges.length}
        </span>
      </div>
      <div className="challenge-progress-row">
        <ToggleButtonGroup
          className="challenge-navigation"
          exclusive
          value={index}
          onChange={(_, value: number | null) => value !== null && setIndex(value)}
          aria-label={tr('Topshiriqni tanlash')}
        >
          {challenges.map((task, number) => {
            const result = challengeResults[challengeResultKey(studyId, task.id)];
            return (
              <ToggleButton
                key={task.id}
                value={number}
                data-result={result || 'new'}
                aria-label={tr('{0}-topshiriq: {1}', [
                  number + 1,
                  tr(
                    result === 'correct'
                      ? 'Bajarildi'
                      : result === 'incorrect'
                        ? 'Qayta urinish'
                        : 'Boshlanmagan',
                  ),
                ])}
              >
                {number + 1}
                {result === 'correct' && <CheckCircleOutlineRounded fontSize="small" />}
                {result === 'incorrect' && <ErrorOutlineRounded fontSize="small" />}
              </ToggleButton>
            );
          })}
        </ToggleButtonGroup>
        <small aria-live="polite">
          {tr('{0}/{1} topshiriq bajarildi', [summary.correct, summary.total])}
        </small>
        {question.difficulty === 'deeper' && (
          <Chip size="small" label={tr('Chuqurroq topshiriq')} />
        )}
      </div>
      {question.preparation && (
        <aside className="challenge-preparation" aria-label={tr('Avval bilib oling')}>
          <MenuBookRounded aria-hidden="true" />
          <div>
            <h3>{tr('Avval bilib oling')}</h3>
            <p>{question.preparation}</p>
            <Button component="a" href="#study-explanation" size="small">
              {tr('Batafsil nazariya')}
            </Button>
          </div>
        </aside>
      )}
      <p className="theory-challenge-prompt">{question.prompt}</p>
      {question.audio.length > 0 && (
        <Button
          variant="outlined"
          startIcon={piano.busy ? <StopRounded /> : <PlayArrowRounded />}
          onClick={() => (piano.busy ? piano.stop() : void piano.play(question.audio))}
        >
          {tr(piano.busy ? 'To‘xtatish' : 'Namunani tinglash')}
        </Button>
      )}
      {piano.error && (
        <Alert severity="error">{tr('Ovozni yuklab bo‘lmadi. Qayta urinib ko‘ring.')}</Alert>
      )}
      {question.mode === 'keyboard' ? (
        <>
          <p className="theory-challenge-hint">
            {tr('Klavishlarni tanlang, keyin javobni tekshiring.')}
          </p>
          <div
            className="challenge-keyboard"
            role="group"
            aria-label={tr('Pianino klavishlari')}
            style={{ maxWidth: white.length * 46 }}
          >
            <div className="challenge-white-keys">
              {white.map((pitch) => (
                <button
                  key={pitch}
                  className={pitches.includes(pitch) ? 'is-selected' : ''}
                  aria-label={keyName(pitch)}
                  aria-pressed={pitches.includes(pitch)}
                  onClick={() => press(pitch)}
                >
                  <span>{keyName(pitch)}</span>
                </button>
              ))}
            </div>
            {keys
              .filter((pitch) => [1, 3, 6, 8, 10].includes(pitch % 12))
              .map((pitch) => (
                <button
                  key={pitch}
                  className={`challenge-black-key ${pitches.includes(pitch) ? 'is-selected' : ''}`}
                  style={{
                    left: `${(white.filter((note) => note < pitch).length / white.length) * 100}%`,
                    width: `${65 / white.length}%`,
                  }}
                  aria-label={keyName(pitch)}
                  aria-pressed={pitches.includes(pitch)}
                  onClick={() => press(pitch)}
                >
                  <span>{keyName(pitch)}</span>
                </button>
              ))}
          </div>
          <p className="challenge-selection" aria-live="polite">
            {pitches
              .slice()
              .sort((a, b) => a - b)
              .map(keyName)
              .join(' · ') || tr('Hali klavish tanlanmagan')}
          </p>
        </>
      ) : (
        <ToggleButtonGroup
          className="challenge-choices"
          exclusive
          value={choice}
          onChange={(_, value) => {
            setChoice(value);
            setChecked(false);
            setRevealed(false);
          }}
          aria-label={tr('Javob variantlari')}
        >
          {question.choices?.map((option) => (
            <ToggleButton key={option.id} value={option.id}>
              {option.label}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
      )}
      <div className="challenge-actions">
        {question.mode === 'keyboard' && (
          <Button
            disabled={!pitches.length}
            startIcon={<PlayArrowRounded />}
            onClick={() =>
              void piano.play(
                pitches.map((pitch) => ({ pitch, onset: 0, duration: 1.2, velocity: 78 })),
              )
            }
          >
            {tr('Tanlanganlarni eshitish')}
          </Button>
        )}
        <Button
          variant="contained"
          disabled={question.mode === 'keyboard' ? !pitches.length : !choice}
          onClick={() => {
            setChecked(true);
            recordChallengeResult(studyId, questionIds, question.id, correct);
          }}
        >
          {tr('Tekshirish')}
        </Button>
        <Button
          onClick={() => {
            setPitches([]);
            setChoice(null);
            setChecked(false);
            setRevealed(false);
          }}
        >
          {tr('Tozalash')}
        </Button>
        <Button onClick={() => setRevealed((value) => !value)}>
          {tr(revealed ? 'Izohni yashirish' : 'Izohni ko‘rish')}
        </Button>
        {challenges.length > 1 && (
          <>
            <Button disabled={index === 0} onClick={() => setIndex((value) => value - 1)}>
              {tr('Oldingi topshiriq')}
            </Button>
            <Button
              disabled={index === challenges.length - 1}
              onClick={() => setIndex((value) => value + 1)}
            >
              {tr('Keyingi topshiriq')}
            </Button>
          </>
        )}
      </div>
      {checked && (
        <Alert severity={correct ? 'success' : 'warning'}>
          {tr(
            correct
              ? summary.correct === summary.total
                ? 'Barcha topshiriqlar bajarildi. Dars o‘zlashtirildi.'
                : 'To‘g‘ri.'
              : 'Yana bir bor eshitib yoki klavishlarni tekshirib ko‘ring.',
          )}
        </Alert>
      )}
      {revealed && (
        <Alert className="challenge-explanation" severity="info">
          <strong>{tr('Javob izohi')}</strong>
          <p>{question.explanation}</p>
          {question.answerPitches && <p>{question.answerPitches.map(keyName).join(' · ')}</p>}
          {question.answerChoice && (
            <p>{question.choices?.find((option) => option.id === question.answerChoice)?.label}</p>
          )}
        </Alert>
      )}
      {!checked && summary.correct === summary.total && (
        <Alert severity="success">
          {tr('Barcha topshiriqlar bajarildi. Dars o‘zlashtirildi.')}
        </Alert>
      )}
    </section>
  );
}
