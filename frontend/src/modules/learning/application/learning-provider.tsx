import { createContext, useContext } from 'react';
import type { LearningRepository } from '../domain';
const Context = createContext<LearningRepository | null>(null);
export function LearningProvider({
  repository,
  children,
}: {
  repository: LearningRepository;
  children: React.ReactNode;
}) {
  return <Context.Provider value={repository}>{children}</Context.Provider>;
}
export function useLearningRepository() {
  const repository = useContext(Context);
  if (!repository) throw new Error('LearningProvider required');
  return repository;
}
