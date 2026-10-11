import {
  demoComposition,
  type Composition,
  type CompositionInput,
  type RepertoireRepository,
} from '../domain/index.ts';

type Snapshot = { compositions: Composition[]; mode: 'loading' | 'online' | 'demo'; error: string };
export class RepertoireResource {
  private snapshot: Snapshot = { compositions: [demoComposition], mode: 'loading', error: '' };
  private generation = 0;
  private listeners = new Set<() => void>();
  private repository: RepertoireRepository;
  constructor(repository: RepertoireRepository) {
    this.repository = repository;
  }
  getSnapshot = () => this.snapshot;
  subscribe = (listener: () => void) => {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  };
  private publish(snapshot: Snapshot) {
    this.snapshot = snapshot;
    this.listeners.forEach((listener) => listener());
  }
  cancel() {
    this.generation++;
  }
  async reload(quiet = false) {
    const generation = ++this.generation;
    if (!quiet) this.publish({ ...this.snapshot, mode: 'loading', error: '' });
    try {
      const compositions = await this.repository.list();
      if (generation === this.generation) this.publish({ compositions, mode: 'online', error: '' });
    } catch {
      if (generation === this.generation)
        this.publish({
          ...this.snapshot,
          mode: quiet && this.snapshot.mode === 'online' ? 'online' : 'demo',
          error: 'Server saqlay olmadi. Qayta urinib ko‘ring.',
        });
    }
  }
  async add(input: CompositionInput) {
    const value = await this.repository.add(input);
    this.cancel();
    this.publish({
      compositions: [...this.snapshot.compositions.filter((item) => item.id !== value.id), value],
      mode: 'online',
      error: '',
    });
    return value;
  }
}
