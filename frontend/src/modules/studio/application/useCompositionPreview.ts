import { useEffect, useState, type RefObject } from 'react';
import type { CompositionPreview } from '../domain';
import { useStudio } from './studio-provider';

/** Fetch only cards that enter the viewport; discard responses for old variants. */
export function useCompositionPreview(
  id: number,
  variant: string | undefined,
  target: RefObject<HTMLElement | null>,
) {
  const { repository } = useStudio();
  const [enabled, setEnabled] = useState(false);
  const [visible, setVisible] = useState(false);
  const [revision, setRevision] = useState(0);
  const key = `${id}:${variant || ''}`;
  const [state, setState] = useState<{
    key: string;
    data: CompositionPreview | null;
    error: boolean;
  }>({ key, data: null, error: false });
  useEffect(() => {
    if (!target.current) return;
    if (!('IntersectionObserver' in window)) {
      setEnabled(true);
      setVisible(true);
      return;
    }
    const observer = new IntersectionObserver(
      ([entry]) => {
        setVisible(entry.isIntersecting);
        if (entry.isIntersecting) setEnabled(true);
      },
      { threshold: 0.05 },
    );
    observer.observe(target.current);
    return () => observer.disconnect();
  }, [target]);
  useEffect(() => {
    if (!enabled) return;
    let active = true;
    setState({ key, data: null, error: false });
    void repository.preview(id, variant).then(
      (data) => {
        if (active) setState({ key, data, error: false });
      },
      () => {
        if (active) setState({ key, data: null, error: true });
      },
    );
    return () => {
      active = false;
    };
  }, [enabled, id, variant, key, revision, repository]);
  return {
    preview: state.key === key ? state.data : null,
    error: state.key === key && state.error,
    visible,
    reload: () => setRevision((value) => value + 1),
  };
}
