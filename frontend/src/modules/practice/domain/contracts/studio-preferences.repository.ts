import type { StudioPreferences } from '../entities/studio-preferences.types.ts';
export interface StudioPreferencePort {
  read(): StudioPreferences;
  write(value: StudioPreferences): void;
  load?(): Promise<StudioPreferences>;
  dispose?(): void;
}
