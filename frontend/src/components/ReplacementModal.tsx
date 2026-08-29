'use client';

import React, { useState } from 'react';
import { RotateCcw, Truck, X } from 'lucide-react';

interface ReplacementModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmitReplacement: (shippingService: string, notes: string) => Promise<void>;
  orderId?: string;
}

export const ReplacementModal: React.FC<ReplacementModalProps> = ({
  isOpen,
  onClose,
  onSubmitReplacement,
  orderId,
}) => {
  const [shippingService, setShippingService] = useState('FEDEX_PRIORITY_OVERNIGHT');
  const [notes, setNotes] = useState('Zero-cost replacement authorized for damaged item');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmitReplacement(shippingService, notes);
      onClose();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-200 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="font-bold text-sm text-slate-900 flex items-center gap-1.5">
            <RotateCcw className="w-4 h-4 text-teal-600" /> Dispatch Zero-Cost Replacement
          </h3>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-600 rounded-lg">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-bold text-slate-700 mb-1">Target Order</label>
            <input
              type="text"
              disabled
              value={`#${orderId || 'ORD-5001'}`}
              className="w-full bg-slate-100 border border-slate-200 rounded-xl px-3 py-2 text-slate-600 font-mono"
            />
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">Shipping Speed / Service Level</label>
            <select
              value={shippingService}
              onChange={(e) => setShippingService(e.target.value)}
              className="w-full border border-slate-200 rounded-xl px-3 py-2.5 bg-white focus:outline-none focus:border-teal-500 font-semibold text-slate-800"
            >
              <option value="FEDEX_PRIORITY_OVERNIGHT">⚡ FedEx Priority Overnight (1 Business Day)</option>
              <option value="UPS_2ND_DAY_AIR">🚀 UPS 2nd Day Air (2 Business Days)</option>
              <option value="USPS_PRIORITY">📦 USPS Priority Ground (2-3 Business Days)</option>
            </select>
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">Fulfillment Authorization Notes</label>
            <input
              type="text"
              required
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full border border-slate-200 rounded-xl px-3 py-2.5 focus:outline-none focus:border-teal-500"
            />
          </div>

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
              className="flex-1 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold transition-colors shadow-sm"
            >
              {loading ? 'Dispatching...' : 'Dispatch Replacement'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
