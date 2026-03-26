// src/i18n/index.ts
import en from './en';
import fr from './fr';

const translations = { en, fr } as const;
type Locale = keyof typeof translations;

export function t(locale: Locale = 'en') {
  return translations[locale];
}

export function getLocale(): Locale {
  return 'en'; // For now, always English. Will use Astro.currentLocale in bilingual phase.
}
