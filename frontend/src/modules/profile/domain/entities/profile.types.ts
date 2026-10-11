export type Profile = {
  display_name: string;
  instrument_model: string;
  keyboard_keys: number;
  experience_level: string;
  daily_minutes: number;
  goals?: string;
};

export type ProfileSnapshot = Profile & { language: 'uz' | 'ru' | 'en'; theme: 'light' | 'dark' };

export type ProfileError = 'required' | 'too_long' | 'control' | 'range';
