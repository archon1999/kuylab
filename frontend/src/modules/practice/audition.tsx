import { useState } from 'react';
import { createSampledPiano } from './data-access/adapters/sampled-piano.adapter';
import { useAudition } from './application/useAudition';
export function usePianoAudition() {
  const [audio] = useState(createSampledPiano);
  return useAudition(audio);
}
