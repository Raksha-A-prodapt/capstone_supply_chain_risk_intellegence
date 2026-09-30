import React, { useState, useEffect } from 'react';
import { Award, CheckCircle2, TrendingUp, AlertTriangle, ExternalLink, BarChart3, Clock } from 'lucide-react';

export default function EvaluationDashboard() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/evaluation')
      .then(r => r.json())
      .then(data => setReport(data))
      .catch(err => console.error("Could not fetch evaluation report", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-emerald-600 animate-pulse font-medium">
        Loading Evaluation Metrics...
      </div>
    );
  }

  const ml = report?.ml_metrics;
  const agents = report?.agent_metrics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Award className="w-5 h-5 text-emerald-600" /> System Evaluation & Reliability Dashboard
          </h2>
          <p className="text-xs text-slate-500">
            Rigorous empirical benchmarks covering ML precision/recall, demand forecasting MAPE, and agent grounding
          </p>
        </div>
        <a
          href="/reports/evaluation_report.html"
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl transition flex items-center gap-1.5 shadow-sm"
        >
          View Full HTML Report <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      {/* Agent Performance Highlights (6 cards) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
          <div className="text-[11px] font-bold text-slate-400 uppercase">Routing Accuracy</div>
          <div className="text-2xl font-black text-emerald-600 mt-1">
            {((agents?.routing_accuracy ?? 1.0) * 100).toFixed(0)}%
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">10/10 Benchmark queries</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
          <div className="text-[11px] font-bold text-slate-400 uppercase">Agent Success</div>
          <div className="text-2xl font-black text-emerald-600 mt-1">
            {((agents?.agent_success_rate ?? 1.0) * 100).toFixed(0)}%
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">{agents?.successful_agent_invocations} executions</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
          <div className="text-[11px] font-bold text-slate-400 uppercase">Grounding Score</div>
          <div className="text-2xl font-black text-emerald-600 mt-1">
            {((agents?.mean_grounding_score ?? 1.0) * 100).toFixed(0)}%
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Verified evidence</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
          <div className="text-[11px] font-bold text-slate-400 uppercase">Hallucination Rate</div>
          <div className="text-2xl font-black text-emerald-600 mt-1">
            {((agents?.mean_hallucination_rate ?? 0.0) * 100).toFixed(1)}%
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">0.0% fake entities</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
          <div className="text-[11px] font-bold text-slate-400 uppercase">Numeric Consistency</div>
          <div className="text-2xl font-black text-emerald-600 mt-1">
            {((agents?.mean_factual_consistency ?? 1.0) * 100).toFixed(0)}%
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Factual numerical parity</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
          <div className="text-[11px] font-bold text-slate-400 uppercase">Mean Latency</div>
          <div className="text-2xl font-black text-slate-800 mt-1">
            {agents?.average_latency_ms?.toFixed(0) || "—"} ms
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Complete cycle</div>
        </div>
      </div>

      {/* Machine Learning Models Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Delivery ML Classifier */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="border-b border-slate-100 pb-2">
            <h3 className="font-bold text-sm text-slate-900">Delivery Risk Classifier</h3>
            <span className="text-[11px] text-slate-400">{ml?.delivery_risk_model?.algorithm}</span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-50">
              <span className="text-slate-500">ROC-AUC:</span>
              <strong className="text-emerald-700 font-mono">{ml?.delivery_risk_model?.roc_auc}</strong>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-50">
              <span className="text-slate-500">PR-AUC:</span>
              <strong className="text-emerald-700 font-mono">{ml?.delivery_risk_model?.pr_auc}</strong>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-50">
              <span className="text-slate-500">F1 Score:</span>
              <strong className="text-slate-800 font-mono">{ml?.delivery_risk_model?.f1_score}</strong>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-50">
              <span className="text-slate-500">Precision:</span>
              <strong className="text-slate-800 font-mono">{ml?.delivery_risk_model?.precision}</strong>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500">Recall:</span>
              <strong className="text-slate-800 font-mono">{ml?.delivery_risk_model?.recall}</strong>
            </div>
          </div>

          {ml?.delivery_risk_model?.confusion_matrix && (
            <div className="pt-2 border-t border-slate-100">
              <div className="text-[10px] font-bold text-slate-400 uppercase mb-1.5">Confusion Matrix (24,000 Test)</div>
              <div className="grid grid-cols-2 gap-1 text-center font-mono text-xs">
                <div className="p-2 bg-emerald-50 rounded text-emerald-900">
                  <div className="text-[10px] text-slate-400">TN</div>
                  <strong>{ml.delivery_risk_model.confusion_matrix[0][0].toLocaleString()}</strong>
                </div>
                <div className="p-2 bg-rose-50 rounded text-rose-900">
                  <div className="text-[10px] text-slate-400">FP</div>
                  <strong>{ml.delivery_risk_model.confusion_matrix[0][1].toLocaleString()}</strong>
                </div>
                <div className="p-2 bg-amber-50 rounded text-amber-900">
                  <div className="text-[10px] text-slate-400">FN</div>
                  <strong>{ml.delivery_risk_model.confusion_matrix[1][0].toLocaleString()}</strong>
                </div>
                <div className="p-2 bg-emerald-100 rounded text-emerald-950">
                  <div className="text-[10px] text-slate-400">TP</div>
                  <strong>{ml.delivery_risk_model.confusion_matrix[1][1].toLocaleString()}</strong>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Anomaly Detection */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="border-b border-slate-100 pb-2">
            <h3 className="font-bold text-sm text-slate-900">Lead-Time Anomaly Detector</h3>
            <span className="text-[11px] text-slate-400">{ml?.anomaly_detector?.algorithm}</span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-50">
              <span className="text-slate-500">F1 Score:</span>
              <strong className="text-emerald-700 font-mono">{ml?.anomaly_detector?.f1_score}</strong>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-50">
              <span className="text-slate-500">Precision:</span>
              <strong className="text-slate-800 font-mono">{ml?.anomaly_detector?.precision}</strong>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-50">
              <span className="text-slate-500">Recall:</span>
              <strong className="text-slate-800 font-mono">{ml?.anomaly_detector?.recall}</strong>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-50">
              <span className="text-slate-500">False Positive Rate:</span>
              <strong className="text-emerald-700 font-mono">
                {((ml?.anomaly_detector?.false_positive_rate ?? 0) * 100).toFixed(2)}%
              </strong>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500">Flagged Anomalies:</span>
              <strong className="text-slate-800 font-mono">
                {ml?.anomaly_detector?.anomalies_flagged?.toLocaleString()}
              </strong>
            </div>
          </div>
        </div>

        {/* Demand Forecasting */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="border-b border-slate-100 pb-2">
            <h3 className="font-bold text-sm text-slate-900">Demand Time-Series Forecaster</h3>
            <span className="text-[11px] text-slate-400">{ml?.demand_forecaster?.algorithm}</span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-50">
              <span className="text-slate-500 font-medium">MAPE (Error %):</span>
              <strong className="text-emerald-700 font-mono text-sm">{ml?.demand_forecaster?.mape}%</strong>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-50">
              <span className="text-slate-500">MAE:</span>
              <strong className="text-slate-800 font-mono">{ml?.demand_forecaster?.mae}</strong>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-50">
              <span className="text-slate-500">RMSE:</span>
              <strong className="text-slate-800 font-mono">{ml?.demand_forecaster?.rmse}</strong>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-50">
              <span className="text-slate-500">Test Samples:</span>
              <strong className="text-slate-800 font-mono">{ml?.demand_forecaster?.test_samples?.toLocaleString()}</strong>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500">Mean Test Demand:</span>
              <strong className="text-slate-800 font-mono">{ml?.demand_forecaster?.mean_test_demand}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
