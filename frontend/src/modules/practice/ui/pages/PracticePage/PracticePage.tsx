import { useRepertoire } from '@modules/repertoire';
import { PauseRounded, PlayArrowRounded, RefreshRounded, SaveRounded } from '@mui/icons-material';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Slider,
  TextField,
} from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { navigate, useRoute } from '@shared/routing';
import { SectionHeading } from '@shared/ui/StudyPrimitives';
import { useMemo } from 'react';
import { useSessionTimer } from '../../../application/Sessions';
import { validateRequestedTempo } from '../../../domain';
import ScoreWorkspace from '../../shared/ScoreWorkspace';
const noop = () => {};
export default function PracticePage() {
  const tr = useTranslation();
  const { current, mode, refresh } = useRepertoire();
  const { params } = useRoute();
  const timer = useSessionTimer(current.id);
  const requestedRange = useMemo(() => {
    const start = Number(params.get('start_index')),
      end = Number(params.get('end_index'));
    return params.has('start_index') &&
      params.has('end_index') &&
      Number.isInteger(start) &&
      Number.isInteger(end) &&
      start >= 0 &&
      end >= start
      ? ([start, end] as [number, number])
      : null;
  }, [params.toString()]);
  const requestedSeconds = useMemo(() => {
    const start = Number(params.get('start_seconds')),
      end = Number(params.get('end_seconds'));
    return params.has('start_seconds') &&
      params.has('end_seconds') &&
      Number.isFinite(start) &&
      Number.isFinite(end) &&
      start >= 0 &&
      end > start
      ? ([start, end] as [number, number])
      : null;
  }, [params.toString()]);
  const requestedTempo = useMemo(
    () => validateRequestedTempo(params.get('bpm'), params.get('beat_unit')),
    [params.toString()],
  );
  return (
    <>
      <SectionHeading
        title={current.title}
        description={current.arrangement_label}
        action={
          <Button color="inherit" onClick={() => navigate('detail')}>
            {tr('Darslar')}
          </Button>
        }
      />
      <div className="primary-practice">
        <ScoreWorkspace
          composition={current}
          online={mode === 'online'}
          scoreId={Number(params.get('score')) || current.arrangement?.active_score_id || null}
          sectionId={params.get('section')}
          requestedRange={requestedRange}
          requestedTempo={requestedTempo}
          requestedSeconds={requestedSeconds}
          onScoreChange={refresh}
          onSettingsChange={(bpm, hand) => {
            timer.setBpm(bpm);
            timer.setHand(hand);
          }}
          onPresence={noop}
        />
        <section className="timer-panel panel" style={{ marginTop: 18 }}>
          <div>
            <span className="eyebrow">{tr('MASHQ VAQTI')}</span>
            <strong>
              {String(Math.floor(timer.elapsed / 60)).padStart(2, '0')}:
              {String(timer.elapsed % 60).padStart(2, '0')}
            </strong>
          </div>
          <IconButton
            aria-label={tr(timer.running ? 'Vaqtni pauza qilish' : 'Vaqtni boshlash')}
            onClick={() => timer.setRunning((value) => !value)}
          >
            {timer.running ? <PauseRounded /> : <PlayArrowRounded />}
          </IconButton>
          <IconButton
            aria-label={tr('Vaqtni nollash')}
            onClick={() => {
              timer.setRunning(false);
              timer.setElapsed(0);
            }}
          >
            <RefreshRounded />
          </IconButton>
          <Button
            variant="contained"
            disabled={timer.elapsed < 1}
            startIcon={<SaveRounded />}
            onClick={() => {
              timer.setRunning(false);
              timer.setOpen(true);
            }}
          >
            {tr('Saqlash')}
          </Button>
        </section>
      </div>
      <Dialog
        open={timer.open}
        onClose={() => !timer.busy && timer.setOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>{tr('Bugungi mashqni qayd eting')}</DialogTitle>
        <DialogContent>
          <p className="dialog-intro">
            {current.title} · {Math.floor(timer.elapsed / 60)}:
            {String(timer.elapsed % 60).padStart(2, '0')} · {timer.bpm} BPM
          </p>
          <TextField
            label={tr('Nima yaxshilandi? Qayeri qiyin bo‘ldi?')}
            multiline
            minRows={3}
            disabled={timer.busy}
            slotProps={{ htmlInput: { maxLength: 2000 } }}
            value={timer.notes}
            onChange={(e) => timer.setNotes(e.target.value)}
            sx={{ my: 2 }}
          />
          <span className="control-label">
            {tr('O‘ZINGIZNI QANCHALIK ISHONCHLI HIS QILDINGIZ?')}
          </span>
          <Slider
            min={1}
            max={5}
            step={1}
            marks
            disabled={timer.busy}
            value={timer.confidence}
            onChange={(_, value) => timer.setConfidence(value as number)}
            aria-label={tr('Shaxsiy ishonch darajasi')}
          />
          <p className="footnote">
            {tr('Bu shaxsiy kuzatuvingiz. Avtomatik ijro bahosi hisoblanmaydi.')}
          </p>
        </DialogContent>
        <DialogActions>
          <Button color="inherit" disabled={timer.busy} onClick={() => timer.setOpen(false)}>
            {tr('Qaytish')}
          </Button>
          <Button variant="contained" disabled={timer.busy} onClick={() => void timer.save()}>
            {tr(timer.busy ? 'Saqlanmoqda…' : 'Mashqni saqlash')}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
