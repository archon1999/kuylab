import type { Arrangement, Composition, CompositionInput } from './entities/repertoire.types.ts';

export const demoComposition: Composition = {
  id: 1,
  title: "He's a Pirate",
  composer: 'Klaus Badelt · Hans Zimmer · Geoff Zanelli',
  source_url: 'https://bitmidi.com/pirates-of-the-caribbean-hes-a-pirate-3-mid',
  source_type: 'link',
  arrangement_label: 'BitMidi (3) · RH / LH',
  source_status: 'full_midi_ready',
  arrangement: {
    id: 0,
    title: "He's a Pirate · BitMidi (3)",
    source_url: 'https://bitmidi.com/pirates-of-the-caribbean-hes-a-pirate-3-mid',
    exact_version_confirmed: true,
    time_signature: '6/8',
    tempo_bpm: 200,
    tempo_beat_unit: 'quarter',
  },
};

export function validateCompositionInput(
  input: CompositionInput,
): Partial<Record<keyof CompositionInput, 'required' | 'too_long' | 'url'>> {
  const errors: Partial<Record<keyof CompositionInput, 'required' | 'too_long' | 'url'>> = {};
  if (!input.title.trim()) errors.title = 'required';
  else if (input.title.length > 160) errors.title = 'too_long';
  if (input.composer.length > 160) errors.composer = 'too_long';
  if (input.arrangement_title.length > 180) errors.arrangement_title = 'too_long';
  if (input.source_url.length > 1000) errors.source_url = 'too_long';
  else if (input.source_url.trim()) {
    try {
      if (!['http:', 'https:'].includes(new URL(input.source_url.trim()).protocol))
        errors.source_url = 'url';
    } catch {
      errors.source_url = 'url';
    }
  }
  return errors;
}

/** Completeness belongs to the current file, not an earlier arrangement source. */
export function classifySource(arrangement?: Arrangement): string {
  if (arrangement?.active_score_id) {
    if (arrangement.active_score_format === 'midi')
      return arrangement.active_score_completeness_verified_at
        ? 'full_midi_ready'
        : 'midi_uploaded';
    return 'score_uploaded';
  }
  return arrangement?.exact_version_confirmed ? 'source_selected' : 'unconfirmed';
}

export function hasMidiSource(composition: Composition): boolean {
  return (
    !!composition.arrangement?.active_score_id &&
    composition.arrangement.active_score_format === 'midi'
  );
}
