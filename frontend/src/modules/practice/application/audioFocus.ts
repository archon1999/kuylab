export class AudioFocus {
  private owner: symbol | null = null;
  private pause: (() => void) | null = null;
  claim(owner: symbol, pause: () => void) {
    if (this.owner !== owner) this.pause?.();
    this.owner = owner;
    this.pause = pause;
  }
  release(owner: symbol) {
    if (this.owner === owner) {
      this.owner = null;
      this.pause = null;
    }
  }
}
export const audioFocus = new AudioFocus();
