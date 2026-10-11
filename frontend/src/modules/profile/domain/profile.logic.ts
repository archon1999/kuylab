import type { Profile, ProfileError } from './entities/profile.types.ts';

export const defaultProfile: Profile = {
  display_name: 'Pianinochi',
  instrument_model: 'Yamaha YDP-145',
  keyboard_keys: 88,
  experience_level: 'intermediate',
  daily_minutes: 30,
  goals: 'Sevimli kompozitsiyalarimni ongli va ravon chalish',
};

export function validateProfile(profile: Profile): Partial<Record<keyof Profile, ProfileError>> {
  const errors: Partial<Record<keyof Profile, ProfileError>> = {};
  if (!profile.display_name.trim()) errors.display_name = 'required';
  else if (/[\x00-\x1f\x7f]/.test(profile.display_name)) errors.display_name = 'control';
  else if (profile.display_name.length > 80) errors.display_name = 'too_long';
  if (!profile.instrument_model.trim()) errors.instrument_model = 'required';
  else if (profile.instrument_model.length > 120) errors.instrument_model = 'too_long';
  if ((profile.goals || '').length > 240) errors.goals = 'too_long';
  if (
    !Number.isInteger(profile.daily_minutes) ||
    profile.daily_minutes < 5 ||
    profile.daily_minutes > 180
  )
    errors.daily_minutes = 'range';
  if (![49, 61, 76, 88].includes(profile.keyboard_keys)) errors.keyboard_keys = 'range';
  return errors;
}
