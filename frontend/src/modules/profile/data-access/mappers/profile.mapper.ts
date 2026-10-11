import type { Profile, ProfileSnapshot } from '../../domain/entities/profile.types.ts';
import type { ProfileDto, ProfilePayload } from '../dto/profile.dto.ts';
export function normalizeProfile(raw: ProfileDto): Profile {
  return {
    display_name: String(raw.display_name || 'Pianinochi'),
    instrument_model: String(raw.instrument_model || 'Yamaha YDP-145'),
    keyboard_keys: Number(raw.keys || raw.keyboard_keys || 88),
    experience_level: String(raw.level || raw.experience_level || 'intermediate'),
    daily_minutes: Number(raw.practice_minutes || raw.daily_minutes || 30),
    goals: String(raw.goal || raw.goals || ''),
  };
}
export function mapProfileSnapshot(raw: ProfileDto): ProfileSnapshot {
  return {
    ...normalizeProfile(raw),
    language: raw.language as ProfileSnapshot['language'],
    theme: raw.theme as ProfileSnapshot['theme'],
  };
}
export function profilePayload(profile: Profile): ProfilePayload {
  return {
    display_name: profile.display_name,
    instrument_model: profile.instrument_model,
    keys: profile.keyboard_keys,
    level: profile.experience_level,
    practice_minutes: profile.daily_minutes,
    goal: profile.goals,
  };
}
