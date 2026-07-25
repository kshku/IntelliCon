import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  FileText,
  FolderOpen,
  Users2,
  Activity,
  AlertTriangle,
  ChevronDown,
  Layers,
  ZoomIn,
  ZoomOut,
  MapPin,
  Clock,
  ExternalLink,
  Sliders
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface KpiData {
  title: string;
  value: string;
  change: string;
  changeType: 'increase' | 'decrease';
  color: string;
  icon: React.ComponentType<any>;
}

interface AlertData {
  title: string;
  type: string;
  time: string;
  desc: string;
  color: string;
}

interface RecentCase {
  fir: string;
  type: string;
  station: string;
  status: 'common.closed' | 'common.chargesheet' | 'dashboard.under_investigation' | 'common.pending';
  statusColor: string;
}

export const DashboardPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [zoomLevel, setZoomLevel] = useState(1);
  const [timeFilter, setTimeFilter] = useState('Last 6 Months');
  const [hotspotFilter, setHotspotFilter] = useState('Last 30 Days');

  // KPI Data Configuration
  const kpis: KpiData[] = [
    { title: t('dashboard.total_firs'), value: '24,532', change: '+8.4%', changeType: 'increase', color: 'bg-blue-500/10 text-blue-600', icon: FileText },
    { title: t('dashboard.registered_cases'), value: '18,732', change: '+5.2%', changeType: 'increase', color: 'bg-purple-500/10 text-purple-600', icon: FolderOpen },
    { title: t('dashboard.accused_persons'), value: '13,892', change: '+11.1%', changeType: 'increase', color: 'bg-orange-500/10 text-orange-600', icon: Users2 },
    { title: t('dashboard.active_investigations'), value: '7,896', change: '+3.7%', changeType: 'increase', color: 'bg-green-500/10 text-green-600', icon: Activity },
    { title: t('dashboard.alerts'), value: '56', change: '-12.4%', changeType: 'decrease', color: 'bg-red-500/10 text-red-600', icon: AlertTriangle },
  ];

  // Alerts Timeline Configuration
  const alerts: AlertData[] = [
    { title: t('dashboard.robbery_spike'), type: t('dashboard.property_crime'), time: t('dashboard.mins_ago'), desc: '4 robberies reported in Whitefield in a 2-hour window.', color: 'bg-red-500 text-white' },
    { title: t('dashboard.repeat_offender'), type: t('dashboard.alert_trigger'), time: t('dashboard.mins_ago'), desc: 'Accused Raju (Bail) spotted near Koramangala block.', color: 'bg-orange-500 text-white' },
    { title: t('dashboard.gang_association'), type: t('dashboard.intelligence_match'), time: t('dashboard.hours_ago'), desc: 'Co-accused link discovered via transaction trail.', color: 'bg-purple-500 text-white' },
    { title: t('dashboard.financial_alert'), type: t('dashboard.audit_match'), time: t('dashboard.hours_ago'), desc: 'INR 15L flagged under case FIR-482-2025.', color: 'bg-blue-500 text-white' },
    { title: t('dashboard.night_activity'), type: t('dashboard.patrol_dispatch'), time: t('dashboard.hours_ago'), desc: 'Unusual gathering near HSR Layout industrial area.', color: 'bg-teal-500 text-white' },
  ];

  // Recent Case List
  const recentCases: RecentCase[] = [
    { fir: 'FIR-0432/2026', type: 'Theft / IPC 379', station: 'Koramangala PS', status: 'dashboard.under_investigation', statusColor: 'bg-blue-50 text-blue-700 border-blue-200' },
    { fir: 'FIR-0431/2026', type: 'Assault / IPC 324', station: 'Shivajinagar PS', status: 'common.chargesheet', statusColor: 'bg-purple-50 text-purple-700 border-purple-200' },
    { fir: 'FIR-0430/2026', type: 'Fraud / IPC 420', station: 'HSR Layout PS', status: 'common.pending', statusColor: 'bg-amber-50 text-amber-700 border-amber-200' },
    { fir: 'FIR-0429/2026', type: 'Property / IPC 447', station: 'Whitefield PS', status: 'common.closed', statusColor: 'bg-green-50 text-green-700 border-green-200' },
  ];

  // Hotspot Map Pin Coordinates (Bangalore Map Mockup)
  const mapPins = [
    { name: 'Koramangala', x: '45%', y: '60%', count: '28 cases', color: 'bg-red-500' },
    { name: 'Whitefield', x: '82%', y: '35%', count: '41 cases', color: 'bg-red-600' },
    { name: 'Yeshwanthpur', x: '25%', y: '25%', count: '19 cases', color: 'bg-orange-500' },
    { name: 'HSR Layout', x: '58%', y: '75%', count: '22 cases', color: 'bg-orange-500' },
    { name: 'Shivajinagar', x: '48%', y: '42%', count: '35 cases', color: 'bg-red-500' },
  ];

  return (
    <div className="space-y-8 font-sans pb-12">
      {/* KPI ROW */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              className="bg-white rounded-card border border-border-light p-5 flex items-center justify-between shadow-sm hover:shadow-md hover:-translate-y-[2px] transition-all duration-150 h-[110px] select-none"
            >
              <div className="space-y-1.5 truncate">
                <span className="text-[13px] text-gray-text font-semibold block">{kpi.title}</span>
                <div className="flex items-baseline gap-2.5">
                  <span className="text-[28px] font-bold text-heading-dark leading-none">{kpi.value}</span>
                  <span className={`text-[12px] font-bold ${
                    kpi.changeType === 'increase' ? 'text-green-600' : 'text-danger-red'
                  }`}>
                    {kpi.change}
                  </span>
                </div>
              </div>
              <div className={`w-12 h-12 rounded-btn ${kpi.color} flex items-center justify-center flex-shrink-0 shadow-inner`}>
                <Icon className="w-6 h-6" strokeWidth={2} />
              </div>
            </div>
          );
        })}
      </div>

      {/* SECOND ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Crime Trend Overview (Line Chart) */}
        <div className="lg:col-span-5 bg-white rounded-card border border-border-light p-6 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <div className="w-2 h-5 bg-primary-blue rounded-full" />
              <h2 className="text-[18px] font-bold text-heading-dark">{t('dashboard.crime_trend_overview')}</h2>
            </div>
            {/* Filter Dropdown */}
            <div className="relative">
              <select 
                value={timeFilter}
                onChange={(e) => setTimeFilter(e.target.value)}
                className="appearance-none bg-bg-light border border-border-light text-[13px] font-semibold text-slate-700 px-4 py-2 pr-9 rounded-btn focus:outline-none focus:border-primary-blue cursor-pointer"
              >
                <option>{t('dashboard.last_30_days')}</option>
                <option>{t('dashboard.last_6_months')}</option>
                <option>{t('dashboard.last_year')}</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
            </div>
          </div>

          {/* SVG Line Chart */}
          <div className="flex-1 min-h-[220px] relative mt-2 flex items-end">
            <svg className="w-full h-full" viewBox="0 0 500 220" preserveAspectRatio="none">
              {/* Grid Lines */}
              <line x1="0" y1="50" x2="500" y2="50" stroke="#F1F5F9" strokeWidth="1" />
              <line x1="0" y1="110" x2="500" y2="110" stroke="#F1F5F9" strokeWidth="1" />
              <line x1="0" y1="170" x2="500" y2="170" stroke="#F1F5F9" strokeWidth="1" />
              
              {/* Total Crimes: Smooth Curve (Blue) */}
              <path
                d="M 0 170 Q 100 130 200 100 T 400 40 T 500 20"
                fill="none"
                stroke="#2563EB"
                strokeWidth="3.5"
                strokeLinecap="round"
              />
              {/* IPC Crimes (Purple) */}
              <path
                d="M 0 190 Q 100 160 200 130 T 400 80 T 500 60"
                fill="none"
                stroke="#7C3AED"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
              {/* Property Crimes (Orange) */}
              <path
                d="M 0 210 Q 100 190 200 170 T 400 130 T 500 110"
                fill="none"
                stroke="#F97316"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
              {/* Violent Crimes (Red) */}
              <path
                d="M 0 200 Q 100 180 200 150 T 400 140 T 500 140"
                fill="none"
                stroke="#EF4444"
                strokeWidth="2"
                strokeLinecap="round"
              />

              {/* Data points */}
              <circle cx="200" cy="100" r="5" fill="#2563EB" stroke="#FFFFFF" strokeWidth="2" />
              <circle cx="400" cy="40" r="5" fill="#2563EB" stroke="#FFFFFF" strokeWidth="2" />
            </svg>

            {/* Tooltip Overlay Mockup */}
            <div className="absolute top-[30px] left-[170px] bg-slate-900 text-white rounded-btn p-2 text-[11px] font-semibold shadow-xl border border-slate-700/50 pointer-events-none select-none z-10">
              <span className="block text-slate-400">Month: May 2026</span>
              <span className="block text-blue-400">Total: 4,120</span>
              <span className="block text-red-400">Violent: 890</span>
            </div>
          </div>

          {/* Minimal Legend */}
          <div className="flex items-center justify-between border-t border-slate-100 pt-4 mt-4 text-[12px] font-bold text-slate-500 select-none">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-primary-blue inline-block" />
              <span>{t('dashboard.total_crimes')}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-purple-accent inline-block" />
              <span>{t('dashboard.ipc_crimes')}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-orange-accent inline-block" />
              <span>{t('dashboard.property')}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-danger-red inline-block" />
              <span>{t('dashboard.violent')}</span>
            </div>
          </div>
        </div>

        {/* Crime Hotspots (City Map Placeholder) */}
        <div className="lg:col-span-4 bg-white rounded-card border border-border-light p-6 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-5 bg-orange-500 rounded-full" />
              <h2 className="text-[18px] font-bold text-heading-dark">{t('dashboard.crime_hotspots_map')}</h2>
            </div>
            
            <div className="relative">
              <select 
                value={hotspotFilter}
                onChange={(e) => setHotspotFilter(e.target.value)}
                className="appearance-none bg-bg-light border border-border-light text-[13px] font-semibold text-slate-700 px-4 py-2 pr-9 rounded-btn focus:outline-none focus:border-primary-blue cursor-pointer"
              >
                <option>{t('dashboard.last_24_hours')}</option>
                <option>{t('dashboard.last_30_days')}</option>
                <option>{t('dashboard.last_90_days')}</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
            </div>
          </div>

          {/* Interactive Map Layout Canvas */}
          <div className="flex-1 bg-slate-100 rounded-custom-lg relative overflow-hidden border border-slate-200 min-h-[220px]">
            {/* Vector City Grid Background Grid */}
            <div 
              className="absolute inset-0 bg-[radial-gradient(#CBD5E1_1px,transparent_1px)] [background-size:16px_16px] transition-transform duration-200"
              style={{ transform: `scale(${zoomLevel})` }}
            />
            
            {/* Heatmap overlay circles */}
            <div 
              className="absolute inset-0 flex items-center justify-center pointer-events-none transition-transform duration-200"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              <div className="absolute top-[35%] left-[45%] w-24 h-24 rounded-full bg-red-500/20 blur-xl animate-pulse" />
              <div className="absolute top-[50%] left-[65%] w-32 h-32 rounded-full bg-orange-500/15 blur-2xl" />
              <div className="absolute top-[20%] left-[25%] w-20 h-20 rounded-full bg-red-400/25 blur-lg" />
            </div>

            {/* Pins */}
            <div 
              className="absolute inset-0 transition-transform duration-200"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              {mapPins.map((pin, idx) => (
                <div
                  key={idx}
                  className="absolute cursor-pointer group"
                  style={{ left: pin.x, top: pin.y }}
                >
                  <MapPin className="w-6 h-6 text-red-600 drop-shadow group-hover:scale-110 transition-transform duration-100" fill="#EF4444" />
                  
                  {/* Tooltip on Pin Hover */}
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 bg-slate-900 text-white rounded-btn px-2 py-1 text-[10px] font-bold whitespace-nowrap opacity-0 group-hover:opacity-100 shadow-lg pointer-events-none transition-opacity duration-150 z-20">
                    <span className="block font-bold">{pin.name}</span>
                    <span className="text-slate-400">{pin.count}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Map Controls */}
            <div className="absolute bottom-3 right-3 bg-white/95 backdrop-blur shadow rounded-btn border border-slate-200 flex flex-col p-1 gap-1 z-10">
              <button
                onClick={() => setZoomLevel(prev => Math.min(prev + 0.2, 2))}
                className="w-8 h-8 rounded-btn hover:bg-slate-100 flex items-center justify-center text-slate-700 cursor-pointer"
              >
                <ZoomIn className="w-4 h-4" />
              </button>
              <button
                onClick={() => setZoomLevel(prev => Math.max(prev - 0.2, 0.6))}
                className="w-8 h-8 rounded-btn hover:bg-slate-100 flex items-center justify-center text-slate-700 cursor-pointer"
              >
                <ZoomOut className="w-4 h-4" />
              </button>
            </div>

            {/* Layers controls */}
            <button className="absolute top-3 right-3 bg-white/95 backdrop-blur shadow rounded-btn border border-slate-200 px-3 py-2 text-[12px] font-bold text-slate-700 hover:bg-slate-100 flex items-center gap-1.5 cursor-pointer z-10">
              <Layers className="w-3.5 h-3.5" />
              <span>{t('common.layers')}</span>
            </button>
          </div>
        </div>

        {/* Recent Alerts (Vertical Timeline) */}
        <div className="lg:col-span-3 bg-white rounded-card border border-border-light p-6 shadow-sm flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-2 h-5 bg-red-500 rounded-full" />
            <h2 className="text-[18px] font-bold text-heading-dark">{t('dashboard.recent_alerts')}</h2>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto max-h-[250px] pr-1">
            {alerts.map((alert, idx) => (
              <div
                key={idx}
                className="flex gap-3 hover:-translate-y-[1px] transition-transform duration-100"
              >
                {/* Timeline node line */}
                <div className="flex flex-col items-center">
                   <div className={`w-3.5 h-3.5 rounded-full ${alert.color} ring-4 ring-slate-200 flex-shrink-0 flex items-center justify-center`} />
                  {idx !== alerts.length - 1 && (
                    <div className="w-[1.5px] bg-slate-100 h-full mt-2" />
                  )}
                </div>

                {/* Timeline text content card */}
                <div className="flex-1 bg-slate-50 border border-slate-200/50 rounded-btn p-3 shadow-inner">
                  <div className="flex items-start justify-between gap-1.5">
                    <span className="text-[13px] font-bold text-heading-dark leading-tight">{alert.title}</span>
                    <span className="text-[10px] text-gray-text font-bold whitespace-nowrap flex items-center gap-1">
                      <Clock className="w-2.5 h-2.5" />
                      {alert.time}
                    </span>
                  </div>
                  <span className="text-[11px] font-bold text-primary-blue mt-0.5 block">{alert.type}</span>
                  <p className="text-[12px] text-slate-500 font-medium mt-1 leading-normal">
                    {alert.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* THIRD ROW */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Crime by Category Donut Chart */}
        <div className="bg-white rounded-card border border-border-light p-5 shadow-sm flex flex-col justify-between min-h-[240px]">
          <span className="text-[14px] font-bold text-heading-dark mb-4 block">{t('dashboard.crime_by_category')}</span>
          
          <div className="flex-1 flex items-center justify-center gap-4">
            {/* SVG Donut */}
            <div className="relative w-24 h-24 flex-shrink-0">
              <svg className="w-full h-full transform -rotate-95" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15.915" fill="none" stroke="#E2E8F0" strokeWidth="3" />
                <circle cx="18" cy="18" r="15.915" fill="none" stroke="#2563EB" strokeWidth="3.5" strokeDasharray="35 65" strokeDashoffset="0" />
                <circle cx="18" cy="18" r="15.915" fill="none" stroke="#7C3AED" strokeWidth="3.5" strokeDasharray="25 75" strokeDashoffset="-35" />
                <circle cx="18" cy="18" r="15.915" fill="none" stroke="#F97316" strokeWidth="3.5" strokeDasharray="20 80" strokeDashoffset="-60" />
                <circle cx="18" cy="18" r="15.915" fill="none" stroke="#16A34A" strokeWidth="3.5" strokeDasharray="12 88" strokeDashoffset="-80" />
                <circle cx="18" cy="18" r="15.915" fill="none" stroke="#EF4444" strokeWidth="3.5" strokeDasharray="8 92" strokeDashoffset="-92" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center select-none">
                <span className="text-[16px] font-bold text-heading-dark">35%</span>
                <span className="text-[9px] text-gray-text font-bold">{t('dashboard.theft')}</span>
              </div>
            </div>

            {/* List legends */}
            <div className="flex-1 text-[11px] font-bold text-slate-500 space-y-1.5">
              <div className="flex items-center gap-1.5 justify-between">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-blue-500" />{t('dashboard.theft')}</span>
                <span className="text-slate-700">35%</span>
              </div>
              <div className="flex items-center gap-1.5 justify-between">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-purple-500" />{t('dashboard.robbery')}</span>
                <span className="text-slate-700">25%</span>
              </div>
              <div className="flex items-center gap-1.5 justify-between">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-orange-500" />{t('dashboard.assault')}</span>
                <span className="text-slate-700">20%</span>
              </div>
              <div className="flex items-center gap-1.5 justify-between">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-green-500" />{t('dashboard.women')}</span>
                <span className="text-slate-700">12%</span>
              </div>
              <div className="flex items-center gap-1.5 justify-between">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-red-500" />{t('dashboard.others')}</span>
                <span className="text-slate-700">8%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Top Crime Locations Horizontal Bar */}
        <div className="bg-white rounded-card border border-border-light p-5 shadow-sm flex flex-col justify-between min-h-[240px]">
          <span className="text-[14px] font-bold text-heading-dark mb-4 block">{t('dashboard.top_crime_locations')}</span>
          
          <div className="flex-1 space-y-3.5">
            {[
              { name: 'Koramangala', val: 78, label: '342 cases', color: 'bg-blue-500' },
              { name: 'Whitefield', val: 92, label: '388 cases', color: 'bg-primary-blue' },
              { name: 'Yeshwanthpur', val: 65, label: '280 cases', color: 'bg-purple-600' },
              { name: 'HSR Layout', val: 58, label: '232 cases', color: 'bg-orange-500' },
              { name: 'Shivajinagar', val: 42, label: '178 cases', color: 'bg-teal-500' }
            ].map((loc, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-[11px] font-bold">
                  <span className="text-slate-700">{loc.name}</span>
                  <span className="text-slate-400">{loc.label}</span>
                </div>
                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div className={`h-full ${loc.color} rounded-full`} style={{ width: `${loc.val}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Case Status Donut Chart */}
        <div className="bg-white rounded-card border border-border-light p-5 shadow-sm flex flex-col justify-between min-h-[240px]">
          <span className="text-[14px] font-bold text-heading-dark mb-4 block">{t('dashboard.case_status_distribution')}</span>
          
          <div className="flex-1 flex items-center justify-center gap-4">
            {/* SVG Donut */}
            <div className="relative w-24 h-24 flex-shrink-0">
              <svg className="w-full h-full transform -rotate-95" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15.915" fill="none" stroke="#E2E8F0" strokeWidth="3" />
                <circle cx="18" cy="18" r="15.915" fill="none" stroke="#16A34A" strokeWidth="3.5" strokeDasharray="45 55" strokeDashoffset="0" />
                <circle cx="18" cy="18" r="15.915" fill="none" stroke="#7C3AED" strokeWidth="3.5" strokeDasharray="25 75" strokeDashoffset="-45" />
                <circle cx="18" cy="18" r="15.915" fill="none" stroke="#2563EB" strokeWidth="3.5" strokeDasharray="20 80" strokeDashoffset="-70" />
                <circle cx="18" cy="18" r="15.915" fill="none" stroke="#F59E0B" strokeWidth="3.5" strokeDasharray="10 90" strokeDashoffset="-90" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center select-none">
                <span className="text-[16px] font-bold text-heading-dark">45%</span>
                <span className="text-[9px] text-gray-text font-bold">{t('common.closed')}</span>
              </div>
            </div>

            {/* List legends */}
            <div className="flex-1 text-[11px] font-bold text-slate-500 space-y-1.5">
              <div className="flex items-center gap-1.5 justify-between">
                <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-green-600" />{t('common.closed')}</span>
                <span className="text-slate-700">45%</span>
              </div>
              <div className="flex items-center gap-1.5 justify-between">
                <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-purple-500" />{t('common.chargesheet')}</span>
                <span className="text-slate-700">25%</span>
              </div>
              <div className="flex items-center gap-1.5 justify-between">
                <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-blue-500" />{t('common.active')}</span>
                <span className="text-slate-700">20%</span>
              </div>
              <div className="flex items-center gap-1.5 justify-between">
                <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-amber-500" />{t('common.pending')}</span>
                <span className="text-slate-700">10%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Cases list */}
        <div className="bg-white rounded-card border border-border-light p-5 shadow-sm flex flex-col justify-between min-h-[240px]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[14px] font-bold text-heading-dark">{t('dashboard.recent_cases')}</span>
            <button className="text-[11px] font-bold text-primary-blue hover:underline cursor-pointer flex items-center gap-0.5">
              <span>{t('common.view_all')}</span>
              <ExternalLink className="w-3 h-3" />
            </button>
          </div>

          <div className="flex-1 space-y-3">
            {recentCases.map((c, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2 rounded-btn border border-slate-100 hover:bg-slate-50 transition-colors"
              >
                <div className="truncate">
                  <span className="text-[12px] font-bold text-heading-dark block">{c.fir}</span>
                  <span className="text-[10px] text-gray-text font-bold block">{c.type} • {c.station}</span>
                </div>
                
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${c.statusColor} flex-shrink-0`}>
                  {t(c.status)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* QUICK ACTIONS ROW */}
      <div className="bg-white border border-border-light rounded-card p-6 shadow-sm">
        <h2 className="text-[15px] font-bold text-heading-dark mb-4 flex items-center gap-1.5">
          <Sliders className="w-4 h-4 text-primary-blue" />
          <span>{t('dashboard.quick_investigation_commands')}</span>
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          {[
            { label: t('dashboard.ask_ai_assistant'), action: () => navigate('/chat'), color: 'bg-primary-blue hover:bg-blue-600 text-white shadow-blue-500/10' },
            { label: t('dashboard.advanced_search'), action: () => navigate('/chat'), color: 'bg-slate-100 hover:bg-slate-200 text-slate-700' },
            { label: t('dashboard.network_analysis_btn'), action: () => navigate('/network'), color: 'bg-slate-100 hover:bg-slate-200 text-slate-700' },
            { label: t('dashboard.geospatial_map'), action: () => console.log('Geospatial Map - coming soon'), color: 'bg-slate-100 hover:bg-slate-200 text-slate-700' },
            { label: t('dashboard.generate_report'), action: () => console.log('Generate Report - coming soon'), color: 'bg-slate-100 hover:bg-slate-200 text-slate-700' },
            { label: t('dashboard.upload_data'), action: () => console.log('Upload Data - coming soon'), color: 'bg-slate-100 hover:bg-slate-200 text-slate-700' },
          ].map((act, idx) => (
            <button
              key={idx}
              onClick={act.action}
              className={`h-11 rounded-btn px-4 text-[13px] font-bold transition-all hover:scale-102 flex items-center justify-center text-center cursor-pointer shadow-sm ${act.color}`}
            >
              {act.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
