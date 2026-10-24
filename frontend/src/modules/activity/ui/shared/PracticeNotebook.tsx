import { useState } from 'react';
import { Alert, Button, CircularProgress, IconButton, TextField, Tooltip } from '@mui/material';
import {
  BookmarkBorderRounded,
  CloseRounded,
  DeleteOutlineRounded,
  EditOutlined,
  PlayArrowRounded,
} from '@mui/icons-material';
import { useTranslation } from '@shared/i18n';
import { usePracticeNotes } from '../../application/usePracticeNotes';
import './notebook.css';
const time = (value: number) =>
  `${Math.floor(value / 60)}:${String(Math.floor(value) % 60).padStart(2, '0')}`;
export default function PracticeNotebook({
  contentId,
  position,
  onSeek,
  onClose,
}: {
  contentId: string;
  position: number;
  onSeek: (value: number) => void;
  onClose: () => void;
}) {
  const tr = useTranslation();
  const data = usePracticeNotes(contentId);
  const [text, setText] = useState('');
  const [editing, setEditing] = useState<string | null>(null);
  const [removed, setRemoved] = useState<string | null>(null);
  const save = async () => {
    if (!text.trim()) return;
    const saved = editing ? await data.edit(editing, text) : await data.add(position, text);
    if (saved) {
      setText('');
      setEditing(null);
    }
  };
  return (
    <div className="practice-notebook">
      <div className="notebook-heading">
        <h2>{tr('Qaydlar')}</h2>
        <IconButton aria-label={tr('Yopish')} onClick={onClose}>
          <CloseRounded />
        </IconButton>
      </div>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          void save();
        }}
      >
        <span className="notebook-timestamp">
          {editing
            ? time(data.notes.find((note) => note.id === editing)?.position || 0)
            : time(position)}
        </span>
        <TextField
          fullWidth
          multiline
          minRows={3}
          maxRows={7}
          label={tr(editing ? 'Qaydni tahrirlash' : 'Shu joy haqida qayd')}
          value={text}
          onChange={(event) => setText(event.target.value)}
          slotProps={{ htmlInput: { maxLength: 1000 } }}
          disabled={data.busy}
        />
        <div className="notebook-actions">
          <Button type="submit" variant="contained" disabled={data.busy || !text.trim()}>
            {tr('Saqlash')}
          </Button>
          {editing && (
            <Button
              onClick={() => {
                setEditing(null);
                setText('');
              }}
            >
              {tr('Bekor qilish')}
            </Button>
          )}
        </div>
      </form>
      {data.error && (
        <Alert
          severity="error"
          action={<Button onClick={() => void data.reload()}>{tr('Qayta urinish')}</Button>}
        >
          {tr('Qaydlarni saqlab yoki yuklab bo‘lmadi. Internetni tekshiring.')}
        </Alert>
      )}
      {removed && (
        <Alert
          severity="info"
          action={
            <Button
              disabled={data.busy}
              onClick={() => void data.restore(removed).then((ok) => ok && setRemoved(null))}
            >
              {tr('Qaytarish')}
            </Button>
          }
        >
          {tr('Qayd olib tashlandi.')}
        </Alert>
      )}
      {data.loading ? (
        <div className="notebook-empty">
          <CircularProgress size={22} aria-label={tr('Yuklanmoqda…')} />
        </div>
      ) : data.notes.length ? (
        <ul className="notebook-list">
          {data.notes
            .slice()
            .sort((a, b) => a.position - b.position)
            .map((note) => (
              <li key={note.id}>
                <div className="notebook-note-top">
                  <button
                    className="notebook-seek"
                    onClick={() => {
                      onSeek(note.position);
                      onClose();
                    }}
                    aria-label={tr('{0} vaqtidagi qaydni ochish', [time(note.position)])}
                  >
                    <PlayArrowRounded fontSize="small" />
                    {time(note.position)}
                  </button>
                  <div>
                    <Tooltip title={tr('Tahrirlash')}>
                      <IconButton
                        size="small"
                        aria-label={tr('Tahrirlash')}
                        disabled={data.busy}
                        onClick={() => {
                          setEditing(note.id);
                          setText(note.text);
                        }}
                      >
                        <EditOutlined fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={tr('Olib tashlash')}>
                      <IconButton
                        size="small"
                        aria-label={tr('Olib tashlash')}
                        disabled={data.busy}
                        onClick={() =>
                          void data.remove(note.id).then((ok) => {
                            if (ok) {
                              setRemoved(note.id);
                              if (editing === note.id) {
                                setEditing(null);
                                setText('');
                              }
                            }
                          })
                        }
                      >
                        <DeleteOutlineRounded fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </div>
                </div>
                <p>{note.text}</p>
              </li>
            ))}
        </ul>
      ) : (
        !data.error && (
          <div className="notebook-empty">
            <BookmarkBorderRounded />
            <p>{tr('Mashqdagi muhim joylarni shu yerda saqlang.')}</p>
          </div>
        )
      )}
    </div>
  );
}
