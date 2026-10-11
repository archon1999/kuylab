import type { Curriculum, QuizResult } from '../../domain/entities/learning.types.ts';
import type { CurriculumDto, QuizResultDto } from '../dto/learning.dto.ts';
export const mapCurriculum = (dto: CurriculumDto): Curriculum => structuredClone(dto);
export const mapQuizResult = (dto: QuizResultDto): QuizResult => structuredClone(dto);
