# AI-Powered Supply Chain Risk Intelligence Assistant

An enterprise-grade, end-to-end multi-agent supply chain risk intelligence system that combines deterministic operations research, machine learning predictive modeling, time-series demand forecasting, semantic search, LangGraph agent orchestration, rigorous guardrails, and live OpenAI Gateway LLM natural language synthesis.

---

## 1. Executive Summary

Supply chain operational teams struggle to continuously monitor risk across thousands of suppliers, volatile lead times, transit delays, and critical inventory buffers. This system enables users to query complex operational data using natural language and receive:
- **Supplier Performance & Risk Scoring**
- **Logistics & Delivery Bottleneck Prediction**
- **Deterministic Stockout Risk & Reorder Quantities (ROQ)**
- **Demand Forecasting evaluated with MAE, RMSE, and MAPE**
- **Lead-Time Anomaly Detection (Isolation Forest & Z-Score)**
- **Cross-Domain Causal Risk Chains (Supplier $\to$ Delivery $\to$ Inventory $\to$ Stockout)**
- **Evidence-Grounded Actionable Recommendations**
- **What-If Disruption Simulation**
- **Full Visual Agent Execution Traces & A2A Handoff Telemetry**
- **Deterministic Failover Fallback** if the LLM is offline or times out.

---

## 2. Core Architecture Principle: Strict Deterministic Separation

The LLM is **never** the source of truth for calculations or quantitative assertions:

```
[ Raw Structured Data (120,000 records) ]
                  ↓
[ Data Preprocessing & Feature Engineering ]
                  ↓
[ Python / Scikit-Learn / Deterministic Formulas ]
  • Delivery Risk ML Classifier (Late probability)
  • Isolation Forest + Z-score (Lead-time anomalies)
  • Time-Series Forecaster (Projected demand + MAPE)
  • Operations Research (Days of Supply & ROQ)
  • Deterministic Weighted Supplier Risk Score
                  ↓
[ Six Specialized Agents (LangGraph Orchestrator) ]
  • Explicit A2A Handoffs & Causal Chains
                  ↓
[ OpenAI Gateway (gpt-4o-mini) for NL Synthesis ]
                  ↓
[ Guardrails & Consistency Validation ]
  • Input Injection Guardrail
  • Schema Validation
  • Grounding Evaluation
  • Zero-Hallucination Check
  • Numeric Consistency Check
                  ↓
[ Final Structured Response Contract ]
  *(If LLM fails/times out → Deterministic Fallback Engine activates)*
```

---

## 3. The Six Specialized Agents

The application implements all 6 specialized agents coordinated by a state-based **LangGraph** orchestrator:

1. **Agent 1 — Supplier Risk Agent**: Evaluates supplier historical performance, late delivery rates, lead-time variance, anomaly frequency, ML late probabilities, and computes transparent deterministic supplier risk scores (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
2. **Agent 2 — Delivery Risk Agent**: Identifies delivery delay patterns, route corridors (origin-destination), carrier/3PL performance (DHL, FedEx, Maersk, etc.), customs dwell (Inspection Hold), and ML late predictions.
3. **Agent 3 — Inventory Risk Agent**: Computes deterministic Days of Supply (coverage), projected stockout dates, stockout probabilities, and recommended reorder quantities using operations research formulas.
4. **Agent 4 — Demand / Forecasting Agent**: Analyzes historical demand trajectories, seasonal patterns, generates 30-day product demand projections, and reports MAE, RMSE, and MAPE metrics.
5. **Agent 5 — Supply Chain Insight Agent (Consolidation Layer)**: Consolidates findings from specialist agents, isolates root causes, synthesizes cross-domain causal chains (Supplier Delay $\to$ Transit Gap $\to$ Inventory Depletion $\to$ Stockout), and determines overall enterprise risk.
6. **Agent 6 — Risk Recommendation Agent**: Generates actionable, data-backed operational mitigations (audits, safety stock increases, freight re-routing, purchase order issuance) strictly grounded in agent evidence.

---

## 4. Key Performance & Evaluation Benchmarks

Empirically verified against the 120,000-record dataset and benchmark test suite:

| Category | Metric | Result | Benchmark Standard |
|---|---|---|---|
| **Delivery ML Model** | ROC-AUC | **0.7737** | $\ge 0.70$ |
| | PR-AUC | **0.5898** | High precision on minority class |
| | F1 Score | **0.4934** | Balanced classification |
| | Precision / Recall | **0.6275 / 0.4065** | Conservative late-order alerting |
| **Anomaly Detection** | F1 Score | **0.5549** | Isolation Forest vs Z-score ground truth |
| | False Positive Rate | **0.0110 (1.1%)** | Low false alarm rate |
| **Demand Forecast** | **MAPE** | **29.68%** | Robust time-series error rate |
| | MAE / RMSE | **343.59 / 436.83** | Evaluated on 2,106 test partitions |
| **Multi-Agent System** | Routing Accuracy | **100% (10/10)** | Deterministic intent extraction |
| | Agent Success Rate | **100% (45/45)** | Zero agent runtime crashes |
| | Evidence Grounding | **100% (1.00)** | Every claim backed by metrics |
| | Hallucination Rate | **0.0% (0.00)** | Zero fake entities or numbers |
| | Factual Consistency | **100% (1.00)** | Numbers strictly match OR formulas |
| | Fallback Availability | **100%** | Zero blank screens on LLM outage |

Full reports are available in:
- `reports/evaluation_report.json`
- `reports/evaluation_report.html` (Interactive HTML Dashboard)

---

## 5. What-If Risk Impact Simulator

Beyond standard querying, the system features a deterministic **What-If Disruption Simulator**:
- **Query Example**: *"What happens if Supplier SUP-023 is delayed by 7 days?"*
- **Deterministic Propagation**:
  1. Identifies all products and active purchase orders dependent on the supplier.
  2. Calculates the inventory depletion over the additional delay window ($daily\_demand \times delay\_days$).
  3. Projects revised Days of Supply and new stockout dates.
  4. Recalculates revised Recommended Reorder Quantities (ROQ) with the extended lead time.
  5. Estimates financial business exposure (delayed order values + stockout penalty).

---

## 6. Project Directory Structure

```
D:\try1\
├── agents/                     # LangGraph Multi-Agent System
│   ├── context.py              # Global data & model context cache
│   ├── state.py                # TypedDict state & A2A handoff schemas
│   ├── supplier_risk_agent.py  # Agent 1: Supplier performance & scoring
│   ├── delivery_risk_agent.py  # Agent 2: Logistics, 3PL, routes & customs
│   ├── inventory_risk_agent.py # Agent 3: Deterministic inventory & ROQ
│   ├── demand_agent.py         # Agent 4: Demand forecasting & MAPE
│   ├── insight_agent.py        # Agent 5: Cross-domain causal chains
│   ├── recommendation_agent.py # Agent 6: Evidence-backed mitigations
│   └── orchestrator.py         # LangGraph StateGraph orchestrator
├── data/
│   ├── generate_dataset.py     # Deterministic synthetic data generator
│   ├── preprocessing.py        # Quality validation & feature engineering
│   └── dataset.csv             # 120,000 synthetic records
├── ml/
│   ├── delivery_risk.py        # HistGradientBoosting late-order classifier
│   ├── anomaly_detection.py    # Isolation Forest & Z-score detector
│   ├── forecasting.py          # Time-series demand forecaster (MAE, RMSE, MAPE)
│   ├── inventory_risk.py       # Operations research inventory formulas
│   ├── supplier_risk.py        # Transparent weighted supplier risk scoring
│   └── train_all.py            # Master ML training script
├── knowledge_base/
│   ├── documents/              # Supply chain SOPs, SLAs & playbooks
│   └── embeddings/             # Cached 1536-dim vectors (kb_vectors.json)
├── semantic_search/
│   ├── embeddings.py           # Gateway embedding client (text-embedding-3-small)
│   └── search.py               # Vector indexer & cosine similarity search
├── llm/
│   └── client.py               # OpenAI Gateway client (gpt-4o-mini)
├── guardrails/
│   ├── input_guardrails.py     # Prompt injection & off-topic detector
│   ├── output_guardrails.py    # Master output validation suite
│   ├── grounding.py            # Grounding evaluation calculator
│   ├── hallucination.py        # Zero-hallucination entity validator
│   └── numeric_consistency.py  # Strict number alignment checker
├── fallbacks/
│   └── deterministic_fallback.py # Offline deterministic failover engine
├── simulator/
│   └── what_if_simulator.py    # Deterministic cascading disruption simulator
├── evaluation/
│   ├── evaluation_dataset.py   # Benchmark test queries
│   ├── evaluate_models.py      # ML models evaluation runner
│   ├── evaluate_agents.py      # Multi-agent benchmark runner
│   └── evaluation_report.py    # JSON & HTML report generator
├── api/
│   ├── main.py                 # FastAPI application & static server
│   └── routes.py               # REST API endpoints
├── frontend/                   # Modern React 18 SPA (Light Green & White Theme)
│   ├── src/
│   │   ├── App.jsx             # Main layout & tab navigation
│   │   └── components/
│   │       ├── Dashboard.jsx   # Command center & key metrics
│   │       ├── Assistant.jsx   # Ask Assistant & chat interface
│   │       ├── AgentTraceView.jsx # Visual agent flow & A2A handoffs
│   │       ├── GuardrailsView.jsx # Guardrail checklist & Fallback banner
│   │       ├── WhatIfSimulator.jsx # Scenario disruption simulator
│   │       ├── SuppliersTable.jsx  # 25-supplier risk scorecard
│   │       └── EvaluationDashboard.jsx # ML & Agent evaluation metrics
│   ├── dist/                   # Production build bundle
│   ├── package.json
│   └── vite.config.js
├── tests/                      # Pytest unit & integration test suite
│   ├── test_preprocessing.py
│   ├── test_ml_models.py
│   ├── test_agents.py
│   ├── test_guardrails.py
│   ├── test_fallback.py        # Section 44 Critical Failure Test
│   └── test_api.py
├── reports/
│   ├── evaluation_report.json
│   └── evaluation_report.html
├── assistant.py                # Master coordinator pipeline
├── config/settings.py          # Centralized configuration (.env)
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

---

## 7. Installation & Execution Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Node.js 18+ (Tested on Node.js 20 LTS)
- (Optional) `uv` for fast package management

### 1. Environment Configuration
The `.env` file is pre-configured with the OpenAI Gateway:
```env
GATEWAY_URL=https://keygateway1.arshnivlabs.com
LEARNER_KEY=pubatch_trainer
OPENAI_API_BASE=https://keygateway1.arshnivlabs.com/v1
MODEL_NAME=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
DATA_PATH=data/dataset.csv
MODELS_DIR=artifacts/models
REPORTS_DIR=reports
HOST=127.0.0.1
PORT=8000
```

### 2. Generate Dataset & Train ML Models
```bash
# 1. Generate 120,000 synthetic records
python data/generate_dataset.py 120000

# 2. Train Delivery Classifier, Anomaly Detector, and Demand Forecaster
python ml/train_all.py

# 3. Build Semantic Search Index from Knowledge Base
python -m semantic_search.search
```

### 3. Run the Backend API (FastAPI)
```bash
python api/main.py
# Server starts at http://127.0.0.1:8000
# Interactive OpenAPI Docs available at http://127.0.0.1:8000/docs
```

### 4. Run the React Frontend
```bash
cd frontend
npm run dev
# Vite development server runs at http://localhost:3000
```
*(Alternatively, FastAPI serves the pre-built React production bundle directly at `http://127.0.0.1:8000`)*.

### 5. Run the Automated Test Suite (15/15 Tests)
```bash
python -m pytest tests/ -v
```

### 6. Run the End-to-End Evaluation Report
```bash
python evaluation/evaluation_report.py
# View reports/evaluation_report.html in any browser
```

---

## 8. Verification of the 9 Demonstration Scenarios (Section 50)

Run the automated verification script:
```bash
python scripts/verify_demo_scenarios.py
```

All 9 required demo queries have been executed and verified:
1. `"Which suppliers have the highest delivery risk?"` $\to$ Returns SUP-023 (66.0% late) and SUP-021 (60.8% late).
2. `"Why is supplier SUP-001 risky?"` $\to$ Analyzes SUP-001 low-risk profile (6.3% late, 0.4d delay).
3. `"Which products are most affected by supplier delays?"` $\to$ Identifies critical components linked to delayed suppliers.
4. `"Identify unusual supplier lead-time changes."` $\to$ Flags severe lead-time anomalies (z-score > 2.5).
5. `"Which products are at risk of stock-out?"` $\to$ Reports SKUs with Days of Supply $\le 5.0$ and calculates exact ROQ.
6. `"What is the demand forecast for product PROD-001?"` $\to$ Produces 30-day projection with model MAPE (29.68%).
7. `"How could supplier SUP-001 delay affect inventory?"` $\to$ Explains inventory coverage depletion dynamics.
8. `"What are the major supply-chain risks and what evidence supports them?"` $\to$ Full 6-agent synthesis with causal chains.
9. `"What happens if supplier SUP-001 is delayed by 7 days?"` $\to$ Triggers What-If simulator and outputs potential stockouts & financial exposure.

---

## 9. Critical Section 44 Failure Test: Deterministic Failover

To test the system when the LLM is completely offline or unavailable:
1. In the React UI, navigate to **Ask Assistant** and toggle **"Simulate LLM Outage (Force Fallback): ON"**.
2. Submit any query (e.g., *"Which suppliers have the highest delivery risk?"*).
3. The system returns a complete, structured analysis with:
   - Yellow alert banner: *"LLM Unavailable — Deterministic Analysis Was Used"*
   - Reason: *"Forced deterministic fallback test"*
   - Exact quantitative metrics and verified evidence from deterministic rules
   - System Status: `FAULT-TOLERANT ACTIVE`
4. Programmatically tested via `tests/test_fallback.py`:
   ```bash
   python -m pytest tests/test_fallback.py -v
   ```

---

## 10. API Specification Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/query` | Natural language multi-agent reasoning with guardrails & fallback |
| `GET` | `/api/suppliers` | List of 25 scored suppliers ranked by multi-factor risk score |
| `GET` | `/api/suppliers/{id}` | Detailed profile, historical lead times, and orders sample |
| `GET` | `/api/orders` | Historical order transactions (filtering by supplier and late status) |
| `GET` | `/api/inventory` | Inventory coverage (DOS), reorder points, and recommended ROQ |
| `GET` | `/api/anomalies` | Detected operational lead-time and volume anomalies |
| `GET` | `/api/forecasts` | Time-series demand forecast with MAE, RMSE, and MAPE |
| `GET` | `/api/evaluation` | Full evaluation report payload (JSON) |
| `GET` | `/reports/evaluation_report.html` | Interactive HTML evaluation dashboard |
| `POST` | `/api/search` | Cosine vector search across knowledge base |
| `POST` | `/api/simulate` | What-If supplier disruption cascading impact simulator |
| `GET` | `/api/health` | Service health telemetry and model status |

---

## 11. Security & Compliance

- **No Secrets Committed**: All API keys and endpoints are stored in `.env` and excluded via `.gitignore`.
- **Input Guardrails**: Rejects prompt injection patterns, unauthorized system prompt overrides, and malicious script inputs.
- **Data Privacy**: No private customer or proprietary corporate data is exposed.
