export type { Arrangement, Composition, CompositionInput } from './entities/index.ts';
export type { RepertoireRepository } from './contracts/index.ts';
export {
  demoComposition,
  validateCompositionInput,
  classifySource,
  hasMidiSource,
} from './repertoire.logic.ts';
