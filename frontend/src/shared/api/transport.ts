import { accountId } from '../lib/accountScope.ts';
const invalidResponse = 'Server javobi noto‘g‘ri.';

function message(value: unknown): string {
  if (typeof value === 'string') return value.trim() || invalidResponse;
  if (Array.isArray(value)) return value.map(message).join(' ') || invalidResponse;
  if (value && typeof value === 'object')
    return (
      Object.entries(value)
        .map(([key, detail]) =>
          key === 'detail' || key === 'non_field_errors'
            ? message(detail)
            : `${key}: ${message(detail)}`,
        )
        .join(' ') || invalidResponse
    );
  return invalidResponse;
}

/** Bound stalled requests without automatically repeating a potentially successful write. */
export async function requestJson<T>(
  path: string,
  method = 'GET',
  body?: unknown,
  language = 'uz',
  timeoutMs = method === 'GET' ? 15_000 : 60_000,
): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  const multipart = body instanceof FormData;
  try {
    let response: Response;
    try {
      response = await fetch('/api/' + path, {
        method,
        credentials: 'same-origin',
        signal: controller.signal,
        headers: {
          Accept: 'application/json',
          ...(accountId() ? { 'X-KuyLab-User': String(accountId()) } : {}),
          ...(!['GET', 'HEAD'].includes(method)
            ? {
                'X-CSRFToken': decodeURIComponent(
                  (typeof document !== 'undefined' ? document.cookie : '').match(
                    /(?:^|; )kuylab_csrftoken=([^;]*)/,
                  )?.[1] ||
                    (typeof document !== 'undefined' ? document.cookie : '').match(
                      /(?:^|; )csrftoken=([^;]*)/,
                    )?.[1] ||
                    '',
                ),
              }
            : {}),
          'Accept-Language': language,
          ...(multipart || body === undefined ? {} : { 'Content-Type': 'application/json' }),
        },
        body: body === undefined ? undefined : multipart ? body : JSON.stringify(body),
      });
    } catch (error) {
      if (controller.signal.aborted) throw error;
      throw new Error('Server bilan bog‘lanib bo‘lmadi. Qayta urinib ko‘ring.');
    }
    if (response.status === 204) return undefined as T;
    let data: unknown;
    try {
      data = await response.json();
    } catch (error) {
      if (controller.signal.aborted) throw error;
      throw new Error(invalidResponse);
    }
    if (
      response.status === 401 ||
      (response.status === 403 &&
        (data as { detail?: string })?.detail === 'Authentication credentials were not provided.')
    )
      window.dispatchEvent(new Event('kuylab-session-expired'));
    if (!response.ok) throw new Error(message(data));
    return data as T;
  } catch (error) {
    if (controller.signal.aborted) {
      throw new Error(
        method === 'GET'
          ? 'Server javobi kutilganidan uzoq davom etdi. Qayta urinib ko‘ring.'
          : 'Server javobi kelmadi. Takror saqlashdan oldin natijani tekshiring.',
      );
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
