import { useEffect, type RefObject } from 'react';
import { useActivity } from '@modules/activity';

/** Opening a route alone is not study activity. A deliberate interaction or
 * reading scroll starts an untouched item after two visible seconds. */
export function useStudyEngagement(id: string, article: RefObject<HTMLElement | null>) {
  const { startStudy } = useActivity();
  useEffect(() => {
    const element = article.current;
    if (!element || !id) return;
    const main = element.closest('main');
    let initialScroll: number | null = null;
    // The route layout resets its scroll after child effects. Establish the
    // reading baseline on the next frame so that reset is not mistaken for study.
    const frame = requestAnimationFrame(() => {
      initialScroll = main?.scrollTop ?? window.scrollY;
    });
    const opened = performance.now();
    let pending: ReturnType<typeof setTimeout> | undefined;
    let done = false;
    const engage = () => {
      if (done || document.visibilityState !== 'visible') return;
      clearTimeout(pending);
      pending = setTimeout(
        () => {
          if (document.visibilityState !== 'visible') return;
          done = true;
          startStudy(id);
        },
        Math.max(0, 2000 - (performance.now() - opened)),
      );
    };
    const interact = (event: Event) => {
      const target = event.target as HTMLElement;
      if (target.closest('[data-study-progress]')) return;
      if (event.type === 'keydown') {
        const key = (event as KeyboardEvent).key;
        if (
          ![
            'Enter',
            ' ',
            'ArrowLeft',
            'ArrowRight',
            'ArrowDown',
            'ArrowUp',
            'PageDown',
            'PageUp',
          ].includes(key)
        )
          return;
      }
      engage();
    };
    const scroll = () => {
      if (
        initialScroll !== null &&
        Math.abs((main?.scrollTop ?? window.scrollY) - initialScroll) >= 80
      )
        engage();
    };
    element.addEventListener('click', interact);
    element.addEventListener('keydown', interact);
    (main || window).addEventListener('scroll', scroll, { passive: true });
    return () => {
      clearTimeout(pending);
      cancelAnimationFrame(frame);
      element.removeEventListener('click', interact);
      element.removeEventListener('keydown', interact);
      (main || window).removeEventListener('scroll', scroll);
    };
  }, [id, article, startStudy]);
}
