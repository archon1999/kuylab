import type { PersonalState, ActivitySession } from '../entities/activity.types.ts';

export interface ActivityRepository {
  readPersonal(): PersonalState;
  writePersonal(value: PersonalState): void;
  readHistory(): ActivitySession[];
  writeHistory(value: ActivitySession[]): void;
  readLive(): { session: ActivitySession; touched: number } | null;
  writeLive(session: ActivitySession, touched: number): void;
  getPersonal(): Promise<PersonalState>;
  savePersonal(value: PersonalState): Promise<PersonalState>;
  getVisits(): Promise<ActivitySession[]>;
  saveVisit(value: ActivitySession): Promise<ActivitySession>;
}
