'use client';

import React, { useState, useEffect } from 'react';
import {
  Package,
  Search,
  MessageSquare,
  RotateCcw,
  HelpCircle,
  Clock,
  CheckCircle,
  Truck,
  AlertTriangle,
  Send,
  Sparkles,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';
import { ApiClient } from '@/lib/api';

export default function CustomerPortalPage() {
  const [orderQuery, setOrderQuery] = useState('ORD-5001');
  const [orderData, setOrderData] = useState<any>(null);
  const [loadingOrder, setLoadingOrder] = useState(false);
  const [orderError, setOrderError] = useState<string | null>(null);

  // Guided Troubleshooting state
  const [troubleshootingNode, setTroubleshootingNode] = useState<any>(null);
  const [isResolvedDeflected, setIsResolvedDeflected] = useState(false);

  // New Case Filing state
  const [caseTitle, setCaseTitle] = useState('');
  const [caseDesc, setCaseDesc] = useState('');
  const [aiTriage, setAiTriage] = useState<any>(null);
  const [filingCase, setFilingCase] = useState(false);
  const [filedCaseNumber, setFiledCaseNumber] = useState<string | null>(null);

  // Quick Live Chat Widget state
  const [chatMessages, setChatMessages] = useState<Array<{ sender: string; text: string; time: string }>>([
    {
      sender: 'BOT',
      text: 'Hello! I am your AI Support Assistant. Enter your order issue or tracking number and I will guide you to a fast resolution.',
      time: 'Just now',
    },
  ]);
  const [chatInput, setChatInput] = useState('');

  // Initial order search
  useEffect(() => {
    handleLookupOrder('ORD-5001');
    handleStartTroubleshooting();
  }, []);

  const handleLookupOrder = async (orderId: string) => {
    setLoadingOrder(true);
    setOrderError(null);
    try {
      const data = await ApiClient.trackOrder(orderId.trim());
      if (data) {
        setOrderData(data);
      } else {
        setOrderError('Order not found. Please verify order number (e.g. ORD-5001 or ORD-5002).');
      }
    } catch (e: any) {
      setOrderError(e.message || 'Unable to fetch order status');
    } finally {
      setLoadingOrder(false);
    }
  };

  const handleStartTroubleshooting = () => {
    setTroubleshootingNode({
      question: 'What issue are you experiencing with your purchase today?',
      options: [
        { key: 'DAMAGED', label: 'Item arrived damaged or cracked in transit', next: 'DAMAGED_OPTIONS' },
        { key: 'LATE', label: 'Package has not arrived / Delivery is overdue', next: 'LATE_OPTIONS' },
        { key: 'WRONG_ITEM', label: 'Received incorrect item or wrong color', next: 'WRONG_ITEM_OPTIONS' },
      ],
    });
    setIsResolvedDeflected(false);
  };

  const handleTroubleshootChoice = (opt: any) => {
    if (opt.key === 'DAMAGED') {
      setTroubleshootingNode({
        question: 'All electronics and audio items are covered under our 30-Day Zero-Cost Replacement Guarantee. Would you like to file a replacement request?',
        options: [
          { key: 'PROCEED_REPLACE', label: 'Yes, request immediate replacement dispatch', action: 'PREFILL_CASE_DAMAGED' },
          { key: 'READ_POLICY', label: 'View 30-Day Return & Replacement Policy', action: 'DEFLECT' },
        ],
      });
    } else if (opt.action === 'PREFILL_CASE_DAMAGED') {
      setCaseTitle('AeroSound Headphones Arrived Damaged');
      setCaseDesc('The shipping container was crushed upon arrival and the headband is cracked. Please send an expedited replacement.');
      handleAnalyzeDescription('The shipping container was crushed upon arrival and the headband is cracked. Please send an expedited replacement.');
    } else if (opt.action === 'DEFLECT') {
      setIsResolvedDeflected(true);
    } else {
      setTroubleshootingNode({
        question: 'Thank you. Our support system is ready to assist you. Would you like to submit a ticket for our priority queue?',
        options: [
          { key: 'SUBMIT_TICKET', label: 'File support ticket now', action: 'PREFILL_CASE_DAMAGED' },
        ],
      });
    }
  };

  const handleAnalyzeDescription = async (text: string) => {
    if (text.length > 10) {
      try {
        const triage = await ApiClient.classifyText(text);
        setAiTriage(triage);
      } catch (e) {
        console.error(e);
      }
    }
  };

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    setFilingCase(true);
    try {
      const res = await ApiClient.createCase({
        customer_id: 'CUST-1001', // Default seeded VIP customer
        title: caseTitle || 'Product Support Claim',
        description: caseDesc,
        category: aiTriage?.suggested_category || 'PRODUCT',
        priority: aiTriage?.suggested_priority || 'HIGH',
        order_id: orderQuery || 'ORD-5001',
        source: 'WEB_PORTAL',
      });
      setFiledCaseNumber(res.case_number);
    } catch (e: any) {
      alert(`Error submitting case: ${e.message}`);
    } finally {
      setFilingCase(false);
    }
  };

  const handleSendChat = async () => {
    if (!chatInput.trim()) return;
    const userText = chatInput;
    setChatMessages((prev) => [...prev, { sender: 'CUSTOMER', text: userText, time: 'Just now' }]);
    setChatInput('');

    // AI smart response simulation
    try {
      const triage = await ApiClient.classifyText(userText);
      let reply = "Thank you for reaching out. I've logged your issue and our support agents are reviewing your order context.";
      if (triage.intent === 'DAMAGED_PRODUCT') {
        reply = "I'm so sorry your product arrived damaged! We can send a replacement right away under our 30-day warranty. I've pre-filled the resolution form below for you.";
        setCaseTitle('Damaged Order Claim');
        setCaseDesc(userText);
        setAiTriage(triage);
      } else if (triage.intent === 'LATE_DELIVERY') {
        reply = "I checked our carrier feeds for you. If your package is delayed, our system can trace the shipment and apply a $10 credit to your account.";
      }
      setTimeout(() => {
        setChatMessages((prev) => [...prev, { sender: 'BOT', text: reply, time: 'Just now' }]);
      }, 500);
    } catch (e) {
      setChatMessages((prev) => [...prev, { sender: 'BOT', text: "Thank you! An agent has received your message.", time: 'Just now' }]);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 space-y-8">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-teal-700 to-slate-900 rounded-3xl p-8 text-white shadow-md flex flex-col md:flex-row justify-between items-center gap-6">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-teal-500/20 text-teal-300 text-xs font-semibold mb-3 border border-teal-400/30">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Customer Self-Service &amp; Resolution Hub</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight">How can we help you today, Sarah?</h1>
          <p className="text-slate-300 text-sm mt-1">Look up live order tracking, file a return/replacement, or chat with AI support.</p>
        </div>

        {/* Quick Order Lookup input */}
        <div className="w-full md:w-96 bg-white/10 backdrop-blur-md p-2 rounded-2xl border border-white/20 flex items-center space-x-2">
          <Search className="w-5 h-5 text-teal-300 ml-2 shrink-0" />
          <input
            type="text"
            value={orderQuery}
            onChange={(e) => setOrderQuery(e.target.value)}
            placeholder="Enter Order # (e.g. ORD-5001)"
            className="bg-transparent text-white placeholder-slate-400 text-sm focus:outline-none w-full font-medium"
          />
          <button
            onClick={() => handleLookupOrder(orderQuery)}
            className="bg-teal-500 hover:bg-teal-400 text-slate-950 px-4 py-2 rounded-xl text-xs font-bold transition-colors shrink-0"
          >
            Track
          </button>
        </div>
      </div>

      {/* Main Grid: Left Column (Order Status & Guided Flow) | Right Column (Live Chat & Filing) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: 7 Cols */}
        <div className="lg:col-span-7 space-y-6">
          {/* Order Details & Logistics Tracking Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center font-bold">
                  <Package className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="font-bold text-slate-900 text-base">
                    Order #{orderData?.order_id || 'ORD-5001'}
                  </h2>
                  <p className="text-xs text-slate-500">
                    Placed on {orderData ? new Date(orderData.placed_at).toLocaleDateString() : 'Recent'} &bull; Delivered
                  </p>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5">
                <CheckCircle className="w-3.5 h-3.5" />
                <span>{orderData?.status || 'DELIVERED'}</span>
              </span>
            </div>

            {/* Order Items */}
            <div className="py-4 space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Items in this order</h3>
              {orderData?.items?.map((item: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="flex items-center space-x-3">
                    <img
                      src={item.image_url || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=100'}
                      alt={item.title}
                      className="w-12 h-12 rounded-lg object-cover border border-slate-200"
                    />
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 line-clamp-1">{item.title}</h4>
                      <p className="text-[11px] text-slate-500 font-mono">SKU: {item.sku} &bull; Qty: {item.quantity}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs font-bold text-slate-900">${(item.total_price_cents / 100).toFixed(2)}</p>
                    <span className="text-[10px] text-teal-600 font-semibold">Eligible for Replacement</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Carrier Tracking Milestones */}
            {orderData?.shipments?.[0] && (
              <div className="pt-4 border-t border-slate-100">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                    <Truck className="w-3.5 h-3.5 text-teal-600" /> Carrier Milestone Feed ({orderData.shipments[0].carrier})
                  </h3>
                  <span className="text-xs font-mono text-slate-600 font-medium">Tracking: {orderData.shipments[0].tracking_number}</span>
                </div>
                <div className="space-y-3 relative pl-4 border-l-2 border-teal-500">
                  {orderData.shipments[0].tracking_history?.map((event: any, i: number) => (
                    <div key={i} className="relative">
                      <div className="w-2.5 h-2.5 rounded-full bg-teal-500 absolute -left-[21px] top-1 ring-4 ring-white" />
                      <p className="text-xs font-bold text-slate-900">{event.status}: {event.description}</p>
                      <p className="text-[11px] text-slate-400">{event.location} &bull; {new Date(event.timestamp).toLocaleString()}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Guided Interactive Troubleshooting Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <div className="flex items-center space-x-2 mb-4">
              <Sparkles className="w-5 h-5 text-teal-600" />
              <h2 className="font-bold text-base text-slate-900">Guided Troubleshooting &amp; Deflection</h2>
            </div>

            {isResolvedDeflected ? (
              <div className="p-4 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200">
                <h3 className="font-bold text-sm">Issue Resolved!</h3>
                <p className="text-xs mt-1">Thank you for checking our self-service guides. If you need anything else, feel free to chat with us anytime.</p>
                <button
                  onClick={handleStartTroubleshooting}
                  className="mt-3 text-xs font-bold text-emerald-700 underline"
                >
                  Restart Troubleshooting
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-sm font-semibold text-slate-800">{troubleshootingNode?.question}</p>
                <div className="space-y-2">
                  {troubleshootingNode?.options?.map((opt: any, idx: number) => (
                    <button
                      key={idx}
                      onClick={() => handleTroubleshootChoice(opt)}
                      className="w-full text-left p-3 rounded-xl border border-slate-200 hover:border-teal-500 hover:bg-teal-50/50 transition-all flex items-center justify-between text-xs font-medium text-slate-700"
                    >
                      <span>{opt.label}</span>
                      <ChevronRight className="w-4 h-4 text-slate-400" />
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: 5 Cols (Live Chat & Instant Ticket Filing) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Real-Time Live Support Chat */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[420px]">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/70 rounded-t-2xl">
              <div className="flex items-center space-x-2">
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                <h3 className="font-bold text-xs text-slate-900">Live AI Support Concierge</h3>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-teal-100 text-teal-800 font-semibold">Online</span>
            </div>

            {/* Messages Scroll Area */}
            <div className="flex-1 p-4 overflow-y-auto space-y-3">
              {chatMessages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex flex-col ${msg.sender === 'CUSTOMER' ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl p-3 text-xs ${
                      msg.sender === 'CUSTOMER'
                        ? 'bg-teal-600 text-white rounded-br-none'
                        : 'bg-slate-100 text-slate-800 rounded-bl-none'
                    }`}
                  >
                    <p>{msg.text}</p>
                  </div>
                  <span className="text-[10px] text-slate-400 mt-1 px-1">{msg.time}</span>
                </div>
              ))}
            </div>

            {/* Chat Input */}
            <div className="p-3 border-t border-slate-100 flex items-center space-x-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
                placeholder="Type your question or issue..."
                className="flex-1 text-xs border border-slate-200 rounded-xl px-3 py-2.5 focus:outline-none focus:border-teal-500"
              />
              <button
                onClick={handleSendChat}
                className="p-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-xl transition-colors shrink-0"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Instant Ticket Submission Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <h3 className="font-bold text-sm text-slate-900 mb-1">File a Support &amp; Resolution Claim</h3>
            <p className="text-xs text-slate-500 mb-4">Our AI will automatically assign a specialized agent and calculate SLA urgency.</p>

            {filedCaseNumber ? (
              <div className="p-4 rounded-xl bg-teal-50 border border-teal-200 text-teal-900">
                <div className="flex items-center space-x-2 font-bold text-sm">
                  <CheckCircle className="w-5 h-5 text-teal-600" />
                  <span>Case Filed: #{filedCaseNumber}</span>
                </div>
                <p className="text-xs mt-2 leading-relaxed">
                  Your claim has been assigned to our Hardware &amp; Replacement specialist team. You will receive email notifications with tracking updates.
                </p>
              </div>
            ) : (
              <form onSubmit={handleCreateCase} className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Issue Title</label>
                  <input
                    type="text"
                    required
                    value={caseTitle}
                    onChange={(e) => setCaseTitle(e.target.value)}
                    placeholder="e.g. Headphones arrived damaged in box"
                    className="w-full text-xs border border-slate-200 rounded-xl px-3 py-2 focus:outline-none focus:border-teal-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Details &amp; Description</label>
                  <textarea
                    required
                    rows={3}
                    value={caseDesc}
                    onChange={(e) => {
                      setCaseDesc(e.target.value);
                      handleAnalyzeDescription(e.target.value);
                    }}
                    placeholder="Describe what happened with the product or delivery..."
                    className="w-full text-xs border border-slate-200 rounded-xl px-3 py-2 focus:outline-none focus:border-teal-500"
                  />
                </div>

                {aiTriage && (
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-bold text-slate-700">AI Intent Detection:</span>
                      <span className="px-2 py-0.5 rounded-full bg-teal-100 text-teal-800 text-[10px] font-bold">
                        {aiTriage.intent} ({Math.round(aiTriage.confidence_score * 100)}%)
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Recommended Category: <strong className="text-slate-800">{aiTriage.suggested_category}</strong> &bull; Priority: <strong className="text-slate-800">{aiTriage.suggested_priority}</strong>
                    </p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={filingCase}
                  className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-md transition-colors"
                >
                  {filingCase ? 'Submitting & Routing Case...' : 'Submit Resolution Request'}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
