export const MAX_SESSION_SECONDS = 14_400;

/** Elapsed time is measured from a monotonic clock, not the number of browser timer callbacks. */
export class SessionClock {
  private accumulatedMs = 0;
  private startedAt: number | null = null;
  private now: () => number;

  constructor(now: () => number) {
    this.now = now;
  }

  seconds() {
    const active = this.startedAt === null ? 0 : Math.max(0, this.now() - this.startedAt);
    return Math.min(MAX_SESSION_SECONDS, Math.floor((this.accumulatedMs + active) / 1000));
  }

  start() {
    if (this.startedAt === null) this.startedAt = this.now();
  }

  pause() {
    if (this.startedAt !== null) {
      this.accumulatedMs += Math.max(0, this.now() - this.startedAt);
      this.startedAt = null;
    }
    return this.seconds();
  }

  reset(seconds = 0) {
    this.accumulatedMs =
      Math.max(0, Math.min(MAX_SESSION_SECONDS, Number.isFinite(seconds) ? seconds : 0)) * 1000;
    if (this.startedAt !== null) this.startedAt = this.now();
  }
}
