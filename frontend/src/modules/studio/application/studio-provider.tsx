import { usePreferences } from '@shared/i18n';
import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import type { StudioCatalog, StudioRepository } from '../domain';
const Context = createContext<{
  catalog: StudioCatalog | null;
  loading: boolean;
  error: string;
  reload: () => Promise<void>;
  repository: StudioRepository;
} | null>(null);
export function StudioProvider({
  repository,
  children,
}: {
  repository: StudioRepository;
  children: React.ReactNode;
}) {
  const { language } = usePreferences();
  const [catalog, setCatalog] = useState<StudioCatalog | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const generation = useRef(0);
  const reload = useCallback(async () => {
    const current = ++generation.current;
    setLoading(true);
    setError('');
    try {
      const value = await repository.catalog();
      if (current === generation.current) setCatalog(value);
    } catch (reason) {
      if (current === generation.current)
        setError(reason instanceof Error ? reason.message : 'Kontentni ochib bo‘lmadi.');
    } finally {
      if (current === generation.current) setLoading(false);
    }
  }, [repository]);
  useEffect(() => {
    void reload();
    return () => {
      generation.current++;
    };
  }, [reload, language]);
  return (
    <Context.Provider value={{ catalog, loading, error, reload, repository }}>
      {children}
    </Context.Provider>
  );
}
export function useStudio() {
  const value = useContext(Context);
  if (!value) throw new Error('StudioProvider required');
  return value;
}
