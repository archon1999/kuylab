import type { Curriculum, LearningRepository } from '../domain/index.ts';

type Snapshot = { key: string; data: Curriculum | null; loading: boolean; error: string };

/** Every read belongs to one composition/language and one request generation. */
export class CurriculumResource {
  private snapshot: Snapshot = { key: '', data: null, loading: false, error: '' };
  private generation = 0;
  private listeners = new Set<() => void>();
  private selection: { id: number; language: string; enabled: boolean } | null = null;
  private repository: LearningRepository;
  constructor(repository: LearningRepository) {
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
    this.selection = null;
  }
  async select(id: number, language: string, enabled: boolean) {
    this.selection = { id, language, enabled };
    const key = `${id}:${language}:${enabled}`;
    const generation = ++this.generation;
    const retained = key === this.snapshot.key ? this.snapshot.data : null;
    if (!enabled) {
      this.publish({ key, data: null, loading: false, error: '' });
      return;
    }
    this.publish({ key, data: retained, loading: true, error: '' });
    try {
      const data = await this.repository.curriculum(id);
      if (generation === this.generation) this.publish({ key, data, loading: false, error: '' });
    } catch {
      if (generation === this.generation)
        this.publish({
          key,
          data: retained,
          loading: false,
          error: 'Darslar yuklanmadi. Serverga qayta ulanishni sinab ko‘ring.',
        });
    }
  }
  async refresh(_expectedKey: string) {
    if (!this.selection) return;
    const { id, language, enabled } = this.selection;
    await this.select(id, language, enabled);
  }
}
