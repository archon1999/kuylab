import { getInterfaceLanguage, translate } from '@shared/i18n';
import { requestJson } from './transport';
import { cacheableContent, readContent, saveContent } from '@shared/offline/cache';

export async function request<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const language = getInterfaceLanguage();
  const offline = method === 'GET' && cacheableContent(path);
  if (offline && !navigator.onLine) {
    const cached = await readContent<T>(path, language);
    if (cached !== undefined) return cached;
  }
  try {
    const data = await requestJson<T>(path, method, body, language);
    if (offline) void saveContent(path, language, data);
    return data;
  } catch (error) {
    if (offline) {
      const cached = await readContent<T>(path, language);
      if (cached !== undefined) return cached;
    }
    throw new Error(translate(error instanceof Error ? error.message : 'Server javobi noto‘g‘ri.'));
  }
}
