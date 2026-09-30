import React, { useState, useEffect } from 'react';
import { Search, ArrowUpRight, Filter, ShieldAlert } from 'lucide-react';

export default function SuppliersTable({ onSelectSupplier }) {
  const [suppliers, setSuppliers] = useState([]);
  const [search, setSearch] = useState("");
  const [filterTier, setFilterTier] = useState("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/suppliers')
      .then(r => r.json())
      .then(data => setSuppliers(data || []))
      .catch(err => console.error("Error loading suppliers", err))
      .finally(() => setLoading(false));
  }, []);

  const filtered = suppliers.filter(s => {
    const matchSearch = s.supplier_name.toLowerCase().includes(search.toLowerCase()) || 
                        s.supplier_id.toLowerCase().includes(search.toLowerCase());
    const matchTier = filterTier === "ALL" || s.supplier_risk_level === filterTier;
    return matchSearch && matchTier;
  });

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-emerald-600" /> Supplier Operational Risk Scorecard
          </h2>
          <p className="text-xs text-slate-500">
            Deterministic risk profiling across 25 global tier-1/tier-2 suppliers
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Search */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search supplier..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-1.5 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500/50"
            />
          </div>

          {/* Filter */}
          <select
            value={filterTier}
            onChange={(e) => setFilterTier(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg border border-slate-300 text-xs font-medium focus:ring-2 focus:ring-emerald-500/50 bg-slate-50"
          >
            <option value="ALL">All Tiers</option>
            <option value="CRITICAL">Critical Only</option>
            <option value="HIGH">High Only</option>
            <option value="MEDIUM">Medium Only</option>
            <option value="LOW">Low Only</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-500 uppercase font-semibold border-b border-slate-200">
            <tr>
              <th className="py-3 px-3">Supplier Name & ID</th>
              <th className="py-3 px-3">Risk Tier</th>
              <th className="py-3 px-3">Risk Score</th>
              <th className="py-3 px-3">Late Delivery %</th>
              <th className="py-3 px-3">Avg Delay</th>
              <th className="py-3 px-3">Lead Time (Mean ± Std)</th>
              <th className="py-3 px-3">Anomalies</th>
              <th className="py-3 px-3">Total Orders</th>
              <th className="py-3 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {filtered.map((s) => (
              <tr key={s.supplier_id} className="hover:bg-slate-50/80 transition">
                <td className="py-3 px-3">
                  <div className="font-bold text-slate-900">{s.supplier_name}</div>
                  <div className="text-[11px] text-slate-400 font-mono">{s.supplier_id}</div>
                </td>
                <td className="py-3 px-3">
                  <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                    s.supplier_risk_level === 'CRITICAL' ? 'bg-rose-100 text-rose-800 border border-rose-200' :
                    s.supplier_risk_level === 'HIGH' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
                    s.supplier_risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-emerald-100 text-emerald-800'
                  }`}>
                    {s.supplier_risk_level}
                  </span>
                </td>
                <td className="py-3 px-3 font-mono font-bold text-slate-900">{s.supplier_risk_score}</td>
                <td className="py-3 px-3 font-semibold text-slate-900">
                  {(s.late_delivery_rate * 100).toFixed(1)}%
                </td>
                <td className="py-3 px-3">{s.avg_delay_days} days</td>
                <td className="py-3 px-3 font-mono text-slate-600">
                  {s.lead_time_mean_days}d ± {s.lead_time_std_days}d
                </td>
                <td className="py-3 px-3">
                  <span className={s.anomaly_count > 0 ? "font-bold text-amber-700" : "text-slate-400"}>
                    {s.anomaly_count}
                  </span>
                </td>
                <td className="py-3 px-3 font-mono">{s.total_orders.toLocaleString()}</td>
                <td className="py-3 px-3 text-right">
                  <button
                    onClick={() => onSelectSupplier(`Why is supplier ${s.supplier_id} risky?`)}
                    className="text-xs px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-semibold rounded-lg transition inline-flex items-center gap-1"
                  >
                    Investigate <ArrowUpRight className="w-3 h-3" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
