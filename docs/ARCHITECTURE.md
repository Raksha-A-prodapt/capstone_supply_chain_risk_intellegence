# Supply Chain Risk Intelligence Assistant — Architecture & Design

## 1. End-to-End System Architecture

```mermaid
flowchart TD
    subgraph Data Layer
        RAW["data/dataset.csv (120,000 Records)"]
        PRE["data/preprocessing.py (Quality Checks & Feature Engineering)"]
        RAW --> PRE
    end

    subgraph Analytical & ML Core
        DELIV["ml/delivery_risk.py (Gradient Boosting Classifier - ROC-AUC: 0.774)"]
        ANOM["ml/anomaly_detection.py (Isolation Forest & Z-Score - F1: 0.555)"]
        FORECAST["ml/forecasting.py (Demand Time-Series - MAPE: 29.68%)"]
        INV["ml/inventory_risk.py (Deterministic Days-of-Supply & ROQ)"]
        SUP_SCORE["ml/supplier_risk.py (Transparent Weighted Scoring Engine)"]
        
        PRE --> DELIV
        PRE --> ANOM
        PRE --> FORECAST
        PRE --> INV
        PRE --> SUP_SCORE
    end

    subgraph Knowledge & Semantic Search
        DOCS["knowledge_base/documents/*.md (SLA, SOP, Playbooks)"]
        VEC["knowledge_base/embeddings/kb_vectors.json (1536-dim Vectors)"]
        SEARCH["semantic_search/search.py (Cosine Vector Search)"]
        DOCS --> SEARCH
        VEC --> SEARCH
    end

    subgraph Multi-Agent Orchestration LangGraph
        USER_Q["User Question"] --> IN_GUARD["Input Guardrail (Injection & Safety Check)"]
        IN_GUARD --> ROUTER["LangGraph Router & Entity Extractor"]
        SEARCH --> ROUTER
        
        ROUTER --> A1["Agent 1: Supplier Risk Agent"]
        A1 -- "A2A Handoff (Supplier Profiles)" --> A2["Agent 2: Delivery Risk Agent"]
        A2 -- "A2A Handoff (Transit Bottlenecks)" --> A3["Agent 3: Inventory Risk Agent"]
        A3 -- "A2A Handoff (Stockout Exposures)" --> A4["Agent 4: Demand / Forecasting Agent"]
        A4 -- "A2A Handoff (Projected Trajectories)" --> A5["Agent 5: Supply Chain Insight Agent (Causal Consolidation)"]
        A5 -- "A2A Handoff (Consolidated Chains)" --> A6["Agent 6: Risk Recommendation Agent"]
    end

    subgraph Synthesis, Guardrails & Fallbacks
        A6 --> LLM_CALL{"Call OpenAI Gateway (gpt-4o-mini)"}
        LLM_CALL -- "Success" --> OUT_GUARD["Output Guardrails Validation"]
        OUT_GUARD -- "Schema Valid + Grounded + 0 Hallucination" --> FINAL_RESP["Verified Structured Response Contract"]
        
        LLM_CALL -- "Error / Timeout / Offline" --> FALLBACK["fallbacks/deterministic_fallback.py"]
        OUT_GUARD -- "Guardrail Violation" --> FALLBACK
        FALLBACK --> FINAL_RESP
    end

    subgraph Presentation Layer
        FINAL_RESP --> API["FastAPI REST Endpoints (/api/query, /api/simulate, ...)"]
        API --> UI["React 18 Single Page Application (Light Green & White Modern Theme)"]
    end
```

---

## 2. Six Specialized Agents & A2A Communication Protocol

| Agent | Responsibility | Key Deterministic Metrics | Outbound Handoff Payload |
|---|---|---|---|
| **Agent 1: Supplier Risk Agent** | Evaluates supplier reliability, variance, and order volume | Late delivery rate, average delay days, lead-time variance, supplier risk score & tier | `supplier_profiles`, `highest_risk_supplier`, `scoring_weights` |
| **Agent 2: Delivery Risk Agent** | Analyzes transit delays, routes, carriers (3PL), and customs dwell | Late order rate, average delay, carrier delay rankings, ML forward probability | `late_order_rate`, `avg_delay_days`, `carrier_performance`, `customs_impact` |
| **Agent 3: Inventory Risk Agent** | Analyzes inventory buffers, days of supply, and stockouts | Days of Supply (DOS), projected stockout date, deterministic Recommended Reorder Quantity (ROQ) | `product_inventory_details`, `critical_stockouts_count` |
| **Agent 4: Demand Agent** | Evaluates historical consumption, seasonality, and 30-day forecast | 30-day total projected demand, daily demand rate, MAE, RMSE, and MAPE | `total_projected_demand`, `evaluation_metrics` |
| **Agent 5: Supply Chain Insight Agent** | Consolidates specialist outputs and identifies cross-domain causal chains | Overall system risk level (CRITICAL / HIGH / MEDIUM / LOW), causal risk chains | `overall_supply_chain_risk`, `causal_risk_chains`, `consolidated_evidence` |
| **Agent 6: Risk Recommendation Agent** | Formulates data-backed operational mitigations | Action, category, priority, target entity, rationale, evidence ref | `recommendations`, `grounding_check` |

---

## 3. Strict Deterministic Separation Principle

In strict accordance with the system design requirements:
1. **The LLM is NEVER the source of truth for calculations:**
   - Order counts, delivery delays, days of supply, recommended reorder quantities, anomaly scores, risk scores, forecast numbers, and percentages are computed exclusively by Python, Scikit-Learn, and deterministic formulas.
2. **Operations Research Formulas:**
   $$\text{ROQ} = \max\left(0, \left\lceil \text{Daily Demand} \times \text{Lead Time} + \text{Safety Stock} - \text{Current Inventory} \right\rceil\right)$$
   $$\text{Safety Stock} = Z \times \sqrt{\left(\overline{LT} \times \sigma_{\text{demand}}^2\right) + \left(\overline{D}^2 \times \sigma_{LT}^2\right)}$$
   $$\text{Supplier Risk Score} = 0.35 \cdot \text{LateRate} + 0.20 \cdot \overline{\text{Delay}}_{\text{norm}} + 0.15 \cdot \sigma_{LT,\text{norm}} + 0.15 \cdot \text{AnomRate}_{\text{norm}} + 0.15 \cdot P_{\text{ML}}(\text{Late})$$
3. **The LLM is used solely for natural-language synthesis:**
   - Interprets deterministic results.
   - Summarizes key operational implications.
   - Explains causal chains to decision-makers without altering any numbers.

---

## 4. Guardrails & Deterministic Fallback Architecture

Every incoming and outgoing message passes through an exhaustive verification battery:
- **Input Guardrails**: Rejects prompt injection patterns, malicious payloads, and off-topic questions.
- **Schema Guardrails**: Validates that responses conform strictly to the defined JSON response schema.
- **Grounding Guardrails**: Evaluates that generated claims map directly to verified evidence produced by upstream agents (Grounding Score $\ge 0.75$).
- **Zero-Hallucination Guardrails**: Cross-references all mentioned supplier IDs, product SKUs, and numerical figures against ground-truth tables.
- **Numeric Consistency Guardrails**: Validates that all extracted numbers match calculated analytical values within a 5% tolerance.
- **Deterministic Failover Engine**: If the LLM gateway times out, is unavailable, or violates any guardrail, the system triggers the deterministic fallback engine, returning verified structured operational insights directly with `fallback_used: true`.
