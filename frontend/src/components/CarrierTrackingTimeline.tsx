'use client';

import React from 'react';
import { Truck, CheckCircle2, Clock, AlertTriangle, MapPin } from 'lucide-react';
import { CommerceShipment } from '@/types';

interface CarrierTrackingTimelineProps {
  shipment?: CommerceShipment;
}

export const CarrierTrackingTimeline: React.FC<CarrierTrackingTimelineProps> = ({ shipment }) => {
  if (!shipment) {
    return (
      <div className="p-4 text-center text-xs text-slate-400 bg-slate-50 rounded-xl">
        No tracking data available.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs pb-2 border-b border-slate-100">
        <span className="font-bold text-slate-800 flex items-center gap-1.5">
          <Truck className="w-4 h-4 text-teal-600" /> Carrier: {shipment.carrier}
        </span>
        <span className="font-mono text-slate-600 font-medium">#{shipment.tracking_number}</span>
      </div>

      <div className="relative pl-4 space-y-3 border-l-2 border-teal-500">
        {shipment.tracking_history?.map((event, idx) => (
          <div key={idx} className="relative text-xs">
            <div className="w-2.5 h-2.5 rounded-full bg-teal-500 absolute -left-[21px] top-1 ring-4 ring-white" />
            <p className="font-bold text-slate-900">{event.status}: {event.description}</p>
            <p className="text-[10px] text-slate-400 flex items-center gap-1 mt-0.5">
              {event.location && (
                <>
                  <MapPin className="w-3 h-3 text-slate-400" /> {event.location} &bull;
                </>
              )}
              {new Date(event.timestamp).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
