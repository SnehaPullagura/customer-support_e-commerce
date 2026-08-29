import Link from 'next/link';
import {
  ShoppingBag,
  Headphones,
  ShieldCheck,
  Zap,
  Clock,
  BookOpen,
  ArrowRight,
  TrendingUp,
  Cpu,
  Workflow,
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 flex flex-col justify-center">
      {/* Hero Banner */}
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-teal-50 text-teal-700 text-xs font-semibold uppercase tracking-wider mb-4 border border-teal-200">
          <Cpu className="w-3.5 h-3.5 text-teal-600" />
          <span>Production Support & Resolution Engine</span>
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
          Unified Commerce Context &amp; <span className="text-teal-600">AI-Powered Resolution</span>
        </h1>
        <p className="mt-4 text-base sm:text-lg text-slate-600 leading-relaxed">
          Resolve customer order issues, investigate logistics exceptions, execute structured resolution playbooks, and automate refunds with full omnichannel telemetry.
        </p>
      </div>

      {/* 3 Main Workspaces Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto w-full mb-14">
        {/* Customer Self-Service Portal */}
        <Link
          href="/customer"
          className="group relative bg-white rounded-2xl p-7 shadow-sm hover:shadow-xl border border-slate-200 hover:border-teal-400 transition-all flex flex-col justify-between"
        >
          <div>
            <div className="w-12 h-12 rounded-xl bg-teal-100/70 text-teal-700 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <ShoppingBag className="w-6 h-6" />
            </div>
            <div className="flex items-center space-x-2 mb-2">
              <h2 className="text-xl font-bold text-slate-900 group-hover:text-teal-600 transition-colors">
                Customer Portal
              </h2>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-mono font-medium">Self-Service</span>
            </div>
            <p className="text-sm text-slate-600 leading-relaxed">
              Order tracking, real-time live chat widget, return &amp; RMA filings, and guided interactive troubleshooting deflection.
            </p>
          </div>
          <div className="mt-6 flex items-center text-sm font-semibold text-teal-600 group-hover:translate-x-1 transition-transform">
            <span>Enter Customer Portal</span>
            <ArrowRight className="w-4 h-4 ml-1.5" />
          </div>
        </Link>

        {/* Agent Support Cockpit */}
        <Link
          href="/agent"
          className="group relative bg-white rounded-2xl p-7 shadow-sm hover:shadow-xl border border-slate-200 hover:border-indigo-400 transition-all flex flex-col justify-between"
        >
          <div>
            <div className="w-12 h-12 rounded-xl bg-indigo-100/70 text-indigo-700 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Headphones className="w-6 h-6" />
            </div>
            <div className="flex items-center space-x-2 mb-2">
              <h2 className="text-xl font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                Agent Cockpit
              </h2>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 font-mono font-medium">3-Column Live</span>
            </div>
            <p className="text-sm text-slate-600 leading-relaxed">
              360° unified commerce context, real-time omnichannel threads, AI response copilot, and automated resolution playbook execution.
            </p>
          </div>
          <div className="mt-6 flex items-center text-sm font-semibold text-indigo-600 group-hover:translate-x-1 transition-transform">
            <span>Launch Agent Cockpit</span>
            <ArrowRight className="w-4 h-4 ml-1.5" />
          </div>
        </Link>

        {/* Admin & Operations Console */}
        <Link
          href="/admin"
          className="group relative bg-white rounded-2xl p-7 shadow-sm hover:shadow-xl border border-slate-200 hover:border-amber-400 transition-all flex flex-col justify-between"
        >
          <div>
            <div className="w-12 h-12 rounded-xl bg-amber-100/70 text-amber-700 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div className="flex items-center space-x-2 mb-2">
              <h2 className="text-xl font-bold text-slate-900 group-hover:text-amber-600 transition-colors">
                Admin Console
              </h2>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 font-mono font-medium">Operations</span>
            </div>
            <p className="text-sm text-slate-600 leading-relaxed">
              Live operational metrics, SLA breach streams, intelligent routing rules, agent workloads, and immutable audit explorer.
            </p>
          </div>
          <div className="mt-6 flex items-center text-sm font-semibold text-amber-600 group-hover:translate-x-1 transition-transform">
            <span>Open Admin Dashboard</span>
            <ArrowRight className="w-4 h-4 ml-1.5" />
          </div>
        </Link>
      </div>

      {/* Feature Capabilities Highlights */}
      <div className="bg-slate-900 text-white rounded-3xl p-8 max-w-6xl mx-auto w-full">
        <h3 className="text-lg font-bold mb-6 text-slate-200 flex items-center gap-2">
          <Zap className="w-5 h-5 text-teal-400" /> Platform Architecture &amp; Engines
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 text-sm">
          <div className="border-l border-slate-800 pl-4">
            <p className="text-xs text-teal-400 font-mono font-medium">Domain 08</p>
            <h4 className="font-bold text-white mt-1">Unified Commerce Graph</h4>
            <p className="text-xs text-slate-400 mt-1">Orders, Shipments, Payments, Returns &amp; Tracking aggregated with zero data duplication.</p>
          </div>
          <div className="border-l border-slate-800 pl-4">
            <p className="text-xs text-indigo-400 font-mono font-medium">Domain 07 &amp; 09</p>
            <h4 className="font-bold text-white mt-1">Routing &amp; SLA Engine</h4>
            <p className="text-xs text-slate-400 mt-1">Multi-factor skill/workload routing with business hours SLA timers and breach triggers.</p>
          </div>
          <div className="border-l border-slate-800 pl-4">
            <p className="text-xs text-amber-400 font-mono font-medium">Domain 12 &amp; 19</p>
            <h4 className="font-bold text-white mt-1">Resolution Playbooks</h4>
            <p className="text-xs text-slate-400 mt-1">Interactive step-by-step decision trees for damaged goods, late shipments, and refunds.</p>
          </div>
          <div className="border-l border-slate-800 pl-4">
            <p className="text-xs text-purple-400 font-mono font-medium">Domain 20 &amp; 23</p>
            <h4 className="font-bold text-white mt-1">Vector RAG &amp; Audit</h4>
            <p className="text-xs text-slate-400 mt-1">Semantic vector retrieval for policy grounded replies and immutable security audit ledger.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
