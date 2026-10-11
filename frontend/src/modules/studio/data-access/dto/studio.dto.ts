export type StudyItemDto = {
  id: string;
  kind: 'lesson' | 'exercise' | 'theory';
  title: string;
  subtitle: string;
  category: string;
  goals: string[];
  level: 'easy' | 'intermediate' | 'advanced' | null;
  minutes: number;
  score_id: number | null;
  composition_id?: number;
  intro: string;
  explanation: { title: string; text: string }[];
  steps: { title: string; instruction: string }[];
  fingering?: string;
  related_ids?: string[];
  comparisons?: { id: string; title: string; instruction: string; score_id: number }[];
  ready_when?: string;
  stages?: StudyStageDto[];
  source?: { start_seconds: number; end_seconds: number; transformation: string };
};

export type StudyStageDto = {
  id: string;
  title: string;
  instruction: string;
  score_id: number;
  source_speed_percent: number;
};

export type CompositionDto = {
  id: number;
  slug: string;
  title: string;
  subtitle: string;
  composer: string;
  score_id: number;
  duration_seconds: number;
  lesson_ids: string[];
};

export type StudioCatalogDto = {
  revision: string;
  compositions: CompositionDto[];
  lessons: StudyItemDto[];
  exercises: StudyItemDto[];
  theory: StudyItemDto[];
  categories: { id: string; label: string }[];
  goals: { id: string; label: string }[];
};
