import {
  CableRounded,
  CheckCircleRounded,
  CloseRounded,
  PianoRounded,
  VolumeOffRounded,
} from '@mui/icons-material';
import {
  Alert,
  Button,
  CircularProgress,
  Dialog,
  DialogContent,
  DialogTitle,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
} from '@mui/material';
import { useId } from 'react';
import { useTranslation } from '@shared/i18n';
import { useMidi } from '../../application/MidiProvider';
import type { MidiConnectionStatus } from '../../domain/contracts/midi-connection.port';
import { pianoPitchName } from '../../domain/liveKeyboard';
import './midiConnection.css';

const labels: Record<MidiConnectionStatus, string> = {
  idle: 'Pianino ulanmagan',
  connecting: 'Pianino qidirilmoqda…',
  choosing: 'MIDI qurilmani tanlang',
  connected: 'Pianino ulangan',
  waiting: 'MIDI qurilma topilmadi',
  disconnected: 'Pianino uzildi',
  denied: 'MIDI uchun ruxsat berilmadi',
  unsupported: 'Bu brauzer MIDI ulanishni qo‘llamaydi',
  insecure: 'MIDI ulanish uchun HTTPS kerak',
  error: 'MIDI qurilmani ochib bo‘lmadi',
};
export function MidiButton({ compact = false }: { compact?: boolean }) {
  const midi = useMidi();
  const tr = useTranslation();
  const connected = midi.connection.status === 'connected';
  const title = tr(connected ? 'Pianino ulangan' : 'Pianino ulash');
  return (
    <Tooltip title={title}>
      <Button
        className={`midi-connect-button ${compact ? 'is-compact' : ''}`}
        onClick={midi.show}
        aria-label={title}
        aria-haspopup="dialog"
        aria-expanded={midi.open}
        data-connected={connected}
      >
        <PianoRounded />
        {!compact && <span>{title}</span>}
        {connected && <i aria-hidden="true" />}
      </Button>
    </Tooltip>
  );
}
export function MidiConnectionPanel() {
  const midi = useMidi();
  const tr = useTranslation();
  const id = useId();
  const { status, devices, selectedId } = midi.connection;
  const connected = status === 'connected';
  const busy = status === 'connecting';
  const failed = ['denied', 'unsupported', 'insecure', 'error'].includes(status);
  const selected = devices.find((device) => device.id === selectedId);
  return (
    <div className="midi-connection-panel">
      <div className="midi-device-status" data-connected={connected} role="status">
        <div className="midi-device-icon">
          {busy ? (
            <CircularProgress size={25} />
          ) : connected ? (
            <CheckCircleRounded />
          ) : (
            <CableRounded />
          )}
        </div>
        <div>
          <strong>{tr(labels[status])}</strong>
          <span>{selected?.name || 'USB MIDI'}</span>
        </div>
      </div>
      {devices.length > 0 && (
        <FormControl fullWidth size="small">
          <InputLabel id={`${id}-device`}>{tr('MIDI qurilma')}</InputLabel>
          <Select
            labelId={`${id}-device`}
            label={tr('MIDI qurilma')}
            value={selected ? selectedId : ''}
            onChange={(event) => midi.select(event.target.value || '')}
          >
            {devices.map((device) => (
              <MenuItem key={device.id} value={device.id}>
                {device.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}
      {status === 'idle' && (
        <p className="midi-help">
          {tr('Pianinoni USB kabel bilan ulang, keyin ulanishga ruxsat bering.')}
        </p>
      )}
      {['waiting', 'disconnected'].includes(status) && (
        <Alert severity="info">
          {tr(
            'USB kabelni va pianino yoqilganini tekshiring. Qurilma ulanganda shu yerda paydo bo‘ladi.',
          )}
        </Alert>
      )}
      {status === 'denied' && (
        <Alert severity="warning">
          {tr('Brauzerning sayt sozlamalarida MIDI ruxsatini yoqing, keyin qayta urinib ko‘ring.')}
        </Alert>
      )}
      {status === 'unsupported' && (
        <Alert severity="info">
          {tr('MIDI uchun Windows kompyuterda Chrome yoki Edge orqali oching.')}
        </Alert>
      )}
      {status === 'insecure' && (
        <Alert severity="warning">{tr('Saytni https://kuylab.uz manzilidan oching.')}</Alert>
      )}
      {status === 'error' && (
        <Alert severity="warning">
          {tr('Boshqa MIDI dasturini yopib, USB ulanishni tekshiring va qayta urinib ko‘ring.')}
        </Alert>
      )}
      <div className="midi-connection-actions">
        {!connected && !['choosing', 'unsupported', 'insecure'].includes(status) && (
          <Button
            variant="contained"
            disabled={busy}
            startIcon={busy ? <CircularProgress size={17} color="inherit" /> : <CableRounded />}
            onClick={() => void midi.connect()}
          >
            {tr(failed ? 'Qayta urinish' : 'Pianino ulash')}
          </Button>
        )}
        {['connected', 'waiting', 'choosing', 'disconnected', 'connecting'].includes(status) && (
          <Button variant="outlined" onClick={midi.disconnect}>
            {tr('Ulanishni uzish')}
          </Button>
        )}
      </div>
      <div className="midi-sound-setting">
        <h3>{tr('Chalayotgan pianino ovozi')}</h3>
        <ToggleButtonGroup
          value={midi.sound}
          exclusive
          fullWidth
          size="small"
          aria-label={tr('Chalayotgan pianino ovozi')}
          onChange={(_, value) => value && midi.setSound(value)}
        >
          <ToggleButton value="instrument">{tr('Pianinoning o‘zi')}</ToggleButton>
          <ToggleButton value="browser">KuyLab Grand</ToggleButton>
        </ToggleButtonGroup>
        <p className="midi-help">
          {tr(
            midi.sound === 'instrument'
              ? 'Sayt bosilgan klavishlarni ko‘rsatadi. Kompozitsiyaning fon ijrosi alohida eshitiladi.'
              : 'Ikki ovoz chiqmasligi uchun pianinoning Local Control sozlamasini o‘chiring. Bu faqat siz chalayotgan ovozga tegishli.',
          )}
        </p>
      </div>
      {connected && (
        <div className="midi-test" aria-label={tr('Ulanishni sinash')}>
          <div className="midi-test-heading">
            <span>{tr('Klavishni bosib sinang')}</span>
            <span className={midi.pedal ? 'is-on' : ''}>
              {tr('Pedal')}: {tr(midi.pedal ? 'Bosilgan' : 'Qo‘yib yuborilgan')}
            </span>
          </div>
          <output aria-live="polite">
            {midi.pitches.length ? midi.pitches.map(pianoPitchName).join(' · ') : '—'}
          </output>
          {midi.loading && (
            <span className="midi-audio-loading">
              <CircularProgress size={13} />
              {tr('Ovoz yuklanmoqda…')}
            </span>
          )}
          <Button size="small" startIcon={<VolumeOffRounded />} onClick={midi.stop}>
            {tr('Tovushlarni to‘xtatish')}
          </Button>
        </div>
      )}
      {midi.audioError && (
        <Alert
          severity="warning"
          action={
            <Button color="inherit" size="small" onClick={() => void midi.connect()}>
              {tr('Qayta urinish')}
            </Button>
          }
        >
          {tr('Ovozni yuklab bo‘lmadi. Qayta urinib ko‘ring.')}
        </Alert>
      )}
    </div>
  );
}
export function MidiConnectionDialog() {
  const midi = useMidi();
  const tr = useTranslation();
  return (
    <Dialog
      className="midi-dialog"
      open={midi.open}
      onClose={midi.hide}
      maxWidth="xs"
      fullWidth
      aria-labelledby="midi-dialog-title"
    >
      <DialogTitle id="midi-dialog-title" className="midi-dialog-heading">
        <span>{tr('Pianino ulash')}</span>
        <IconButton aria-label={tr('Yopish')} onClick={midi.hide}>
          <CloseRounded />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <MidiConnectionPanel />
      </DialogContent>
    </Dialog>
  );
}
