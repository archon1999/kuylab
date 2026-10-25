import type {
  StudyItem,
  StudioCatalog,
  StudyFilter,
  StudyStatusFilter,
  StudyProgressMap,
  Composition,
} from './entities/studio.types.ts';

export function selectStudyStage(item: StudyItem | undefined, requested: string | null) {
  return item?.stages?.find((stage) => stage.id === requested) || item?.stages?.[0];
}

export function selectCompositionVariant(
  composition: Composition | undefined,
  requested?: string | null,
  remembered?: string,
) {
  const variants = composition?.variants || [];
  return (
    variants.find((variant) => variant.id === requested) ||
    variants.find((variant) => variant.id === remembered) ||
    variants.find((variant) => variant.id === composition?.default_variant_id) ||
    variants[0]
  );
}

export function compositionPlaybackContext(composition: Composition, variantId?: string) {
  const id = `composition:${composition.id}`;
  return variantId && composition.variants?.some((variant) => variant.id === variantId)
    ? `${id}:variant:${variantId}`
    : id;
}

export const emptyFilter: StudyFilter = {
  query: '',
  category: '',
  goal: '',
  level: '',
  favoritesOnly: false,
  status: '',
};

export function filterStudyItems(
  items: StudyItem[],
  filter: StudyFilter,
  favorites: string[],
  progress: StudyProgressMap = {},
) {
  const query = filter.query.trim().toLocaleLowerCase();
  return filterByStudyStatus(items, filter.status, progress).filter(
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
  return [...catalog.lessons, ...catalog.exercises, ...catalog.theory, ...(catalog.journeys || [])];
}

export function studyProgress(item: StudyItem, progress: StudyProgressMap) {
  const stages = item.stages || [];
  const states = stages.map((stage) => progress[stage.id]).filter(Boolean);
  const completed = stages.filter((stage) => progress[stage.id] === 'mastered').length;
  const state = states.length
    ? completed === stages.length
      ? 'mastered'
      : states.includes('struggling')
        ? 'struggling'
        : 'learning'
    : progress[item.id];
  return { state, completed, total: stages.length };
}

export function filterByStudyStatus(
  items: StudyItem[],
  status: StudyStatusFilter,
  progress: StudyProgressMap,
) {
  if (!status) return items;
  return items.filter((item) => (studyProgress(item, progress).state || 'not_started') === status);
}

export function summarizeStudyProgress(items: StudyItem[], progress: StudyProgressMap) {
  const totals = { total: 0, not_started: 0, learning: 0, struggling: 0, mastered: 0 };
  const counted = new Set<string>();
  for (const item of items) {
    if (counted.has(item.id)) continue;
    counted.add(item.id);
    totals.total++;
    totals[studyProgress(item, progress).state || 'not_started']++;
  }
  return totals;
}

export function durationLabel(seconds: number) {
  const total = Math.max(0, Math.floor(seconds));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`;
}
