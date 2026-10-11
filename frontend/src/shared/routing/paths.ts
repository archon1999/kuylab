export const pagePaths = {
  dashboard: '/',
  library: '/compositions',
  detail: '/compositions',
  lesson: '/lessons',
  study: '/study',
  practice: '/practice',
  theory: '/theory',
  exercises: '/exercises',
  statistics: '/statistics',
  settings: '/settings',
  notFound: '/404',
} as const;
export type Page = keyof typeof pagePaths;

export function routePath(
  page: Page,
  values: URLSearchParams | Record<string, string | number | null> = {},
) {
  const params =
    values instanceof URLSearchParams
      ? values
      : new URLSearchParams(
          Object.entries(values)
            .filter(([, value]) => value !== null)
            .map(([key, value]) => [key, String(value)]),
        );
  const segment = (key: string) =>
    params.get(key) ? '/' + encodeURIComponent(params.get(key)!) : '';
  if (page === 'detail' || page === 'practice') return pagePaths[page] + segment('composition');
  if (page === 'study')
    return (
      pagePaths[page] +
      segment('item') +
      (params.get('stage')
        ? '/stages' + segment('stage')
        : params.get('example')
          ? '/examples' + segment('example')
          : '')
    );
  if (page === 'lesson') return pagePaths[page] + segment('lesson');
  return pagePaths[page];
}

export function parseRoute(pathname: string, search = '') {
  const params = new URLSearchParams();
  let page: Page = 'notFound';
  // Old bookmarks are accepted once and canonicalized by the browser adapter.
  const legacy = new URLSearchParams(search);
  const legacyPage = legacy.get('page');
  if (pathname === '/' && legacyPage && legacyPage in pagePaths) {
    legacy.forEach((value, key) => params.set(key, value));
    page = legacyPage as Page;
  } else {
    let parts: string[];
    try {
      parts = pathname.split('/').filter(Boolean).map(decodeURIComponent);
    } catch {
      return { page, params };
    }
    if (!parts.length) page = 'dashboard';
    else if (parts[0] === 'compositions' && parts.length <= 2) {
      page = parts[1] ? 'detail' : 'library';
      if (parts[1]) params.set('composition', parts[1]);
    } else if (parts[0] === 'practice' && parts.length <= 2) {
      page = 'practice';
      if (parts[1]) params.set('composition', parts[1]);
    } else if (
      parts[0] === 'study' &&
      (parts.length === 2 || (parts.length === 4 && ['stages', 'examples'].includes(parts[2])))
    ) {
      page = 'study';
      params.set('item', parts[1]);
      if (parts[3]) params.set(parts[2] === 'stages' ? 'stage' : 'example', parts[3]);
    } else if (parts[0] === 'lessons' && parts.length === 2) {
      page = 'lesson';
      params.set('lesson', parts[1]);
    } else if (parts.length === 1) {
      page =
        (Object.keys(pagePaths) as Page[]).find(
          (key) => !['study', 'lesson'].includes(key) && pagePaths[key] === '/' + parts[0],
        ) ?? 'notFound';
    }
  }
  params.set('page', page);
  return { page, params };
}
