import { useEffect, useRef, useState } from 'react';
import { useNotify } from '@shared/ui/Notifications';
import { validateProfile, type Profile } from '../domain';
import { useProfile } from './profile-provider';

export function useProfileEditor() {
  const { profile, online, loading, error: loadError, reload, save } = useProfile();
  const [draft, setDraftState] = useState(profile);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const saving = useRef(false);
  const dirty = useRef(new Set<keyof Profile>());
  const revision = useRef(0);
  const notify = useNotify();
  const validation = validateProfile(draft);
  function setDraft(update: React.SetStateAction<Profile>) {
    revision.current++;
    setError('');
    setDraftState((previous) => {
      const next = typeof update === 'function' ? update(previous) : update;
      for (const key of Object.keys(next) as (keyof Profile)[])
        if (next[key] !== previous[key]) dirty.current.add(key);
      return next;
    });
  }
  useEffect(() => {
    setDraftState((previous) => {
      const value = { ...profile };
      for (const key of dirty.current) (value as Record<string, unknown>)[key] = previous[key];
      return value;
    });
  }, [profile]);
  async function submit() {
    if (saving.current || loading) return;
    if (Object.keys(validation).length) {
      setError('Barcha maydonlarni tekshiring.');
      return;
    }
    saving.current = true;
    setBusy(true);
    setError('');
    const savedRevision = revision.current;
    try {
      const value = await save({
        ...draft,
        display_name: draft.display_name.trim(),
        instrument_model: draft.instrument_model.trim(),
      });
      if (savedRevision === revision.current) {
        dirty.current.clear();
        setDraftState(value);
      }
      notify(online ? 'Shaxsiy sozlamalar saqlandi.' : 'Sozlamalar shu brauzerda saqlandi (demo).');
    } catch {
      setError('Sozlamalar saqlanmadi. Qayta urinib ko‘ring.');
    } finally {
      saving.current = false;
      setBusy(false);
    }
  }
  return { draft, setDraft, busy, online, loading, loadError, reload, error, validation, submit };
}
