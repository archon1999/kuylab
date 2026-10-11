import type { PersonalState, ActivitySession, ActivityStats } from './entities/activity.types.ts';

export const emptyPersonal: PersonalState = {
  progress: {},
  lastStages: {},
  favorites: [],
  recents: [],
  positions: {},
};

export function tashkentDate(epoch: number): string {
  return new Date(epoch + 5 * 3600000).toISOString().slice(0, 10);
}

/** Pure elapsed clock. Visibility/player state and a cross-tab lease are supplied by the host. */
export class ActivityClock {
  private last: number;
  private remainder = 0;
  private active = false;
  private content: string | null = null;
  readonly session: ActivitySession;
  constructor(session: ActivitySession, now: number) {
    this.session = structuredClone(session);
    this.last = now;
  }
  advance(now: number, wallTime: number, active: boolean, content: string | null) {
    const elapsed = Math.max(0, now - this.last) / 1000;
    this.last = now;
    if (this.active) {
      this.remainder += elapsed;
      const whole = Math.min(Math.floor(this.remainder), 86400 - this.session.seconds);
      this.remainder -= whole;
      if (whole > 0) {
        this.session.seconds += whole;
        if (this.content)
          this.session.contentSeconds[this.content] =
            (this.session.contentSeconds[this.content] || 0) + whole;
        // Allocate elapsed seconds across the local midnight boundary, including background playback.
        let cursor = wallTime - whole * 1000;
        let remaining = whole;
        while (remaining > 0) {
          const day = tashkentDate(cursor);
          const nextMidnight = Date.parse(day + 'T00:00:00+05:00') + 86400000;
          const count = Math.min(remaining, Math.max(1, Math.ceil((nextMidnight - cursor) / 1000)));
          this.session.daySeconds[day] = (this.session.daySeconds[day] || 0) + count;
          cursor += count * 1000;
          remaining -= count;
        }
      }
    }
    this.active = active;
    this.content = content;
    return this.session;
  }
}

export function mergeVisits(...lists: ActivitySession[][]): ActivitySession[] {
  const records = new Map<string, ActivitySession>();
  for (const list of lists)
    for (const visit of list) {
      if (visit.seconds < 300 || !Number.isFinite(visit.seconds)) continue;
      const previous = records.get(visit.id);
      if (!previous || visit.seconds > previous.seconds) records.set(visit.id, visit);
    }
  return [...records.values()].sort((a, b) => b.startedAt.localeCompare(a.startedAt));
}

export function activityStats(visits: ActivitySession[], now: number): ActivityStats {
  const days = new Map<string, number>();
  const content = new Map<string, number>();
  let totalSeconds = 0;
  for (const visit of mergeVisits(visits)) {
    totalSeconds += visit.seconds;
    for (const [date, seconds] of Object.entries(visit.daySeconds))
      days.set(date, (days.get(date) || 0) + seconds);
    for (const [id, seconds] of Object.entries(visit.contentSeconds))
      content.set(id, (content.get(id) || 0) + seconds);
  }
  const today = tashkentDate(now);
  const dayOfWeek = new Date(today + 'T00:00:00Z').getUTCDay();
  const weekStart = new Date(Date.parse(today) - ((dayOfWeek + 6) % 7) * 86400000)
    .toISOString()
    .slice(0, 10);
  return {
    totalSeconds,
    weekSeconds: [...days].reduce(
      (sum, [day, seconds]) => sum + (day >= weekStart && day <= today ? seconds : 0),
      0,
    ),
    activeDays: days.size,
    days: Array.from({ length: 28 }, (_, index) => {
      const date = tashkentDate(now - (27 - index) * 86400000);
      return { date, seconds: days.get(date) || 0 };
    }),
    content: [...content]
      .map(([id, seconds]) => ({ id, seconds }))
      .sort((a, b) => b.seconds - a.seconds),
  };
}
