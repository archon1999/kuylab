import { classifySource } from '../../domain/repertoire.logic.ts';
import type { Arrangement, Composition } from '../../domain/entities/repertoire.types.ts';
import type { CompositionDto } from '../dto/repertoire.dto.ts';
export function normalizeComposition(raw: CompositionDto): Composition {
  const arrangement = raw.arrangement as Arrangement | undefined;
  return {
    ...raw,
    id: Number(raw.id),
    title: String(raw.title),
    composer: String(raw.composer || ''),
    source_url: arrangement?.source_url || String(raw.source_url || ''),
    source_type: 'link',
    arrangement_label: arrangement?.title || String(raw.arrangement_label || ''),
    source_status: classifySource(arrangement),
    arrangement,
  } as Composition;
}
