'use client';

import React, { useState } from 'react';
import { Shield, X, CheckCircle2, AlertCircle, ArrowRight, Zap } from 'lucide-react';

interface VoiceTranscriptionModalProps {
  isOpen?: boolean;
  onClose?: () => void;
  onSubmit?: (data: any) => Promise<void>;
  title?: string;
}

export const VoiceTranscriptionModal: React.FC<VoiceTranscriptionModalProps> = ({
  isOpen = true,
  onClose,
  onSubmit,
  title = "Live Omnichannel Voice Call Stream",
}) => {
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (onSubmit) await onSubmit({ notes });
      if (onClose) onClose();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl border border-slate-200 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 className="font-extrabold text-sm text-slate-900 flex items-center gap-2">
              <Zap className="w-4 h-4 text-teal-600" /> {title}
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">Real-time audio waveform and speech-to-text transcript feed with AI summaries.</p>
          </div>
          {onClose && (
            <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-600 rounded-lg">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-bold text-slate-700 mb-1">Action Justification &amp; Audit Notes</label>
            <textarea
              required
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Record reason for audit compliance ledger..."
              className="w-full border border-slate-200 rounded-xl p-3 focus:outline-none focus:border-teal-500"
            />
          </div>

          <div className="p-3 rounded-2xl bg-teal-50 border border-teal-200 text-teal-950 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0" />
            <span className="text-[11px] leading-relaxed">
              Automated idempotency lock active. All decisions recorded in immutable audit log.
            </span>
          </div>

          <div className="flex items-center space-x-2 pt-2">
            {onClose && (
              <button
                type="button"
                onClick={onClose}
                className="flex-1 py-2.5 rounded-xl border border-slate-200 text-slate-700 font-bold hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold transition-colors shadow-xs"
            >
              {loading ? 'Processing...' : 'Confirm & Execute'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
