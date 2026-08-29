'use client';

import React, { useState } from 'react';
import { Activity, CheckCircle2, AlertCircle, BarChart3, ArrowRight, ShieldCheck } from 'lucide-react';

interface SLAComplianceRadarProps {
  title?: string;
  data?: any;
  onAction?: (payload: any) => void;
}

export const SLAComplianceRadar: React.FC<SLAComplianceRadarProps> = ({
  title = "SLA First-Response & Resolution Radar",
  data,
  onAction,
}) => {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
            <Activity className="w-4 h-4 text-teal-600" /> {title}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">Visual compliance gauge tracking percent of tickets meeting strict 15-minute response.</p>
        </div>
        <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200">
          LIVE TELEMETRY
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 text-xs">
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Throughput</span>
          <p className="text-base font-extrabold text-slate-900 font-mono">98.4%</p>
          <span className="text-[10px] text-emerald-600 font-semibold">&uarr; +2.3% vs avg</span>
        </div>
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Avg Duration</span>
          <p className="text-base font-extrabold text-slate-900 font-mono">4m 12s</p>
          <span className="text-[10px] text-teal-600 font-semibold">Optimal</span>
        </div>
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Audit Status</span>
          <p className="text-base font-extrabold text-emerald-600 font-mono">VERIFIED</p>
          <span className="text-[10px] text-slate-400">100% Logged</span>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-gradient-to-r from-slate-900 to-slate-800 text-white text-xs space-y-2">
        <div className="flex justify-between items-center text-[11px] text-slate-300 font-medium">
          <span>Enterprise Real-Time Event Stream</span>
          <span className="font-mono text-teal-400">Node Sync: OK</span>
        </div>
        <div className="font-mono text-[10px] text-slate-400 bg-black/40 p-2.5 rounded-lg space-y-1">
          <p className="text-emerald-400">&gt; [OK] Telemetry connection active on socket wss://stream.support.internal</p>
          <p className="text-slate-300">&gt; [SYNC] Verified 2,490 active ledger checkpoints with zero anomalies.</p>
        </div>
      </div>
    </div>
  );
};
