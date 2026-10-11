import { readLocal, writeLocal } from '@shared/lib/storage';
import { useNotify } from '@shared/ui/Notifications';
import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import type { Session, SessionRepository } from '../domain/session';
import { SessionClock, MAX_SESSION_SECONDS } from './SessionClock';
import { mergeSessionHistory } from './SessionHistory';
const Context = createContext<{
  sessions: Session[];
  record: (session: Session) => Promise<void>;
  reload: () => Promise<void>;
} | null>(null);
export function SessionsProvider({
  repository,
  children,
}: {
  repository: SessionRepository;
  children: React.ReactNode;
}) {
  const [sessions, setSessions] = useState<Session[]>(() => readLocal('kuylab-sessions', []));
  const pendingRecords = useRef<Session[]>([]);
  const generation = useRef(0);
  const reload = useCallback(async () => {
    const request = ++generation.current;
    try {
      const value = await repository.list();
      if (request !== generation.current) return;
      setSessions(mergeSessionHistory(value, pendingRecords.current));
      const received = new Set(value.map((session) => session.id));
      pendingRecords.current = pendingRecords.current.filter(
        (session) => !received.has(session.id),
      );
    } catch {
      /* Preserve existing history when offline. */
    }
  }, [repository]);
  useEffect(() => {
    void reload();
    return () => {
      generation.current++;
    };
  }, [reload]);
  useEffect(() => {
    writeLocal('kuylab-sessions', sessions);
  }, [sessions]);
  async function record(session: Session) {
    const value = await repository.save(session);
    pendingRecords.current = [value, ...pendingRecords.current];
    setSessions((items) => mergeSessionHistory(items, [value]));
  }
  return <Context.Provider value={{ sessions, record, reload }}>{children}</Context.Provider>;
}
export function useSessions() {
  const value = useContext(Context);
  if (!value) throw new Error('SessionsProvider required');
  return value;
}
export function useSessionTimer(compositionId: number) {
  const { record } = useSessions();
  const notify = useNotify();
  const [clock] = useState(() => new SessionClock(() => performance.now()));
  const saving = useRef(false);
  const [running, setRunning] = useState(false),
    [elapsed, setElapsedDisplay] = useState(0),
    [notes, setNotes] = useState(''),
    [confidence, setConfidence] = useState(3),
    [open, setOpen] = useState(false),
    [busy, setBusy] = useState(false),
    [bpm, setBpm] = useState(200),
    [hand, setHand] = useState('both');
  useEffect(() => {
    if (!running) {
      setElapsedDisplay(clock.pause());
      return;
    }
    clock.start();
    const timer = setInterval(() => {
      const seconds = clock.seconds();
      setElapsedDisplay(seconds);
      if (seconds >= MAX_SESSION_SECONDS) {
        setRunning(false);
        notify('Mashq vaqti 4 soatga yetdi. Qaydni saqlang.');
      }
    }, 250);
    return () => {
      clearInterval(timer);
      clock.pause();
    };
  }, [running, clock, notify]);
  function setElapsed(value: number) {
    clock.reset(value);
    setElapsedDisplay(clock.seconds());
  }
  async function save() {
    if (saving.current || elapsed < 1) return;
    saving.current = true;
    setBusy(true);
    try {
      await record({
        composition: compositionId,
        duration_seconds: elapsed,
        bpm,
        hand,
        notes,
        confidence,
      });
      setOpen(false);
      setRunning(false);
      setElapsed(0);
      setNotes('');
      notify('Mashq qaydi saqlandi.');
    } catch (error) {
      notify(
        error instanceof Error
          ? error.message
          : 'Mashq qaydi saqlanmadi. Vaqt saqlanib turibdi, qayta urinib ko‘ring.',
      );
    } finally {
      saving.current = false;
      setBusy(false);
    }
  }
  return {
    running,
    setRunning,
    elapsed,
    setElapsed,
    notes,
    setNotes,
    confidence,
    setConfidence,
    open,
    setOpen,
    busy,
    bpm,
    setBpm,
    setHand,
    save,
  };
}
