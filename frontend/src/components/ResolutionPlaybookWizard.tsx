'use client';

import React, { useState } from 'react';
import { Workflow, CheckCircle2, ChevronRight, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react';
import { Playbook, PlaybookExecution, PlaybookStep } from '@/types';

interface ResolutionPlaybookWizardProps {
  execution: PlaybookExecution | null;
  onExecuteStep: (stepId: string, notes?: string) => Promise<void>;
}

export const ResolutionPlaybookWizard: React.FC<ResolutionPlaybookWizardProps> = ({
  execution,
  onExecuteStep,
}) => {
  const [stepNotes, setStepNotes] = useState('');
  const [executing, setExecuting] = useState(false);

  if (!execution || !execution.playbook) {
    return (
      <div className="p-6 text-center text-xs text-slate-400 bg-slate-50 rounded-xl border border-slate-200">
        No active resolution playbook loaded for this ticket.
      </div>
    );
  }

  const pb = execution.playbook;
  const currentStep = pb.steps.find((s) => s.step_order === execution.current_step_order);
  const totalSteps = pb.steps.length;
  const progressPercent = Math.min(100, Math.round(((execution.current_step_order - 1) / totalSteps) * 100));

  const handleStepComplete = async () => {
    if (!currentStep) return;
    setExecuting(true);
    try {
      await onExecuteStep(currentStep.id, stepNotes);
      setStepNotes('');
    } catch (e: any) {
      alert(`Error executing step: ${e.message}`);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Playbook Header & Progress Bar */}
      <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-amber-950 space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-xs flex items-center gap-1.5">
            <Workflow className="w-4 h-4 text-amber-600" /> {pb.name}
          </h3>
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-amber-200/60 text-amber-900">
            Step {execution.current_step_order} of {totalSteps}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-amber-200/60 rounded-full h-1.5 overflow-hidden">
          <div
            className="bg-amber-600 h-1.5 rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Active Step Card */}
      {currentStep ? (
        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded-full bg-indigo-600 text-white font-bold text-xs flex items-center justify-center">
              {currentStep.step_order}
            </div>
            <h4 className="font-bold text-xs text-slate-900">{currentStep.title}</h4>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
            {currentStep.instructions}
          </p>

          <div>
            <label className="block text-[11px] font-bold text-slate-700 mb-1">
              Resolution Audit Notes &amp; Observations
            </label>
            <input
              type="text"
              value={stepNotes}
              onChange={(e) => setStepNotes(e.target.value)}
              placeholder="e.g. Delivery signature verified, authorized zero-cost reshipment"
              className="w-full text-xs border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <button
            onClick={handleStepComplete}
            disabled={executing}
            className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs transition-colors flex items-center justify-center gap-1.5 shadow-sm"
          >
            <span>{executing ? 'Executing Step...' : 'Complete Step & Proceed'}</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <div>
            <h4 className="font-bold">Playbook Completed Successfully</h4>
            <p className="text-[11px] text-emerald-700">All required resolution steps and carrier logs have been verified.</p>
          </div>
        </div>
      )}
    </div>
  );
};
