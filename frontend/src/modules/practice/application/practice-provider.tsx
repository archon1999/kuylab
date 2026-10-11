import { createContext, useContext, useState } from 'react';
import type { MidiInputPort, PlaybackAudioPort } from '../domain/contracts/playback.ports';
import type { ScoreRepository } from '../domain/contracts/score.repository';
type Ports = {
  repository: ScoreRepository;
  audio: PlaybackAudioPort;
  midi: MidiInputPort;
};
const Context = createContext<Ports | null>(null);
export function PracticeProvider({
  repository,
  createAudio,
  createMidi,
  children,
}: {
  repository: ScoreRepository;
  createAudio: () => PlaybackAudioPort;
  createMidi: () => MidiInputPort;
  children: React.ReactNode;
}) {
  const [audio] = useState(createAudio);
  const [midi] = useState(createMidi);
  return <Context.Provider value={{ repository, audio, midi }}>{children}</Context.Provider>;
}
export function usePracticePorts() {
  const ports = useContext(Context);
  if (!ports) throw new Error('PracticeProvider required');
  return ports;
}
