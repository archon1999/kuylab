import type { Session } from '../entities/session.types.ts';
export interface SessionRepository {
  list(): Promise<Session[]>;
  save(value: Session): Promise<Session>;
}
