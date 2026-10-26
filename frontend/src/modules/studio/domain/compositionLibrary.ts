import type { Composition, CompositionFilter } from './entities/studio.types.ts';

export const emptyCompositionFilter: CompositionFilter = {
  query: '',
  difficulty: 0,
  collection: '',
  favoritesOnly: false,
  sort: 'curated',
};
const searchable = (value: string) =>
  value
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[‘’ʼ`]/g, "'")
    .toLocaleLowerCase();

export function libraryVariant(composition: Composition, difficulty = 0) {
  const variants = composition.variants || [];
  const preferred =
    variants.find((value) => value.id === composition.default_variant_id) || variants[0];
  return difficulty && preferred?.difficulty !== difficulty
    ? variants.find((value) => value.difficulty === difficulty) || preferred
    : preferred;
}

export function filterCompositions(
  items: Composition[],
  filter: CompositionFilter,
  favorites: string[],
) {
  const terms = searchable(filter.query).trim().split(/\s+/).filter(Boolean);
  const shown = items.filter((item) => {
    const haystack = searchable(
      `${item.title} ${item.composer} ${item.collection || ''} ${item.subtitle}`,
    );
    return (
      terms.every((word) => haystack.includes(word)) &&
      (!filter.difficulty ||
        item.difficulty === filter.difficulty ||
        item.variants?.some((value) => value.difficulty === filter.difficulty)) &&
      (!filter.collection || (item.collection || '__other__') === filter.collection) &&
      (!filter.favoritesOnly || favorites.includes(`composition:${item.id}`))
    );
  });
  return shown.sort((a, b) =>
    filter.sort === 'title'
      ? a.title.localeCompare(b.title)
      : filter.sort === 'duration'
        ? a.duration_seconds - b.duration_seconds
        : filter.sort === 'difficulty'
          ? (a.difficulty || 0) - (b.difficulty || 0)
          : 0,
  );
}

export function compositionPage(items: Composition[], requested: number, size: number) {
  const pageSize = [6, 12, 24].includes(size) ? size : 6;
  const pages = Math.max(1, Math.ceil(items.length / pageSize));
  const page = Math.min(pages, Math.max(1, Math.floor(Number.isFinite(requested) ? requested : 1)));
  return {
    items: items.slice((page - 1) * pageSize, page * pageSize),
    page,
    pages,
    pageSize,
    from: items.length ? (page - 1) * pageSize + 1 : 0,
    to: Math.min(page * pageSize, items.length),
    total: items.length,
  };
}
