import type { StudyItem, StudioCatalog, StudyFilter } from './entities/studio.types.ts';

export function selectStudyStage(item: StudyItem | undefined, requested: string | null) {
  return item?.stages?.find((stage) => stage.id === requested) || item?.stages?.[0];
}

export const emptyFilter: StudyFilter = {
  query: '',
  category: '',
  goal: '',
  level: '',
  favoritesOnly: false,
};

export function filterStudyItems(items: StudyItem[], filter: StudyFilter, favorites: string[]) {
  const query = filter.query.trim().toLocaleLowerCase();
  return items.filter(
    (item) =>
      (!query ||
        `${item.title} ${item.subtitle} ${item.intro}`.toLocaleLowerCase().includes(query)) &&
      (!filter.category || item.category === filter.category) &&
      (!filter.goal || item.goals.includes(filter.goal)) &&
      (!filter.level || item.level === filter.level) &&
      (!filter.favoritesOnly || favorites.includes(item.id)),
  );
}

export function allStudyItems(catalog: StudioCatalog) {
  return [...catalog.lessons, ...catalog.exercises, ...catalog.theory];
}

export function durationLabel(seconds: number) {
  const total = Math.max(0, Math.floor(seconds));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`;
}
