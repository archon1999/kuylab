import { accountStorage } from '@shared/lib/accountScope';
import {
  PreferenceContext,
  getInterfaceLanguage,
  type ColorMode,
  type InterfaceLanguage,
} from '@shared/i18n';
import { readLocal, writeLocal } from '@shared/lib/storage';
import { transitionColorMode } from '@shared/ui/colorModeTransition';
import {
  createContext,
  useContext,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
} from 'react';
import { defaultProfile, type Profile, type ProfileRepository } from '../domain';
import { PreferenceSynchronizer, type PreferenceChanges } from './PreferenceSynchronizer';
import { ProfileResource, serializeProfileWrites } from './ProfileResource';
const validLanguage = (value: unknown): value is InterfaceLanguage =>
  ['uz', 'ru', 'en'].includes(String(value));
const validMode = (value: unknown): value is ColorMode => ['light', 'dark'].includes(String(value));
const pendingKey = 'kuylab-pending-preferences';
function stored(key: string) {
  try {
    return accountStorage.getItem(key);
  } catch {
    return null;
  }
}
function store(key: string, value: string) {
  try {
    accountStorage.setItem(key, value);
  } catch {
    /* Remote persistence still works without browser storage. */
  }
}
const Context = createContext<{
  profile: Profile;
  online: boolean;
  loading: boolean;
  error: string;
  save: (value: Profile) => Promise<Profile>;
  reload: () => Promise<void>;
} | null>(null);
export function ProfileProvider({
  repository,
  children,
}: {
  repository: ProfileRepository;
  children: React.ReactNode;
}) {
  const port = useMemo(() => serializeProfileWrites(repository), [repository]);
  const [language, setLanguageState] = useState<InterfaceLanguage>(getInterfaceLanguage);
  const [mode, setMode] = useState<ColorMode>(() =>
    validMode(stored('kuylab-theme')) ? (stored('kuylab-theme') as ColorMode) : 'light',
  );
  const modeRef = useRef(mode);
  modeRef.current = mode;
  const sync = useRef<PreferenceSynchronizer | null>(null);
  if (!sync.current) {
    const raw = readLocal<PreferenceChanges>(pendingKey, {});
    const pending = {
      ...(validLanguage(raw.language) ? { language: raw.language } : {}),
      ...(validMode(raw.theme) ? { theme: raw.theme } : {}),
    };
    sync.current = new PreferenceSynchronizer(
      (changes) => port.savePreferences(changes),
      (changes) => writeLocal(pendingKey, changes),
      pending,
    );
  }
  function setLanguage(next: InterfaceLanguage) {
    setLanguageState(next);
    store('kuylab-language', next);
    void sync.current?.choose({ language: next });
  }
  function toggleMode() {
    const next = modeRef.current === 'light' ? 'dark' : 'light';
    modeRef.current = next;
    transitionColorMode(() => setMode(next));
    store('kuylab-theme', next);
    void sync.current?.choose({ theme: next });
  }
  function hydrate(serverLanguage: unknown, serverMode: unknown) {
    if (!sync.current?.canHydrate()) {
      void sync.current?.flush();
      return;
    }
    const nextLanguage = validLanguage(serverLanguage) ? serverLanguage : language;
    const nextMode = validMode(serverMode) ? serverMode : mode;
    setLanguageState(nextLanguage);
    setMode(nextMode);
    store('kuylab-language', nextLanguage);
    store('kuylab-theme', nextMode);
  }
  const hydrateRef = useRef(hydrate);
  hydrateRef.current = hydrate;
  const [resource] = useState(
    () =>
      new ProfileResource(
        port,
        readLocal('kuylab-profile', defaultProfile),
        (value) => writeLocal('kuylab-profile', value),
        (value) => hydrateRef.current(value.language, value.theme),
      ),
  );
  const snapshot = useSyncExternalStore(resource.subscribe, resource.getSnapshot);
  const reload = () => resource.reload();
  const save = (value: Profile) => resource.save(value);
  useEffect(() => {
    void reload();
    return () => resource.cancel();
  }, [resource]);
  useLayoutEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dataset.theme = mode;
  }, [language, mode]);
  return (
    <PreferenceContext.Provider value={{ language, mode, setLanguage, toggleMode, hydrate }}>
      <Context.Provider value={{ ...snapshot, save, reload }}>{children}</Context.Provider>
    </PreferenceContext.Provider>
  );
}
export function useProfile() {
  const value = useContext(Context);
  if (!value) throw new Error('ProfileProvider required');
  return value;
}
