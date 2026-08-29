'use client';

import React from 'react';
import { Clock, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface SLAProgressCountdownProps {
  dueAtString?: string;
  isBreached?: boolean;
  isPaused?: boolean;
}

export const SLAProgressCountdown: React.FC<SLAProgressCountdownProps> = ({
  dueAtString,
  isBreached,
  isPaused,
}) => {
  if (!dueAtString) {
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-500">
        No SLA Active
      </span>
    );
  }

  if (isPaused) {
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200 flex items-center gap-1">
        <Clock className="w-3 h-3 text-amber-600" /> Paused (Waiting for Customer)
      </span>
    );
  }

  if (isBreached) {
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-300 flex items-center gap-1">
        <AlertTriangle className="w-3 h-3 text-rose-600" /> SLA Breached
      </span>
    );
  }

  return (
    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
      <Clock className="w-3 h-3 text-emerald-600" /> SLA: On Track
    </span>
  );
};
