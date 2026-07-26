import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { X, Upload, FileText, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { apiFetch } from '../api/client';

interface UploadDataModalProps {
  onClose: () => void;
  onUploadSuccess?: () => void;
}

export const UploadDataModal: React.FC<UploadDataModalProps> = ({ onClose, onUploadSuccess }) => {
  const { t } = useTranslation();
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [insertedCount, setInsertedCount] = useState(0);
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0];
      if (dropped.name.endsWith('.csv') || dropped.name.endsWith('.json')) {
        setFile(dropped);
        setStatus('idle');
        setMessage('');
      } else {
        setStatus('error');
        setMessage('Only CSV or JSON files are supported');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setStatus('idle');
      setMessage('');
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async () => {
    if (!file) return;
    setStatus('uploading');
    setMessage('');

    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const fileContent = event.target?.result as string;
        const res = await apiFetch<{ message: string; inserted_count: number }>('/cases/upload', {
          method: 'POST',
          json: {
            file_content: fileContent,
            filename: file.name,
          },
        });
        setInsertedCount(res.inserted_count);
        setStatus('success');
        if (onUploadSuccess) onUploadSuccess();
      } catch (err: any) {
        setStatus('error');
        setMessage(err.message || 'An error occurred during upload');
      }
    };

    reader.onerror = () => {
      setStatus('error');
      setMessage('Failed to read file');
    };

    reader.readAsText(file);
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[9999] p-4">
      <div className="bg-white rounded-card w-full max-w-md shadow-2xl border border-border-light overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-border-light bg-slate-50/50 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-btn bg-primary-blue/10 flex items-center justify-center text-primary-blue">
              <Upload className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-[16px] font-bold text-heading-dark leading-tight">{t('dashboard.upload_data')}</h2>
              <p className="text-[11px] text-gray-text font-semibold">Bulk FIR Importer</p>
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
        <div className="p-6 space-y-5">
          {status === 'success' ? (
            <div className="text-center py-6 space-y-3">
              <div className="w-12 h-12 rounded-full bg-green-50 text-green-500 flex items-center justify-center mx-auto border border-green-200">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-[16px] font-bold text-heading-dark">{t('dashboard.upload_success')}</h3>
              <p className="text-[13px] text-gray-text font-semibold">
                Successfully processed and imported <span className="text-primary-blue font-bold">{insertedCount}</span> new cases. Database index and criminal networks have been synced.
              </p>
            </div>
          ) : (
            <>
              {/* Drag and Drop Zone */}
              <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={triggerFileInput}
                className={`border-2 border-dashed rounded-btn p-8 text-center cursor-pointer transition-all ${
                  isDragActive ? 'border-primary-blue bg-blue-50/10' : 'border-slate-200 hover:border-primary-blue/60 hover:bg-slate-50/50'
                }`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept=".csv,.json"
                  className="hidden"
                />
                <Upload className="w-8 h-8 text-slate-400 mx-auto mb-3" />
                <span className="block text-[14px] font-bold text-heading-dark mb-1">
                  Drag & Drop files here
                </span>
                <span className="block text-[12px] text-gray-text font-semibold">
                  or <span className="text-primary-blue underline">browse your device</span>
                </span>
                <span className="block text-[10px] text-gray-text font-bold uppercase tracking-wider mt-4">
                  Supports CSV, JSON
                </span>
              </div>

              {/* Selected File Details */}
              {file && (
                <div className="flex items-center justify-between p-3.5 rounded-btn bg-slate-50 border border-slate-100">
                  <div className="flex items-center gap-3 truncate">
                    <FileText className="w-5 h-5 text-primary-blue flex-shrink-0" />
                    <div className="truncate">
                      <span className="text-[13px] font-bold text-heading-dark block truncate">{file.name}</span>
                      <span className="text-[10px] text-gray-text font-bold block">{(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setFile(null);
                    }}
                    className="text-slate-400 hover:text-red-500 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}

              {/* Status Indicator */}
              {status === 'uploading' && (
                <div className="flex items-center gap-3 p-3.5 rounded-btn bg-blue-50 text-blue-600 border border-blue-200">
                  <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" />
                  <span className="text-[13px] font-semibold">{t('dashboard.uploading')}</span>
                </div>
              )}

              {status === 'error' && (
                <div className="flex items-center gap-3 p-3.5 rounded-btn bg-red-50 text-red-600 border border-red-200">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span className="text-[13px] font-semibold">{message}</span>
                </div>
              )}

              <p className="text-[11px] text-gray-text leading-relaxed font-medium">
                <strong>Format requirement:</strong> The CSV/JSON should contain at least a <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">case_no</code> column/key. You may optionally provide coordinates (<code className="bg-slate-100 px-1 py-0.5 rounded font-mono">latitude, longitude</code>), <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">complainant_name</code>, <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">accused_name</code>, and <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">brief_facts</code>.
              </p>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-border-light bg-slate-50/50 flex justify-end gap-3">
          {status === 'success' ? (
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm bg-primary-blue text-white rounded-lg font-bold hover:opacity-90 transition cursor-pointer"
            >
              Done
            </button>
          ) : (
            <>
              <button
                onClick={onClose}
                disabled={status === 'uploading'}
                className="px-4 py-2 text-sm text-[var(--color-gray-text)] hover:bg-[var(--color-hover-light)] rounded-lg cursor-pointer"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={handleUpload}
                disabled={!file || status === 'uploading'}
                className="px-4 py-2 text-sm bg-primary-blue text-white rounded-lg font-bold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition cursor-pointer"
              >
                Upload & Sync
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
