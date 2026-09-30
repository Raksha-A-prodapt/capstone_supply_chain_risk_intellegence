import React, { useState } from 'react';
import { 
  LayoutDashboard, Sparkles, RefreshCw, Truck, Award, 
  ShieldCheck, Layers, GitBranch 
} from 'lucide-react';

import Dashboard from './components/Dashboard';
import Assistant from './components/Assistant';
import WhatIfSimulator from './components/WhatIfSimulator';
import SuppliersTable from './components/SuppliersTable';
import EvaluationDashboard from './components/EvaluationDashboard';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [pendingQuery, setPendingQuery] = useState('');

  const navigateToAssistant = (query) => {
    setPendingQuery(query);
    setActiveTab('assistant');
  };

  const navItems = [
    { id: 'dashboard', label: 'Command Center', icon: LayoutDashboard },
    { id: 'assistant', label: 'Ask Assistant', icon: Sparkles },
    { id: 'simulator', label: 'What-If Simulator', icon: RefreshCw },
    { id: 'suppliers', label: 'Suppliers Scorecard', icon: Truck },
    { id: 'evaluation', label: 'Evaluation & ML', icon: Award },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Title */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-700 to-teal-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div>
                <div className="font-extrabold text-slate-900 text-base leading-tight tracking-tight flex items-center gap-2">
                  Supply Chain Risk Intelligence
                  <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
                    6-Agent LangGraph
                  </span>
                </div>
                <div className="text-xs text-slate-400">
                  Deterministic OR Analytics • Live Gateway LLM • Zero-Hallucination Guardrails
                </div>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="flex items-center gap-1">
              {navItems.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => {
                      if (tab.id !== 'assistant') setPendingQuery('');
                      setActiveTab(tab.id);
                    }}
                    className={`px-3 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
                      isActive
                        ? 'bg-emerald-50 text-emerald-800 border border-emerald-200/80 shadow-xs'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-600' : 'text-slate-400'}`} />
                    <span className="hidden md:inline">{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'dashboard' && (
          <Dashboard onSelectQuery={navigateToAssistant} />
        )}

        {activeTab === 'assistant' && (
          <Assistant initialQuery={pendingQuery} key={pendingQuery} />
        )}

        {activeTab === 'simulator' && (
          <WhatIfSimulator />
        )}

        {activeTab === 'suppliers' && (
          <SuppliersTable onSelectSupplier={navigateToAssistant} />
        )}

        {activeTab === 'evaluation' && (
          <EvaluationDashboard />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 mt-12 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div>
            AI-Powered Supply Chain Risk Intelligence Assistant • End-to-End Modular Architecture
          </div>
          <div className="flex items-center gap-4 text-slate-500">
            <span>FastAPI Backend (Python 3.13)</span>
            <span>•</span>
            <span>React 18 + Vite</span>
            <span>•</span>
            <span>OpenAI Gateway (gpt-4o-mini)</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
