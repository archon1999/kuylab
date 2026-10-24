import { useEffect, useMemo, useState } from 'react';
import { createSampledPiano } from './data-access/adapters/sampled-piano.adapter';
import { createStudioPreferences } from './data-access/repository/studio-preferences.repository.impl';
import StudioPlayerView from './ui/shared/StudioPlayerView';
import type { StudioPlayerProps } from './application/useStudioPlayer';

export function StudioPlayer(props: StudioPlayerProps) {
  const [audio] = useState(createSampledPiano);
  const preferences = useMemo(
    () => createStudioPreferences(undefined, props.contextId || 'score:' + props.score.id),
    [props.contextId, props.score.id],
  );
  useEffect(() => () => audio.close(), [audio]);
  return <StudioPlayerView {...props} audio={audio} preferences={preferences} />;
}
