import React, { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, Check, Clock3, RefreshCw } from 'lucide-react';

export default function IncidentHistory() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadIncidents = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('/api/incidents');
      if (!response.ok) throw new Error('Could not load incident history');
      setIncidents(await response.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadIncidents();
  }, [loadIncidents]);

  const acknowledge = async (incidentId) => {
    try {
      const response = await fetch(`/api/incidents/${incidentId}/acknowledge`, { method: 'POST' });
      if (!response.ok) throw new Error('Could not acknowledge incident');
      const updated = await response.json();
      setIncidents((current) => current.map((item) => item.id === incidentId ? updated : item));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-base font-bold text-slate-900">
            <AlertTriangle className="h-5 w-5 text-amber-600" /> Risk Incident History
          </h2>
          <p className="mt-1 text-xs text-slate-500">High and critical supplier and inventory risks, with acknowledgement history</p>
        </div>
        <button
          type="button"
          onClick={loadIncidents}
          disabled={loading}
          title="Refresh incidents"
          className="inline-flex items-center gap-1.5 self-start rounded-lg border border-slate-300 px-2.5 py-2 text-xs font-semibold text-slate-600 transition hover:border-emerald-500 hover:text-emerald-700 disabled:opacity-50 sm:self-auto"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </div>

      {error && <p className="px-5 pt-4 text-sm text-rose-700" role="alert">{error}</p>}
      {loading ? (
        <div className="flex items-center gap-2 px-5 py-10 text-sm text-slate-500">
          <Clock3 className="h-4 w-4 animate-pulse" /> Loading incident history...
        </div>
      ) : incidents.length === 0 ? (
        <p className="px-5 py-10 text-sm text-slate-500">No high or critical incidents detected.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-xs">
            <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-5 py-3">Incident</th>
                <th className="px-3 py-3">Severity</th>
                <th className="px-3 py-3">Status</th>
                <th className="px-3 py-3">Detected</th>
                <th className="px-3 py-3">Acknowledged by</th>
                <th className="px-5 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {incidents.map((incident) => (
                <tr key={incident.id} className="align-top hover:bg-slate-50/70">
                  <td className="max-w-lg px-5 py-3">
                    <div className="font-semibold text-slate-900">{incident.title}</div>
                    <div className="mt-1 text-slate-500">{incident.description}</div>
                    <div className="mt-1 font-mono text-[10px] text-slate-400">{incident.category} · {incident.entity_id}</div>
                  </td>
                  <td className="px-3 py-3">
                    <span className={`rounded px-2 py-1 text-[10px] font-bold ${incident.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'}`}>
                      {incident.severity}
                    </span>
                  </td>
                  <td className="px-3 py-3">
                    <span className={`rounded px-2 py-1 text-[10px] font-bold ${incident.status === 'ACKNOWLEDGED' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'}`}>
                      {incident.status}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-slate-500">{incident.created_at}</td>
                  <td className="px-3 py-3 text-slate-500">
                    {incident.acknowledged_by ? `${incident.acknowledged_by} · ${incident.acknowledged_at}` : '—'}
                  </td>
                  <td className="px-5 py-3 text-right">
                    {incident.status === 'OPEN' && (
                      <button
                        type="button"
                        onClick={() => acknowledge(incident.id)}
                        className="inline-flex items-center gap-1 rounded-lg border border-emerald-200 px-2.5 py-1.5 font-semibold text-emerald-800 transition hover:bg-emerald-50"
                      >
                        <Check className="h-3.5 w-3.5" /> Acknowledge
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}