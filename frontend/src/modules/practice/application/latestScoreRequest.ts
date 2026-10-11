import type { Score } from '../domain/score.ts';

/** A slow response from an earlier source selection cannot replace the newer one. */
export function createLatestScoreRequest() {
  let generation = 0;
  return {
    invalidate() {
      generation++;
    },
    async run(load: () => Promise<Score>): Promise<Score | null> {
      const ticket = ++generation;
      try {
        const score = await load();
        return ticket === generation ? score : null;
      } catch (error) {
        if (ticket === generation) throw error;
        return null;
      }
    },
  };
}
