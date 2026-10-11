import { request } from '@shared/api/http';
import type { LearningRepository } from '../../domain';
import type { CurriculumDto, QuizResultDto } from '../dto';
import { mapCurriculum, mapQuizResult } from '../mappers';
export const createLearningRepository = (): LearningRepository => ({
  curriculum: async (id) =>
    mapCurriculum(await request<CurriculumDto>('compositions/' + id + '/curriculum/')),
  diagnostic: async (id, answers) => {
    await request('compositions/' + id + '/diagnostic/', 'POST', { answers });
  },
  quiz: async (id, answers) =>
    mapQuizResult(await request<QuizResultDto>('lessons/' + id + '/quiz/', 'POST', { answers })),
  practice: async (id, value) => {
    await request('lessons/' + id + '/practice/', 'POST', value);
  },
});
