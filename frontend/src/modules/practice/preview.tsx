import { useEffect, useMemo, useState } from 'react';
import { createSampledPiano } from './data-access/adapters/sampled-piano.adapter';
import { createStudioPreferences } from './data-access/repository/studio-preferences.repository.impl';
import { useStudioPreferences } from './application/useStudioPreferences';
import { PreviewPlayback } from './application/previewPlayback';
import PianoRollPreviewView from './ui/shared/PianoRollPreview';
import type { StudioNote } from './domain/studioTransport';

export type PianoRollPreviewProps = {
  notes: StudioNote[];
  duration: number;
  active: boolean;
  label: string;
  compactHolds?: boolean;
};

export function PianoRollPreview(props: PianoRollPreviewProps) {
  const [audio] = useState(createSampledPiano);
  const [preferences] = useState(createStudioPreferences);
  const { preferences: settings } = useStudioPreferences(preferences, false);
  const controller = useMemo(
    () => new PreviewPlayback(props.notes, props.duration, audio, (state) => setPlayback(state)),
    [props.notes, props.duration, audio],
  );
  const [playback, setPlayback] = useState(() => controller.snapshot());
  useEffect(() => {
    controller.settings(settings);
  }, [controller, settings]);
  useEffect(() => {
    setPlayback(controller.snapshot());
    const visibility = () => {
      if (document.hidden) controller.pause();
    };
    document.addEventListener('visibilitychange', visibility);
    return () => {
      document.removeEventListener('visibilitychange', visibility);
      controller.dispose();
    };
  }, [controller]);
  useEffect(() => {
    if (!props.active) controller.pause();
  }, [controller, props.active]);
  useEffect(() => {
    if (!playback.playing) return;
    const timer = setInterval(() => controller.tick(), 25);
    return () => clearInterval(timer);
  }, [controller, playback.playing]);
  return (
    <PianoRollPreviewView
      {...props}
      playback={playback}
      settings={settings}
      onToggle={() => {
        void controller.toggle(settings);
      }}
    />
  );
}
