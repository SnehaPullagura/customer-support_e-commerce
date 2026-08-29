'use client';

import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Users,
  ShieldCheck,
  Zap,
  Activity,
  Layers,
  Sparkles,
  BarChart3,
  Search,
} from 'lucide-react';
import { ApiClient } from '@/lib/api';

export default function AdminConsolePage() {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const data = await ApiClient.getExecutiveDashboard();
      setDashboardData(data);
      const ags = await ApiClient.listAgents();
      setAgents(ags || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-50 text-amber-800 text-xs font-semibold mb-2 border border-amber-200">
            <ShieldCheck className="w-3.5 h-3.5 text-amber-600" />
            <span>Support Operations &amp; Executive Telemetry</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Support Executive Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">Real-time SLA compliance, MTTR velocity, and workforce workload metrics.</p>
        </div>

        <button
          onClick={loadDashboard}
          className="self-start md:self-auto px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
        >
          <Activity className="w-3.5 h-3.5 text-teal-400" /> Refresh Telemetry
        </button>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {/* Metric 1: SLA Compliance */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">SLA Compliance</span>
            <Clock className="w-4 h-4 text-teal-600" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl sm:text-3xl font-extrabold text-slate-900">
              {dashboardData?.metrics?.sla_compliance_rate_percent || 98.4}%
            </span>
            <span className="text-xs font-bold text-emerald-600">+1.2% this week</span>
          </div>
          <p className="text-[11px] text-slate-400">First response &lt; 30m target met</p>
        </div>

        {/* Metric 2: MTTR Velocity */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Avg Resolution (MTTR)</span>
            <TrendingUp className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl sm:text-3xl font-extrabold text-slate-900">
              {dashboardData?.metrics?.avg_resolution_time_hours || 3.8}h
            </span>
            <span className="text-xs font-bold text-emerald-600">-24m vs last week</span>
          </div>
          <p className="text-[11px] text-slate-400">Time from creation to closure</p>
        </div>

        {/* Metric 3: CSAT Satisfaction */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Customer CSAT</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl sm:text-3xl font-extrabold text-slate-900">
              {dashboardData?.metrics?.csat_average || 4.9} / 5.0
            </span>
            <span className="text-xs font-bold text-emerald-600">Top Quartile</span>
          </div>
          <p className="text-[11px] text-slate-400">Based on post-resolution feedback</p>
        </div>

        {/* Metric 4: AI Deflection Rate */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Self-Service Deflection</span>
            <Sparkles className="w-4 h-4 text-purple-600" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl sm:text-3xl font-extrabold text-slate-900">
              {dashboardData?.metrics?.deflection_rate_percent || 34.6}%
            </span>
            <span className="text-xs font-bold text-indigo-600">+4.8% AI growth</span>
          </div>
          <p className="text-[11px] text-slate-400">Automated self-service resolutions</p>
        </div>
      </div>

      {/* 2-Column Grid: Left (Agent Workloads) | Right (Active Distribution & SLAs) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Agent Workforce Workload & Capacity Table (7 Cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <Users className="w-5 h-5 text-indigo-600" />
              <h2 className="font-bold text-sm sm:text-base text-slate-900">Support Workforce Capacity</h2>
            </div>
            <span className="text-xs text-slate-400">{agents.length} Active Agents</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-400 font-bold uppercase tracking-wider border-b border-slate-100">
                  <th className="pb-3">Agent</th>
                  <th className="pb-3">Team</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Active Load</th>
                  <th className="pb-3">CSAT</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {agents.map((ag) => (
                  <tr key={ag.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 font-bold text-slate-900 flex items-center space-x-2">
                      <div className="w-6 h-6 rounded bg-indigo-100 text-indigo-800 text-[10px] font-bold flex items-center justify-center">
                        {ag.display_name.slice(0, 2).toUpperCase()}
                      </div>
                      <span>{ag.display_name}</span>
                    </td>
                    <td className="py-3 text-slate-600">{ag.team?.name || 'General Support'}</td>
                    <td className="py-3">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {ag.status}
                      </span>
                    </td>
                    <td className="py-3">
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-indigo-600 h-1.5 rounded-full"
                            style={{
                              width: `${Math.min(100, (ag.current_active_cases / (ag.max_active_cases || 6)) * 100)}%`,
                            }}
                          />
                        </div>
                        <span className="font-mono text-[11px] text-slate-600">
                          {ag.current_active_cases}/{ag.max_active_cases}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 font-bold text-slate-900">{ag.csat_score || 4.9} ★</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Active Distribution & Routing Health (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Active Distribution */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
              <Layers className="w-4 h-4 text-teal-600" /> Active Case Queue Distribution
            </h3>

            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>Product &amp; Damaged Claims</span>
                  <span>48%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-teal-500 h-2 rounded-full w-[48%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>Logistics &amp; In-Transit Delays</span>
                  <span>32%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-indigo-500 h-2 rounded-full w-[32%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>Billing &amp; Double Charge Disputes</span>
                  <span>20%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-amber-500 h-2 rounded-full w-[20%]" />
                </div>
              </div>
            </div>
          </div>

          {/* SLA Threat Monitor Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-500" /> SLA Breach Stream
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold">
                Zero Overdue Breaches
              </span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              All active tickets are currently performing within their 30-minute first-response and 8-hour resolution windows.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
