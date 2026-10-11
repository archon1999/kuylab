import type { Score } from '@modules/practice';
import { request } from '@shared/api/http';
import type { StudioRepository } from '../../domain';
import type { StudioCatalogDto } from '../dto';
import { mapStudioCatalog } from '../mappers';
export function createStudioRepository(): StudioRepository {
  return {
    catalog: async () => mapStudioCatalog(await request<StudioCatalogDto>('studio/catalog/')),
    score: (id) => request<Score>(`scores/${id}/`),
  };
}
