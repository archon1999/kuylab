import { flushSync } from 'react-dom';

let active: ViewTransition | undefined;
let revision = 0;

/** One crossfade includes the canvas, CSS surfaces and portaled MUI controls. */
export function transitionColorMode(update: () => void) {
  const ticket = ++revision;
  active?.skipTransition();
  if (
    !document.startViewTransition ||
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  ) {
    active = undefined;
    delete document.documentElement.dataset.themeTransition;
    update();
    return;
  }
  document.documentElement.dataset.themeTransition = 'true';
  const transition = document.startViewTransition(() => {
    if (ticket === revision) flushSync(update);
  });
  active = transition;
  void transition.ready.catch(() => undefined);
  void transition.finished
    .catch(() => undefined)
    .finally(() => {
      if (active === transition) {
        active = undefined;
        delete document.documentElement.dataset.themeTransition;
      }
    });
}
