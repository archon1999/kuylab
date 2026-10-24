import { PageSkeleton } from '@shared/ui/Loading';
import { createElement, type ReactNode } from 'react';
import { ActivityStateProvider } from './application';
import { createActivityRepository } from './data-access';
import { createNotesRepository } from './data-access/repository/notes.repository.impl';
import { NotesContext } from './application/usePracticeNotes';
const repository = createActivityRepository();
const notesRepository = createNotesRepository();
export function ActivityProvider({ children }: { children: ReactNode }) {
  return createElement(ActivityStateProvider, {
    repository,
    children: createElement(NotesContext.Provider, { value: notesRepository, children }),
    fallback: createElement(PageSkeleton),
  });
}
export { useActivity } from './application';
export { usePracticeNotes } from './application/usePracticeNotes';
export { default as PracticeNotebook } from './ui/shared/PracticeNotebook';
export type { PracticeNote } from './domain/entities/activity.types';
export type { ActivitySession, ActivityStats } from './domain';
