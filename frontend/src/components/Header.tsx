import React from 'react';
import { useTranslation } from 'react-i18next';
import { Search, Mic, Bell, HelpCircle } from 'lucide-react';
import { useLocation } from 'react-router-dom';

export const Header: React.FC = () => {
  const { t, i18n } = useTranslation();
  const location = useLocation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  const getPageTitle = () => {
    switch (location.pathname) {
      case '/chat':
        return t('common.conversational_ai');
      case '/network':
        return t('common.network_analysis');
      case '/settings':
        return t('common.system_settings');
      case '/dashboard':
      default:
        return t('common.welcome');
    }
  };

  return (
    <header className="h-[90px] bg-white border-b border-border-light px-8 flex items-center justify-between sticky top-0 z-20 font-sans">
      {/* Title & Subtitle */}
      <div className="flex flex-col">
        <h1 className="text-[24px] font-bold text-heading-dark leading-tight tracking-tight">
          {getPageTitle()}
        </h1>
        <p className="text-[13px] text-gray-text font-medium mt-0.5">
          {t('common.subtitle')}
        </p>
      </div>

      {/* Search & Actions */}
      <div className="flex items-center gap-6">
        {/* Large AI Search Bar */}
        <div className="relative w-[340px] flex items-center">
          <input
            type="text"
            placeholder={t('common.ask_placeholder')}
            onChange={() => {}}
            className="w-full h-11 pl-11 pr-10 rounded-full bg-bg-light border border-border-light text-[14px] text-heading-dark placeholder-gray-text/75 focus:outline-none focus:border-primary-blue focus:ring-2 focus:ring-primary-blue/10 transition-all font-medium"
          />
          <Search className="absolute left-4 w-4 h-4 text-gray-text" strokeWidth={2.5} />
          
          <button 
            title={t('common.voice_search')}
            onClick={() => console.log('Voice search - not yet implemented')}
            className="absolute right-3 w-7 h-7 rounded-full hover:bg-slate-200 flex items-center justify-center text-gray-text hover:text-primary-blue transition-colors cursor-pointer"
          >
            <Mic className="w-3.5 h-3.5" strokeWidth={2.5} />
          </button>
        </div>

        {/* Vertical divider */}
        <div className="w-[1px] h-6 bg-border-light" />

        {/* Language Toggler */}
        <div className="flex items-center gap-1 bg-bg-light border border-border-light rounded-btn p-1">
          <button
            onClick={() => changeLanguage('en')}
            className={`px-3 py-1 rounded-[8px] text-[12px] font-bold transition-all cursor-pointer ${
              i18n.language?.startsWith('en')
                ? 'bg-white text-primary-blue shadow-sm'
                : 'text-gray-text hover:text-heading-dark'
            }`}
          >
            EN
          </button>
          <button
            onClick={() => changeLanguage('kn')}
            className={`px-3 py-1 rounded-[8px] text-[12px] font-bold transition-all cursor-pointer ${
              i18n.language?.startsWith('kn')
                ? 'bg-white text-primary-blue shadow-sm'
                : 'text-gray-text hover:text-heading-dark'
            }`}
          >
            ಕನ್ನಡ
          </button>
        </div>

        {/* Utilities */}
        <div className="flex items-center gap-2">
          {/* Notification icon */}
          <button onClick={() => console.log('Notifications - not yet implemented')} className="w-10 h-10 rounded-btn hover:bg-bg-light flex items-center justify-center text-slate-500 hover:text-heading-dark transition-colors relative cursor-pointer">
            <Bell className="w-5 h-5" strokeWidth={2} />
            <span className="absolute top-2.5 right-2.5 w-2 h-2 rounded-full bg-danger-red ring-2 ring-white" />
          </button>

          {/* Help icon */}
          <button onClick={() => console.log('Help - not yet implemented')} className="w-10 h-10 rounded-btn hover:bg-bg-light flex items-center justify-center text-slate-500 hover:text-heading-dark transition-colors cursor-pointer">
            <HelpCircle className="w-5 h-5" strokeWidth={2} />
          </button>
        </div>

        {/* Divider */}
        <div className="w-[1px] h-6 bg-border-light" />

        {/* User Card */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-btn bg-slate-200 border border-slate-300/80 overflow-hidden shadow-inner flex items-center justify-center">
            <div className="w-full h-full bg-primary-blue text-white font-bold flex items-center justify-center text-[13px]">
              IO
            </div>
          </div>
          <div className="hidden xl:flex flex-col">
            <span className="text-[14px] font-bold text-heading-dark leading-tight">Shreekrishna U.</span>
            <span className="text-[11px] text-gray-text font-semibold">Senior Analyst</span>
          </div>
        </div>
      </div>
    </header>
  );
};
