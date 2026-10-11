import { useRef, useState } from 'react';
import { useNotify } from '@shared/ui/Notifications';
import { navigate } from '@shared/routing';
import { validateCompositionInput } from '../domain';
import { useRepertoire } from './repertoire-provider';

export function useCompositionEditor() {
  const { add, mode } = useRepertoire();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [composer, setComposer] = useState('');
  const [url, setUrl] = useState('');
  const [arrangement, setArrangement] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const notify = useNotify();
  const saving = useRef(false);
  async function submit() {
    if (saving.current) return;
    const input = {
      title: title.trim(),
      composer: composer.trim(),
      source_url: url.trim(),
      arrangement_title: arrangement.trim(),
    };
    const validation = validateCompositionInput(input);
    if (Object.values(validation).includes('too_long')) {
      setError('Barcha maydonlarni tekshiring.');
      return;
    }
    if (!title.trim()) {
      setError('Kompozitsiya nomini kiriting.');
      return;
    }
    if (url.trim()) {
      try {
        if (!['http:', 'https:'].includes(new URL(url).protocol)) throw new Error();
      } catch {
        setError('http yoki https bilan boshlanadigan to‘g‘ri havola kiriting.');
        return;
      }
    }
    saving.current = true;
    setBusy(true);
    setError('');
    try {
      const item = await add({
        title: title.trim(),
        composer: composer.trim(),
        source_url: url.trim(),
        arrangement_title: arrangement.trim(),
      });
      setOpen(false);
      setTitle('');
      setComposer('');
      setUrl('');
      setArrangement('');
      notify('Kompozitsiya saqlandi.');
      navigate('detail', { composition: item.id });
    } catch (error) {
      setError(
        error instanceof Error ? error.message : 'Server saqlay olmadi. Qayta urinib ko‘ring.',
      );
    } finally {
      saving.current = false;
      setBusy(false);
    }
  }
  return {
    open,
    setOpen,
    title,
    setTitle,
    composer,
    setComposer,
    url,
    setUrl,
    arrangement,
    setArrangement,
    error,
    busy,
    submit,
    online: mode === 'online',
  };
}
