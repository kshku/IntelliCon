import React from 'react';
import { useTranslation } from 'react-i18next';
import { X, FileText, Calendar, MapPin, AlignLeft, Users } from 'lucide-react';

interface Person {
  name: string;
  age: number | null;
  gender: string | null;
}

interface CaseDetails {
  case_id: number;
  case_no: string;
  crime_no: string | null;
  crime_registered_date: string | null;
  incident_from_date: string | null;
  incident_to_date: string | null;
  latitude: number | null;
  longitude: number | null;
  brief_facts: string | null;
  station_name: string;
  status_name: string;
  crime_type: string;
  complainants: Person[];
  accused: Person[];
  victims: Person[];
}

interface CaseDetailsModalProps {
  caseDetails: CaseDetails;
  onClose: () => void;
}

export const CaseDetailsModal: React.FC<CaseDetailsModalProps> = ({ caseDetails, onClose }) => {
  const { t } = useTranslation();

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) onClose();
  };

  return (
    <div
      onClick={handleOverlayClick}
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[9999] p-4 overflow-y-auto"
    >
      <div className="bg-white rounded-card w-full max-w-3xl shadow-2xl border border-border-light overflow-hidden flex flex-col my-8 max-h-[85vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-border-light bg-slate-50/50 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-btn bg-primary-blue/10 flex items-center justify-center text-primary-blue">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] text-gray-text font-bold uppercase tracking-wider">Karnataka Police FIR File</span>
              <h2 className="text-[18px] font-bold text-heading-dark leading-tight">{caseDetails.case_no}</h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full hover:bg-slate-200/80 flex items-center justify-center text-slate-500 hover:text-heading-dark transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Metadata Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-btn bg-slate-50 border border-slate-100">
            <div className="space-y-1">
              <span className="text-[10px] text-gray-text font-bold uppercase tracking-wider block">Crime No</span>
              <span className="text-[13px] text-heading-dark font-bold">{caseDetails.crime_no || 'N/A'}</span>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-gray-text font-bold uppercase tracking-wider block">Police Station</span>
              <span className="text-[13px] text-heading-dark font-bold">{caseDetails.station_name}</span>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-gray-text font-bold uppercase tracking-wider block">Status</span>
              <span className="text-[13px] text-heading-dark font-bold text-primary-blue">{caseDetails.status_name}</span>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-gray-text font-bold uppercase tracking-wider block">Crime Category</span>
              <span className="text-[13px] text-heading-dark font-bold">{caseDetails.crime_type}</span>
            </div>
          </div>

          {/* Dates & Locations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h3 className="text-[13px] font-bold text-heading-dark flex items-center gap-1.5 border-b border-slate-100 pb-1.5">
                <Calendar className="w-4 h-4 text-primary-blue" />
                <span>Date & Timing</span>
              </h3>
              <div className="space-y-2 text-[13px] font-semibold text-gray-text">
                <div className="flex justify-between">
                  <span>Registered:</span>
                  <span className="text-heading-dark">{caseDetails.crime_registered_date || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Incident From:</span>
                  <span className="text-heading-dark">{caseDetails.incident_from_date || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Incident To:</span>
                  <span className="text-heading-dark">{caseDetails.incident_to_date || 'N/A'}</span>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="text-[13px] font-bold text-heading-dark flex items-center gap-1.5 border-b border-slate-100 pb-1.5">
                <MapPin className="w-4 h-4 text-red-500" />
                <span>Geospatial Coordinates</span>
              </h3>
              <div className="space-y-2 text-[13px] font-semibold text-gray-text">
                <div className="flex justify-between">
                  <span>Latitude:</span>
                  <span className="text-heading-dark">{caseDetails.latitude !== null ? caseDetails.latitude : 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Longitude:</span>
                  <span className="text-heading-dark">{caseDetails.longitude !== null ? caseDetails.longitude : 'N/A'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* People involved */}
          <div className="space-y-4">
            <h3 className="text-[13px] font-bold text-heading-dark flex items-center gap-1.5 border-b border-slate-100 pb-1.5">
              <Users className="w-4 h-4 text-primary-blue" />
              <span>Associated Individuals</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Complainants */}
              <div className="p-4 rounded-btn border border-slate-100 bg-slate-50/50">
                <span className="text-[11px] text-gray-text font-bold uppercase tracking-wider block mb-2">Complainants</span>
                {caseDetails.complainants.length > 0 ? (
                  caseDetails.complainants.map((p, idx) => (
                    <div key={idx} className="text-[13px] font-semibold text-heading-dark py-1 border-b border-slate-100 last:border-0">
                      <div>{p.name}</div>
                      {(p.age || p.gender) && (
                        <div className="text-[10px] text-gray-text font-bold mt-0.5">
                          {p.gender ? `${p.gender}` : ''}{p.age ? ` • Age: ${p.age}` : ''}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <span className="text-[12px] text-gray-text italic">None recorded</span>
                )}
              </div>

              {/* Victims */}
              <div className="p-4 rounded-btn border border-slate-100 bg-slate-50/50">
                <span className="text-[11px] text-gray-text font-bold uppercase tracking-wider block mb-2">Victims</span>
                {caseDetails.victims.length > 0 ? (
                  caseDetails.victims.map((p, idx) => (
                    <div key={idx} className="text-[13px] font-semibold text-heading-dark py-1 border-b border-slate-100 last:border-0">
                      <div>{p.name}</div>
                      {(p.age || p.gender) && (
                        <div className="text-[10px] text-gray-text font-bold mt-0.5">
                          {p.gender ? `${p.gender}` : ''}{p.age ? ` • Age: ${p.age}` : ''}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <span className="text-[12px] text-gray-text italic">None recorded</span>
                )}
              </div>

              {/* Accused */}
              <div className="p-4 rounded-btn border border-slate-100 bg-slate-50/50">
                <span className="text-[11px] text-gray-text font-bold uppercase tracking-wider block mb-2">Accused SUSPECTS</span>
                {caseDetails.accused.length > 0 ? (
                  caseDetails.accused.map((p, idx) => (
                    <div key={idx} className="text-[13px] font-semibold text-heading-dark py-1 border-b border-slate-100 last:border-0">
                      <div>{p.name}</div>
                      {(p.age || p.gender) && (
                        <div className="text-[10px] text-gray-text font-bold mt-0.5">
                          {p.gender ? `${p.gender}` : ''}{p.age ? ` • Age: ${p.age}` : ''}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <span className="text-[12px] text-gray-text italic">None recorded</span>
                )}
              </div>
            </div>
          </div>

          {/* Brief Facts */}
          <div className="space-y-3">
            <h3 className="text-[13px] font-bold text-heading-dark flex items-center gap-1.5 border-b border-slate-100 pb-1.5">
              <AlignLeft className="w-4 h-4 text-primary-blue" />
              <span>Brief Incident Facts</span>
            </h3>
            <div className="p-4 rounded-btn border border-amber-200/60 bg-amber-50/30 text-[13px] font-medium leading-relaxed text-slate-800 dark:text-slate-200 dark:bg-slate-800/40 dark:border-slate-700">
              {caseDetails.brief_facts || 'No fact statement on record.'}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-border-light bg-slate-50/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm bg-primary-blue text-white rounded-lg font-bold hover:opacity-90 transition cursor-pointer"
          >
            {t('common.closed')}
          </button>
        </div>
      </div>
    </div>
  );
};
