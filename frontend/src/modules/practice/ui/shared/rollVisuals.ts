/** Visual effects never change source pitches, timing, or audio velocity. */
export function velocityStrength(velocity: number) {
  return Math.max(0, Math.min(127, Number.isFinite(velocity) ? velocity : 85)) / 127;
}

export function brighten(color: string, amount: number) {
  const factor = Math.max(0, Math.min(1, amount));
  return `#${[1, 3, 5]
    .map((start) => {
      const value = parseInt(color.slice(start, start + 2), 16);
      return Math.round(value + (255 - value) * factor)
        .toString(16)
        .padStart(2, '0');
    })
    .join('')}`;
}

/** Lift saturation and lightness without washing the chosen hand color into grey. */
function luminousColor(color: string, lift: number, dark: boolean) {
  const [r, g, b] = [1, 3, 5].map((start) => parseInt(color.slice(start, start + 2), 16) / 255);
  const high = Math.max(r, g, b),
    low = Math.min(r, g, b),
    delta = high - low;
  const lightness = (high + low) / 2;
  let hue = !delta
    ? 0
    : high === r
      ? ((g - b) / delta + 6) % 6
      : high === g
        ? (b - r) / delta + 2
        : (r - g) / delta + 4;
  hue *= 60;
  // Cool blue highlights toward cyan; rose highlights toward lilac.
  if (dark && hue >= 180 && hue <= 250) hue -= lift * 55;
  if (dark && hue >= 290) hue -= lift * 35;
  const saturation = delta
    ? Math.min(1, delta / (1 - Math.abs(2 * lightness - 1)) + (dark ? 0.16 : 0.06))
    : 0;
  const light = Math.min(0.9, lightness + lift);
  const chroma = (1 - Math.abs(2 * light - 1)) * saturation;
  const x = chroma * (1 - Math.abs(((hue / 60) % 2) - 1));
  const channels =
    hue < 60
      ? [chroma, x, 0]
      : hue < 120
        ? [x, chroma, 0]
        : hue < 180
          ? [0, chroma, x]
          : hue < 240
            ? [0, x, chroma]
            : hue < 300
              ? [x, 0, chroma]
              : [chroma, 0, x];
  return (
    '#' +
    channels
      .map((value) =>
        Math.round((value + light - chroma / 2) * 255)
          .toString(16)
          .padStart(2, '0'),
      )
      .join('')
  );
}

export function noteShading(color: string, velocity: number, enabled: boolean, dark = false) {
  const strength = enabled ? velocityStrength(velocity) : 0.7;
  return {
    top: luminousColor(color, (dark ? 0.16 : 0.1) + strength * 0.09, dark),
    bottom: luminousColor(color, (dark ? 0.025 : 0) + strength * 0.035, dark),
    opacity: enabled ? 0.9 + strength * 0.1 : 1,
    strength,
  };
}

export function allowsStrikeEffects(playing: boolean, enabled: boolean, reducedMotion: boolean) {
  return playing && enabled && !reducedMotion;
}

export function isContinuousStep(previous: number, position: number) {
  const distance = position - previous;
  return distance > 0 && distance <= 0.25;
}

export type StrikeParticle = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  born: number;
  life: number;
  radius: number;
  color: string;
};

/** A reusable ring buffer bounds both memory and draw work, even for dense chords. */
export class StrikeParticlePool {
  readonly particles: StrikeParticle[];
  private cursor = 0;
  constructor(capacity = 144) {
    const count = Math.max(
      1,
      Math.min(192, Math.floor(Number.isFinite(capacity) ? capacity : 144)),
    );
    this.particles = Array.from({ length: count }, () => ({
      x: 0,
      y: 0,
      vx: 0,
      vy: 0,
      born: -1,
      life: 0,
      radius: 0,
      color: '#ffffff',
    }));
  }
  clear() {
    for (const particle of this.particles) particle.life = 0;
  }
  hasActive(now: number) {
    return this.particles.some(
      (particle) => particle.life > 0 && now - particle.born < particle.life,
    );
  }
  emit(x: number, y: number, color: string, velocity: number, now: number, keyWidth: number) {
    const strength = velocityStrength(velocity);
    const count = 4 + Math.round(strength * 4);
    for (let index = 0; index < count; index++) {
      const particle = this.particles[this.cursor];
      this.cursor = (this.cursor + 1) % this.particles.length;
      const spread = (index / Math.max(1, count - 1) - 0.5) * 2;
      particle.x = x + spread * Math.min(8, keyWidth * 0.3);
      particle.y = y - 2;
      particle.vx = spread * (11 + strength * 17);
      particle.vy = -(23 + strength * 34 + (index % 3) * 9);
      particle.born = now;
      particle.life = 0.48 + strength * 0.25 + (index % 2) * 0.08;
      particle.radius = 1.0 + strength * 1.0 + (index % 3) * 0.35;
      particle.color = color;
    }
  }
}
