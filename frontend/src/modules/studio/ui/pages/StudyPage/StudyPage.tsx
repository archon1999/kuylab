import { useActivity } from '@modules/activity';
import { StudioPlayer } from '@modules/practice';
import { ArrowBackRounded, ArrowForwardRounded } from '@mui/icons-material';
import { Button, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { navigate, useRoute } from '@shared/routing';
import { useEffect } from 'react';
import { useStudio, useStudyScore } from '../../../application';
import { allStudyItems, durationLabel, selectStudyStage } from '../../../domain';
import { Favorite, Heading, Loading, SectionTitle, StudioError } from '../../shared/StudioParts';
import Fingering from '../../shared/Fingering';
import '../../studio.css';
export default function StudyPage() {
  const { catalog } = useStudio();
  const { params } = useRoute();
  const {
    recordOpen,
    setPlaying,
    setPosition,
    positions,
    progress,
    setProgress,
    lastStages,
    setStage,
  } = useActivity();
  const tr = useTranslation();
  const item = catalog && allStudyItems(catalog).find((value) => value.id === params.get('item'));
  const stage = selectStudyStage(
    item || undefined,
    params.get('stage') || (item ? lastStages[item.id] : null),
  );
  useEffect(() => {
    if (item && stage) setStage(item.id, stage.id);
  }, [item?.id, stage?.id]);
  const comparison = item?.comparisons?.find((value) => value.id === params.get('example'));
  const scoreId = comparison?.score_id ?? stage?.score_id ?? item?.score_id;
  const positionId = comparison?.id ?? stage?.id ?? item?.id ?? '';
  const { score, loading, error, reload } = useStudyScore(scoreId);
  useEffect(() => {
    if (item) recordOpen(item.id);
    return () => setPlaying(false);
  }, [item?.id, recordOpen, setPlaying]);
  if (!item) return <StudioError message={tr('Dars topilmadi.')} />;
  const composition = catalog?.compositions.find((value) => value.id === item.composition_id);
  const stageIndex = item.stages?.findIndex((value) => value.id === stage?.id) ?? -1;
  const nextStage = item.stages?.[stageIndex + 1];
  const openStage = (id: string) => {
    setPlaying(false);
    navigate('study', { item: item.id, composition: item.composition_id ?? null, stage: id });
  };
  const goBack = () =>
    navigate(
      item.kind === 'lesson' ? 'detail' : item.kind === 'exercise' ? 'exercises' : 'theory',
      { composition: item.composition_id ?? null },
    );
  const related = catalog
    ? allStudyItems(catalog).filter(
        (value) => value.id !== item.id && item.related_ids?.includes(value.id),
      )
    : [];
  const category =
    catalog?.categories.find((value) => value.id === item.category)?.label ||
    tr(
      item.kind === 'lesson'
        ? 'Kompozitsiya darsi'
        : item.kind === 'exercise'
          ? 'Umumiy mashq'
          : 'Amaliy nazariya',
    );
  return (
    <article className="studio-page studio-study-page">
      <Button className="studio-back" startIcon={<ArrowBackRounded />} onClick={goBack}>
        {tr(
          item.kind === 'lesson'
            ? 'Kompozitsiya darslari'
            : item.kind === 'exercise'
              ? 'Mashqlar'
              : 'Amaliy nazariya',
        )}
      </Button>
      <Heading eyebrow={category} title={item.title} action={<Favorite id={item.id} />} />
      <ToggleButtonGroup
        className="study-progress"
        size="small"
        exclusive
        value={progress[item.id] || null}
        onChange={(_, value) => setProgress(item.id, value)}
        aria-label={tr('O‘zlashtirish holati')}
      >
        <ToggleButton value="learning">{tr('O‘rganyapman')}</ToggleButton>
        <ToggleButton value="struggling">{tr('Qiynalyapman')}</ToggleButton>
        <ToggleButton value="mastered">{tr('O‘zlashtirdim')}</ToggleButton>
      </ToggleButtonGroup>
      <p className="studio-study-intro">{item.intro}</p>
      {stage && (
        <section className="studio-lesson-stages" aria-label={tr('Mashq bosqichlari')}>
          <ToggleButtonGroup
            exclusive
            value={stage.id}
            onChange={(_, id: string | null) => id && openStage(id)}
            aria-label={tr('Mashq bosqichlari')}
          >
            {item.stages?.map((value, index) => (
              <ToggleButton key={value.id} value={value.id}>
                {index + 1}. {value.title}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
          <p>{stage.instruction}</p>
          <small>
            {tr(
              'Namuna asl tezlikning {0}% ida yozilgan. Playerdagi 100% — shu namunaning tezligi.',
              [stage.source_speed_percent],
            )}
          </small>
          {item.source && (
            <small>
              {tr('Asardagi joy')}: {durationLabel(item.source.start_seconds)}–
              {durationLabel(item.source.end_seconds)}
            </small>
          )}
        </section>
      )}
      {!!item.comparisons?.length && (
        <section className="studio-comparisons">
          <ToggleButtonGroup
            size="small"
            exclusive
            value={comparison?.id || 'original'}
            onChange={(_, value) =>
              value &&
              navigate('study', {
                item: item.id,
                example: value === 'original' ? null : value,
                stage: null,
              })
            }
            aria-label={tr('Pianino namunalarini solishtirish')}
          >
            <ToggleButton value="original">{tr('Asosiy namuna')}</ToggleButton>
            {item.comparisons.map((value) => (
              <ToggleButton key={value.id} value={value.id}>
                {value.title}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
          <p>{comparison?.instruction}</p>
        </section>
      )}
      <section className="studio-sample" aria-label={tr('Ovozli namuna')}>
        <div className="studio-sample-label">
          <span>{tr('Avval tinglab ko‘ring')}</span>
        </div>
        {loading && <Loading compact />}
        {error && <StudioError message={error} retry={reload} />}
        {score && Number(score.id) === scoreId && (
          <StudioPlayer
            key={String(score.id)}
            score={score}
            compact
            initialPosition={positions[positionId] || 0}
            onPlaybackChange={setPlaying}
            onPositionChange={(seconds) => setPosition(positionId, seconds)}
          />
        )}
      </section>
      {stage && (
        <div className="studio-stage-actions">
          {nextStage && (
            <Button endIcon={<ArrowForwardRounded />} onClick={() => openStage(nextStage.id)}>
              {tr('Keyingi bosqich')}: {nextStage.title}
            </Button>
          )}
          {composition && item.source && (
            <Button
              onClick={() => {
                setPlaying(false);
                setPosition(`composition:${composition.id}`, item.source!.start_seconds);
                navigate('practice', {
                  composition: composition.id,
                  score: composition.score_id,
                  item: null,
                  stage: null,
                });
              }}
            >
              {tr('Shu joyni to‘liq asarda ochish')}
            </Button>
          )}
        </div>
      )}
      <section className="studio-reading">
        <SectionTitle title={tr('Tushunib oling')} />
        <div className="studio-explanations">
          {item.explanation.map((part, index) => (
            <div key={index}>
              <h3>{part.title}</h3>
              <p>{part.text}</p>
            </div>
          ))}
        </div>
      </section>
      {item.ready_when && (
        <section className="studio-reading studio-readiness">
          <SectionTitle title={tr('Dars yakunidagi mezon')} />
          <p>{item.ready_when}</p>
          <p>
            {tr(
              'Avval joriy bosqichni uch marta qulay va ravon takrorlang. Keyin yangi bosqichga o‘ting yoki tezlikni 5–10% oshiring. Aniqlik yo‘qolsa, oldingi qulay variantga qayting. Bosqichlar doim ochiq.',
            )}
          </p>
        </section>
      )}
      {item.fingering && <Fingering text={item.fingering} />}
      <section className="studio-reading">
        <SectionTitle title={tr('Pianinoda sinab ko‘ring')} />
        <ol className="studio-steps">
          {item.steps.map((step, index) => (
            <li key={index}>
              <span aria-hidden="true">{String(index + 1).padStart(2, '0')}</span>
              <div>
                <h3>{step.title}</h3>
                <p>{step.instruction}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>
      {related.length > 0 && (
        <section className="studio-reading">
          <SectionTitle title={tr('Davom ettirish uchun')} />
          <div className="studio-related">
            {related.map((value) => (
              <Button
                key={value.id}
                endIcon={<ArrowForwardRounded />}
                onClick={() =>
                  navigate('study', { item: value.id, composition: value.composition_id ?? null })
                }
              >
                <span className="studio-related-title">{value.title}</span>
                {value.level && (
                  <span className="studio-related-level">
                    {tr({ easy: 'Oson', intermediate: 'O‘rta', advanced: 'Murakkab' }[value.level])}
                  </span>
                )}
              </Button>
            ))}
          </div>
        </section>
      )}
    </article>
  );
}
