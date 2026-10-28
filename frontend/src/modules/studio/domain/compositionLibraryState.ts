import type { CompositionFilter } from './entities/studio.types.ts';
import { emptyCompositionFilter } from './compositionLibrary.ts';

export type CompositionLibraryState = {
  filter: CompositionFilter;
  page: number;
  size: number;
  view: 'list' | 'grid';
};
export const libraryQueryKeys = [
  'q',
  'group',
  'difficulty',
  'collection',
  'favorites',
  'sort',
  'p',
  'size',
  'view',
] as const;
export function normalizeLibraryState(value: unknown): CompositionLibraryState {
  const raw = value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
  const filter =
    raw.filter && typeof raw.filter === 'object' ? (raw.filter as Record<string, unknown>) : {};
  const text = (name: string) =>
    typeof filter[name] === 'string'
      ? (filter[name] as string).replace(/[\x00-\x1f]/g, '').slice(0, 160)
      : '';
  const difficulty = Number(filter.difficulty);
  const page = Number(raw.page);
  const size = Number(raw.size);
  return {
    filter: {
      query: text('query'),
      group: text('group'),
      collection: text('collection'),
      difficulty:
        Number.isInteger(difficulty) && difficulty >= 1 && difficulty <= 5 ? difficulty : 0,
      favoritesOnly: filter.favoritesOnly === true,
      sort: ['curated', 'title', 'difficulty', 'duration'].includes(String(filter.sort))
        ? (filter.sort as CompositionFilter['sort'])
        : emptyCompositionFilter.sort,
    },
    page: Number.isSafeInteger(page) && page >= 1 ? Math.min(page, 100000) : 1,
    size: [6, 12, 24].includes(size) ? size : 6,
    view: raw.view === 'grid' ? 'grid' : 'list',
  };
}
export function hasLibraryQuery(params: URLSearchParams) {
  return libraryQueryKeys.some((key) => params.has(key));
}
export function readLibraryQuery(params: URLSearchParams): CompositionLibraryState {
  return normalizeLibraryState({
    filter: {
      query: params.get('q'),
      group: params.get('group'),
      difficulty: params.get('difficulty'),
      collection: params.get('collection'),
      favoritesOnly: params.get('favorites') === '1',
      sort: params.get('sort'),
    },
    page: params.get('p'),
    size: params.get('size'),
    view: params.get('view'),
  });
}
export function libraryQuery(
  state: CompositionLibraryState,
): Record<string, string | number | null> {
  const { filter, page, size, view } = normalizeLibraryState(state);
  return {
    q: filter.query || null,
    group: filter.group || null,
    difficulty: filter.difficulty || null,
    collection: filter.collection || null,
    favorites: filter.favoritesOnly ? '1' : null,
    sort: filter.sort === 'curated' ? null : filter.sort,
    p: page === 1 ? null : page,
    size: size === 6 ? null : size,
    view: view === 'list' ? null : view,
  };
}
