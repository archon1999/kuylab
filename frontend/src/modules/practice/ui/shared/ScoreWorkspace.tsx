import {
  FileUploadRounded,
  PauseRounded,
  PlayArrowRounded,
  SettingsInputComponentRounded,
} from '@mui/icons-material';
import {
  Alert,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  MenuItem,
  Select,
  Slider,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import { useScoreWorkspace, type ScoreWorkspaceProps } from '../../application/useScoreWorkspace';
import { pitchLabel } from '../../domain';
import Synthesia from './Synthesia';
export default function ScoreWorkspace(props: ScoreWorkspaceProps) {
  const { composition, online, lessonId } = props;
  const {
    tr,
    scores,
    score,
    loading,
    error,
    importOpen,
    setImportOpen,
    file,
    setFile,
    rights,
    setRights,
    exact,
    setExact,
    importing,
    importError,
    setImportError,
    bpm,
    setBpm,
    hand,
    setHand,
    range,
    setRange,
    playing,
    click,
    setClick,
    activeMeasure,
    position,
    sequence,
    tempoMap,
    wait,
    groups,
    playbackSupported,
    waitIndex,
    matched,
    expected,
    waitMessage,
    screenPitches,
    midiStatus,
    midiNote,
    connecting,
    connectMidi,
    sectionTitle,
    setSectionTitle,
    sectionSaving,
    updatingScore,
    importScore,
    classify,
    saveSection,
    togglePlayback,
    unknownStaves,
    arrangementId,
    unitLabel,
    quarterBpm,
    selectVersion,
    seek,
    startWait,
    pressScreen,
    heldPitches,
    viewQuarter,
    elapsedTime,
    totalTime,
    positionTimeLabel,
  } = useScoreWorkspace(props);
  return (
    <div className="score-workspace">
      <section className="score-toolbar panel">
        <div>
          <span className="eyebrow">{score?.is_demo ? tr('ORIGINAL MASHQ') : tr('MIDI')}</span>
          {lessonId && <h3>{score ? score.title : tr('MIDI yuklanmoqda…')}</h3>}
          {lessonId && (
            <p>
              {tr(
                score?.is_demo ? 'Original dars mashqi.' : 'Asarning shu darsga tegishli parchasi.',
              )}
            </p>
          )}
        </div>
        <Button
          size="small"
          variant="outlined"
          startIcon={<FileUploadRounded />}
          disabled={!online || !!lessonId || importing}
          onClick={() => {
            setImportError('');
            setImportOpen(true);
          }}
        >
          {tr('MIDI qo‘shish')}
        </Button>
      </section>
      {error && (
        <Alert severity="error" sx={{ my: 2 }}>
          {tr(error)}
        </Alert>
      )}
      {!online && (
        <Alert severity="info" sx={{ my: 2 }}>
          {tr('Lokal serverga ulaning.')}
        </Alert>
      )}
      {loading && (
        <p className="learning-caption" role="status">
          {tr('MIDI yuklanmoqda…')}
        </p>
      )}
      {score && (
        <>
          {scores.length > 1 && !lessonId && (
            <Select
              className="score-version"
              size="small"
              value={String(score.id)}
              onChange={(event) => {
                void selectVersion(event.target.value);
              }}
              inputProps={{ 'aria-label': tr('MIDI versiyasini tanlash') }}
            >
              {scores.map((item) => (
                <MenuItem key={item.id} value={String(item.id)}>
                  {tr('v')}
                  {item.version} · {tr(item.title)}
                </MenuItem>
              ))}
            </Select>
          )}
          <section className="actual-score panel">
            <div className="score-subbar">
              <span>
                {score.parsed.metadata.time
                  ? score.parsed.metadata.time.beats +
                    '/' +
                    score.parsed.metadata.time.beat_type +
                    ' · '
                  : ''}{' '}
                {score.parsed.measures.length}{' '}
                {tr(score.file_format === 'midi' ? ' bo‘lak' : ' takt')}
              </span>
              <span>
                {activeMeasure
                  ? `${activeMeasure} · ${tr(score.file_format === 'midi' ? 'Bo‘lak' : 'takt')}`
                  : tr('Tayyor')}
              </span>
            </div>
            <Synthesia
              notes={sequence?.notes || []}
              quarter={viewQuarter}
              tempoMap={tempoMap}
              heldPitches={heldPitches}
              onKey={pressScreen}
            />
            <Slider
              min={0}
              max={100}
              step={0.1}
              value={position}
              onChange={(_, value) => seek(value as number)}
              aria-label={tr('Ijro holati')}
              getAriaValueText={positionTimeLabel}
              disabled={loading || !sequence?.length}
            />
            <output
              aria-label={tr('Ijro holati')}
              style={{
                display: 'block',
                textAlign: 'right',
                fontVariantNumeric: 'tabular-nums',
                fontSize: 13,
              }}
            >
              {elapsedTime} / {totalTime}
            </output>
          </section>
          <section className="score-controls panel">
            <div className="score-tempo">
              <span className="control-label">{tr('TEZLIK')}</span>
              <strong>
                {Math.round((bpm / (score.parsed.metadata.tempo?.bpm || 60)) * 100)}
                <small>% · {bpm} BPM</small>
              </strong>
              <Slider
                min={20}
                max={240}
                step={1}
                value={bpm}
                onChange={(_, value) => setBpm(value as number)}
                aria-label={tr('Nota tempi BPM')}
              />
            </div>
            <div>
              <span className="control-label">{tr('QO‘LLAR')}</span>
              <ToggleButtonGroup
                exclusive
                value={hand}
                onChange={(_, value) => value && setHand(value)}
                size="small"
                aria-label={tr('Nota qo‘li')}
              >
                <ToggleButton value="left">{tr('Chap')}</ToggleButton>
                <ToggleButton value="both">{tr('Ikkalasi')}</ToggleButton>
                <ToggleButton value="right">{tr('O‘ng')}</ToggleButton>
              </ToggleButtonGroup>
            </div>
            <div>
              <span className="control-label">
                {tr(score.file_format === 'midi' ? 'BO‘LAK ORALIG‘I' : 'TAKT ORALIG‘I')}
              </span>
              <div className="score-range">
                <Select
                  size="small"
                  value={range[0]}
                  onChange={(event) =>
                    setRange([
                      Number(event.target.value),
                      Math.max(Number(event.target.value), range[1]),
                    ])
                  }
                  inputProps={{ 'aria-label': tr('Birinchi bo‘lak') }}
                >
                  {score.parsed.measures.map((measure, i) => (
                    <MenuItem key={i} value={i + 1}>
                      {measure.number}
                      {tr(score.file_format === 'midi' ? ' · bo‘lak' : '-takt')}
                    </MenuItem>
                  ))}
                </Select>
                <span>→</span>
                <Select
                  size="small"
                  value={range[1]}
                  onChange={(event) =>
                    setRange([
                      Math.min(range[0], Number(event.target.value)),
                      Number(event.target.value),
                    ])
                  }
                  inputProps={{ 'aria-label': tr('Oxirgi bo‘lak') }}
                >
                  {score.parsed.measures.map((measure, i) => (
                    <MenuItem key={i} value={i + 1}>
                      {measure.number}
                      {tr(score.file_format === 'midi' ? ' · bo‘lak' : '-takt')}
                    </MenuItem>
                  ))}
                </Select>
              </div>
            </div>
            <div className="score-audio-actions">
              <Button
                variant="contained"
                startIcon={playing ? <PauseRounded /> : <PlayArrowRounded />}
                disabled={!sequence?.notes.length || !playbackSupported || loading}
                onClick={() => void togglePlayback()}
              >
                {tr(playing ? 'Pauza' : 'Eshitish')}
              </Button>
              <FormControlLabel
                control={
                  <Checkbox
                    size="small"
                    checked={click}
                    onChange={(event) => setClick(event.target.checked)}
                  />
                }
                label={tr('Metronom')}
              />
            </div>
          </section>
          {!playbackSupported && (
            <p className="learning-caption">
              {tr(
                'Bu notadagi ayrim belgilar ijro tahlilida to‘liq qo‘llanmaydi. Nota ko‘rinadi; audio va nota tekshiruvi o‘chirilgan.',
              )}
            </p>
          )}
          {!sequence?.notes.length && (
            <p className="learning-caption">
              {tr('Tanlangan qo‘lda nota topilmadi. Satrlar qo‘lini quyida belgilang.')}
            </p>
          )}
          {!score.is_demo && !lessonId && (
            <details className="score-details">
              <summary>{tr('Parcha va qo‘l taqsimoti')}</summary>
              <div className="score-staff-assignments">
                {unknownStaves.map((staff) => (
                  <div key={`${staff.part}-${staff.staff}`}>
                    <label>{tr(staff.label)}</label>
                    <Select
                      size="small"
                      value={staff.hand}
                      disabled={updatingScore || loading}
                      onChange={(event) =>
                        void classify(staff.part, staff.staff, event.target.value)
                      }
                      inputProps={{ 'aria-label': tr('{0} qo‘li', [staff.label]) }}
                    >
                      <MenuItem value="unknown">{tr('Belgilanmagan')}</MenuItem>
                      <MenuItem value="left">{tr('Chap qo‘l')}</MenuItem>
                      <MenuItem value="right">{tr('O‘ng qo‘l')}</MenuItem>
                    </Select>
                  </div>
                ))}
              </div>
              <div className="score-saved-sections">
                {score.sections?.map((section) => (
                  <Button
                    size="small"
                    key={section.id}
                    onClick={() => setRange([section.start_index + 1, section.end_index + 1])}
                  >
                    {tr(section.title)}
                  </Button>
                ))}
              </div>
              <div className="save-score-section">
                <TextField
                  size="small"
                  label={tr('Parcha nomi')}
                  placeholder={tr('Masalan: chap qo‘ldagi sakrash')}
                  value={sectionTitle}
                  onChange={(event) => setSectionTitle(event.target.value)}
                />
                <Button
                  disabled={sectionSaving || updatingScore || loading || !sectionTitle.trim()}
                  onClick={() => void saveSection()}
                >
                  {tr('Saqlash · ')}
                  {range[0]}–{range[1]}
                </Button>
              </div>
            </details>
          )}
          <section className="wait-panel panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">{tr('BITTA QADAM, BITTA TOVUSH')}</span>
                <h3>{tr('Nota ortidan')}</h3>
              </div>
              <Button
                variant={wait ? 'contained' : 'outlined'}
                disabled={!groups.length || !playbackSupported || loading}
                onClick={startWait}
              >
                {' '}
                {wait ? tr('Mashqni yopish') : tr('Boshlash')}
              </Button>
            </div>
            <p className="learning-caption">
              {tr(
                'To‘g‘ri balandlikdagi nota yoki akkorddan keyin siljiydi. Ritm, pedal va ifoda bu rejimda baholanmaydi.',
              )}
            </p>
            {wait && (
              <div className="wait-active">
                <strong>
                  {expected
                    ? expected.pitches.map(pitchLabel).join(' + ')
                    : tr('Parcha yakunlandi')}
                </strong>
                <span>
                  {Math.min(waitIndex, groups.length)}/{groups.length}
                </span>
                <p role="status">
                  {waitMessage || tr('Pianinoda chaling yoki ekran tugmalarida sinab ko‘ring.')}
                </p>
                <div className="screen-note-buttons">
                  {screenPitches.map((pitch) => (
                    <Button
                      key={pitch}
                      size="small"
                      variant={matched.includes(pitch) ? 'contained' : 'outlined'}
                      onClick={() => pressScreen(pitch)}
                    >
                      {pitchLabel(pitch)}
                    </Button>
                  ))}
                </div>
                <small>
                  {tr(
                    'Ekran tugmalari — sinov. Pianino ijrosi uchun MIDI ulanishidan foydalaning.',
                  )}
                </small>
              </div>
            )}
            <div className="score-midi">
              <SettingsInputComponentRounded />
              <div>
                <strong>{tr(midiStatus)}</strong>
                {midiNote && <span>{tr(midiNote)}</span>}
              </div>
              <Button size="small" disabled={connecting} onClick={() => void connectMidi()}>
                {tr(connecting ? 'Ulanmoqda…' : 'MIDI ulash')}
              </Button>
            </div>
          </section>
          {!!score.parsed.warnings?.length && (
            <details className="score-details">
              <summary>{tr('Nota tahlili izohlari')}</summary>
              {score.parsed.warnings.map((warning, i) => (
                <p className="learning-caption" key={i}>
                  {warning}
                </p>
              ))}
            </details>
          )}
        </>
      )}
      <Dialog
        open={importOpen}
        onClose={() => !importing && setImportOpen(false)}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>{tr('Aranjirovkangizni import qiling')}</DialogTitle>
        <DialogContent>
          <p className="dialog-intro">
            {tr(composition.title)} · {composition.arrangement_label}
            {tr('. To‘liq MIDI (.mid, .midi) faylni tanlang.')}
          </p>
          <input
            className="musicxml-input"
            type="file"
            accept=".mid,.midi"
            aria-label={tr('MIDI faylni tanlash')}
            disabled={importing}
            onChange={(event) => setFile(event.target.files?.[0] || null)}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={rights}
                onChange={(event) => setRights(event.target.checked)}
                disabled={importing}
              />
            }
            label={tr('Bu MIDI faylidan foydalanish huquqim bor')}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={exact}
                onChange={(event) => setExact(event.target.checked)}
                disabled={importing}
              />
            }
            label={tr('Bu aynan tanlagan aranjirovkam')}
          />
          {importError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {tr(importError)}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button color="inherit" disabled={importing} onClick={() => setImportOpen(false)}>
            {tr('Qaytish')}
          </Button>
          <Button
            variant="contained"
            disabled={importing || !file || !rights}
            onClick={() => void importScore()}
          >
            {importing ? tr('Import qilinmoqda…') : tr('MIDI import qilish')}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
