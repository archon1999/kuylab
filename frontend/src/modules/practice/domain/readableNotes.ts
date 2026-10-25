import type { StudioNote } from './entities/studio-transport.types.ts';

/** Reading aid for a reviewed source whose long holds obscure later attacks.
 * These are display lengths, never reconstructed finger releases or audio gates.
 * Group near-simultaneous chord attacks before finding the next same-hand group.
 */
export function readableRollNotes(notes: StudioNote[]): StudioNote[] {
  const lengths = new Map<string, number>();
  for (const hand of ['left', 'right'] as const) {
    const groups: StudioNote[][] = [];
    for (const note of notes
      .filter((value) => value.hand === hand)
      .sort((a, b) => a.onset - b.onset)) {
      const last = groups[groups.length - 1];
      if (last && note.onset - last[0].onset <= 0.045) last.push(note);
      else groups.push([note]);
    }
    for (let index = 0; index < groups.length - 1; index++) {
      const next = groups[index + 1][0].onset;
      for (const note of groups[index]) {
        const gap = next - note.onset;
        if (gap <= 0) continue;
        const length = Math.max(0.09, gap * 0.88);
        // Keep ordinary legato and all final holds. Only clearly overlapping
        // long blocks are abbreviated; the final group retains its real ending.
        if (note.duration > Math.max(0.4, gap * 1.4)) {
          lengths.set(note.id, Math.min(note.duration, length));
        }
      }
    }
  }
  return notes.map((note) =>
    lengths.has(note.id) ? { ...note, duration: lengths.get(note.id)! } : note,
  );
}
