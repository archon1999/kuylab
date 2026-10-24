import { useSyncExternalStore } from 'react';
import { parseRoute, routePath, type Page } from './paths.ts';
export { routePath, type Page } from './paths.ts';
const initial = parseRoute(location.pathname, location.search);
if (location.search.includes('page='))
  history.replaceState({}, '', routePath(initial.page, initial.params));
const listeners = new Set<() => void>();
const notify = () => listeners.forEach((listener) => listener());
window.addEventListener('popstate', notify);
function visit(path: string) {
  if (location.pathname + location.search !== path) {
    history.pushState({}, '', path);
    notify();
  }
  // A new page or lesson passage starts at its heading, including reduced-motion users.
  window.scrollTo({ top: 0, behavior: 'instant' });
}
export function navigate(page: Page, values: Record<string, string | number | null> = {}) {
  const params = parseRoute(location.pathname, location.search).params;
  params.delete('at');
  params.set('page', page);
  if (page !== 'lesson') params.delete('lesson');
  if (page !== 'study') {
    params.delete('item');
    params.delete('stage');
    params.delete('example');
  }
  if (values.item && values.item !== params.get('item')) {
    params.delete('stage');
    params.delete('example');
  }
  if (page !== 'practice')
    for (const key of [
      'score',
      'section',
      'start_index',
      'end_index',
      'start_seconds',
      'end_seconds',
      'bpm',
      'beat_unit',
      'drill',
      'pdf',
      'pdf_page',
      'score_page',
      'bar_start',
      'bar_end',
    ])
      params.delete(key);
  for (const [key, value] of Object.entries(values))
    if (value === null) params.delete(key);
    else params.set(key, String(value));
  visit(routePath(page, params));
}
export function openPractice(composition?: number) {
  const values: Record<string, string | number | null> = {
    lesson: null,
    start_seconds: null,
    end_seconds: null,
    score: null,
    section: null,
    start_index: null,
    end_index: null,
    bpm: null,
    beat_unit: null,
    drill: null,
    pdf: null,
    pdf_page: null,
    score_page: null,
    bar_start: null,
    bar_end: null,
  };
  if (composition) values.composition = composition;
  navigate('practice', values);
}
export function followPractice(link?: string) {
  if (!link) {
    openPractice();
    return;
  }
  let url: URL;
  try {
    url = new URL(link, location.origin);
  } catch {
    return;
  }
  const route = parseRoute(url.pathname, url.search);
  if (url.origin !== location.origin || route.page !== 'practice') return;
  visit(routePath(route.page, route.params));
}
function positiveId(value: string | null, fallback: number) {
  const id = Number(value);
  return Number.isSafeInteger(id) && id > 0 ? id : fallback;
}
export function useRoute() {
  const search = useSyncExternalStore(
    (listener) => {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },
    () => location.pathname + location.search,
  );
  const url = new URL(search, location.origin);
  const { page, params } = parseRoute(url.pathname, url.search);
  return {
    page,
    params,
    compositionId: positiveId(params.get('composition'), 1),
    lessonId: positiveId(params.get('lesson'), 0),
  };
}
