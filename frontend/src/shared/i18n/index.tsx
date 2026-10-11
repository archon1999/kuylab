import { accountStorage } from '@shared/lib/accountScope';
import { createContext, useCallback, useContext } from 'react';
import { uiMessages } from './uiMessages';
export type InterfaceLanguage = 'uz' | 'ru' | 'en';
export type ColorMode = 'light' | 'dark';
const validLanguage = (value: unknown): value is InterfaceLanguage =>
  ['uz', 'ru', 'en'].includes(String(value));
const validMode = (value: unknown): value is ColorMode => ['light', 'dark'].includes(String(value));
function stored(key: string) {
  try {
    return accountStorage.getItem(key);
  } catch {
    return null;
  }
}
export function getInterfaceLanguage(): InterfaceLanguage {
  const value = stored('kuylab-language');
  return validLanguage(value) ? value : 'uz';
}
const templatePatterns = Object.entries(uiMessages)
  .filter(([source]) => /\{\d+\}/.test(source))
  .map(([source, translation]) => {
    const indices: number[] = [];
    const escaped = source
      .split(/(\{\d+\})/g)
      .map((part) => {
        const match = part.match(/^\{(\d+)\}$/);
        if (match) {
          indices.push(Number(match[1]));
          return '(.*?)';
        }
        return part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      })
      .join('');
    return { regex: new RegExp(`^${escaped}$`), indices, translation };
  });
export function translate(
  value: unknown,
  values: unknown[] = [],
  language: InterfaceLanguage = getInterfaceLanguage(),
): string {
  const source = String(value ?? '');
  const key = source.replace(/\s+/g, ' ').trim();
  let entry = uiMessages[key] || uiMessages[key.toLocaleLowerCase()];
  if (!entry && language !== 'uz')
    for (const pattern of templatePatterns) {
      const match = key.match(pattern.regex);
      if (match) {
        entry = pattern.translation;
        values = [...values];
        pattern.indices.forEach((index, position) => {
          values[index] = match[position + 1];
        });
        break;
      }
    }
  let result = language === 'uz' ? key : entry?.[language] || key;
  if (key && key === key.toLocaleUpperCase() && entry && key !== key.toLocaleLowerCase())
    result = result.toLocaleUpperCase(language);
  result = result.replace(/\{(\d+)\}/g, (_, index: string) => String(values[Number(index)] ?? ''));
  return `${source.startsWith(' ') ? ' ' : ''}${result}${source.endsWith(' ') ? ' ' : ''}`;
}

export type PreferenceContext = {
  language: InterfaceLanguage;
  mode: ColorMode;
  setLanguage: (language: InterfaceLanguage) => void;
  toggleMode: () => void;
  hydrate: (language: unknown, mode: unknown) => void;
};
export const PreferenceContext = createContext<PreferenceContext | null>(null);
export function usePreferences() {
  const preferences = useContext(PreferenceContext);
  if (!preferences) throw new Error('PreferencesProvider is required.');
  return preferences;
}
export function useTranslation() {
  const { language } = usePreferences();
  return useCallback(
    (value: unknown, values: unknown[] = []) => translate(value, values, language),
    [language],
  );
}
