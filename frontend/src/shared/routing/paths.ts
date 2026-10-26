export const pagePaths = {
  dashboard: '/studio',
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
const libraryQueryKeys = ['q', 'difficulty', 'collection', 'favorites', 'sort', 'p', 'size'];

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
  if (page === 'library') {
    const query = new URLSearchParams();
    for (const key of libraryQueryKeys) if (params.has(key)) query.set(key, params.get(key)!);
    return pagePaths.library + (query.size ? '?' + query.toString() : '');
  }
  const timestamp =
    params.has('at') &&
    Number.isFinite(Number(params.get('at'))) &&
    Number(params.get('at')) >= 0 &&
    Number(params.get('at')) <= 7200
      ? '?t=' + Number(params.get('at'))
      : '';
  if (page === 'detail')
    return (
      pagePaths.detail +
      (params.get('compositionSlug') ? segment('compositionSlug') : segment('composition'))
    );
  if (page === 'practice')
    return (
      pagePaths[page] +
      segment('composition') +
      (page === 'practice'
        ? (params.get('variant') ? '/variants' + segment('variant') : '') + timestamp
        : '')
    );
  if (page === 'study')
    return (
      pagePaths[page] +
      segment('item') +
      (params.get('stage')
        ? '/stages' + segment('stage')
        : params.get('example')
          ? '/examples' + segment('example')
          : '') +
      timestamp
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
  if (['/', '/studio'].includes(pathname) && legacyPage && legacyPage in pagePaths) {
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
      if (parts[1])
        params.set(/^\d+$/.test(parts[1]) ? 'composition' : 'compositionSlug', parts[1]);
    } else if (
      parts[0] === 'practice' &&
      (parts.length <= 2 || (parts.length === 4 && parts[2] === 'variants'))
    ) {
      page = 'practice';
      if (parts[1]) params.set('composition', parts[1]);
      if (parts[3]) params.set('variant', parts[3]);
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
  const at = legacy.get('t');
  if (page === 'library')
    for (const key of libraryQueryKeys) if (legacy.has(key)) params.set(key, legacy.get(key)!);
  if (
    ['practice', 'study'].includes(page) &&
    at !== null &&
    at.trim() &&
    Number.isFinite(Number(at)) &&
    Number(at) >= 0 &&
    Number(at) <= 7200
  )
    params.set('at', String(Number(at)));
  params.set('page', page);
  return { page, params };
}
