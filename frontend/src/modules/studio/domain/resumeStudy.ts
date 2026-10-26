import type { StudyItem, StudyProgressMap } from './entities/studio.types.ts';
import { studyProgress } from './studio.logic.ts';

/** Recent unfinished lessons take precedence; completed stages are not resumed. */
export function selectResumeStudy(
  items: StudyItem[],
  recents: { id: string }[],
  progress: StudyProgressMap,
  lastStages: Record<string, string>,
) {
  for (const recent of recents) {
    const item = items.find((candidate) => candidate.id === recent.id);
    if (!item || studyProgress(item, progress).state === 'mastered') continue;
    const stages = item.stages || [];
    const remembered = stages.find((stage) => stage.id === lastStages[item.id]);
    const stage =
      remembered && progress[remembered.id] !== 'mastered'
        ? remembered
        : stages.find((value) => ['learning', 'struggling'].includes(progress[value.id])) ||
          stages.find((value) => progress[value.id] !== 'mastered');
    return { item, stage, status: stage ? progress[stage.id] : progress[item.id] };
  }
  return null;
}
