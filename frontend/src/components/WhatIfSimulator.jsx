import React, { useState } from 'react';
import { Play, AlertTriangle, Package, DollarSign, Calendar, RefreshCw, CheckCircle2 } from 'lucide-react';

export default function WhatIfSimulator() {
  const [supplierId, setSupplierId] = useState("SUP-023");
  const [delayDays, setDelayDays] = useState(7);
  const [simulation, setSimulation] = useState(null);
  const [loading, setLoading] = useState(false);

  const runSimulation = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ supplier_id: supplierId, delay_days: delayDays })
      });
      const data = await res.json();
      setSimulation(data);
    } catch (err) {
      console.error("Simulation failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Configuration Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-emerald-600" /> What-If Risk Impact Simulator
          </h2>
          <p className="text-xs text-slate-500">
            Simulate operational disruptions deterministically: Supplier delay → Delivery impact → Inventory reduction → Stock-out risk
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div>
            <label className="block text-xs font-bold uppercase text-slate-500 mb-1.5">
              Target Disrupted Supplier
            </label>
            <select
              value={supplierId}
              onChange={(e) => setSupplierId(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm font-medium focus:ring-2 focus:ring-emerald-500/50 bg-slate-50"
            >
              <option value="SUP-023">SUP-023 (RedStar Cargo & Microchips - Critical)</option>
              <option value="SUP-021">SUP-021 (Harborview Semis & Chips - Critical)</option>
              <option value="SUP-025">SUP-025 (Borealis Extreme Composites - Critical)</option>
              <option value="SUP-020">SUP-020 (Continental Freight & Stamping - High)</option>
              <option value="SUP-019">SUP-019 (Pacific Rim Foundry Corp - High)</option>
              <option value="SUP-001">SUP-001 (Apex Precision Components - Low)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase text-slate-500 mb-1.5">
              Simulated Delay Duration: <span className="text-emerald-700 font-bold">+{delayDays} Days</span>
            </label>
            <input
              type="range"
              min="1"
              max="30"
              value={delayDays}
              onChange={(e) => setDelayDays(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-600 mt-2"
            />
            <div className="flex justify-between text-[11px] text-slate-400 mt-1">
              <span>+1 Day</span>
              <span>+15 Days</span>
              <span>+30 Days</span>
            </div>
          </div>

          <div className="flex items-end">
            <button
              onClick={runSimulation}
              disabled={loading}
              className="w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 text-white font-bold text-sm rounded-xl transition flex items-center justify-center gap-2 shadow-sm"
            >
              {loading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <><Play className="w-4 h-4 fill-white" /> Run Scenario Simulation</>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Simulation Result */}
      {simulation && (
        <div className="space-y-6">
          {/* Top Simulation Summary Card */}
          <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-2xl p-6 shadow-md">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-700 pb-4">
              <div>
                <span className="text-xs uppercase font-bold tracking-wider text-emerald-400">
                  Deterministic Simulation Result
                </span>
                <h3 className="text-xl font-bold mt-1">
                  Scenario: {simulation.scenario.supplier_name} ({simulation.scenario.supplier_id}) +{simulation.scenario.delay_days} Days Delay
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Projected Risk:</span>
                <span className={`px-3 py-1 rounded-full text-xs font-black ${
                  simulation.risk_level === 'CRITICAL' ? 'bg-rose-500 text-white' : 'bg-amber-500 text-white'
                }`}>
                  {simulation.risk_level}
                </span>
              </div>
            </div>

            {/* 4 Impact Stat Counters */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-5">
              <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700">
                <div className="text-xs text-slate-400 font-medium">Affected Product Lines</div>
                <div className="text-2xl font-extrabold text-white mt-1">{simulation.affected_products_count} SKUs</div>
              </div>
              <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700">
                <div className="text-xs text-slate-400 font-medium">Affected Active Orders</div>
                <div className="text-2xl font-extrabold text-white mt-1">{simulation.affected_orders_count}</div>
              </div>
              <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700">
                <div className="text-xs text-rose-300 font-medium">Stockouts Triggered</div>
                <div className="text-2xl font-extrabold text-rose-400 mt-1">{simulation.potential_stockouts_count} SKUs</div>
              </div>
              <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700">
                <div className="text-xs text-emerald-300 font-medium">Financial Risk Exposure</div>
                <div className="text-2xl font-extrabold text-emerald-400 mt-1">
                  ${simulation.estimated_financial_exposure_usd.toLocaleString()}
                </div>
              </div>
            </div>
          </div>

          {/* Affected Products Detail Table */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
            <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
              Product-Level Inventory Cascading Impact
            </h4>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 uppercase font-semibold border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-3">Product SKU</th>
                    <th className="py-2.5 px-3">Baseline Stock</th>
                    <th className="py-2.5 px-3">Simulated Stock</th>
                    <th className="py-2.5 px-3">Baseline DOS</th>
                    <th className="py-2.5 px-3">Simulated DOS</th>
                    <th className="py-2.5 px-3">Stockout Date</th>
                    <th className="py-2.5 px-3">Revised ROQ</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {simulation.affected_products_detail.map((p, idx) => (
                    <tr key={idx} className={p.stockout_triggered ? "bg-rose-50/50" : "hover:bg-slate-50"}>
                      <td className="py-2.5 px-3 font-medium text-slate-900">
                        {p.product_name} <span className="text-slate-400">({p.product_id})</span>
                      </td>
                      <td className="py-2.5 px-3">{p.baseline_inventory.toLocaleString()} u</td>
                      <td className="py-2.5 px-3 font-semibold text-slate-900">{p.simulated_inventory.toLocaleString()} u</td>
                      <td className="py-2.5 px-3">{p.baseline_days_of_supply}d</td>
                      <td className="py-2.5 px-3">
                        <span className={`px-1.5 py-0.5 rounded font-bold ${
                          p.simulated_days_of_supply <= 5.0 ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'
                        }`}>
                          {p.simulated_days_of_supply}d
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-medium text-slate-900">{p.new_projected_stockout_date}</td>
                      <td className="py-2.5 px-3 font-bold text-emerald-700">{p.revised_reorder_quantity.toLocaleString()} u</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Assumptions and Evidence */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-50 rounded-xl border border-slate-200 p-4 text-xs space-y-2">
              <strong className="text-slate-900 block uppercase tracking-wider">Simulation Assumptions:</strong>
              <ul className="list-disc list-inside space-y-1 text-slate-600">
                {simulation.assumptions.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </div>

            <div className="bg-emerald-50/50 rounded-xl border border-emerald-100 p-4 text-xs space-y-2">
              <strong className="text-emerald-950 block uppercase tracking-wider">Grounded Evidence:</strong>
              <ul className="list-disc list-inside space-y-1 text-emerald-900">
                {simulation.evidence.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
