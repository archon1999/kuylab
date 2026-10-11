import type { Profile, ProfileSnapshot } from '../entities/profile.types.ts';

export interface ProfileRepository {
  get(): Promise<ProfileSnapshot>;
  save(profile: Profile): Promise<Profile>;
  savePreferences(changes: {
    language?: 'uz' | 'ru' | 'en';
    theme?: 'light' | 'dark';
  }): Promise<void>;
}
