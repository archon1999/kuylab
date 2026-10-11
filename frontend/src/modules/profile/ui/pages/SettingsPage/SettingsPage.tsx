import { PasswordForm } from '@modules/auth';
import { PageSkeleton } from '@shared/ui/Loading';
import { SaveRounded } from '@mui/icons-material';
import {
  Alert,
  Button,
  FormControl,
  InputLabel,
  Link,
  MenuItem,
  Select,
  TextField,
} from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { SectionHeading } from '@shared/ui/StudyPrimitives';
import { useProfileEditor } from '../../../application';
export default function SettingsPage() {
  const tr = useTranslation();
  const {
    draft: settingsDraft,
    setDraft: setSettingsDraft,
    submit: saveProfile,
    online,
    busy,
    loading,
    loadError,
    reload,
    error,
    validation,
  } = useProfileEditor();
  const fieldError = (code?: string, max?: number) =>
    code === 'too_long'
      ? tr('Eng ko‘pi {0} belgi.', [max])
      : code === 'required'
        ? tr('Bu maydonni to‘ldiring.')
        : code === 'control'
          ? tr('Nazorat belgilarisiz kiriting.')
          : ' ';
  if (loading) return <PageSkeleton variant="settings" />;
  return (
    <>
      <SectionHeading title={tr('Shaxsiy sozlamalar')} />
      {(loadError || !online) && !loading && (
        <Alert
          severity="info"
          action={<Button onClick={() => void reload()}>{tr('Qayta ulanish')}</Button>}
        >
          {tr(loadError || 'Lokal serverga ulaning.')}
        </Alert>
      )}
      <section className="settings-panel panel">
        <div className="settings-section">
          <h3>{tr('Siz haqingizda')}</h3>
          <p>{tr('Studiyadagi shaxsiy profilingiz.')}</p>
          <div className="settings-fields">
            <TextField
              label={tr('Ism yoki taxallus')}
              disabled={busy}
              error={!!validation.display_name}
              helperText={fieldError(validation.display_name, 80)}
              slotProps={{ htmlInput: { maxLength: 80 } }}
              value={settingsDraft.display_name}
              onChange={(e) => setSettingsDraft((d) => ({ ...d, display_name: e.target.value }))}
            />
            <FormControl fullWidth>
              <InputLabel>{tr('Tajriba darajasi')}</InputLabel>
              <Select
                label={tr('Tajriba darajasi')}
                disabled={busy}
                value={settingsDraft.experience_level || 'intermediate'}
                onChange={(e) =>
                  setSettingsDraft((d) => ({ ...d, experience_level: e.target.value }))
                }
              >
                <MenuItem value="beginner">{tr('Boshlang‘ich')}</MenuItem>
                <MenuItem value="intermediate">{tr('O‘rta — qo‘l o‘rgangan')}</MenuItem>
                <MenuItem value="advanced">{tr('Yuqori')}</MenuItem>
              </Select>
            </FormControl>
          </div>
          <TextField
            label={tr('Shaxsiy maqsad')}
            disabled={busy}
            error={!!validation.goals}
            helperText={fieldError(validation.goals, 240)}
            slotProps={{ htmlInput: { maxLength: 240 } }}
            multiline
            minRows={2}
            value={settingsDraft.goals || ''}
            onChange={(e) => setSettingsDraft((d) => ({ ...d, goals: e.target.value }))}
            sx={{ mt: 3 }}
          />
        </div>
        <div className="settings-section">
          <h3>{tr('Pianino')}</h3>
          <p>{tr('Mashq qiladigan instrumentingiz.')}</p>
          <div className="settings-fields">
            <TextField
              label={tr('Instrument modeli')}
              disabled={busy}
              error={!!validation.instrument_model}
              helperText={fieldError(validation.instrument_model, 120)}
              slotProps={{ htmlInput: { maxLength: 120 } }}
              value={settingsDraft.instrument_model}
              onChange={(e) =>
                setSettingsDraft((d) => ({ ...d, instrument_model: e.target.value }))
              }
            />
            <FormControl fullWidth>
              <InputLabel>{tr('Klavishlar')}</InputLabel>
              <Select
                label={tr('Klavishlar')}
                disabled={busy}
                value={settingsDraft.keyboard_keys}
                onChange={(e) =>
                  setSettingsDraft((d) => ({ ...d, keyboard_keys: Number(e.target.value) }))
                }
              >
                <MenuItem value={88}>{tr('88 klavish')}</MenuItem>
                <MenuItem value={76}>{tr('76 klavish')}</MenuItem>
                <MenuItem value={61}>{tr('61 klavish')}</MenuItem>
                <MenuItem value={49}>{tr('49 klavish')}</MenuItem>
              </Select>
            </FormControl>
          </div>
        </div>
        {error && <Alert severity="error">{tr(error)}</Alert>}
        <div className="settings-actions">
          <Button
            variant="contained"
            startIcon={<SaveRounded />}
            onClick={() => void saveProfile()}
            disabled={busy || loading || Object.keys(validation).length > 0}
          >
            {tr('Sozlamalarni saqlash')}
          </Button>
        </div>
      </section>
      <PasswordForm />
      <Link
        href="/licenses.html"
        target="_blank"
        rel="noopener noreferrer"
        color="text.secondary"
        underline="hover"
        sx={{ display: 'inline-block', mt: 3, fontSize: 13 }}
      >
        {tr('Litsenziyalar')}
      </Link>
    </>
  );
}
