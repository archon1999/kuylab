import { scopedKey } from '../../../../shared/lib/accountScope.ts';
import {
  normalizeLibraryState,
  type CompositionLibraryState,
} from '../../domain/compositionLibraryState.ts';

type SessionStorage = {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
};
export function createLibraryStateRepository(storage?: SessionStorage) {
  const getStorage = () => storage || sessionStorage;
  return {
    read() {
      try {
        return normalizeLibraryState(
          JSON.parse(getStorage().getItem(scopedKey('composition-library-v1')) || 'null'),
        );
      } catch {
        return normalizeLibraryState(null);
      }
    },
    write(value: CompositionLibraryState) {
      try {
        getStorage().setItem(
          scopedKey('composition-library-v1'),
          JSON.stringify(normalizeLibraryState(value)),
        );
      } catch {
        /* URL state still works when tab storage is blocked. */
      }
    },
  };
}
