import { useCallback, useEffect, useState, useSyncExternalStore } from 'react';
import { usePreferences } from '@shared/i18n';
import { CurriculumResource } from './CurriculumResource';
import { useLearningRepository } from './learning-provider';

export function useCurriculum(compositionId: number, enabled: boolean) {
  const { language } = usePreferences();
  const repository = useLearningRepository();
  const [resource] = useState(() => new CurriculumResource(repository));
  const snapshot = useSyncExternalStore(resource.subscribe, resource.getSnapshot);
  const key = compositionId + ':' + language + ':' + enabled;
  useEffect(() => {
    void resource.select(compositionId, language, enabled);
    return () => resource.cancel();
  }, [resource, compositionId, language, enabled]);
  const refresh = useCallback(() => resource.refresh(key), [resource, key]);
  return {
    data: snapshot.key === key ? snapshot.data : null,
    error: snapshot.key === key ? snapshot.error : '',
    loading: enabled && (snapshot.key !== key || snapshot.loading),
    refresh,
  };
}
