import { usePreferences } from '@shared/i18n';
import { RepertoireResource } from './RepertoireResource';
import { useRoute } from '@shared/routing';
import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useSyncExternalStore,
} from 'react';
import {
  demoComposition,
  type Composition,
  type CompositionInput,
  type RepertoireRepository,
} from '../domain';
const Context = createContext<{
  compositions: Composition[];
  mode: 'loading' | 'online' | 'demo';
  error: string;
  reload: () => Promise<void>;
  refresh: () => Promise<void>;
  add: (input: CompositionInput) => Promise<Composition>;
} | null>(null);
export function RepertoireProvider({
  repository,
  children,
}: {
  repository: RepertoireRepository;
  children: React.ReactNode;
}) {
  const { language } = usePreferences();
  const [resource] = useState(() => new RepertoireResource(repository));
  const { compositions, mode, error } = useSyncExternalStore(
    resource.subscribe,
    resource.getSnapshot,
  );
  const first = useRef(true);
  useEffect(() => {
    void resource.reload(!first.current);
    first.current = false;
    return () => resource.cancel();
  }, [resource, language]);
  const reload = () => resource.reload();
  const refresh = () => resource.reload(true);
  const add = (input: CompositionInput) => resource.add(input);
  return (
    <Context.Provider value={{ compositions, mode, error, reload, refresh, add }}>
      {children}
    </Context.Provider>
  );
}
export function useRepertoire() {
  const value = useContext(Context);
  if (!value) throw new Error('RepertoireProvider required');
  const { compositionId } = useRoute();
  return {
    ...value,
    selectionExists:
      value.mode !== 'online' || value.compositions.some((item) => item.id === compositionId),
    current:
      value.compositions.find((item) => item.id === compositionId) ||
      value.compositions[0] ||
      demoComposition,
  };
}
