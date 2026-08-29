'use client';

import React, { useState } from 'react';
import { AlertTriangle, ShieldAlert, X, ArrowUpRight } from 'lucide-react';

interface EscalationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmitEscalation: (reason: string, targetRole: string) => Promise<void>;
  caseNumber?: string;
}

export const EscalationDrawer: React.FC<EscalationDrawerProps> = ({
  isOpen,
  onClose,
  onSubmitEscalation,
  caseNumber,
}) => {
  const [targetRole, setTargetRole] = useState('MANAGER');
  const [reason, setReason] = useState('Customer requested supervisor review regarding shipping delay');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmitEscalation(reason, targetRole);
      onClose();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex justify-end">
      <div className="bg-white w-full max-w-md h-full shadow-2xl p-6 flex flex-col justify-between space-y-4">
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="font-bold text-sm text-rose-900 flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4 text-rose-600" /> Case Escalation Matrix
            </h3>
            <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-600 rounded-lg">
              <X className="w-4 h-4" />
            </button>
          </div>

          <p className="text-xs text-slate-500">
            Escalating case <strong className="text-slate-900 font-mono">#{caseNumber}</strong> reassigns the issue to elevated leadership and adjusts SLA priority timers.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block font-bold text-slate-700 mb-1">Target Leadership Tier</label>
              <select
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 bg-white focus:outline-none focus:border-rose-500 font-semibold"
              >
                <option value="TEAM_LEAD">Tier 2 Team Lead (Technical &amp; Hardware)</option>
                <option value="MANAGER">Support Operations Manager</option>
                <option value="EXECUTIVE">Executive / VIP Concierge Escalations</option>
              </select>
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1">Escalation Justification</label>
              <textarea
                required
                rows={4}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Explain why supervisor intervention is required..."
                className="w-full border border-slate-200 rounded-xl p-3 focus:outline-none focus:border-rose-500"
              />
            </div>

            <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-950 flex items-start gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <p className="text-[11px] leading-relaxed">
                Case status will immediately switch to <strong>ESCALATED</strong> and notification alerts will be sent via Slack/Email.
              </p>
            </div>

            <div className="flex items-center space-x-2 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 py-2.5 rounded-xl border border-slate-200 text-slate-700 font-bold hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold transition-colors shadow-sm flex items-center justify-center gap-1.5"
              >
                <span>{loading ? 'Escalating...' : 'Confirm Escalation'}</span>
                <ArrowUpRight className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
