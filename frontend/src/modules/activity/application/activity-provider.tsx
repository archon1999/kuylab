import { accountStorage, scopedKey } from '@shared/lib/accountScope';
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import {
  ActivityClock,
  activityStats,
  mergeVisits,
  type ActivityRepository,
  type ActivitySession,
  type ActivityStats,
  type PersonalState,
} from '../domain';

type ContextValue = PersonalState & {
  setProgress(id: string, state: PersonalState['progress'][string] | null): void;
  setStage(id: string, stage: string): void;
  setComfortableSpeed(id: string, speed: number | null): void;
  sessions: ActivitySession[];
  stats: ActivityStats;
  toggleFavorite(id: string): void;
  recordOpen(id: string): void;
  setPosition(id: string, seconds: number): void;
  setPlaying(playing: boolean): void;
  setContent(id: string | null): void;
};
const Context = createContext<ContextValue | null>(null);
const pendingKey = 'kuylab-studio-personal-pending';
function pending() {
  try {
    return accountStorage.getItem(pendingKey) === '1';
  } catch {
    return false;
  }
}
function markPending(value: boolean) {
  try {
    accountStorage.setItem(pendingKey, value ? '1' : '0');
  } catch {
    /* Local-only use remains possible. */
  }
}

export function ActivityStateProvider({
  repository,
  children,
  fallback,
}: {
  repository: ActivityRepository;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}) {
  const [ready, setReady] = useState(false);
  const [personal, setPersonal] = useState(() => repository.readPersonal());
  const [sessions, setSessions] = useState(() => repository.readHistory());
  const personalRef = useRef(personal),
    historyRef = useRef(sessions);
  const revision = useRef(0),
    playing = useRef(false),
    content = useRef<string | null>(null);
  const notifyClock = useRef<() => void>(() => undefined);
  const savePersonalBusy = useRef(false);
  const syncPersonal = useCallback(async () => {
    if (savePersonalBusy.current || !pending()) return;
    savePersonalBusy.current = true;
    try {
      const save = async () => {
        if (!pending()) return;
        // Read after acquiring the cross-tab lock; a queued tab may hold an older ref.
        const value = repository.readPersonal();
        const signature = JSON.stringify(value);
        const started = revision.current;
        await repository.savePersonal(value);
        if (revision.current === started && JSON.stringify(repository.readPersonal()) === signature)
          markPending(false);
      };
      if (navigator.locks) await navigator.locks.request(scopedKey('kuylab-personal-sync'), save);
      else await save();
    } catch {
      /* Retry idempotent personal state after connectivity returns. */
    } finally {
      savePersonalBusy.current = false;
    }
  }, [repository]);
  const updatePersonal = useCallback(
    (change: (value: PersonalState) => PersonalState) => {
      const value = change(personalRef.current);
      personalRef.current = value;
      revision.current++;
      repository.writePersonal(value);
      markPending(true);
      setPersonal(value);
    },
    [repository],
  );
  const mergeHistory = useCallback(
    (incoming: ActivitySession[]) => {
      const value = mergeVisits(historyRef.current, incoming);
      historyRef.current = value;
      repository.writeHistory(value);
      setSessions(value);
    },
    [repository],
  );

  useEffect(() => {
    let disposed = false;
    const hydrate = async () => {
      const generation = revision.current;
      try {
        const [remote, visits] = await Promise.all([
          repository.getPersonal(),
          repository.getVisits(),
        ]);
        if (disposed) return;
        if (!pending() && revision.current === generation) {
          personalRef.current = remote;
          repository.writePersonal(remote);
          setPersonal(remote);
        }
        mergeHistory(visits);
        // Visits use cumulative IDs, so replaying the offline queue cannot duplicate time.
        for (const visit of historyRef.current) {
          if (disposed) break;
          const remoteVisit = visits.find((item) => item.id === visit.id);
          if (!remoteVisit || remoteVisit.seconds < visit.seconds)
            await repository.saveVisit(visit);
        }
        await syncPersonal();
      } catch {
        /* Offline content and local statistics remain usable. */
      } finally {
        if (!disposed) setReady(true);
      }
    };
    void hydrate();
    const online = () => void hydrate();
    window.addEventListener('online', online);
    const timer = setInterval(() => void syncPersonal(), 3000);
    return () => {
      disposed = true;
      clearInterval(timer);
      window.removeEventListener('online', online);
    };
  }, [repository, mergeHistory, syncPersonal]);

  useEffect(() => {
    let clock: ActivityClock | null = null;
    let owned = false,
      acquiring = false,
      disposed = false;
    let release: (() => void) | null = null;
    let lastPublish = 0,
      lastSave = 0;
    const isActive = () => document.visibilityState === 'visible' || playing.current;
    const acquireClock = () => {
      const live = repository.readLive();
      const session =
        live && Date.now() - live.touched < 30 * 60000 && live.session.seconds < 86400
          ? live.session
          : {
              id: crypto.randomUUID(),
              startedAt: new Date().toISOString(),
              seconds: 0,
              contentSeconds: {},
              daySeconds: {},
            };
      clock = new ActivityClock(session, performance.now());
      owned = true;
      clock.advance(performance.now(), Date.now(), isActive(), content.current);
    };
    const publish = (force = false) => {
      if (!owned || !clock) return;
      const value = clock.advance(performance.now(), Date.now(), isActive(), content.current);
      const now = Date.now();
      if (force || now - lastPublish >= 5000) {
        repository.writeLive(value, now);
        if (value.seconds >= 300) mergeHistory([structuredClone(value)]);
        lastPublish = now;
      }
      if (value.seconds >= 300 && (force || now - lastSave >= 30000)) {
        void repository.saveVisit(structuredClone(value)).catch(() => undefined);
        lastSave = now;
      }
    };
    const tick = () => {
      if (disposed) return;
      publish();
      if (!isActive()) {
        release?.();
        return;
      }
      if (!owned && !acquiring) {
        acquiring = true;
        if (navigator.locks) {
          void navigator.locks
            .request(scopedKey('kuylab-site-time'), { ifAvailable: true }, async (lock) => {
              if (!lock || disposed || !isActive()) return;
              acquireClock();
              await new Promise<void>((resolve) => {
                release = resolve;
              });
              publish(true);
              owned = false;
              clock = null;
              release = null;
            })
            .finally(() => {
              acquiring = false;
            });
        } else {
          // Browsers lacking Web Locks keep local activity functional in one tab.
          acquireClock();
          acquiring = false;
          release = () => {
            publish(true);
            owned = false;
            clock = null;
            release = null;
          };
        }
      }
    };
    const stateChange = () => {
      publish(true);
      tick();
    };
    notifyClock.current = stateChange;
    const pageHide = () => {
      publish(true);
      release?.();
    };
    const storage = (event: StorageEvent) => {
      if (event.key === scopedKey('kuylab-studio-visits-v1')) {
        historyRef.current = repository.readHistory();
        setSessions(historyRef.current);
      }
      if (event.key === scopedKey('kuylab-studio-personal-v1')) {
        revision.current++;
        personalRef.current = repository.readPersonal();
        setPersonal(personalRef.current);
      }
    };
    document.addEventListener('visibilitychange', stateChange);
    window.addEventListener('pagehide', pageHide);
    window.addEventListener('storage', storage);
    const timer = setInterval(tick, 1000);
    tick();
    return () => {
      publish(true);
      disposed = true;
      release?.();
      clearInterval(timer);
      document.removeEventListener('visibilitychange', stateChange);
      window.removeEventListener('pagehide', pageHide);
      window.removeEventListener('storage', storage);
      notifyClock.current = () => undefined;
    };
  }, [repository, mergeHistory]);

  const toggleFavorite = useCallback(
    (id: string) =>
      updatePersonal((value) => ({
        ...value,
        favorites: value.favorites.includes(id)
          ? value.favorites.filter((key) => key !== id)
          : [...value.favorites, id].slice(-500),
      })),
    [updatePersonal],
  );
  const setContent = useCallback((id: string | null) => {
    notifyClock.current();
    content.current = id;
    notifyClock.current();
  }, []);
  const recordOpen = useCallback(
    (id: string) => {
      setContent(id);
      updatePersonal((value) => ({
        ...value,
        recents: [
          { id, openedAt: new Date().toISOString() },
          ...value.recents.filter((item) => item.id !== id),
        ].slice(0, 40),
      }));
    },
    [setContent, updatePersonal],
  );
  const setPosition = useCallback(
    (id: string, seconds: number) => {
      if (!Number.isFinite(seconds) || seconds < 0 || seconds > 7200) return;
      const position = Math.floor(seconds);
      if (personalRef.current.positions[id] === position) return;
      updatePersonal((value) => ({ ...value, positions: { ...value.positions, [id]: position } }));
    },
    [updatePersonal],
  );
  const setPlaying = useCallback((value: boolean) => {
    notifyClock.current();
    playing.current = value;
    notifyClock.current();
  }, []);
  const stats = useMemo(() => activityStats(sessions, Date.now()), [sessions]);
  return (
    <Context.Provider
      value={{
        ...personal,
        setComfortableSpeed: (id, speed) =>
          updatePersonal((value) => {
            const comfortableSpeeds = { ...value.comfortableSpeeds };
            if (speed !== null && Number.isInteger(speed) && speed >= 20 && speed <= 200)
              comfortableSpeeds[id] = speed;
            else delete comfortableSpeeds[id];
            return { ...value, comfortableSpeeds };
          }),
        setProgress: (id, state) =>
          updatePersonal((value) => {
            const progress = { ...value.progress };
            if (state) progress[id] = state;
            else delete progress[id];
            return { ...value, progress };
          }),
        setStage: (id, stage) => {
          if (personalRef.current.lastStages[id] !== stage)
            updatePersonal((value) => ({
              ...value,
              lastStages: { ...value.lastStages, [id]: stage },
            }));
        },
        sessions,
        stats,
        toggleFavorite,
        recordOpen,
        setPosition,
        setPlaying,
        setContent,
      }}
    >
      {ready ? children : fallback}
    </Context.Provider>
  );
}
export function useActivity() {
  const value = useContext(Context);
  if (!value) throw new Error('ActivityProvider is required.');
  return value;
}
