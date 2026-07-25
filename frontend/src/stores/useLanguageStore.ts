import { create } from 'zustand';

interface LanguageState {
  language: string;
  setLanguage: (lng: string) => void;
}

export const useLanguageStore = create<LanguageState>((set) => ({
  language: localStorage.getItem('intellicon_language') || 'en',
  setLanguage: (lng: string) => {
    localStorage.setItem('intellicon_language', lng);
    set({ language: lng });
  },
}));
