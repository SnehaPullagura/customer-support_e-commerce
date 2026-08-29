'use client';

import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badgeText?: string;
  badgeColor?: 'emerald' | 'indigo' | 'amber' | 'teal' | 'rose';
  trend?: string;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badgeText,
  badgeColor = 'emerald',
  trend,
}) => {
  const badgeClasses = {
    emerald: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    amber: 'bg-amber-50 text-amber-700 border-amber-200',
    teal: 'bg-teal-50 text-teal-700 border-teal-200',
    rose: 'bg-rose-50 text-rose-700 border-rose-200',
  }[badgeColor];

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-2 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between text-slate-400">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{title}</span>
        <Icon className="w-4 h-4 text-slate-600" />
      </div>

      <div className="flex items-baseline space-x-2">
        <span className="text-2xl sm:text-3xl font-extrabold text-slate-900">{value}</span>
        {badgeText && (
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeClasses}`}>
            {badgeText}
          </span>
        )}
      </div>

      {(subtitle || trend) && (
        <div className="flex items-center justify-between text-[11px] text-slate-400">
          {subtitle && <span>{subtitle}</span>}
          {trend && <span className="font-semibold text-emerald-600">{trend}</span>}
        </div>
      )}
    </div>
  );
};
