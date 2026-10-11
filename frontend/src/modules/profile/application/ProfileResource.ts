import type { Profile, ProfileRepository, ProfileSnapshot } from '../domain/index.ts';

/** Fields and preferences share a write queue because they update the same profile. */
export function serializeProfileWrites(repository: ProfileRepository): ProfileRepository {
  let tail: Promise<unknown> = Promise.resolve();
  const enqueue = <T>(work: () => Promise<T>): Promise<T> => {
    const result = tail.then(work, work);
    tail = result.then(
      () => undefined,
      () => undefined,
    );
    return result;
  };
  return {
    get: () => repository.get(),
    save: (profile) => {
      const snapshot = { ...profile };
      return enqueue(() => repository.save(snapshot));
    },
    savePreferences: (changes) => {
      const snapshot = { ...changes };
      return enqueue(() => repository.savePreferences(snapshot));
    },
  };
}

type Snapshot = { profile: Profile; online: boolean; loading: boolean; error: string };
export class ProfileResource {
  private snapshot: Snapshot;
  private readGeneration = 0;
  private writeRevision = 0;
  private listeners = new Set<() => void>();
  private repository: ProfileRepository;
  private persist: (profile: Profile) => void;
  private hydrate: (snapshot: ProfileSnapshot) => void;
  constructor(
    repository: ProfileRepository,
    initial: Profile,
    persist: (profile: Profile) => void,
    hydrate: (snapshot: ProfileSnapshot) => void,
  ) {
    this.repository = repository;
    this.persist = persist;
    this.hydrate = hydrate;
    this.snapshot = { profile: initial, online: false, loading: true, error: '' };
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
    this.readGeneration++;
  }
  async reload() {
    const generation = ++this.readGeneration,
      revision = this.writeRevision;
    this.publish({ ...this.snapshot, loading: true, error: '' });
    try {
      const value = await this.repository.get();
      if (generation !== this.readGeneration) return;
      if (revision === this.writeRevision) {
        this.persist(value);
        this.hydrate(value);
      }
      this.publish({
        profile: revision === this.writeRevision ? value : this.snapshot.profile,
        online: true,
        loading: false,
        error: '',
      });
    } catch {
      if (generation === this.readGeneration)
        this.publish({
          ...this.snapshot,
          online: false,
          loading: false,
          error: 'Server ulanmagan. Lokal serverni ishga tushiring.',
        });
    }
  }
  async save(profile: Profile): Promise<Profile> {
    const revision = ++this.writeRevision;
    const saved = this.snapshot.online ? await this.repository.save(profile) : profile;
    if (revision === this.writeRevision) {
      this.persist(saved);
      this.publish({ ...this.snapshot, profile: saved, error: '' });
    }
    return saved;
  }
}
