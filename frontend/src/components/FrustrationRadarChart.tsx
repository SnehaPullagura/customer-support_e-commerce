'use client';

import React from 'react';
import { AlertCircle, TrendingDown, TrendingUp, ShieldAlert } from 'lucide-react';

interface FrustrationRadarChartProps {
  score: number;
  factors?: Record<string, any>;
  riskTier?: string;
}

export const FrustrationRadarChart: React.FC<FrustrationRadarChartProps> = ({
  score,
  factors,
  riskTier = 'LOW',
}) => {
  const getBadge = () => {
    if (score >= 70) return { bg: 'bg-rose-100 text-rose-800 border-rose-300', text: 'Critical Risk' };
    if (score >= 40) return { bg: 'bg-amber-100 text-amber-800 border-amber-300', text: 'Elevated Risk' };
    return { bg: 'bg-emerald-100 text-emerald-800 border-emerald-300', text: 'Low Churn Risk' };
  };

  const badge = getBadge();

  return (
    <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
          <ShieldAlert className="w-4 h-4 text-amber-600" /> Customer Churn &amp; Frustration Telemetry
        </h4>
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badge.bg}`}>
          {badge.text}
        </span>
      </div>

      <div className="space-y-1.5">
        <div className="flex justify-between text-xs font-mono">
          <span className="text-slate-500 font-sans">Frustration Score:</span>
          <span className="font-bold text-slate-900">{score.toFixed(1)} / 100</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
          <div
            className={`h-2 rounded-full transition-all duration-500 ${
              score >= 70 ? 'bg-rose-500' : score >= 40 ? 'bg-amber-500' : 'bg-emerald-500'
            }`}
            style={{ width: `${Math.min(100, score)}%` }}
          />
        </div>
      </div>

      {factors && (
        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-200 text-[11px]">
          <div className="p-2 rounded bg-white border border-slate-100">
            <span className="text-slate-400 block text-[10px]">Repeat Contacts (7d)</span>
            <span className="font-bold text-slate-800">{factors.repeat_contacts_7d || 0}</span>
          </div>
          <div className="p-2 rounded bg-white border border-slate-100">
            <span className="text-slate-400 block text-[10px]">Open Issues</span>
            <span className="font-bold text-slate-800">{factors.unresolved_cases || 0}</span>
          </div>
        </div>
      )}
    </div>
  );
};
