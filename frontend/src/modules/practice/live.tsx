import { useState } from 'react';
import { createSampledPiano } from './data-access/adapters/sampled-piano.adapter';
import type { StudioPreferences } from './domain/studioPreferences';
import { useLivePiano } from './application/useLivePiano';

export function useScreenPiano(settings: StudioPreferences) {
  const [audio] = useState(createSampledPiano);
  return useLivePiano(audio, settings);
}
