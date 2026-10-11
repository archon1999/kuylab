import type { Score } from '@modules/practice';
import type { StudioCatalog } from '../entities/studio.types.ts';

export interface StudioRepository {
  catalog(): Promise<StudioCatalog>;
  score(id: number): Promise<Score>;
}
