import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import en from './translations/en';
import kn from './translations/kn';

const resources = {
  en: { translation: en },
  kn: { translation: kn },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    lng: localStorage.getItem('intellicon_language') || 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
