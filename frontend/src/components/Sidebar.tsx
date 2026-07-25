import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Shield,
  LayoutDashboard,
  MessageSquareCode,
  Network,
  Settings,
  ChevronDown
} from 'lucide-react';

interface NavItem {
  nameKey: string;
  path: string;
  icon: React.ComponentType<any>;
}

export const Sidebar: React.FC = () => {
  const { t } = useTranslation();
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);
  const [activeRole, setActiveRole] = useState('role_investigator');

  const navItems: NavItem[] = [
    { nameKey: 'dashboard', path: '/dashboard', icon: LayoutDashboard },
    { nameKey: 'conversational_ai', path: '/chat', icon: MessageSquareCode },
    { nameKey: 'network_analysis', path: '/network', icon: Network },
    { nameKey: 'system_settings', path: '/settings', icon: Settings },
  ];

  const roles = [
    { id: 'role_investigator', nameKey: 'role_investigator' },
    { id: 'role_analyst', nameKey: 'role_analyst' },
    { id: 'role_supervisor', nameKey: 'role_supervisor' },
  ];

  return (
    <div className="w-[240px] h-screen bg-dark-navy flex flex-col text-slate-300 select-none flex-shrink-0 sticky top-0 z-30 font-sans border-r border-slate-800">
      {/* Brand Header */}
      <div className="p-6 flex items-center gap-3 border-b border-slate-800/60">
        <div className="w-10 h-10 rounded-custom-lg bg-primary-blue flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
          <Shield className="w-6 h-6" strokeWidth={2} />
        </div>
        <div className="flex flex-col">
          <span className="text-[15px] font-bold text-white leading-tight">IntelliCon</span>
          <span className="text-[11px] text-slate-400 font-medium">KSP Intelligence</span>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-4 px-3 overflow-y-auto space-y-1 scrollbar-thin">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3.5 px-4 py-3 rounded-btn text-[14px] font-medium transition-all duration-150 group ${
                isActive
                  ? 'bg-primary-blue text-white shadow-md shadow-blue-500/10'
                  : 'text-slate-400 hover:bg-slate-800/40 hover:text-white'
              }`
            }
          >
            {({ isActive }) => {
              const Icon = item.icon;
              return (
                <>
                  <Icon
                    className={`w-5 h-5 transition-transform duration-150 group-hover:scale-105 ${
                      isActive ? 'text-white' : 'text-slate-400 group-hover:text-white'
                    }`}
                    strokeWidth={2}
                  />
                  <span className="truncate">{t(`common.${item.nameKey}`)}</span>
                </>
              );
            }}
          </NavLink>
        ))}
      </div>

      {/* Bottom Role Selector Section */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-900/40 relative">
        <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2 px-1">
          Active Role
        </div>
        
        <button
          onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
          className="w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-btn bg-slate-800/50 hover:bg-slate-800 text-white transition-colors duration-150 text-[13px] font-semibold border border-slate-700/30"
        >
          <div className="flex items-center gap-2.5 truncate">
            <div className="w-6 h-6 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-400">
              <Shield className="w-3.5 h-3.5" />
            </div>
            <span className="truncate">{t(`common.${activeRole}`)}</span>
          </div>
          <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${roleDropdownOpen ? 'rotate-180' : ''}`} />
        </button>

        {roleDropdownOpen && (
          <div className="absolute bottom-[calc(100%-8px)] left-4 right-4 bg-slate-800 border border-slate-700/50 rounded-custom-lg shadow-2xl p-1.5 z-40 space-y-0.5 animate-in fade-in slide-in-from-bottom-2 duration-150">
            {roles.map((role) => (
              <button
                key={role.id}
                onClick={() => {
                  setActiveRole(role.id);
                  setRoleDropdownOpen(false);
                }}
                className={`w-full text-left px-3 py-2 rounded-btn text-[13px] font-medium transition-colors duration-100 ${
                  activeRole === role.id
                    ? 'bg-primary-blue text-white'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                {t(`common.${role.nameKey}`)}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
