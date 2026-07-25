import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  en: {
    translation: {
      common: {
        dashboard: 'Dashboard',
        conversational_ai: 'Conversational AI',
        crime_analytics: 'Crime Analytics',
        network_analysis: 'Network Analysis',
        offender_profiling: 'Offender Profiling',
        financial_intelligence: 'Financial Intelligence',
        geospatial_insights: 'Geospatial Insights',
        alerts_early_warning: 'Alerts & Early Warning',
        case_management: 'Case Management',
        reports: 'Reports',
        user_management: 'User Management',
        system_settings: 'System Settings',
        role_investigator: 'Investigator',
        role_analyst: 'Police Analyst',
        role_supervisor: 'Supervisor',
        welcome: 'Welcome, Investigator',
        subtitle: 'Intelligent Insights. Safer Communities.',
        ask_placeholder: 'Ask anything about crime data...',
        voice_search: 'Voice Search',
        notifications: 'Notifications',
        help: 'Help',
      },
    },
  },
  kn: {
    translation: {
      common: {
        dashboard: 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
        conversational_ai: 'ಸಂಭಾಷಣಾತ್ಮಕ AI',
        crime_analytics: 'ಅಪರಾಧ ವಿಶ್ಲೇಷಣೆ',
        network_analysis: 'ನೆಟ್‌ವರ್ಕ್ ವಿಶ್ಲೇಷಣೆ',
        offender_profiling: 'ಅಪರಾಧಿ ಪ್ರೊಫೈಲಿಂಗ್',
        financial_intelligence: 'ಹಣಕಾಸು ಗುಪ್ತಚರ',
        geospatial_insights: 'ಭೂ-ಪ್ರಾದೇಶಿಕ ಒಳನೋಟಗಳು',
        alerts_early_warning: 'ಎಚ್ಚರಿಕೆಗಳು ಮತ್ತು ಆರಂಭಿಕ ಎಚ್ಚರಿಕೆ',
        case_management: 'ಪ್ರಕರಣ ನಿರ್ವಹಣೆ',
        reports: 'ವರದಿಗಳು',
        user_management: 'ಬಳಕೆದಾರ ನಿರ್ವಹಣೆ',
        system_settings: 'ಸಿಸ್ಟಮ್ ಸೆಟ್ಟಿಂಗ್‌ಗಳು',
        role_investigator: 'ತನಿಖಾಧಿಕಾರಿ',
        role_analyst: 'ಪೊಲೀಸ್ ವಿಶ್ಲೇಷಕ',
        role_supervisor: 'ಮೇಲ್ವಿಚಾರಕ',
        welcome: 'ಸ್ವಾಗತ, ತನಿಖಾಧಿಕಾರಿ',
        subtitle: 'ಬುದ್ಧಿವಂತ ಒಳನೋಟಗಳು. ಸುರಕ್ಷಿತ ಸಮುದಾಯಗಳು.',
        ask_placeholder: 'ಅಪರಾಧ ಡೇಟಾದ ಬಗ್ಗೆ ಏನೇ ಕೇಳಿ...',
        voice_search: 'ಧ್ವನಿ ಹುಡುಕಾಟ',
        notifications: 'ಅಧಿಸೂಚನೆಗಳು',
        help: 'ಸಹಾಯ',
      },
    },
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    lng: 'en', // default language
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
