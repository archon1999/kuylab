import type { SessionDto } from '../dto';
import { mapSession } from '../mappers';
import { request } from '@shared/api/http';
import type { SessionRepository } from '../../domain/session';
export const createSessionRepository = (): SessionRepository => ({
  async list() {
    const raw = await request<SessionDto>('overview/');
    return ((raw.recent_sessions || raw.sessions || []) as Record<string, unknown>[]).map(
      mapSession,
    );
  },
  async save(value) {
    return mapSession(
      await request<SessionDto>('sessions/', 'POST', {
        composition: value.composition,
        duration_seconds: value.duration_seconds,
        bpm: value.bpm,
        comfort: value.confidence,
        notes: value.notes,
      }),
    );
  },
});
