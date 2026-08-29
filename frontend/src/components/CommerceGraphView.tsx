'use client';

import React from 'react';
import { Package, Truck, CreditCard, RotateCcw, User, ArrowRight, CheckCircle2 } from 'lucide-react';
import { CommerceGraph } from '@/types';

interface CommerceGraphViewProps {
  graph: CommerceGraph | null;
}

export const CommerceGraphView: React.FC<CommerceGraphViewProps> = ({ graph }) => {
  if (!graph || !graph.active_order) {
    return (
      <div className="p-6 text-center text-xs text-slate-400 bg-slate-50 rounded-xl border border-slate-200">
        No active commerce order attached to this case.
      </div>
    );
  }

  const order = graph.active_order;
  const shipment = order.shipments?.[0];

  return (
    <div className="space-y-4">
      {/* Visual Network Architecture Graph */}
      <div className="p-4 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white shadow-md border border-slate-700">
        <h4 className="text-[11px] font-bold uppercase tracking-wider text-teal-400 mb-3 flex items-center gap-1.5">
          <Package className="w-3.5 h-3.5" /> 360° Unified Commerce Topology
        </h4>

        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          {/* Node 1: Customer */}
          <div className="p-2.5 rounded-xl bg-white/10 backdrop-blur-sm border border-white/15 flex flex-col items-center">
            <User className="w-4 h-4 text-teal-300 mb-1" />
            <span className="font-bold text-[11px]">Customer</span>
            <span className="text-[10px] text-slate-300 truncate max-w-[80px]">VIP Platinum</span>
          </div>

          {/* Node 2: Order */}
          <div className="p-2.5 rounded-xl bg-white/10 backdrop-blur-sm border border-teal-400/40 flex flex-col items-center shadow-xs">
            <Package className="w-4 h-4 text-teal-400 mb-1" />
            <span className="font-bold text-[11px]">#{order.order_id}</span>
            <span className="text-[10px] text-teal-300">${(order.total_amount_cents / 100).toFixed(2)}</span>
          </div>

          {/* Node 3: Carrier */}
          <div className="p-2.5 rounded-xl bg-white/10 backdrop-blur-sm border border-white/15 flex flex-col items-center">
            <Truck className="w-4 h-4 text-indigo-300 mb-1" />
            <span className="font-bold text-[11px]">{shipment?.carrier || 'FedEx'}</span>
            <span className="text-[10px] text-emerald-400 font-bold">DELIVERED</span>
          </div>
        </div>
      </div>

      {/* Order Line Items breakdown */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
        <div className="flex justify-between items-center text-xs font-bold text-slate-900 pb-2 border-b border-slate-100">
          <span>Purchased Items ({order.items.length})</span>
          <span className="font-mono">${(order.total_amount_cents / 100).toFixed(2)}</span>
        </div>

        <div className="space-y-2">
          {order.items.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-50 border border-slate-100">
              <div className="space-y-0.5">
                <p className="font-bold text-slate-900 line-clamp-1">{item.title}</p>
                <p className="text-[10px] text-slate-500 font-mono">
                  SKU: {item.sku} &bull; Qty: {item.quantity} &bull; ${(item.unit_price_cents / 100).toFixed(2)} ea
                </p>
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${item.is_returnable ? 'bg-teal-50 text-teal-700' : 'bg-slate-200 text-slate-600'}`}>
                {item.is_returnable ? 'Returnable' : 'Final Sale'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
