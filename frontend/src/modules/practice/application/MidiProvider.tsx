import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import type { MidiConnectionPort } from '../domain/contracts/midi-connection.port';
import type { StudioAudioPort } from '../domain/contracts/studio-audio.port';
import type { StudioPreferencePort } from '../domain/studioPreferences';
import { useStudioPreferences } from './useStudioPreferences';
import { createMidiPiano, initialMidiPianoState, type MidiSound } from './midiPiano';

type MidiContextValue = ReturnType<typeof useMidiController>;
const Context = createContext<MidiContextValue | null>(null);
function useMidiController(
  port: MidiConnectionPort,
  audio: StudioAudioPort,
  preferences: StudioPreferencePort,
) {
  const [state, setState] = useState(() => initialMidiPianoState(port));
  const [controller] = useState(() => createMidiPiano(port, audio, setState));
  const { preferences: settings, update } = useStudioPreferences(preferences);
  const [open, setOpen] = useState(false);
  useEffect(() => controller.setSound(settings.midiSound), [controller, settings.midiSound]);
  useEffect(
    () => controller.setLevels(settings.volume, settings.reverb),
    [controller, settings.volume, settings.reverb],
  );
  useEffect(() => {
    const active = () => controller.setActive(!document.hidden && document.hasFocus());
    active();
    window.addEventListener('focus', active);
    window.addEventListener('blur', active);
    document.addEventListener('visibilitychange', active);
    return () => {
      window.removeEventListener('focus', active);
      window.removeEventListener('blur', active);
      document.removeEventListener('visibilitychange', active);
      controller.close();
    };
  }, [controller]);
  const actions = useMemo(
    () => ({
      connect: controller.connect,
      disconnect: controller.disconnect,
      select: controller.select,
      subscribe: controller.subscribe,
      stop: controller.stop,
      setSound(value: MidiSound) {
        controller.setSound(value);
        update('midiSound', value);
      },
      show: () => setOpen(true),
      hide: () => setOpen(false),
    }),
    [controller, update],
  );
  return { ...state, ...actions, sound: settings.midiSound, open };
}
export function MidiProviderWithPorts({
  port,
  audio,
  preferences,
  children,
}: {
  port: MidiConnectionPort;
  audio: StudioAudioPort;
  preferences: StudioPreferencePort;
  children: ReactNode;
}) {
  const value = useMidiController(port, audio, preferences);
  return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function useMidi() {
  const value = useContext(Context);
  if (!value) throw new Error('MidiProvider required');
  return value;
}
