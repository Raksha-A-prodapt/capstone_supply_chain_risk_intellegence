import React, { useEffect, useState } from 'react';
import { 
  Send, Sparkles, AlertTriangle, ShieldCheck, CheckCircle2, 
  Clock, ArrowRight, ToggleLeft, ToggleRight, HelpCircle, Layers,
  BookmarkPlus, Trash2
} from 'lucide-react';
import AgentTraceView from './AgentTraceView';
import GuardrailsView from './GuardrailsView';

export default function Assistant({ initialQuery }) {
  const [query, setQuery] = useState(initialQuery || "Which suppliers have the highest delivery risk?");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [forceFallback, setForceFallback] = useState(false);
  const [savedQueries, setSavedQueries] = useState([]);
  const [savedMessage, setSavedMessage] = useState('');
  const [savingQuery, setSavingQuery] = useState(false);

  useEffect(() => {
    fetch('/api/saved-queries')
      .then((response) => response.ok ? response.json() : [])
      .then(setSavedQueries)
      .catch((err) => console.error('Failed to load saved queries', err));
  }, []);

  const saveQuery = async () => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery || savingQuery) return;

    setSavingQuery(true);
    setSavedMessage('');
    try {
      const response = await fetch('/api/saved-queries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: trimmedQuery }),
      });
      if (!response.ok) throw new Error('Could not save query');
      const saved = await response.json();
      setSavedQueries((current) => [saved, ...current]);
      setSavedMessage('Saved');
    } catch (err) {
      setSavedMessage(err.message);
    } finally {
      setSavingQuery(false);
    }
  };

  const deleteSavedQuery = async (queryId) => {
    try {
      const response = await fetch(`/api/saved-queries/${queryId}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Could not remove saved query');
      setSavedQueries((current) => current.filter((item) => item.id !== queryId));
      setSavedMessage('Saved query removed');
    } catch (err) {
      setSavedMessage(err.message);
    }
  };

  const sampleQueries = [
    "Which suppliers have the highest delivery risk?",
    "Why is supplier SUP-023 risky?",
    "Which products are most affected by supplier disruptions?",
    "Identify unusual supplier lead-time changes.",
    "What is the demand forecast for product PROD-001?",
    "How could a supplier delay affect inventory availability?",
    "What happens if supplier SUP-023 is delayed by 7 days?"
  ];

  const handleSearch = async (overrideQuery = null) => {
    const q = overrideQuery || query;
    if (!q.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, force_fallback: forceFallback })
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Query failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Query Header and Input */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-emerald-600" /> Ask Supply Chain Assistant
            </h2>
            <p className="text-xs text-slate-500">
              Query multi-agent operational data with deterministic analytics, ML forecasting, and LLM explanation
            </p>
          </div>

          {/* Fallback Simulator Toggle */}
          <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
            <span className="text-xs font-semibold text-slate-600">Simulate LLM Outage (Force Fallback):</span>
            <button
              onClick={() => setForceFallback(!forceFallback)}
              className="text-emerald-700 hover:text-emerald-800 transition"
              title="Force deterministic rule-based analysis without LLM"
            >
              {forceFallback ? (
                <ToggleRight className="w-7 h-7 text-emerald-600" />
              ) : (
                <ToggleLeft className="w-7 h-7 text-slate-400" />
              )}
            </button>
            <span className={`text-[11px] font-bold ${forceFallback ? "text-amber-700" : "text-slate-400"}`}>
              {forceFallback ? "ON (Fallback Mode)" : "OFF (Live Gateway)"}
            </span>
          </div>
        </div>

        {/* Input Bar */}
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Ask a supply-chain risk question (e.g., Which suppliers are high risk?)..."
            className="w-full pl-4 pr-32 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 text-sm bg-slate-50/50"
          />
          <button
            onClick={() => handleSearch()}
            disabled={loading}
            className="absolute right-2 top-2 bottom-2 px-5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 text-white font-semibold text-xs rounded-lg transition flex items-center gap-1.5 shadow-sm"
          >
            {loading ? (
              <Clock className="w-4 h-4 animate-spin" />
            ) : (
              <>Analyze <Send className="w-3.5 h-3.5" /></>
            )}
          </button>
        </div>

        {/* Sample questions chips */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          <span className="text-xs font-medium text-slate-400">Suggestions:</span>
          {sampleQueries.map((sq, i) => (
            <button
              key={i}
              onClick={() => {
                setQuery(sq);
                handleSearch(sq);
              }}
              className="text-xs bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-600 px-2.5 py-1 rounded-full transition duration-150 border border-slate-200/80"
            >
              {sq}
            </button>
          ))}
        </div>

        <div className="space-y-2 border-t border-slate-100 pt-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="text-xs font-bold uppercase tracking-wide text-slate-500">Saved queries</div>
            <div className="flex items-center gap-3">
              {savedMessage && <span className="text-xs text-slate-500" role="status">{savedMessage}</span>}
              <button
                type="button"
                onClick={saveQuery}
                disabled={!query.trim() || savingQuery}
                className="inline-flex items-center gap-1.5 rounded-lg border border-emerald-200 px-2.5 py-1.5 text-xs font-semibold text-emerald-800 transition hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <BookmarkPlus className="h-4 w-4" /> {savingQuery ? 'Saving...' : 'Save current query'}
              </button>
            </div>
          </div>
          {savedQueries.length > 0 ? (
            <div className="divide-y divide-slate-100 rounded-lg border border-slate-200">
              {savedQueries.map((item) => (
                <div key={item.id} className="flex items-center gap-2 px-3 py-2">
                  <button
                    type="button"
                    onClick={() => { setQuery(item.query); handleSearch(item.query); }}
                    className="min-w-0 flex-1 truncate text-left text-xs text-slate-700 hover:text-emerald-800"
                    title={item.query}
                  >
                    {item.query}
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteSavedQuery(item.id)}
                    className="rounded p-1 text-slate-400 transition hover:bg-rose-50 hover:text-rose-700"
                    title="Remove saved query"
                    aria-label={`Remove saved query: ${item.query}`}
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400">No saved queries yet.</p>
          )}
        </div>
      </div>

      {/* Loading Skeleton */}
      {loading && (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center space-y-3">
          <div className="w-10 h-10 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <div className="text-sm font-semibold text-slate-800">
            Dispatching LangGraph Multi-Agent Workflow...
          </div>
          <div className="text-xs text-slate-400 max-w-md mx-auto">
            Routing query to Supplier Risk Agent, Delivery Risk Agent, Inventory Risk Agent, and calculating operations research formulas.
          </div>
        </div>
      )}

      {/* Structured Result Display */}
      {result && !loading && (
        <div className="space-y-6">
          {/* Main Answer Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Assessment Result</span>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-extrabold ${
                  result.risk_level === 'CRITICAL' ? 'bg-rose-100 text-rose-800 border border-rose-300' :
                  result.risk_level === 'HIGH' ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                  'bg-emerald-100 text-emerald-800 border border-emerald-300'
                }`}>
                  {result.risk_level} RISK
                </span>
              </div>
              <div className="text-xs text-slate-400 font-mono">
                Latency: {result.latency_ms} ms
              </div>
            </div>

            {/* Answer Text */}
            <div className="prose prose-sm max-w-none text-slate-800 leading-relaxed whitespace-pre-line bg-slate-50/70 p-4 rounded-xl border border-slate-100">
              {result.answer}
            </div>

            {/* Evidence Chips */}
            {result.evidence && result.evidence.length > 0 && (
              <div className="space-y-2 pt-2">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Verified Supporting Evidence
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {result.evidence.map((ev, i) => (
                    <div key={i} className="p-2.5 rounded-lg bg-emerald-50/50 border border-emerald-100 text-xs text-slate-700 flex items-start gap-2">
                      <span className="text-emerald-600 font-bold shrink-0">•</span>
                      <span>{ev}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actionable Recommendations */}
            {result.recommendations && result.recommendations.length > 0 && (
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Data-Backed Operational Recommendations
                </div>
                <div className="space-y-2.5">
                  {result.recommendations.map((rec, i) => (
                    <div key={i} className="p-3.5 rounded-xl border border-slate-200 bg-slate-50 text-xs space-y-1 hover:border-emerald-300 transition">
                      <div className="flex items-center justify-between font-bold">
                        <span className="text-slate-900">{rec.action}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          rec.priority === 'CRITICAL' ? 'bg-rose-100 text-rose-800' :
                          rec.priority === 'HIGH' ? 'bg-amber-100 text-amber-800' :
                          'bg-emerald-100 text-emerald-800'
                        }`}>
                          {rec.priority}
                        </span>
                      </div>
                      <div className="text-slate-600">
                        <strong>Rationale:</strong> {rec.rationale}
                      </div>
                      <div className="text-slate-400 text-[11px] pt-1">
                        <strong>Evidence Ref:</strong> {rec.evidence_ref}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Guardrails View */}
          <GuardrailsView 
            guardrails={result.guardrails} 
            evaluation={result.evaluation} 
            llmMeta={result.llm} 
          />

          {/* Multi-Agent Trace & Handoff View */}
          <AgentTraceView 
            trace={result.agent_trace || []} 
            agentOutputs={result.agent_outputs || {}} 
            handoffs={result.handoffs || []} 
            agentsInvolved={result.agents_involved || []} 
          />
        </div>
      )}
    </div>
  );
}
