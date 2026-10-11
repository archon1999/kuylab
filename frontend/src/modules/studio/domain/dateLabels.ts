const uzMonths = [
  'yanvar',
  'fevral',
  'mart',
  'aprel',
  'may',
  'iyun',
  'iyul',
  'avgust',
  'sentabr',
  'oktabr',
  'noyabr',
  'dekabr',
];
const uzWeekdays = ['Yak', 'Dush', 'Sesh', 'Chor', 'Pay', 'Jum', 'Shan'];

/** Keep dates readable even in browsers with incomplete Uzbek Intl data. */
export function formatStudioDate(value: string, language: 'uz' | 'ru' | 'en', short = false) {
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return '—';
  if (language === 'uz')
    return short ? uzWeekdays[date.getDay()] : `${date.getDate()}-${uzMonths[date.getMonth()]}`;
  return date.toLocaleDateString(
    language === 'ru' ? 'ru-RU' : 'en-GB',
    short ? { weekday: 'short' } : { day: 'numeric', month: 'short' },
  );
}
