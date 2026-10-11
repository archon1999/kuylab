import type { Composition, CompositionInput } from '../entities/repertoire.types.ts';

export interface RepertoireRepository {
  list(): Promise<Composition[]>;
  add(input: CompositionInput): Promise<Composition>;
}
