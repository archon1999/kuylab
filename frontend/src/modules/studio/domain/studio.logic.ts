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

/** Added recordings do not change the identity of an existing lesson edition. */
function retainedBaseVariant(composition: Composition | undefined) {
  const base = composition?.variants?.find(
    (variant) => variant.id === composition.default_variant_id,
  );
  return base &&
    !base.playback_revision &&
    !composition?.playback_revision &&
    composition?.variants?.some((variant) => variant.playback_revision)
    ? base
    : undefined;
}

export function selectCompositionVariant(
  composition: Composition | undefined,
  requested?: string | null,
  remembered?: string,
  hasTimestamp = false,
) {
  const variants = composition?.variants || [];
  return (
    variants.find((variant) => variant.id === requested) ||
    (!requested && hasTimestamp ? retainedBaseVariant(composition) : undefined) ||
    variants.find((variant) => variant.id === remembered) ||
    variants.find((variant) => variant.id === composition?.default_variant_id) ||
    variants[0]
  );
}

export function compositionPlaybackContext(composition: Composition, variantId?: string) {
  const id = `composition:${composition.id}`;
  const base = retainedBaseVariant(composition);
  if (base && base.id === variantId) return id;
  const revision =
    composition.variants?.find((variant) => variant.id === variantId)?.playback_revision ||
    composition.playback_revision;
  if (revision) return `${id}:source:${revision}`;
  return variantId && composition.variants?.some((variant) => variant.id === variantId)
    ? `${id}:variant:${variantId}`
    : id;
}

export function compositionPositionKeys(composition: Composition, variantId?: string) {
  const context = compositionPlaybackContext(composition, variantId);
  const id = `composition:${composition.id}`;
  return context.includes(':source:') || context === id ? [context] : [context, id];
}

export function compositionResumePosition(
  composition: Composition,
  positions: Readonly<Record<string, number>>,
  variantId?: string,
) {
  for (const key of compositionPositionKeys(composition, variantId))
    if (Number.isFinite(positions[key]) && positions[key] >= 0) return positions[key];
  return 0;
}

/** Lesson seconds belong to the reviewed recording; aligned package editions share them. */
export function studyMatchesPerformance(
  item: StudyItem,
  composition: Composition,
  variantId?: string,
) {
  if (item.composition_id !== composition.id || !item.source) return false;
  const selected = selectCompositionVariant(composition, variantId);
  const revision = selected?.playback_revision ?? composition.playback_revision;
  const source = item.source;
  if (source.playback_revision)
    return (
      source.playback_revision === revision &&
      (!source.composition_variant_id || source.composition_variant_id === selected?.id)
    );
  return !revision;
}

export function compositionNotebookContext(composition: Composition, variantId?: string) {
  const context = compositionPlaybackContext(composition, variantId);
  return context.includes(':source:') ? context : `composition:${composition.id}`;
}

/** Independent recordings resume themselves; aligned legacy arrangements share time. */
export function compositionVariantStartPosition(
  composition: Composition,
  targetVariantId: string,
  currentPosition: number,
) {
  const target = composition.variants?.find((variant) => variant.id === targetVariantId);
  return target?.playback_revision ||
    composition.playback_revision ||
    composition.variants?.some((variant) => variant.playback_revision)
    ? null
    : Number(currentPosition.toFixed(3));
}

/** An old timestamp can identify its work without identifying today's recording. */
export function compositionNoteTarget(compositions: Composition[], contentId: string) {
  const match = contentId.match(/^composition:(\d+)(?::(.+))?$/);
  if (!match) return undefined;
  const composition = compositions.find((item) => item.id === Number(match[1]));
  if (!composition) return undefined;
  const suffix = match[2];
  if (!suffix)
    return {
      composition,
      variant: retainedBaseVariant(composition),
      currentSource: !composition.playback_revision,
    };
  if (suffix.startsWith('source:')) {
    const revision = suffix.slice('source:'.length);
    const variant = composition.variants?.find((item) => item.playback_revision === revision);
    return {
      composition,
      variant,
      currentSource: Boolean(variant || composition.playback_revision === revision),
    };
  }
  const variant = suffix.startsWith('variant:')
    ? composition.variants?.find((item) => item.id === suffix.slice('variant:'.length))
    : undefined;
  return {
    composition,
    variant,
    currentSource: Boolean(variant && !variant.playback_revision && !composition.playback_revision),
  };
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
