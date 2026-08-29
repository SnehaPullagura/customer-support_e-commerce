'use client';

import React, { useState, useEffect } from 'react';
import {
  Inbox,
  Clock,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  Send,
  Lock,
  User,
  ShoppingBag,
  CreditCard,
  Truck,
  RotateCcw,
  BookOpen,
  ArrowUpRight,
  TrendingUp,
  Workflow,
  Zap,
  Tag,
  MessageSquare,
  DollarSign,
  AlertTriangle,
  ChevronRight,
  Check,
} from 'lucide-react';
import { ApiClient } from '@/lib/api';

export default function AgentCockpitPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [conversation, setConversation] = useState<any>(null);
  const [commerceContext, setCommerceContext] = useState<any>(null);
  const [aiSuggestedReply, setAiSuggestedReply] = useState<any>(null);
  const [playbooks, setPlaybooks] = useState<any[]>([]);
  const [activePlaybookExecution, setActivePlaybookExecution] = useState<any>(null);

  // Filters & Agent State
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'MINE' | 'HIGH_PRIORITY'>('ALL');
  const [agentStatus, setAgentStatus] = useState<'AVAILABLE' | 'BUSY' | 'AWAY'>('AVAILABLE');
  const [activeTab, setActiveTab] = useState<'COMMERCE' | 'AI_COPILOT' | 'PLAYBOOK' | 'ACTIONS'>('COMMERCE');

  // Composer State
  const [messageText, setMessageText] = useState('');
  const [isInternalNote, setIsInternalNote] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);

  // Quick Action Modal states
  const [actionLoading, setActionLoading] = useState(false);
  const [actionSuccessMsg, setActionSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    loadCases();
    loadPlaybooks();
  }, []);

  const loadCases = async () => {
    try {
      const res = await ApiClient.listCases();
      if (res?.items && res.items.length > 0) {
        setCases(res.items);
        handleSelectCase(res.items[0].id);
      }
    } catch (e) {
      console.error('Failed to load cases:', e);
    }
  };

  const loadPlaybooks = async () => {
    try {
      const pbs = await ApiClient.listPlaybooks();
      setPlaybooks(pbs || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSelectCase = async (caseId: string) => {
    try {
      const caseDetail = await ApiClient.getCase(caseId);
      setSelectedCase(caseDetail);

      // Load conversation
      const conv = await ApiClient.getCaseConversation(caseId);
      setConversation(conv);

      // Load Commerce context graph
      const graph = await ApiClient.getCaseCommerceContext(caseId);
      setCommerceContext(graph);

      // Load AI Suggested Reply
      if (conv?.id) {
        const reply = await ApiClient.getSuggestedReply(conv.id).catch(() => null);
        setAiSuggestedReply(reply);
      }

      // Check if playbook execution exists or start Damaged Product Playbook
      if (caseDetail.category === 'PRODUCT') {
        const exec = await ApiClient.startPlaybook(caseId, 'DAMAGED_PRODUCT_PLAYBOOK').catch(() => null);
        setActivePlaybookExecution(exec);
      }
    } catch (e) {
      console.error('Failed to select case:', e);
    }
  };

  const handleSendMessage = async () => {
    if (!messageText.trim() || !conversation?.id) return;
    setSendingMessage(true);
    try {
      const msg = await ApiClient.sendMessage(conversation.id, messageText, isInternalNote);
      setConversation((prev: any) => ({
        ...prev,
        messages: [...(prev?.messages || []), msg],
      }));
      setMessageText('');
    } catch (e: any) {
      alert(`Failed to send message: ${e.message}`);
    } finally {
      setSendingMessage(false);
    }
  };

  const handleExecutePlaybookStep = async (stepId: string) => {
    if (!activePlaybookExecution?.id) return;
    try {
      const updated = await ApiClient.executePlaybookStep(
        activePlaybookExecution.id,
        stepId,
        'Completed via Agent Cockpit'
      );
      setActivePlaybookExecution(updated);
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleExecuteReplacement = async () => {
    if (!selectedCase?.id) return;
    setActionLoading(true);
    try {
      await ApiClient.resolveCase(
        selectedCase.id,
        'REPLACEMENT',
        'Expedited Zero-Cost Replacement Order authorized for damaged item'
      );
      setActionSuccessMsg('Replacement order dispatched to fulfillment engine!');
      await loadCases();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleExecuteRefund = async () => {
    if (!selectedCase?.id) return;
    setActionLoading(true);
    try {
      await ApiClient.resolveCase(
        selectedCase.id,
        'REFUND',
        'Full refund issued for damaged item ($149.99)',
        14999
      );
      setActionSuccessMsg('Refund processed and credited to original payment method!');
      await loadCases();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleEscalateCase = async () => {
    if (!selectedCase?.id) return;
    setActionLoading(true);
    try {
      await ApiClient.escalateCase(
        selectedCase.id,
        'Customer requested supervisor review for shipping exception',
        'MANAGER'
      );
      setActionSuccessMsg('Case successfully escalated to Tier 2 Support Lead!');
      await loadCases();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="flex-1 flex overflow-hidden h-[calc(100vh-4rem)]">
      {/* ========================================================================= */}
      {/* COLUMN 1: Case Queue & Agent Workload Sidebar (Width: 320px)              */}
      {/* ========================================================================= */}
      <aside className="w-80 bg-white border-r border-slate-200 flex flex-col shrink-0">
        {/* Agent Presence & Workload Card */}
        <div className="p-4 border-b border-slate-100 bg-slate-50/70">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white font-bold flex items-center justify-center text-xs shadow-sm">
                MV
              </div>
              <div>
                <h3 className="text-xs font-bold text-slate-900">Marcus Vance</h3>
                <p className="text-[10px] text-slate-500 font-mono">Tier 2 Hardware Specialist</p>
              </div>
            </div>
            <select
              value={agentStatus}
              onChange={(e: any) => setAgentStatus(e.target.value)}
              className="text-[11px] font-bold bg-white border border-slate-200 rounded-lg px-2 py-1 text-slate-700 focus:outline-none"
            >
              <option value="AVAILABLE">🟢 Available</option>
              <option value="BUSY">🔴 Busy</option>
              <option value="AWAY">🟡 Away</option>
            </select>
          </div>
          {/* Workload Meter */}
          <div className="space-y-1 mt-3">
            <div className="flex justify-between text-[11px] font-medium text-slate-500">
              <span>Active Workload</span>
              <span className="font-bold text-indigo-600">2 / 6 Capacity</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div className="bg-indigo-600 h-1.5 rounded-full w-1/3" />
            </div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex border-b border-slate-100 text-xs font-semibold text-slate-500 bg-slate-50/40 px-2 pt-2">
          <button
            onClick={() => setActiveFilter('ALL')}
            className={`flex-1 pb-2 text-center border-b-2 transition-colors ${
              activeFilter === 'ALL'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            All ({cases.length})
          </button>
          <button
            onClick={() => setActiveFilter('MINE')}
            className={`flex-1 pb-2 text-center border-b-2 transition-colors ${
              activeFilter === 'MINE'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            Assigned (1)
          </button>
          <button
            onClick={() => setActiveFilter('HIGH_PRIORITY')}
            className={`flex-1 pb-2 text-center border-b-2 transition-colors ${
              activeFilter === 'HIGH_PRIORITY'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            Urgent (1)
          </button>
        </div>

        {/* Case List Feed */}
        <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
          {cases.map((c) => {
            const isSelected = selectedCase?.id === c.id;
            return (
              <button
                key={c.id}
                onClick={() => handleSelectCase(c.id)}
                className={`w-full text-left p-3.5 transition-colors flex flex-col space-y-1.5 ${
                  isSelected ? 'bg-indigo-50/60 border-l-4 border-indigo-600' : 'hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono font-bold text-slate-700">
                    {c.case_number}
                  </span>
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      c.priority === 'CRITICAL'
                        ? 'bg-rose-100 text-rose-800'
                        : c.priority === 'HIGH'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-slate-100 text-slate-700'
                    }`}
                  >
                    {c.priority}
                  </span>
                </div>

                <h4 className="text-xs font-bold text-slate-900 line-clamp-1">{c.title}</h4>
                <p className="text-[11px] text-slate-500 line-clamp-1">{c.description}</p>

                <div className="flex items-center justify-between pt-1 text-[10px] text-slate-400">
                  <span className="flex items-center gap-1 font-medium text-emerald-600">
                    <Clock className="w-3 h-3" /> SLA: 28m left
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold font-mono">
                    {c.status}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </aside>

      {/* ========================================================================= */}
      {/* COLUMN 2: Omnichannel Conversation Stream & Composer                      */}
      {/* ========================================================================= */}
      <section className="flex-1 flex flex-col bg-slate-50/60 min-w-0 border-r border-slate-200">
        {/* Case Header Bar */}
        {selectedCase ? (
          <div className="p-4 bg-white border-b border-slate-200 flex items-center justify-between shadow-xs">
            <div className="space-y-0.5">
              <div className="flex items-center space-x-2">
                <h2 className="font-bold text-sm text-slate-900">{selectedCase.title}</h2>
                <span className="text-xs font-mono font-medium text-slate-400">
                  #{selectedCase.case_number}
                </span>
              </div>
              <p className="text-xs text-slate-500 flex items-center gap-2">
                <span>Customer: <strong className="text-slate-800">Sarah Connor</strong></span>
                <span className="px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 text-[10px] font-bold">
                  VIP Platinum
                </span>
                <span>&bull; Order: <strong className="text-slate-800">{selectedCase.order_id || 'ORD-5001'}</strong></span>
              </p>
            </div>

            {/* Quick Status Buttons */}
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-1 rounded-lg bg-teal-50 text-teal-800 border border-teal-200 text-xs font-bold">
                {selectedCase.status}
              </span>
            </div>
          </div>
        ) : (
          <div className="p-4 bg-white border-b border-slate-200">
            <p className="text-xs text-slate-400">Select a case from the queue</p>
          </div>
        )}

        {/* Chronological Messages Stream */}
        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {conversation?.messages?.map((msg: any) => {
            const isInternal = msg.is_internal;
            const isCustomer = msg.sender_type === 'CUSTOMER';
            const isAgent = msg.sender_type === 'AGENT';

            if (isInternal) {
              return (
                <div
                  key={msg.id}
                  className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs space-y-1 shadow-xs max-w-2xl mx-auto"
                >
                  <div className="flex items-center justify-between font-bold text-[11px] text-amber-800">
                    <span className="flex items-center gap-1.5">
                      <Lock className="w-3.5 h-3.5 text-amber-600" /> Internal Staff Note &bull; {msg.sender_name}
                    </span>
                    <span className="text-[10px] font-normal text-amber-700">
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-xs font-medium leading-relaxed">{msg.content}</p>
                </div>
              );
            }

            return (
              <div
                key={msg.id}
                className={`flex flex-col ${isAgent ? 'items-end' : 'items-start'}`}
              >
                <div className="flex items-center space-x-1.5 mb-1 px-1 text-[11px] text-slate-400">
                  <span className="font-bold text-slate-700">{msg.sender_name}</span>
                  <span>&bull; {new Date(msg.created_at).toLocaleTimeString()}</span>
                </div>
                <div
                  className={`max-w-[75%] rounded-2xl p-3.5 text-xs shadow-xs ${
                    isAgent
                      ? 'bg-indigo-600 text-white rounded-br-none'
                      : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none'
                  }`}
                >
                  <p className="leading-relaxed">{msg.content}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* AI Suggested Response Banner */}
        {aiSuggestedReply && (
          <div className="mx-4 mb-2 p-3 rounded-xl bg-gradient-to-r from-indigo-50 to-teal-50 border border-indigo-200 text-xs flex items-start justify-between gap-3 shadow-xs">
            <div className="space-y-1 flex-1">
              <div className="flex items-center space-x-1.5 text-indigo-900 font-bold text-[11px]">
                <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                <span>AI Copilot Suggested Resolution (Confidence: {Math.round(aiSuggestedReply.confidence * 100)}%)</span>
              </div>
              <p className="text-xs text-slate-700 line-clamp-2 italic">
                &ldquo;{aiSuggestedReply.suggested_text}&rdquo;
              </p>
            </div>
            <button
              onClick={() => setMessageText(aiSuggestedReply.suggested_text)}
              className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shrink-0 transition-colors shadow-xs"
            >
              Insert Reply
            </button>
          </div>
        )}

        {/* Message Composer Area */}
        <div className="p-4 bg-white border-t border-slate-200 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={() => setIsInternalNote(false)}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition-colors ${
                  !isInternalNote
                    ? 'bg-indigo-100 text-indigo-800'
                    : 'text-slate-500 hover:bg-slate-100'
                }`}
              >
                Public Message
              </button>
              <button
                type="button"
                onClick={() => setIsInternalNote(true)}
                className={`px-3 py-1 rounded-lg text-xs font-bold flex items-center gap-1 transition-colors ${
                  isInternalNote
                    ? 'bg-amber-100 text-amber-900'
                    : 'text-slate-500 hover:bg-slate-100'
                }`}
              >
                <Lock className="w-3 h-3 text-amber-700" /> Internal Note
              </button>
            </div>
          </div>

          <div className="flex items-end space-x-2">
            <textarea
              rows={2}
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              placeholder={
                isInternalNote
                  ? 'Add private internal notes visible only to support agents...'
                  : 'Type your reply to the customer...'
              }
              className={`flex-1 text-xs border rounded-xl p-3 focus:outline-none ${
                isInternalNote
                  ? 'bg-amber-50/40 border-amber-300 focus:border-amber-500'
                  : 'border-slate-200 focus:border-indigo-500'
              }`}
            />
            <button
              onClick={handleSendMessage}
              disabled={sendingMessage || !messageText.trim()}
              className={`p-3 rounded-xl font-bold text-white transition-colors shrink-0 ${
                isInternalNote ? 'bg-amber-600 hover:bg-amber-500' : 'bg-indigo-600 hover:bg-indigo-500'
              }`}
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* COLUMN 3: Tabbed 360° Context, AI Copilot, Playbook, & Quick Actions     */}
      {/* ========================================================================= */}
      <aside className="w-96 bg-white flex flex-col shrink-0 overflow-hidden">
        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 bg-slate-50 text-[11px] font-bold text-slate-500">
          <button
            onClick={() => setActiveTab('COMMERCE')}
            className={`flex-1 py-3 text-center border-b-2 flex items-center justify-center gap-1 transition-colors ${
              activeTab === 'COMMERCE' ? 'border-teal-600 text-teal-700 bg-white' : 'border-transparent hover:text-slate-900'
            }`}
          >
            <ShoppingBag className="w-3.5 h-3.5" /> 360° Commerce
          </button>
          <button
            onClick={() => setActiveTab('AI_COPILOT')}
            className={`flex-1 py-3 text-center border-b-2 flex items-center justify-center gap-1 transition-colors ${
              activeTab === 'AI_COPILOT' ? 'border-indigo-600 text-indigo-700 bg-white' : 'border-transparent hover:text-slate-900'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" /> AI Copilot
          </button>
          <button
            onClick={() => setActiveTab('PLAYBOOK')}
            className={`flex-1 py-3 text-center border-b-2 flex items-center justify-center gap-1 transition-colors ${
              activeTab === 'PLAYBOOK' ? 'border-amber-600 text-amber-700 bg-white' : 'border-transparent hover:text-slate-900'
            }`}
          >
            <Workflow className="w-3.5 h-3.5" /> Playbook
          </button>
          <button
            onClick={() => setActiveTab('ACTIONS')}
            className={`flex-1 py-3 text-center border-b-2 flex items-center justify-center gap-1 transition-colors ${
              activeTab === 'ACTIONS' ? 'border-purple-600 text-purple-700 bg-white' : 'border-transparent hover:text-slate-900'
            }`}
          >
            <Zap className="w-3.5 h-3.5" /> Actions
          </button>
        </div>

        {/* Tab Content Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* TAB 1: 360° Commerce Context */}
          {activeTab === 'COMMERCE' && (
            <div className="space-y-4">
              {/* Order Card */}
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900">
                    Order #{commerceContext?.active_order?.order_id || 'ORD-5001'}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                    {commerceContext?.active_order?.status || 'DELIVERED'}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500">
                  Total: <strong className="text-slate-800">${((commerceContext?.active_order?.total_amount_cents || 18499) / 100).toFixed(2)}</strong> &bull; Placed: 3 days ago
                </p>

                {/* Items list */}
                <div className="space-y-2 pt-2 border-t border-slate-200">
                  {commerceContext?.active_order?.items?.map((item: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between text-xs bg-white p-2 rounded-lg border border-slate-200">
                      <div className="space-y-0.5">
                        <p className="font-bold text-slate-900 line-clamp-1">{item.title}</p>
                        <p className="text-[10px] text-slate-500 font-mono">SKU: {item.sku} &bull; Qty: {item.quantity}</p>
                      </div>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-teal-50 text-teal-700 font-bold">
                        Returnable
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Carrier Milestone Feed */}
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                  <Truck className="w-3.5 h-3.5 text-teal-600" /> Carrier Milestone Feed (FedEx)
                </h4>
                <div className="space-y-2 text-[11px] pl-2 border-l-2 border-teal-500">
                  <div>
                    <p className="font-bold text-slate-900">DELIVERED: Signed by Front Desk</p>
                    <p className="text-[10px] text-slate-400">Austin, TX &bull; Confirmed 2 days ago</p>
                  </div>
                  <div>
                    <p className="font-bold text-slate-900">OUT FOR DELIVERY</p>
                    <p className="text-[10px] text-slate-400">Austin Hub &bull; 3 days ago</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: AI Copilot & Customer Intelligence */}
          {activeTab === 'AI_COPILOT' && (
            <div className="space-y-4">
              {/* Frustration Gauge */}
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-slate-700">Frustration Index</span>
                  <span className="font-mono font-bold text-amber-600">45.0 / 100 (Medium)</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div className="bg-amber-500 h-2 rounded-full w-[45%]" />
                </div>
                <p className="text-[10px] text-slate-500">
                  Factors: Negative sentiment in latest claim (-0.7), repeat VIP customer.
                </p>
              </div>

              {/* Vector RAG Knowledge Citations */}
              <div className="p-3.5 rounded-xl bg-indigo-50/60 border border-indigo-200 space-y-2">
                <h4 className="text-xs font-bold text-indigo-950 flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-indigo-600" /> Vector RAG Policy Citations
                </h4>
                <div className="p-2 bg-white rounded-lg border border-indigo-100 text-xs space-y-1">
                  <p className="font-bold text-slate-900 text-[11px]">30-Day Electronics Replacement Policy</p>
                  <p className="text-[11px] text-slate-600 italic">
                    &ldquo;All consumer electronics including headphones are eligible for immediate zero-cost replacement dispatch upon carrier delivery verification within 30 days.&rdquo;
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: Interactive Playbook Runner */}
          {activeTab === 'PLAYBOOK' && (
            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-900">
                    {activePlaybookExecution?.playbook?.name || 'Damaged Product Resolution Playbook'}
                  </h4>
                  <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 text-[10px] font-bold">
                    In Progress
                  </span>
                </div>

                {/* Steps Checklist */}
                <div className="space-y-2.5">
                  <div className="flex items-start space-x-2.5 p-2 rounded-lg bg-emerald-50 border border-emerald-200 text-xs">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-emerald-900">1. Verify Order &amp; Delivery Date</p>
                      <p className="text-[10px] text-emerald-700">ORD-5001 verified delivered within 30-day window.</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-2.5 p-2 rounded-lg bg-white border border-slate-200 text-xs">
                    <div className="w-4 h-4 rounded-full border-2 border-indigo-600 shrink-0 mt-0.5" />
                    <div className="flex-1 space-y-1">
                      <p className="font-bold text-slate-900">2. Determine Customer Preference</p>
                      <p className="text-[10px] text-slate-500">Customer prefers zero-cost replacement over refund.</p>
                      <button
                        onClick={() => handleExecutePlaybookStep('step-2')}
                        className="mt-1 px-2.5 py-1 rounded bg-indigo-600 text-white font-bold text-[10px]"
                      >
                        Mark Step Done
                      </button>
                    </div>
                  </div>

                  <div className="flex items-start space-x-2.5 p-2 rounded-lg bg-slate-100/70 border border-slate-200 text-xs opacity-75">
                    <div className="w-4 h-4 rounded-full border-2 border-slate-300 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-slate-700">3. Authorize Zero-Cost Replacement Order</p>
                      <p className="text-[10px] text-slate-400">Trigger replacement in Commerce adapter.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: Quick Resolution Actions */}
          {activeTab === 'ACTIONS' && (
            <div className="space-y-3">
              {actionSuccessMsg && (
                <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>{actionSuccessMsg}</span>
                </div>
              )}

              {/* Action 1: Dispatch Replacement */}
              <button
                onClick={handleExecuteReplacement}
                disabled={actionLoading}
                className="w-full text-left p-3.5 rounded-xl border border-teal-200 bg-teal-50/50 hover:bg-teal-100/70 transition-colors flex items-center justify-between"
              >
                <div>
                  <h4 className="text-xs font-bold text-teal-900 flex items-center gap-1.5">
                    <RotateCcw className="w-4 h-4 text-teal-600" /> Dispatch Zero-Cost Replacement
                  </h4>
                  <p className="text-[11px] text-teal-700 mt-0.5">Authorizes replacement order with 1-day shipping.</p>
                </div>
                <ChevronRight className="w-4 h-4 text-teal-500" />
              </button>

              {/* Action 2: Issue Full Refund */}
              <button
                onClick={handleExecuteRefund}
                disabled={actionLoading}
                className="w-full text-left p-3.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 transition-colors flex items-center justify-between"
              >
                <div>
                  <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                    <DollarSign className="w-4 h-4 text-emerald-600" /> Issue Full Refund ($149.99)
                  </h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">Credits original Stripe payment transaction.</p>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400" />
              </button>

              {/* Action 3: Escalate to Supervisor */}
              <button
                onClick={handleEscalateCase}
                disabled={actionLoading}
                className="w-full text-left p-3.5 rounded-xl border border-rose-200 bg-rose-50/40 hover:bg-rose-100/60 transition-colors flex items-center justify-between"
              >
                <div>
                  <h4 className="text-xs font-bold text-rose-900 flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4 text-rose-600" /> Escalate to Tier 2 Lead
                  </h4>
                  <p className="text-[11px] text-rose-700 mt-0.5">Reassigns case with elevated priority flag.</p>
                </div>
                <ChevronRight className="w-4 h-4 text-rose-500" />
              </button>
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}
