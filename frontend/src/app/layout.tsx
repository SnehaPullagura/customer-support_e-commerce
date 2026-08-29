import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';
import { ShoppingBag, Headphones, ShieldCheck, LifeBuoy } from 'lucide-react';

export const metadata: Metadata = {
  title: 'E-Commerce Customer Support & Resolution Platform',
  description: 'Enterprise omnichannel customer support, unified commerce context, and AI resolution cockpit.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 min-h-screen text-slate-900 flex flex-col">
        {/* Global Enterprise Topbar Navigation */}
        <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-lg bg-teal-500 flex items-center justify-center text-slate-950 font-bold shadow-md shadow-teal-500/20">
                <LifeBuoy className="w-5 h-5 text-slate-950" />
              </div>
              <div>
                <Link href="/" className="font-bold text-base tracking-tight text-white flex items-center gap-1.5 hover:text-teal-400 transition-colors">
                  ResolutionCore <span className="text-xs px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-300 font-mono font-medium">Enterprise v1.0</span>
                </Link>
                <p className="text-[11px] text-slate-400 font-medium">Omnichannel Support & Resolution Cockpit</p>
              </div>
            </div>

            {/* Workspace Navigation Switcher */}
            <nav className="flex items-center space-x-1.5 sm:space-x-2 bg-slate-800/80 p-1 rounded-xl border border-slate-700/60">
              <Link
                href="/customer"
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
              >
                <ShoppingBag className="w-3.5 h-3.5 text-teal-400" />
                <span>Customer Portal</span>
              </Link>
              <Link
                href="/agent"
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
              >
                <Headphones className="w-3.5 h-3.5 text-indigo-400" />
                <span>Agent Cockpit</span>
              </Link>
              <Link
                href="/admin"
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
              >
                <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
                <span>Admin Console</span>
              </Link>
            </nav>
          </div>
        </header>

        {/* Workspace Body */}
        <main className="flex-1 flex flex-col">{children}</main>
      </body>
    </html>
  );
}
