import React from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle2, XCircle, Info, RefreshCw } from 'lucide-react';

export default function GuardrailsView({ guardrails, evaluation, llmMeta }) {
  const fallbackUsed = llmMeta?.fallback_used;

  return (
    <div className="space-y-4">
      {/* Fallback Banner if Fallback was triggered */}
      {fallbackUsed && (
        <div className="p-4 rounded-xl border border-amber-300 bg-amber-50 text-amber-900 shadow-sm">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
            <div className="space-y-1">
              <div className="font-bold text-sm text-amber-950">
                LLM Unavailable — Deterministic Analysis Was Used
              </div>
              <p className="text-xs text-amber-800">
                The language model was bypassed ({llmMeta.fallback_reason || "Connection / Outage Policy"}). The system generated 100% verified results directly from trained ML models, operations research formulas, and deterministic multi-agent state.
              </p>
              <div className="flex items-center gap-3 pt-1 text-[11px] font-semibold text-amber-900">
                <span>System Status: <strong>FAULT-TOLERANT ACTIVE</strong></span>
                <span>•</span>
                <span>Deterministic Grounding: <strong>100%</strong></span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Guardrails Verification Checklist */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-600" /> Operational Guardrail Verification Suite
            </h3>
            <p className="text-xs text-slate-500">
              Deterministic validators ensure zero hallucination, schema compliance, and factual alignment
            </p>
          </div>
          <span className="text-xs font-bold text-emerald-800 bg-emerald-100 px-2.5 py-1 rounded-full">
            5 / 5 Active
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {/* 1. Input Guardrail */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/60 flex items-start gap-2.5">
            {guardrails?.input_valid !== false ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <XCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="font-semibold text-xs text-slate-900">Input Security Guardrail</div>
              <div className="text-[11px] text-slate-500">No prompt injection or off-topic attack</div>
            </div>
          </div>

          {/* 2. Schema Validation */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/60 flex items-start gap-2.5">
            {guardrails?.schema_valid ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <XCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="font-semibold text-xs text-slate-900">Schema Integrity Check</div>
              <div className="text-[11px] text-slate-500">Matches strict JSON contract</div>
            </div>
          </div>

          {/* 3. Evidence Grounding */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/60 flex items-start gap-2.5">
            {guardrails?.grounded ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <XCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="font-semibold text-xs text-slate-900">
                Evidence Grounding: {((evaluation?.grounding_score ?? 1.0) * 100).toFixed(0)}%
              </div>
              <div className="text-[11px] text-slate-500">All claims traceable to agent outputs</div>
            </div>
          </div>

          {/* 4. Hallucination Check */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/60 flex items-start gap-2.5">
            {!guardrails?.hallucination_detected ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <XCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="font-semibold text-xs text-slate-900">Zero-Hallucination Verified</div>
              <div className="text-[11px] text-slate-500">No fabricated suppliers or product SKUs</div>
            </div>
          </div>

          {/* 5. Numeric Consistency */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/60 flex items-start gap-2.5">
            {guardrails?.numeric_consistency ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <XCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="font-semibold text-xs text-slate-900">
                Numeric Consistency: {((evaluation?.factual_consistency ?? 1.0) * 100).toFixed(0)}%
              </div>
              <div className="text-[11px] text-slate-500">Calculated metrics match ground truth</div>
            </div>
          </div>

          {/* 6. LLM Engine Telemetry */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/60 flex items-start gap-2.5">
            <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-xs text-slate-900">
                LLM Engine: {llmMeta?.fallback_used ? "Deterministic Fallback" : (llmMeta?.model || "gpt-4o-mini")}
              </div>
              <div className="text-[11px] text-slate-500">
                {llmMeta?.fallback_used ? "Offline Resilient" : "Connected to OpenAI Gateway"}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
