import type { Score } from '@modules/practice';
import { usePreferences } from '@shared/i18n';
import { useEffect, useState } from 'react';
import { useStudio } from './studio-provider';

export function useStudyScore(id: number | null | undefined) {
  const { repository } = useStudio();
  const { language } = usePreferences();
  const [state, setState] = useState<{
    id: number | null | undefined;
    score: Score | null;
    error: string;
    loading: boolean;
  }>({
    id,
    score: null,
    error: '',
    loading: !!id,
  });
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    let active = true;
    setState({ id, score: null, error: '', loading: !!id });
    if (id)
      void repository.score(id).then(
        (score) => {
          if (active) setState({ id, score, error: '', loading: false });
        },
        (reason) => {
          if (active)
            setState({
              id,
              score: null,
              error: reason instanceof Error ? reason.message : 'Kontentni ochib bo‘lmadi.',
              loading: false,
            });
        },
      );
    return () => {
      active = false;
    };
  }, [repository, id, revision, language]);
  // Never mount the preceding variant under the new variant's context while
  // the effect starts its request. Late responses are discarded above too.
  return {
    ...(state.id === id ? state : { score: null, error: '', loading: !!id }),
    reload: () => setRevision((value) => value + 1),
  };
}
