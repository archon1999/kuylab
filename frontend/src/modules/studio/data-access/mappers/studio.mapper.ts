import type { StudioCatalog, StudyItem } from '../../domain/entities/studio.types.ts';
import type { StudioCatalogDto, StudyItemDto } from '../dto/studio.dto.ts';
export function mapStudyItem(dto: StudyItemDto): StudyItem {
  return {
    ...dto,
    goals: [...dto.goals],
    explanation: dto.explanation.map((section) => ({ ...section })),
    steps: dto.steps.map((step) => ({ ...step })),
    stages: dto.stages?.map((stage) => ({ ...stage })),
    source: dto.source ? { ...dto.source } : undefined,
    related_ids: dto.related_ids ? [...dto.related_ids] : undefined,
  };
}
export function mapStudioCatalog(dto: StudioCatalogDto): StudioCatalog {
  return {
    revision: dto.revision,
    compositions: dto.compositions.map((item) => ({ ...item, lesson_ids: [...item.lesson_ids] })),
    lessons: dto.lessons.map(mapStudyItem),
    exercises: dto.exercises.map(mapStudyItem),
    theory: dto.theory.map(mapStudyItem),
    categories: dto.categories.map((item) => ({ ...item })),
    goals: dto.goals.map((item) => ({ ...item })),
  };
}
