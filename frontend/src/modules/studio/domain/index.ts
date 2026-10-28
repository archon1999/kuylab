export type {
  StudyItem,
  StudyStage,
  Composition,
  CompositionVariant,
  CompositionPreview,
  CompositionFilter,
  StudioCatalog,
  StudyFilter,
  StudyStatus,
  StudyStatusFilter,
  StudyProgressMap,
} from './entities/index.ts';
export type { StudioRepository } from './contracts/index.ts';
export { studyCountLabel } from './countLabels.ts';
export {
  selectStudyStage,
  selectCompositionVariant,
  compositionPlaybackContext,
  compositionPositionKeys,
  compositionResumePosition,
  studyMatchesPerformance,
  compositionNotebookContext,
  compositionVariantStartPosition,
  compositionNoteTarget,
  emptyFilter,
  filterStudyItems,
  allStudyItems,
  studyProgress,
  filterByStudyStatus,
  summarizeStudyProgress,
  durationLabel,
} from './studio.logic.ts';
export { selectResumeStudy } from './resumeStudy.ts';
export {
  normalizeLibraryState,
  hasLibraryQuery,
  readLibraryQuery,
  libraryQuery,
} from './compositionLibraryState.ts';
export type { CompositionLibraryState } from './compositionLibraryState.ts';
export {
  emptyCompositionFilter,
  filterCompositions,
  compositionPage,
  libraryVariant,
  compositionGroups,
  compositionCollections,
  inferCompositionGroup,
  collectionForGroup,
  compositionCollectionLabel,
  compositionAttribution,
} from './compositionLibrary.ts';
