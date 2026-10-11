import { request } from '@shared/api/http';
import type { RepertoireRepository } from '../../domain';
import type { CompositionDto, CompositionListDto } from '../dto';
import { normalizeComposition } from '../mappers';
export const createRepertoireRepository = (): RepertoireRepository => ({
  async list() {
    const raw = await request<CompositionListDto>('compositions/');
    return (Array.isArray(raw) ? raw : raw.results).map(normalizeComposition);
  },
  async add(input) {
    return normalizeComposition(await request<CompositionDto>('compositions/', 'POST', input));
  },
});
