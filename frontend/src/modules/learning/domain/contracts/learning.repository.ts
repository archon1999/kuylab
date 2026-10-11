import type { Curriculum, QuizResult } from '../entities/learning.types.ts';

export interface LearningRepository {
  curriculum(id: number): Promise<Curriculum>;
  diagnostic(id: number, answers: Record<string, string>): Promise<void>;
  quiz(id: number, answers: Record<string, string>): Promise<QuizResult>;
  practice(
    id: number,
    value: { successful_repetitions: number; comfort: number; bpm: number; reflection: string },
  ): Promise<void>;
}
