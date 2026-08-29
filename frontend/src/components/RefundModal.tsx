'use client';

import React, { useState } from 'react';
import { DollarSign, ShieldAlert, X } from 'lucide-react';

interface RefundModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmitRefund: (amountCents: number, reason: string) => Promise<void>;
  maxRefundableCents: number;
}

export const RefundModal: React.FC<RefundModalProps> = ({
  isOpen,
  onClose,
  onSubmitRefund,
  maxRefundableCents,
}) => {
  const [amountStr, setAmountStr] = useState((maxRefundableCents / 100).toFixed(2));
  const [reason, setReason] = useState('Damaged in transit compensation');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cents = Math.round(parseFloat(amountStr) * 100);
    if (isNaN(cents) || cents <= 0) {
      alert('Please enter a valid refund amount.');
      return;
    }
    setLoading(true);
    try {
      await onSubmitRefund(cents, reason);
      onClose();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  const isHighValue = parseFloat(amountStr) > 100.0;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-200 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="font-bold text-sm text-slate-900 flex items-center gap-1.5">
            <DollarSign className="w-4 h-4 text-emerald-600" /> Issue Customer Refund
          </h3>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-600 rounded-lg">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-bold text-slate-700 mb-1">Refund Amount ($ USD)</label>
            <input
              type="number"
              step="0.01"
              max={(maxRefundableCents / 100).toFixed(2)}
              value={amountStr}
              onChange={(e) => setAmountStr(e.target.value)}
              className="w-full text-sm font-bold border border-slate-200 rounded-xl px-3 py-2.5 focus:outline-none focus:border-emerald-500"
            />
            <p className="text-[10px] text-slate-400 mt-1">Maximum refundable: ${(maxRefundableCents / 100).toFixed(2)}</p>
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">Reason for Refund</label>
            <input
              type="text"
              required
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full border border-slate-200 rounded-xl px-3 py-2.5 focus:outline-none focus:border-emerald-500"
            />
          </div>

          {isHighValue && (
            <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <p className="text-[11px] leading-relaxed">
                Refunds over $100.00 require automated Team Lead approval before payment gateway execution.
              </p>
            </div>
          )}

          <div className="flex items-center space-x-2 pt-2">
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
              className="flex-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition-colors shadow-sm"
            >
              {loading ? 'Submitting...' : 'Authorize Refund'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
