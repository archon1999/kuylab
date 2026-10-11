import { useState, type FormEvent } from 'react';
import { Alert, Button, TextField } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { useAuth } from '../application';
export default function PasswordForm() {
  const auth = useAuth(),
    tr = useTranslation();
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(''),
    [saved, setSaved] = useState(false);
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget,
      data = new FormData(form);
    setBusy(true);
    setError('');
    setSaved(false);
    try {
      await auth.password(String(data.get('current')), String(data.get('next')));
      form.reset();
      setSaved(true);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  };
  return (
    <details className="account-password">
      <summary>{tr('Parolni o‘zgartirish')}</summary>
      <form onSubmit={submit} style={{ display: 'grid', gap: 16, maxWidth: 440, marginTop: 20 }}>
        <TextField
          name="current"
          label={tr('Joriy parol')}
          type="password"
          autoComplete="current-password"
          required
        />
        <TextField
          name="next"
          label={tr('Yangi parol')}
          type="password"
          autoComplete="new-password"
          required
          slotProps={{ htmlInput: { minLength: 8, maxLength: 1024 } }}
        />
        {error && <Alert severity="error">{error}</Alert>}
        {saved && <Alert severity="success">{tr('Parol yangilandi')}</Alert>}
        <Button type="submit" variant="contained" disabled={busy}>
          {tr('Parolni o‘zgartirish')}
        </Button>
      </form>
    </details>
  );
}
