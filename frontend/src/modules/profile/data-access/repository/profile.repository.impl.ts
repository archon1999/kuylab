import { request } from '@shared/api/http';
import type { ProfileRepository } from '../../domain';
import type { ProfileDto } from '../dto';
import { mapProfileSnapshot, normalizeProfile, profilePayload } from '../mappers';
export const createProfileRepository = (): ProfileRepository => ({
  async get() {
    return mapProfileSnapshot(await request<ProfileDto>('profile/'));
  },
  async save(profile) {
    return normalizeProfile(
      await request<ProfileDto>('profile/', 'PATCH', profilePayload(profile)),
    );
  },
  async savePreferences(changes) {
    await request('profile/', 'PATCH', changes);
  },
});
