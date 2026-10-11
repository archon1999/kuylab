import type { Session } from '../domain/session';

export function mergeSessionHistory(remote: Session[], savedDuringLoad: Session[]): Session[] {
  const ids = new Set(savedDuringLoad.map((session) => session.id));
  return [...savedDuringLoad, ...remote.filter((session) => !ids.has(session.id))];
}
