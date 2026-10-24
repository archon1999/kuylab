import type { PracticeNote } from '../entities/activity.types';
export interface NotesRepository {
  list(contentId?: string): Promise<PracticeNote[]>;
  add(value: Pick<PracticeNote, 'contentId' | 'position' | 'text'>): Promise<PracticeNote>;
  edit(id: string, text: string): Promise<PracticeNote>;
  remove(id: string): Promise<void>;
  restore(id: string): Promise<PracticeNote>;
}
