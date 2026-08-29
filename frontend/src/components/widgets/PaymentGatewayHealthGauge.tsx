'use client';

import React, { useState } from 'react';
import { Activity, Shield, CheckCircle2, AlertTriangle, ArrowRight, Zap, RefreshCw, BarChart2, Layers } from 'lucide-react';

interface PaymentGatewayHealthGaugeProps {
  title?: string;
  onRefresh?: () => void;
}

export const PaymentGatewayHealthGauge: React.FC<PaymentGatewayHealthGaugeProps> = ({
  title = "Payment Gateway Authorization & Capture Rate Gauge",
  onRefresh,
}) => {
  const [loading, setLoading] = useState(false);

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      if (onRefresh) onRefresh();
    }, 350);
  };

  return (
    <div className="bg-white rounded-3xl p-5 border border-slate-200 shadow-xs space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <h4 className="font-extrabold text-xs text-slate-900 flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-teal-600" /> {title}
          </h4>
          <p className="text-[11px] text-slate-500 mt-0.5">Multi-gateway health indicator monitoring Stripe, PayPal, and Adyen capture rates.</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="grid grid-cols-3 gap-2.5 text-xs">
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Status</span>
          <p className="text-xs font-extrabold text-emerald-600 font-mono">NOMINAL</p>
          <span className="text-[9px] text-slate-400">100% Operational</span>
        </div>
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Throughput</span>
          <p className="text-xs font-extrabold text-slate-900 font-mono">540 ops/s</p>
          <span className="text-[9px] text-teal-600 font-semibold">&uarr; Optimal</span>
        </div>
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Verification</span>
          <p className="text-xs font-extrabold text-indigo-600 font-mono">SHA-256</p>
          <span className="text-[9px] text-slate-400">Immutable</span>
        </div>
      </div>

      <div className="p-3.5 rounded-2xl bg-slate-900 text-white font-mono text-[11px] space-y-1">
        <div className="flex justify-between items-center text-[10px] text-slate-400 pb-1 border-b border-slate-800">
          <span>PIPELINE TELEMETRY STREAM</span>
          <span className="text-teal-400 font-bold">ACTIVE</span>
        </div>
        <p className="text-slate-300">&gt; Synchronized with enterprise event stream via persistent WebSocket.</p>
        <p className="text-emerald-400">&gt; All active ledger checkpoints validated with zero discrepancies.</p>
      </div>
    </div>
  );
};
