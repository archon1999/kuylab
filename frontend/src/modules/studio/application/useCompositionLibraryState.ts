import { useEffect, useMemo } from 'react';
import { navigate, replaceRoute, useRoute } from '@shared/routing';
import {
  hasLibraryQuery,
  readLibraryQuery,
  libraryQuery,
  normalizeLibraryState,
  type CompositionFilter,
  type CompositionLibraryState,
} from '../domain';
import { useStudio } from './studio-provider';

export function useCompositionLibraryState() {
  const { repository } = useStudio();
  const { params, canonical } = useRoute();
  const signature = params.toString();
  const state = useMemo(
    () =>
      hasLibraryQuery(params) || canonical
        ? readLibraryQuery(params)
        : repository.readLibraryState(),
    [signature, canonical, repository],
  );
  useEffect(() => {
    repository.saveLibraryState(state);
    // Normalize only this route; a bare fresh visit restores this tab's session.
    replaceRoute('library', libraryQuery(state));
  }, [state, repository]);
  const commit = (next: CompositionLibraryState, replace = false) => {
    const normalized = normalizeLibraryState(next);
    repository.saveLibraryState(normalized);
    (replace ? replaceRoute : navigate)('library', libraryQuery(normalized));
  };
  return {
    ...state,
    change(value: Partial<CompositionFilter>) {
      commit({ ...state, filter: { ...state.filter, ...value }, page: 1 }, 'query' in value);
    },
    setPage(page: number, replace = false) {
      commit({ ...state, page }, replace);
    },
    setSize(size: number) {
      commit({ ...state, size, page: 1 });
    },
    reset() {
      commit(normalizeLibraryState({ size: state.size }));
    },
    canonical: libraryQuery(state),
  };
}
