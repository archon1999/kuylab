import { request } from '@shared/api/http';
import type { PracticeNote } from '../../domain/entities/activity.types';
import type { NotesRepository } from '../../domain/contracts/notes.repository';
export function createNotesRepository(): NotesRepository {
  return {
    list: (content) =>
      request<PracticeNote[]>(
        'activity/notes/' + (content ? '?content=' + encodeURIComponent(content) : ''),
      ),
    add: (value) => request<PracticeNote>('activity/notes/', 'POST', value),
    edit: (id, text) =>
      request<PracticeNote>('activity/notes/' + encodeURIComponent(id) + '/', 'PATCH', { text }),
    remove: (id) => request<void>('activity/notes/' + encodeURIComponent(id) + '/', 'DELETE'),
    restore: (id) =>
      request<PracticeNote>('activity/notes/' + encodeURIComponent(id) + '/', 'PATCH', {
        deleted: false,
      }),
  };
}
