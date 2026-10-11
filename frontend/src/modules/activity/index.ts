import { PageSkeleton } from '@shared/ui/Loading';
import { createElement, type ReactNode } from 'react';
import { ActivityStateProvider } from './application';
import { createActivityRepository } from './data-access';
const repository = createActivityRepository();
export function ActivityProvider({ children }: { children: ReactNode }) {
  return createElement(ActivityStateProvider, {
    repository,
    children,
    fallback: createElement(PageSkeleton),
  });
}
export { useActivity } from './application';
export type { ActivitySession, ActivityStats } from './domain';
