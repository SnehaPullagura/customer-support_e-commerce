'use client';

import React, { useState } from 'react';
import { Activity, ShieldCheck, CheckCircle2, AlertTriangle, ArrowRight, Zap, RefreshCw, BarChart2 } from 'lucide-react';

interface AutomatedDeflectionGaugeProps {
  title?: string;
  onRefresh?: () => void;
}

export const AutomatedDeflectionGauge: React.FC<AutomatedDeflectionGaugeProps> = ({
  title = "AI Self-Service Deflection & Deflection Rate",
  onRefresh,
}) => {
  const [loading, setLoading] = useState(false);

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      if (onRefresh) onRefresh();
    }, 400);
  };

  return (
    <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-extrabold text-sm text-slate-900 flex items-center gap-2">
            <Zap className="w-4 h-4 text-teal-600" /> {title}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">Measures percent of customer queries resolved without human agent touch.</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-3 gap-3 text-xs">
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Operational Status</span>
          <p className="text-sm font-extrabold text-emerald-600 font-mono">100% ONLINE</p>
          <span className="text-[10px] text-slate-400">Zero errors</span>
        </div>
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Processing Rate</span>
          <p className="text-sm font-extrabold text-slate-900 font-mono">420 msg/sec</p>
          <span className="text-[10px] text-teal-600 font-semibold">Healthy</span>
        </div>
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Audit Verified</span>
          <p className="text-sm font-extrabold text-indigo-600 font-mono">ENCRYPTED</p>
          <span className="text-[10px] text-slate-400">SHA-256 Ledger</span>
        </div>
      </div>

      <div className="p-4 rounded-2xl bg-slate-900 text-white font-mono text-xs space-y-1.5">
        <div className="flex justify-between items-center text-[10px] text-slate-400 pb-1 border-b border-slate-800">
          <span>LIVE TELEMETRY FEED</span>
          <span className="text-teal-400 font-bold">SOCKET CONNECTED</span>
        </div>
        <p className="text-slate-300 text-[11px]">&gt; [OK] Pipeline throughput synchronized at 420 events/sec.</p>
        <p className="text-emerald-400 text-[11px]">&gt; [COMMITTED] All active transactions reconciled with zero exceptions.</p>
      </div>
    </div>
  );
};
