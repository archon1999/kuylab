import type { Score } from '@modules/practice';
import type { StudioCatalog, CompositionPreview } from '../entities/studio.types.ts';
import type { CompositionLibraryState } from '../compositionLibraryState.ts';

export interface StudioRepository {
  readLibraryState(): CompositionLibraryState;
  saveLibraryState(state: CompositionLibraryState): void;
  catalog(): Promise<StudioCatalog>;
  score(id: number): Promise<Score>;
  preview(id: number, variant?: string): Promise<CompositionPreview>;
}
