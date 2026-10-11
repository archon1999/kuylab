export type PreferenceChanges = { language?: 'uz' | 'ru' | 'en'; theme?: 'light' | 'dark' };
export class PreferenceSynchronizer {
  private changes: PreferenceChanges;
  private generation = 0;
  private running: Promise<void> | null = null;
  private save: (changes: PreferenceChanges) => Promise<void>;
  private store: (changes: PreferenceChanges) => void;
  constructor(
    save: (changes: PreferenceChanges) => Promise<void>,
    store: (changes: PreferenceChanges) => void,
    initial: PreferenceChanges = {},
  ) {
    this.save = save;
    this.store = store;
    this.changes = { ...initial };
  }
  canHydrate() {
    return this.generation === 0 && Object.keys(this.changes).length === 0;
  }
  pending() {
    return { ...this.changes };
  }
  choose(changes: PreferenceChanges) {
    this.generation++;
    this.changes = { ...this.changes, ...changes };
    this.store(this.changes);
    return this.flush();
  }
  flush(): Promise<void> {
    if (this.running) return this.running;
    this.running = this.drain().finally(() => {
      this.running = null;
    });
    return this.running;
  }
  private async drain() {
    while (Object.keys(this.changes).length) {
      const sent = { ...this.changes };
      try {
        await this.save(sent);
      } catch {
        return;
      }
      for (const field of Object.keys(sent) as (keyof PreferenceChanges)[])
        if (this.changes[field] === sent[field]) delete this.changes[field];
      this.store(this.changes);
    }
  }
}
