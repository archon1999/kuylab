import { AddRounded, ArrowForwardRounded, MusicNoteRounded } from '@mui/icons-material';
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  TextField,
} from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { navigate } from '@shared/routing';
import { SectionHeading } from '@shared/ui/StudyPrimitives';
import { useState } from 'react';
import { useCompositionEditor, useRepertoire } from '../../../application';
export default function LibraryPage() {
  const tr = useTranslation();
  const { compositions, error: libraryError, refresh } = useRepertoire();
  const [filter, setFilter] = useState('');
  const editor = useCompositionEditor();
  const {
    open: addOpen,
    setOpen: setAddOpen,
    title: sourceTitle,
    setTitle: setSourceTitle,
    composer: sourceComposer,
    setComposer: setSourceComposer,
    url: sourceUrl,
    setUrl: setSourceUrl,
    arrangement,
    setArrangement,
    error: sourceError,
    busy: adding,
    submit: addComposition,
  } = editor;
  const setSelectedId = (id: number) => navigate('detail', { composition: id });
  return (
    <>
      <>
        <SectionHeading
          title={tr('Kompozitsiyalar')}
          action={
            <Button variant="contained" startIcon={<AddRounded />} onClick={() => setAddOpen(true)}>
              {tr('Kompozitsiya qo‘shish')}
            </Button>
          }
        />
        <div className="library-tools">
          <TextField
            placeholder={tr('Kompozitsiya yoki bastakorni izlash')}
            slotProps={{ htmlInput: { 'aria-label': tr('Kompozitsiya yoki bastakorni izlash') } }}
            size="small"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            sx={{ maxWidth: 380 }}
          />
          <span className="muted">
            {compositions.length} {tr(' ta kompozitsiya')}
          </span>
        </div>
        <div className="composition-grid">
          {compositions
            .filter((c) => `${c.title} ${c.composer}`.toLowerCase().includes(filter.toLowerCase()))
            .map((c) => (
              <article className="composition-card panel" key={c.id}>
                <button
                  className="cover-button"
                  onClick={() => {
                    setSelectedId(c.id);
                  }}
                  aria-label={tr(`${c.title} rejasini ochish`)}
                >
                  <span className="composition-glyph">
                    <MusicNoteRounded />
                  </span>
                </button>
                <div className="composition-info">
                  <span className="eyebrow">
                    {c.arrangement?.exact_version_confirmed
                      ? tr('MANBA TANLANGAN')
                      : c.source_url
                        ? tr('HAVOLA KIRITILGAN')
                        : c.category?.includes('OST')
                          ? tr('TREK TANLASH KERAK')
                          : tr('ARANJIROVKA KUTILMOQDA')}
                  </span>
                  <h3>{tr(c.title)}</h3>
                  <p>{c.composer || tr('Bastakor kiritilmagan')}</p>
                  <div className="composition-footer">
                    <span>
                      {tr(
                        c.source_status === 'full_midi_ready'
                          ? 'To‘liq MIDI tayyor'
                          : c.source_status === 'midi_uploaded'
                            ? 'MIDI tayyor'
                            : 'MIDI kerak',
                      )}
                    </span>
                    <IconButton
                      aria-label={tr(`${c.title} ni ochish`)}
                      onClick={() => {
                        setSelectedId(c.id);
                      }}
                    >
                      <ArrowForwardRounded />
                    </IconButton>
                  </div>
                </div>
              </article>
            ))}
          <button className="add-composition-card" onClick={() => setAddOpen(true)}>
            <span>
              <AddRounded sx={{ fontSize: 32 }} />
            </span>
            <h3>{tr('Kompozitsiya qo‘shish')}</h3>
            <p>{tr('Video yoki MIDI havolasi')}</p>
          </button>
        </div>
        {filter &&
          !compositions.some((c) =>
            `${c.title} ${c.composer}`.toLowerCase().includes(filter.toLowerCase()),
          ) && (
            <Alert severity="info" sx={{ mt: 3 }}>
              {tr('Bu nom bilan kompozitsiya topilmadi. Yangi kompozitsiya qo‘shishingiz mumkin.')}
            </Alert>
          )}
      </>
      {libraryError && (
        <Alert
          severity="warning"
          action={<Button onClick={() => void refresh()}>{tr('Qayta yuklash')}</Button>}
        >
          {tr(libraryError)}
        </Alert>
      )}
      <Dialog open={addOpen} onClose={() => !adding && setAddOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{tr('Sevimli kompozitsiyangizni qo‘shing')}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            label={tr('Kompozitsiya nomi')}
            disabled={adding}
            slotProps={{ htmlInput: { maxLength: 160 } }}
            value={sourceTitle}
            onChange={(e) => setSourceTitle(e.target.value)}
            sx={{ mt: 1, mb: 2 }}
          />
          <TextField
            label={tr('Bastakor (ixtiyoriy)')}
            disabled={adding}
            slotProps={{ htmlInput: { maxLength: 160 } }}
            value={sourceComposer}
            onChange={(e) => setSourceComposer(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            label={tr('Video yoki MIDI havolasi (ixtiyoriy)')}
            disabled={adding}
            slotProps={{ htmlInput: { maxLength: 1000 } }}
            value={sourceUrl}
            onChange={(e) => setSourceUrl(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            label={tr('Aranjirovka / kanal / versiya')}
            disabled={adding}
            slotProps={{ htmlInput: { maxLength: 180 } }}
            value={arrangement}
            onChange={(e) => setArrangement(e.target.value)}
          />
          {sourceError && <Alert severity="error">{tr(sourceError)}</Alert>}
        </DialogContent>
        <DialogActions>
          <Button color="inherit" onClick={() => setAddOpen(false)} disabled={adding}>
            {tr('Bekor qilish')}
          </Button>
          <Button
            variant="contained"
            disabled={adding || !editor.online}
            onClick={() => void addComposition()}
          >
            {tr(adding ? 'Saqlanmoqda…' : 'Kompozitsiyani saqlash')}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
