import type { ActivitySessionDto, PersonalStateDto } from '../dto';
import { mapPersonal, validVisit } from '../mappers';
import { request } from '@shared/api/http';
import { readLocal, writeLocal } from '@shared/lib/storage';
import { emptyPersonal, type ActivityRepository, type ActivitySession } from '../../domain';

const personalKey = 'kuylab-studio-personal-v1';
const historyKey = 'kuylab-studio-visits-v1';
const liveKey = 'kuylab-studio-live-v1';
export function createActivityRepository(): ActivityRepository {
  return {
    readPersonal: () => mapPersonal(readLocal(personalKey, emptyPersonal)),
    writePersonal: (value) => writeLocal(personalKey, value),
    readHistory: () => {
      const value = readLocal<ActivitySession[]>(historyKey, []);
      return Array.isArray(value) ? value.filter(validVisit) : [];
    },
    writeHistory: (value) => writeLocal(historyKey, value),
    readLive: () => {
      const value = readLocal<{ session: ActivitySession; touched: number } | null>(liveKey, null);
      return value && validVisit(value.session) && Number.isFinite(value.touched) ? value : null;
    },
    writeLive: (session, touched) => writeLocal(liveKey, { session, touched }),
    getPersonal: () => request<PersonalStateDto>('activity/state/').then(mapPersonal),
    savePersonal: (value) =>
      request<PersonalStateDto>('activity/state/', 'PATCH', value).then(mapPersonal),
    getVisits: () => request<ActivitySessionDto[]>('activity/visits/'),
    saveVisit: (value) => request<ActivitySessionDto>('activity/visits/', 'PUT', value),
  };
}
