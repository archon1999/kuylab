import type { StudioPreferences } from '../entities/studio-preferences.types.ts';
export interface StudioPreferencePort {
  read(): StudioPreferences;
  write(value: StudioPreferences): void;
  load?(): Promise<StudioPreferences>;
  subscribe?(listener: () => void): () => void;
  dispose?(): void;
}
