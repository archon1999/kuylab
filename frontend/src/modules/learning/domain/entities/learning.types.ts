export type Choice = { id: string; label: string };

export type Question = {
  id: string;
  prompt?: string;
  title?: string;
  kind?: string;
  choices: Choice[];
};

export type Progress = {
  quiz_score: number | null;
  quiz_passed: boolean;
  drill_completed: boolean;
  successful_repetitions: number;
  comfort: number | null;
  review_due_at: string | null;
  status: string;
  review_count: number;
};

export type Lesson = {
  id: number;
  arrangement_id: number;
  code: string;
  title: string;
  skill: string;
  summary: string;
  minutes: number;
  context: string;
  explanation: { title: string; text: string }[];
  steps: { title: string; instruction: string }[];
  exercise?: {
    label: string;
    original: boolean;
    notes?: string | string[];
    counting?: string | string[];
    bpm?: number;
    beat_unit?: string;
    score_url?: string;
    tempo_choice?: { bpm: number; beat_unit: string };
  };
  transfer?: string;
  practice_link?: string;
  sources?: { title: string; url: string }[];
  success_criterion: string;
  quiz: { questions: Question[] };
  progress: Progress;
};

export type Plan = {
  minutes: number;
  items: {
    kind: string;
    lesson_id?: number;
    title: string;
    minutes: number;
    reason: string;
    practice_link?: string;
  }[];
  basis: string | string[];
  source_notice?: string;
};

export type Curriculum = {
  composition_id: number;
  arrangement_id: number;
  readiness: string;
  source_notice: string;
  score_binding?: { score_id: number };
  skills: {
    id: string;
    label: string;
    score: number | null;
    knowledge_score: number | null;
    self_reported_score: number | null;
    evidence: string;
  }[];
  diagnostic: { questions: Question[]; latest_attempt: unknown };
  lessons: Lesson[];
  adaptive_plan: Plan;
};

export type QuizResult = {
  score: number;
  passed: boolean;
  feedback: { id: string; correct: boolean; correct_choice: string; explanation: string }[];
  progress: Progress;
  adaptive_plan: Plan;
};
