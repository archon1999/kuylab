import type { Score } from '@modules/practice';
import { request } from '@shared/api/http';
import type { StudioRepository, CompositionPreview } from '../../domain';
import type { StudioCatalogDto } from '../dto';
import { mapStudioCatalog } from '../mappers';
import { createLibraryStateRepository } from './library-state.repository';
export function createStudioRepository(): StudioRepository {
  const previews = new Map<string, Promise<CompositionPreview>>();
  const libraryState = createLibraryStateRepository();
  return {
    readLibraryState: libraryState.read,
    saveLibraryState: libraryState.write,
    catalog: async () => mapStudioCatalog(await request<StudioCatalogDto>('studio/catalog/')),
    score: (id) => request<Score>(`scores/${id}/`),
    preview: (id, variant) => {
      const key = `${id}:${variant || ''}`;
      let value = previews.get(key);
      if (!value) {
        value = request<CompositionPreview>(
          `studio/compositions/${id}/preview/${variant ? '?variant=' + encodeURIComponent(variant) : ''}`,
        ).catch((error: unknown) => {
          previews.delete(key);
          throw error;
        });
        previews.set(key, value);
      }
      return value;
    },
  };
}
