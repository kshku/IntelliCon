import React from 'react';
import { useTranslation } from 'react-i18next';
import { InteractiveMap } from '../components/InteractiveMap';
import { Globe, MapPin, HelpCircle, Layers } from 'lucide-react';

export const MapPage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="h-full flex flex-col md:flex-row gap-6 font-sans pb-6">
      {/* Side Stats Card */}
      <div className="w-full md:w-[320px] flex flex-col gap-6 flex-shrink-0">
        <div className="bg-white rounded-card border border-border-light shadow-sm p-6 space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-btn bg-red-500/10 flex items-center justify-center text-red-600">
              <Globe className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-[16px] font-bold text-heading-dark leading-tight">{t('common.geospatial_insights')}</h2>
              <p className="text-[11px] text-gray-text font-semibold">Bengaluru Crime Hotspots</p>
            </div>
          </div>

          <div className="border-t border-slate-100 pt-5 space-y-4">
            <div>
              <span className="text-[11px] text-gray-text font-bold uppercase tracking-wider">Hotspot Clusters</span>
              <div className="mt-2.5 space-y-2">
                {[
                  { name: 'Whitefield', count: '41 cases', level: 'Critical' },
                  { name: 'Shivajinagar', count: '35 cases', level: 'High' },
                  { name: 'Koramangala', count: '28 cases', level: 'High' },
                  { name: 'HSR Layout', count: '22 cases', level: 'Medium' },
                  { name: 'Yeshwanthpur', count: '19 cases', level: 'Medium' },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-[13px] font-semibold py-1">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-red-500" />
                      <span>{item.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-text text-[11px]">{item.count}</span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                        item.level === 'Critical' ? 'bg-red-50 text-red-600 border border-red-200' :
                        item.level === 'High' ? 'bg-orange-50 text-orange-600 border border-orange-200' :
                        'bg-blue-50 text-blue-600 border border-blue-200'
                      }`}>{item.level}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t border-slate-100 pt-4">
              <span className="text-[11px] text-gray-text font-bold uppercase tracking-wider">Map Layers</span>
              <div className="mt-3 space-y-2.5">
                {[
                  { label: 'Crime Hotspot Clusters', checked: true },
                  { label: 'Active Patrol Zones', checked: false },
                  { label: 'Precinct Boundaries', checked: false },
                ].map((layer, idx) => (
                  <label key={idx} className="flex items-center gap-2.5 text-[13px] text-heading-dark font-medium cursor-pointer">
                    <input
                      type="checkbox"
                      defaultChecked={layer.checked}
                      className="w-4 h-4 rounded text-primary-blue focus:ring-primary-blue border-slate-300 cursor-pointer"
                    />
                    <span>{layer.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Legend / Info Card */}
        <div className="bg-slate-50 border border-border-light rounded-card p-5">
          <h3 className="text-[13px] font-bold text-heading-dark flex items-center gap-1.5 mb-2">
            <HelpCircle className="w-4 h-4 text-slate-500" />
            <span>Map Navigation Guide</span>
          </h3>
          <p className="text-[12px] text-gray-text font-medium leading-relaxed">
            Click on any pulsing crime hotspot pin to open the details popup. Scroll or pinch to zoom. CartoDB tiles adjust dynamically to the app's active light/dark theme.
          </p>
        </div>
      </div>

      {/* Main Map Card */}
      <div className="flex-1 bg-white rounded-card border border-border-light shadow-sm overflow-hidden flex flex-col h-[500px] md:h-auto min-h-[400px]">
        <div className="px-6 py-4 border-b border-border-light flex items-center justify-between bg-slate-50/30">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-primary-blue" />
            <span className="text-[14px] font-bold text-heading-dark">Live Incident Map</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping inline-block" />
            <span>Live Data Sync</span>
          </div>
        </div>
        <div className="flex-1 relative">
          <InteractiveMap />
        </div>
      </div>
    </div>
  );
};
