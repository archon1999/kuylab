import type { TheoryChallenge } from '../../domain/theoryChallenges';
export type StudyItemDto = {
  challenges?: TheoryChallenge[];
  id: string;
  kind: 'lesson' | 'exercise' | 'theory' | 'journey';
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
  source_speed_percent?: number;
  tempo_bpm?: number;
  composition_variant_id?: string;
};

export type CompositionDto = {
  difficulty?: number;
  collection?: string;
  preview_start_seconds?: number;
  id: number;
  slug: string;
  title: string;
  subtitle: string;
  composer: string;
  score_id: number;
  duration_seconds: number;
  lesson_ids: string[];
  variants?: {
    difficulty?: number;
    id: string;
    title: string;
    description: string;
    score_id: number;
    duration_seconds: number;
  }[];
  default_variant_id?: string;
  readable_holds?: boolean;
};

export type StudioCatalogDto = {
  journeys?: StudyItemDto[];
  revision: string;
  compositions: CompositionDto[];
  lessons: StudyItemDto[];
  exercises: StudyItemDto[];
  theory: StudyItemDto[];
  categories: { id: string; label: string }[];
  goals: { id: string; label: string }[];
};
