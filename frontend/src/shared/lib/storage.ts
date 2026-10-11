import { accountStorage } from '@shared/lib/accountScope';
export function readLocal<T>(key: string, fallback: T): T {
  try {
    return JSON.parse(accountStorage.getItem(key) || 'null') ?? fallback;
  } catch {
    return fallback;
  }
}
export function writeLocal(key: string, value: unknown) {
  try {
    accountStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* Storage unavailable. */
  }
}
