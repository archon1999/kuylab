import { useMemo } from 'react';
import { createStudioPreferences } from './data-access/repository/studio-preferences.repository.impl';
import PianoPageView from './ui/pages/PianoPage/PianoPageView';

export default function PianoPage() {
  const preferences = useMemo(() => createStudioPreferences(), []);
  return <PianoPageView preferences={preferences} />;
}
