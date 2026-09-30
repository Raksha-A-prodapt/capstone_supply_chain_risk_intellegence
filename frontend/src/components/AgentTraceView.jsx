import React, { useState } from 'react';
import { 
  GitBranch, CheckCircle2, ChevronDown, ChevronRight, 
  ArrowRight, ShieldCheck, Database, Layers, Sparkles 
} from 'lucide-react';

export default function AgentTraceView({ trace, agentOutputs, handoffs, agentsInvolved }) {
  const [expandedAgent, setExpandedAgent] = useState(null);
  const [showRawJson, setShowRawJson] = useState(false);

  const toggleAgent = (name) => {
    setExpandedAgent(expandedAgent === name ? null : name);
  };

  return (
    <div className="space-y-5 bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-emerald-600" /> Multi-Agent Execution Flow & Trace
          </h3>
          <p className="text-xs text-slate-500">
            State-based LangGraph orchestration with explicit A2A handoffs and deterministic telemetry
          </p>
        </div>
        <button
          onClick={() => setShowRawJson(!showRawJson)}
          className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition"
        >
          {showRawJson ? "Hide Raw State" : "View Raw State JSON"}
        </button>
      </div>

      {/* Visual Agent Pipeline Flow */}
      <div className="bg-slate-50/80 rounded-xl p-4 border border-slate-200/80 overflow-x-auto">
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5">
          Dynamic Graph Pipeline
        </div>
        <div className="flex items-center gap-2 min-w-max">
          <div className="px-3 py-1.5 rounded-lg bg-slate-200 text-slate-700 font-semibold text-xs">
            User Query
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400" />
          <div className="px-3 py-1.5 rounded-lg bg-emerald-100 border border-emerald-300 text-emerald-800 font-bold text-xs flex items-center gap-1">
            <Layers className="w-3.5 h-3.5 text-emerald-600" /> Orchestrator
          </div>

          {agentsInvolved.map((agentId, idx) => {
            const cleanName = agentId.replace("_agent", "").replace("_", " ").toUpperCase();
            return (
              <React.Fragment key={idx}>
                <ArrowRight className="w-4 h-4 text-emerald-500" />
                <div className="px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900 font-medium text-xs shadow-xs">
                  {cleanName}
                </div>
              </React.Fragment>
            );
          })}

          <ArrowRight className="w-4 h-4 text-emerald-500" />
          <div className="px-3 py-1.5 rounded-lg bg-teal-100 border border-teal-300 text-teal-900 font-bold text-xs flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-teal-600" /> Guardrails
          </div>
          <ArrowRight className="w-4 h-4 text-teal-500" />
          <div className="px-3 py-1.5 rounded-lg bg-emerald-700 text-white font-bold text-xs">
            Verified Response
          </div>
        </div>
      </div>

      {/* A2A Explicit Handoff Section */}
      {handoffs && handoffs.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" /> A2A Inter-Agent Communication (Handoffs)
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {handoffs.map((h, i) => (
              <div key={i} className="p-3 rounded-lg border border-emerald-200/70 bg-emerald-50/40 text-xs space-y-1">
                <div className="flex items-center justify-between font-semibold text-emerald-900">
                  <span>{h.from_agent} → {h.to_agent}</span>
                  <span className="text-[10px] text-slate-400 font-mono">{h.timestamp}</span>
                </div>
                <div className="text-slate-600 text-[11px]">{h.summary}</div>
                <div className="flex flex-wrap gap-1 pt-1">
                  {h.payload_keys.map((k, kidx) => (
                    <span key={kidx} className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-mono">
                      {k}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Expandable Individual Agent Execution Cards */}
      <div className="space-y-2.5 pt-2">
        <div className="text-xs font-bold text-slate-700 uppercase tracking-wider">
          Individual Specialist Agent Telemetry
        </div>

        {trace.map((stepItem, idx) => {
          const isExpanded = expandedAgent === stepItem.agent_name;
          // Map agent name to outputs key
          const agentKeyMap = {
            "Supplier Risk Agent": "supplier_risk_agent",
            "Delivery Risk Agent": "delivery_risk_agent",
            "Inventory Risk Agent": "inventory_risk_agent",
            "Demand / Forecasting Agent": "demand_agent",
            "Supply Chain Insight Agent": "insight_agent",
            "Risk Recommendation Agent": "recommendation_agent"
          };
          const rawOutput = agentOutputs[agentKeyMap[stepItem.agent_name]];

          return (
            <div key={idx} className="border border-slate-200 rounded-xl overflow-hidden">
              <button
                onClick={() => toggleAgent(stepItem.agent_name)}
                className="w-full px-4 py-3 bg-slate-50 hover:bg-slate-100/80 transition flex items-center justify-between text-left"
              >
                <div className="flex items-center gap-3">
                  <span className="w-5 h-5 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center">
                    {stepItem.step}
                  </span>
                  <div>
                    <span className="font-bold text-sm text-slate-900">{stepItem.agent_name}</span>
                    <span className="ml-2 text-xs text-slate-500 font-mono">({stepItem.latency_ms} ms)</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-xs font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" /> SUCCESS
                  </span>
                  {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                </div>
              </button>

              {isExpanded && (
                <div className="p-4 bg-white border-t border-slate-100 space-y-3 text-xs">
                  <div className="text-slate-700 font-medium bg-emerald-50/50 p-2.5 rounded-lg border border-emerald-100">
                    <strong>Summary:</strong> {stepItem.summary}
                  </div>

                  {rawOutput && rawOutput.evidence && (
                    <div className="space-y-1">
                      <strong className="text-slate-900">Extracted Ground Truth Evidence:</strong>
                      <ul className="list-disc list-inside space-y-1 text-slate-600 pl-1">
                        {rawOutput.evidence.map((ev, evIdx) => (
                          <li key={evIdx}>{ev}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {rawOutput && (
                    <div className="mt-2">
                      <strong className="text-slate-900 block mb-1">Agent Structured Payload:</strong>
                      <pre className="p-2.5 rounded bg-slate-900 text-emerald-300 font-mono text-[11px] overflow-x-auto max-h-48 custom-scrollbar">
                        {JSON.stringify(rawOutput, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {showRawJson && (
        <div className="mt-4 pt-4 border-t border-slate-200">
          <strong className="text-xs text-slate-700 uppercase tracking-wider block mb-2">Complete Orchestrator State JSON:</strong>
          <pre className="p-3 rounded-lg bg-slate-950 text-slate-100 font-mono text-[11px] overflow-x-auto max-h-64 custom-scrollbar">
            {JSON.stringify({ trace, agentOutputs, handoffs, agentsInvolved }, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
