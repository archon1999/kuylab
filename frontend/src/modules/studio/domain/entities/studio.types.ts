import type { TheoryChallenge } from '../theoryChallenges';
export type StudyItem = {
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
  stages?: StudyStage[];
  source?: { start_seconds: number; end_seconds: number; transformation: string };
};

export type StudyStage = {
  id: string;
  title: string;
  instruction: string;
  score_id: number;
  source_speed_percent?: number;
  tempo_bpm?: number;
  composition_variant_id?: string;
};

export type CompositionVariant = {
  id: string;
  title: string;
  description: string;
  score_id: number;
  duration_seconds: number;
};

export type Composition = {
  id: number;
  slug: string;
  title: string;
  subtitle: string;
  composer: string;
  score_id: number;
  duration_seconds: number;
  lesson_ids: string[];
  variants?: CompositionVariant[];
  default_variant_id?: string;
  readable_holds?: boolean;
};

export type StudioCatalog = {
  journeys?: StudyItem[];
  revision: string;
  compositions: Composition[];
  lessons: StudyItem[];
  exercises: StudyItem[];
  theory: StudyItem[];
  categories: { id: string; label: string }[];
  goals: { id: string; label: string }[];
};

export type StudyFilter = {
  query: string;
  category: string;
  goal: string;
  level: string;
  favoritesOnly: boolean;
  status: StudyStatusFilter;
};

export type StudyStatus = 'learning' | 'struggling' | 'mastered';
export type StudyStatusFilter = StudyStatus | 'not_started' | '';
export type StudyProgressMap = Record<string, StudyStatus>;
