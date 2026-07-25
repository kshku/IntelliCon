import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Settings,
  Key,
  Server,
  Database,
  Check,
  Save,
  Moon,
  Sun,
  Lock
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { t } = useTranslation();
  const [llmProvider, setLlmProvider] = useState(() => localStorage.getItem('intellicon_llm_provider') || 'openai');
  const [llmModel, setLlmModel] = useState(() => localStorage.getItem('intellicon_llm_model') || 'gpt-4o');
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('intellicon_api_key') || '');
  const [theme, setTheme] = useState<'light' | 'dark'>(() => (localStorage.getItem('intellicon_theme') as 'light' | 'dark') || 'light');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('intellicon_llm_provider', llmProvider);
    localStorage.setItem('intellicon_llm_model', llmModel);
    localStorage.setItem('intellicon_api_key', apiKey);
    localStorage.setItem('intellicon_theme', theme);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const toggleTheme = (newTheme: 'light' | 'dark') => {
    setTheme(newTheme);
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  return (
    <div className="max-w-[800px] mx-auto space-y-6 font-sans pb-12">
      <div className="bg-white rounded-card border border-border-light shadow-sm overflow-hidden">
        {/* Settings Header banner */}
        <div className="px-6 py-5 border-b border-border-light bg-slate-50/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-btn bg-slate-100 flex items-center justify-center text-slate-700 border border-slate-200">
              <Settings className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-[18px] font-bold text-heading-dark leading-tight">{t('settings.system_settings')}</h2>
              <p className="text-[12px] text-gray-text font-semibold">{t('settings.settings_description')}</p>
            </div>
          </div>
        </div>

        {/* Configuration forms */}
        <form onSubmit={handleSave} className="p-6 space-y-6">
          {/* Section 1: LLM Settings */}
          <div className="space-y-4 border-b border-slate-100 pb-6">
            <h3 className="text-[14px] font-bold text-heading-dark flex items-center gap-2">
              <Key className="w-4 h-4 text-primary-blue" />
              <span>{t('settings.llm_engine_config')}</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <span className="text-[12px] text-gray-text font-bold uppercase tracking-wider">{t('settings.llm_provider')}</span>
                <select
                  value={llmProvider}
                  onChange={(e) => setLlmProvider(e.target.value)}
                  className="w-full h-11 px-4 bg-bg-light border border-border-light rounded-btn text-[13px] text-heading-dark font-semibold focus:outline-none focus:border-primary-blue cursor-pointer"
                >
                  <option value="openai">{t('settings.openai_recommended')}</option>
                  <option value="anthropic">{t('settings.anthropic')}</option>
                  <option value="gemini">{t('settings.gemini')}</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <span className="text-[12px] text-gray-text font-bold uppercase tracking-wider">{t('settings.model_variant')}</span>
                <select
                  value={llmModel}
                  onChange={(e) => setLlmModel(e.target.value)}
                  className="w-full h-11 px-4 bg-bg-light border border-border-light rounded-btn text-[13px] text-heading-dark font-semibold focus:outline-none focus:border-primary-blue cursor-pointer"
                >
                  <option value="gpt-4o">gpt-4o</option>
                  <option value="claude-3-5-sonnet">claude-3-5-sonnet</option>
                  <option value="gemini-1.5-pro">gemini-1.5-pro</option>
                </select>
              </div>

              <div className="md:col-span-2 space-y-1.5">
                <span className="text-[12px] text-gray-text font-bold uppercase tracking-wider">{t('settings.api_token')}</span>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder={t('settings.api_key_placeholder')}
                  className="w-full h-11 px-4 bg-bg-light border border-border-light rounded-btn text-[13px] text-heading-dark font-medium focus:outline-none focus:border-primary-blue"
                />
              </div>
            </div>
          </div>

          {/* Section 2: Databases */}
          <div className="space-y-4 border-b border-slate-100 pb-6">
            <h3 className="text-[14px] font-bold text-heading-dark flex items-center gap-2">
              <Database className="w-4 h-4 text-primary-blue" />
              <span>{t('settings.database_linkage')}</span>
            </h3>

            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-btn border border-slate-100 bg-slate-50">
                <div className="flex items-center gap-2.5">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <div>
                    <span className="text-[13px] font-bold text-heading-dark block leading-tight">{t('settings.postgres_desc')}</span>
                    <span className="text-[10px] text-gray-text font-semibold">postgresql://intellicon:***@postgres:5432/intellicon</span>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-50 text-green-700 border border-green-200">ACTIVE</span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-btn border border-slate-100 bg-slate-50">
                <div className="flex items-center gap-2.5">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <div>
                    <span className="text-[13px] font-bold text-heading-dark block leading-tight">{t('settings.neo4j_desc')}</span>
                    <span className="text-[10px] text-gray-text font-semibold">bolt://neo4j:7687</span>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-50 text-green-700 border border-green-200">ACTIVE</span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-btn border border-slate-100 bg-slate-50">
                <div className="flex items-center gap-2.5">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <div>
                    <span className="text-[13px] font-bold text-heading-dark block leading-tight">{t('settings.redis_desc')}</span>
                    <span className="text-[10px] text-gray-text font-semibold">redis://redis:6379/0</span>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-50 text-green-700 border border-green-200">ACTIVE</span>
              </div>
            </div>
          </div>

          {/* Section 3: Preference */}
          <div className="space-y-4">
            <h3 className="text-[14px] font-bold text-heading-dark flex items-center gap-2">
              <Server className="w-4 h-4 text-primary-blue" />
              <span>{t('settings.workspace_config')}</span>
            </h3>

            <div className="flex items-center justify-between">
              <div>
                <span className="text-[13px] font-bold text-heading-dark block leading-tight">{t('settings.shift_mode')}</span>
                <span className="text-[11px] text-slate-500 font-semibold">{t('settings.shift_mode_desc')}</span>
              </div>
              <div className="flex bg-slate-100 p-0.5 border border-slate-200 rounded-btn gap-0.5">
                <button type="button" onClick={() => toggleTheme('light')} className={`w-9 h-9 rounded-btn flex items-center justify-center cursor-pointer ${theme === 'light' ? 'bg-white shadow-sm text-primary-blue' : 'hover:bg-slate-200 text-slate-500'}`}>
                  <Sun className="w-4 h-4" />
                </button>
                <button type="button" onClick={() => toggleTheme('dark')} className={`w-9 h-9 rounded-btn flex items-center justify-center cursor-pointer ${theme === 'dark' ? 'bg-white shadow-sm text-primary-blue' : 'hover:bg-slate-200 text-slate-500'}`}>
                  <Moon className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Footer Controls */}
          <div className="flex items-center justify-between border-t border-slate-100 pt-6 mt-6">
            <span className="text-[11px] text-gray-text font-semibold flex items-center gap-1">
              <Lock className="w-3.5 h-3.5 text-slate-400" />
              <span>{t('settings.restricted_access')}</span>
            </span>

            <button
              type="submit"
              className="h-11 px-5 rounded-btn bg-primary-blue hover:bg-blue-600 text-white text-[13px] font-bold shadow-md shadow-blue-500/10 flex items-center gap-2 cursor-pointer transition-all hover:scale-102"
            >
              {saved ? (
                <>
                  <Check className="w-4.5 h-4.5" />
                  <span>{t('common.settings_saved')}</span>
                </>
              ) : (
                <>
                  <Save className="w-4.5 h-4.5" />
                  <span>{t('common.save_configuration')}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
