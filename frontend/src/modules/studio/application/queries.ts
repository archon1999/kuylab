import type { Score } from '@modules/practice';
import { usePreferences } from '@shared/i18n';
import { useEffect, useState } from 'react';
import { useStudio } from './studio-provider';

export function useStudyScore(id: number | null | undefined) {
  const { repository } = useStudio();
  const { language } = usePreferences();
  const [state, setState] = useState<{ score: Score | null; error: string; loading: boolean }>({
    score: null,
    error: '',
    loading: !!id,
  });
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    let active = true;
    setState({ score: null, error: '', loading: !!id });
    if (id)
      void repository.score(id).then(
        (score) => {
          if (active) setState({ score, error: '', loading: false });
        },
        (reason) => {
          if (active)
            setState({
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
  return { ...state, reload: () => setRevision((value) => value + 1) };
}
