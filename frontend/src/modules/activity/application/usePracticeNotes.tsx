import { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import type { NotesRepository } from '../domain/contracts/notes.repository';
import type { PracticeNote } from '../domain/entities/activity.types';
export const NotesContext = createContext<NotesRepository | null>(null);
export function usePracticeNotes(contentId?: string) {
  const repository = useContext(NotesContext);
  if (!repository) throw new Error('NotesProvider required');
  const [notes, setNotes] = useState<PracticeNote[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);
  const generation = useRef(0);
  const reload = useCallback(async () => {
    const ticket = ++generation.current;
    setLoading(true);
    setError(false);
    try {
      const value = await repository.list(contentId);
      if (generation.current === ticket) setNotes(value);
    } catch {
      if (generation.current === ticket) setError(true);
    } finally {
      if (generation.current === ticket) setLoading(false);
    }
  }, [repository, contentId]);
  useEffect(() => {
    setNotes([]);
    void reload();
    return () => {
      generation.current++;
    };
  }, [reload]);
  const mutate = async (action: () => Promise<unknown>) => {
    setBusy(true);
    setError(false);
    try {
      await action();
      await reload();
      return true;
    } catch {
      setError(true);
      return false;
    } finally {
      setBusy(false);
    }
  };
  return {
    notes,
    loading,
    busy,
    error,
    reload,
    add: (position: number, text: string) =>
      mutate(() => repository.add({ contentId: contentId!, position, text })),
    edit: (id: string, text: string) => mutate(() => repository.edit(id, text)),
    remove: (id: string) => mutate(() => repository.remove(id)),
    restore: (id: string) => mutate(() => repository.restore(id)),
  };
}
