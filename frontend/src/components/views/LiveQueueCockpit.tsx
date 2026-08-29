'use client';

import React, { useState, useEffect } from 'react';
import { Layout, Shield, Bell, Search, Filter, RefreshCw, CheckCircle2, ArrowRight, Zap, Database } from 'lucide-react';

interface LiveQueueCockpitProps {
  initialData?: any;
  onRefresh?: () => void;
}

export const LiveQueueCockpit: React.FC<LiveQueueCockpitProps> = ({
  initialData,
  onRefresh,
}) => {
  const [loading, setLoading] = useState(false);
  const [filterText, setFilterText] = useState('');
  const [activeSegment, setActiveSegment] = useState('ALL');

  const handleTriggerAction = async () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      if (onRefresh) onRefresh();
    }, 500);
  };

  return (
    <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-xl bg-teal-50 text-teal-700 border border-teal-200">
              <Zap className="w-4 h-4" />
            </span>
            <h2 className="text-base font-extrabold text-slate-900 tracking-tight">Live Agent Queue Real-Time Cockpit</h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">High-density queue monitor with live WebSocket status and priority filters.</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleTriggerAction}
            disabled={loading}
            className="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Sync Live</span>
          </button>
          <button className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs transition-colors shadow-xs">
            Export Report
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase">Real-Time Load</span>
          <p className="text-xl font-extrabold text-slate-900 font-mono">1,482</p>
          <span className="text-[10px] text-emerald-600 font-bold">Stable &bull; 99.98%</span>
        </div>
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase">Avg Response</span>
          <p className="text-xl font-extrabold text-slate-900 font-mono">1m 42s</p>
          <span className="text-[10px] text-teal-600 font-bold">&darr; 18s vs benchmark</span>
        </div>
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase">First-Contact SLA</span>
          <p className="text-xl font-extrabold text-slate-900 font-mono">97.4%</p>
          <span className="text-[10px] text-emerald-600 font-bold">Target: &gt;95.0%</span>
        </div>
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase">CSAT Index</span>
          <p className="text-xl font-extrabold text-amber-600 font-mono">4.92 / 5.0</p>
          <span className="text-[10px] text-slate-500">340 ratings today</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            placeholder="Search active streams, order numbers, or telemetry events..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:border-teal-500"
          />
        </div>
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs font-bold text-slate-600">
          <button
            onClick={() => setActiveSegment('ALL')}
            className="px-3 py-1.5 rounded-lg bg-white text-slate-900 shadow-xs"
          >
            All
          </button>
          <button
            onClick={() => setActiveSegment('VIP')}
            className="px-3 py-1.5 rounded-lg text-slate-600"
          >
            VIP Platinum
          </button>
          <button
            onClick={() => setActiveSegment('ESCALATED')}
            className="px-3 py-1.5 rounded-lg text-slate-600"
          >
            Escalations
          </button>
        </div>
      </div>

      <div className="p-4 rounded-2xl bg-slate-900 text-white font-mono text-xs space-y-2">
        <div className="flex items-center justify-between text-slate-400 pb-2 border-b border-slate-800 text-[11px]">
          <span className="flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-teal-400" /> Event Pipeline Ledger
          </span>
          <span className="text-emerald-400 font-bold">STREAM ACTIVE</span>
        </div>
        <div className="space-y-1 text-[11px] text-slate-300">
          <p><span className="text-teal-400">[2026-08-29 10:14:02]</span> Order ORD-9901 shipment milestone updated &rarr; DELIVERED</p>
          <p><span className="text-teal-400">[2026-08-29 10:14:15]</span> Playbook DAMAGED_PRODUCT_PLAYBOOK step 3 executed by Agent ID: AG-4001</p>
          <p><span className="text-teal-400">[2026-08-29 10:14:28]</span> Zero-cost replacement order ORD-9901-REPLACE created in fulfillment queue</p>
          <p><span className="text-emerald-400">[2026-08-29 10:14:40]</span> Customer satisfaction pulse received: 5/5 Stars &bull; "Extremely fast resolution!"</p>
        </div>
      </div>
    </div>
  );
};
