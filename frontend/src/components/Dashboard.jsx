import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, ShieldCheck, TrendingUp, Package, Truck, 
  ArrowUpRight, AlertCircle, Clock, CheckCircle2, Download
} from 'lucide-react';
import { downloadCsv } from '../utils/downloadCsv';

export default function Dashboard({ onSelectQuery }) {
  const [suppliers, setSuppliers] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [supRes, invRes, anomRes] = await Promise.all([
          fetch('/api/suppliers').then(r => r.json()),
          fetch('/api/inventory?limit=100').then(r => r.json()),
          fetch('/api/anomalies?limit=6').then(r => r.json())
        ]);
        setSuppliers(supRes || []);
        setInventory(invRes || []);
        setAnomalies(anomRes || []);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const highRiskCount = suppliers.filter(s => s.supplier_risk_level === 'CRITICAL' || s.supplier_risk_level === 'HIGH').length;

  const sampleQuestions = [
    "Which suppliers have the highest delivery risk?",
    "Why is supplier SUP-023 risky?",
    "Which products are most affected by supplier disruptions?",
    "What is the demand forecast for product PROD-001?",
    "What happens if supplier SUP-023 is delayed by 7 days?"
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-emerald-600 font-medium animate-pulse flex items-center gap-2">
          <Clock className="w-5 h-5 animate-spin" /> Loading Supply Chain Operational Intelligence...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner / Risk State */}
      <div className="bg-gradient-to-r from-emerald-700 via-emerald-600 to-teal-600 rounded-2xl p-6 text-white shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-800/60 text-xs font-semibold uppercase tracking-wider text-emerald-100 mb-2">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-300" /> System Status: Operational & Verified
            </div>
            <h1 className="text-2xl font-bold">Supply Chain Risk Command Center</h1>
            <p className="text-emerald-100/90 text-sm mt-1 max-w-2xl">
              Real-time multi-agent risk assessment monitoring 120,000 shipment transactions, 25 global suppliers, and critical inventory buffers.
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 text-center min-w-[180px]">
            <span className="text-xs font-medium text-emerald-100 uppercase tracking-wider">Enterprise Risk Level</span>
            <div className="text-2xl font-extrabold text-amber-300 mt-1 flex items-center justify-center gap-1.5">
              <AlertTriangle className="w-6 h-6 text-amber-300" /> CRITICAL
            </div>
            <span className="text-xs text-emerald-200 mt-1 block">Driven by SUP-023 & SUP-021</span>
          </div>
        </div>

        {/* Quick query launcher chips */}
        <div className="mt-5 pt-4 border-t border-emerald-500/40 flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium text-emerald-200">Ask Quick Question:</span>
          {sampleQuestions.slice(0, 3).map((q, idx) => (
            <button
              key={idx}
              onClick={() => onSelectQuery(q)}
              className="text-xs bg-white/15 hover:bg-white/25 text-white px-3 py-1 rounded-full transition duration-150 flex items-center gap-1"
            >
              {q} <ArrowUpRight className="w-3 h-3 text-emerald-200" />
            </button>
          ))}
        </div>
      </div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium uppercase tracking-wider">
            <span>Total Shipments</span>
            <Truck className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-800 mt-2">120,000</div>
          <div className="text-xs text-emerald-600 mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> 100% Quality Validated
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium uppercase tracking-wider">
            <span>Overall Late Rate</span>
            <Clock className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-slate-800 mt-2">27.8%</div>
          <div className="text-xs text-slate-500 mt-1">Avg late delay: 7.4 days</div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium uppercase tracking-wider">
            <span>High/Critical Suppliers</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-bold text-rose-600 mt-2">{highRiskCount} / {suppliers.length}</div>
          <div className="text-xs text-rose-500 mt-1">Requiring dual-source review</div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium uppercase tracking-wider">
            <span>Lead-Time Anomalies</span>
            <AlertCircle className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-2xl font-bold text-slate-800 mt-2">3,600</div>
          <div className="text-xs text-slate-500 mt-1">Isolation Forest (F1: 0.55)</div>
        </div>
      </div>

      {/* Main Grid: Suppliers Table & Critical Inventory */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Suppliers List (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Highest Risk Suppliers</h2>
              <p className="text-xs text-slate-500">Ranked by deterministic multi-factor risk score</p>
            </div>
            <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full">
              Deterministic Weights
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-medium border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Supplier</th>
                  <th className="py-2.5 px-3">Risk Level</th>
                  <th className="py-2.5 px-3">Score</th>
                  <th className="py-2.5 px-3">Late Rate</th>
                  <th className="py-2.5 px-3">Avg Delay</th>
                  <th className="py-2.5 px-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {suppliers.slice(0, 6).map((sup) => (
                  <tr key={sup.supplier_id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-3">
                      <div className="font-semibold text-slate-900">{sup.supplier_name}</div>
                      <div className="text-xs text-slate-400">{sup.supplier_id} • {sup.total_orders.toLocaleString()} orders</div>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        sup.supplier_risk_level === 'CRITICAL' 
                          ? 'bg-rose-100 text-rose-700 border border-rose-200' 
                          : sup.supplier_risk_level === 'HIGH'
                          ? 'bg-amber-100 text-amber-800 border border-amber-200'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}>
                        {sup.supplier_risk_level}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono font-medium">{sup.supplier_risk_score}</td>
                    <td className="py-3 px-3 font-medium text-slate-900">
                      {(sup.late_delivery_rate * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-3">{sup.avg_delay_days}d</td>
                    <td className="py-3 px-3">
                      <button
                        onClick={() => onSelectQuery(`Why is supplier ${sup.supplier_id} risky?`)}
                        className="text-xs text-emerald-600 hover:text-emerald-800 font-medium hover:underline flex items-center gap-0.5"
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

        {/* Critical Inventory & Stockouts (1 col) */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Package className="w-4 h-4 text-emerald-600" /> Critical Stockout Watch
              </h2>
              <p className="text-xs text-slate-500">Deterministic inventory coverage & ROQ</p>
            </div>
            <button
              type="button"
              onClick={() => downloadCsv('inventory-risk.csv', inventory)}
              disabled={!inventory.length}
              title="Export inventory risks as CSV"
              className="inline-flex shrink-0 items-center gap-1 rounded-lg border border-slate-300 px-2.5 py-2 text-xs font-semibold text-slate-600 transition hover:border-emerald-500 hover:text-emerald-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Download className="h-4 w-4" /> CSV
            </button>
          </div>

          <div className="space-y-3">
            {inventory.slice(0, 4).map((item) => (
              <div key={item.product_id} className="p-3 rounded-lg border border-slate-100 bg-slate-50/60 hover:bg-slate-50 transition">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-xs font-bold text-slate-900">{item.product_name}</div>
                    <div className="text-xs text-slate-400">{item.product_id}</div>
                  </div>
                  <span className={`text-[11px] font-bold px-1.5 py-0.5 rounded ${
                    item.risk_level === 'CRITICAL' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                  }`}>
                    {item.days_of_supply} DOS
                  </span>
                </div>
                <div className="mt-2 flex items-center justify-between text-xs text-slate-600 pt-2 border-t border-slate-200/60">
                  <span>Stockout: <strong>{item.projected_stockout_date}</strong></span>
                  <span className="text-emerald-700 font-semibold">ROQ: {item.recommended_reorder_quantity.toLocaleString()} u</span>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={() => onSelectQuery("Which products are at risk of stock-out?")}
            className="w-full text-xs py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-semibold rounded-lg transition text-center"
          >
            Analyze Complete Inventory Risk →
          </button>
        </div>
      </div>

      {/* Recent Anomalies Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Detected Operational Anomalies</h2>
            <p className="text-xs text-slate-500">Unusual lead-time changes and sudden shipment delays</p>
          </div>
          <span className="text-xs text-slate-500">Isolation Forest Contamination: 3%</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {anomalies.slice(0, 3).map((anom, idx) => (
            <div key={idx} className="p-3.5 rounded-lg border border-amber-200 bg-amber-50/40 text-xs space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-bold text-amber-900">{anom.supplier_id}</span>
                <span className="px-1.5 py-0.5 rounded bg-amber-200 text-amber-900 font-bold text-[10px]">
                  {anom.severity}
                </span>
              </div>
              <div className="text-slate-700">{anom.reason}</div>
              <div className="text-slate-400 text-[11px] pt-1 border-t border-amber-200/50 flex justify-between">
                <span>Order: {anom.order_id}</span>
                <span>Z-score: {anom.z_score}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
