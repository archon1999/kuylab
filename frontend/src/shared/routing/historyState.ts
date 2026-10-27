/** A canonical entry can intentionally have no query parameters. */
export function isCanonicalEntry(state: unknown, path: string) {
  return (
    !!state &&
    typeof state === 'object' &&
    (state as Record<string, unknown>).kuylabCanonicalPath === path
  );
}

export function canonicalEntryState(state: unknown, path: string) {
  return {
    ...(state && typeof state === 'object' ? state : {}),
    kuylabCanonicalPath: path,
  };
}
