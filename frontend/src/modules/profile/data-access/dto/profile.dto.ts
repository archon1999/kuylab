/** The API accepts legacy field names; keep them at the transport boundary. */
export type ProfileDto = {
  display_name?: unknown;
  instrument_model?: unknown;
  keys?: unknown;
  keyboard_keys?: unknown;
  level?: unknown;
  experience_level?: unknown;
  practice_minutes?: unknown;
  daily_minutes?: unknown;
  goal?: unknown;
  goals?: unknown;
  language?: unknown;
  theme?: unknown;
};
export type ProfilePayload = {
  display_name: string;
  instrument_model: string;
  keys: number;
  level: string;
  practice_minutes: number;
  goal?: string;
};
