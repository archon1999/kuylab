import { StudioSplash } from '@shared/ui/Loading';
import { useTranslation } from '@shared/i18n';
import { createElement, type ReactNode } from 'react';
import { ActivityStateProvider } from './application';
import { createActivityRepository } from './data-access';
import { createNotesRepository } from './data-access/repository/notes.repository.impl';
import { NotesContext } from './application/usePracticeNotes';
const repository = createActivityRepository();
const notesRepository = createNotesRepository();
export function ActivityProvider({ children }: { children: ReactNode }) {
  const tr = useTranslation();
  return createElement(ActivityStateProvider, {
    repository,
    children: createElement(NotesContext.Provider, { value: notesRepository, children }),
    fallback: createElement(StudioSplash, { label: tr('Yuklanmoqda…') }),
  });
}
export { useActivity } from './application';
export { usePracticeNotes } from './application/usePracticeNotes';
export { default as PracticeNotebook } from './ui/shared/PracticeNotebook';
export type { PracticeNote } from './domain/entities/activity.types';
export type { ActivitySession, ActivityStats } from './domain';
