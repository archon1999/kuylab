import type { Score } from '../score';

export type ScoreImportInput = (
  | { arrangementId: number; compositionId?: never }
  | { compositionId: number; arrangementId?: never }
) & {
  filename: string;
  title: string;
  bytes: ArrayBuffer;
  rightsConfirmed: boolean;
  exactVersionConfirmed: boolean;
};
export type ScoreSummary = Pick<
  Score,
  'id' | 'version' | 'arrangement_id' | 'title' | 'file_format' | 'exact_version_confirmed'
>;
export interface ScoreRepository {
  list(arrangementId: number): Promise<ScoreSummary[]>;
  get(id: number | string): Promise<Score>;
  lesson(id: number): Promise<Score>;
  patch(id: number | string, value: Pick<Score, 'hand_overrides' | 'sections'>): Promise<Score>;
  import(input: ScoreImportInput): Promise<Score>;
}
