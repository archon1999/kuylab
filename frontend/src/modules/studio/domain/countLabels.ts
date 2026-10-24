/** Authored labels for studio counts, including Russian 1/2–4/5+ forms. */
export function studyCountLabel(
  count: number,
  kind: 'theory' | 'exercise' | 'lesson',
  language: 'uz' | 'ru' | 'en',
) {
  const words = {
    theory: { uz: ['mavzu'], ru: ['тема', 'темы', 'тем'], en: ['topic', 'topics'] },
    exercise: {
      uz: ['mashq'],
      ru: ['упражнение', 'упражнения', 'упражнений'],
      en: ['exercise', 'exercises'],
    },
    lesson: { uz: ['dars'], ru: ['урок', 'урока', 'уроков'], en: ['lesson', 'lessons'] },
  }[kind][language];
  const form =
    language === 'ru'
      ? count % 100 >= 11 && count % 100 <= 14
        ? 2
        : count % 10 === 1
          ? 0
          : count % 10 >= 2 && count % 10 <= 4
            ? 1
            : 2
      : language === 'en' && count !== 1
        ? 1
        : 0;
  return `${count} ${words[form]}`;
}
