import { useState, type ReactNode } from 'react';
import { MidiProviderWithPorts } from './application/MidiProvider';
import { createWebMidiInput } from './data-access/adapters/web-midi.adapter';
import { createSampledPiano } from './data-access/adapters/sampled-piano.adapter';
import { createStudioPreferences } from './data-access/repository/studio-preferences.repository.impl';

export function MidiProvider({ children }: { children: ReactNode }) {
  const [ports] = useState(() => ({
    port: createWebMidiInput(),
    audio: createSampledPiano(),
    preferences: createStudioPreferences(),
  }));
  return <MidiProviderWithPorts {...ports}>{children}</MidiProviderWithPorts>;
}
