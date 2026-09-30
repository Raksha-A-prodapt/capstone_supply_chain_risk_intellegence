"""
Supply Chain Risk Intelligence Master Assistant
Glues together the entire system:
Input Guardrails -> Vector Retrieval -> LangGraph Orchestrator -> LLM Interpretation
-> Grounding & Hallucination Guardrails -> Deterministic Fallbacks -> Final Response Contract.
"""

import time
import re
from typing import Dict, Any, Optional
from config.settings import settings
from agents.context import SupplyChainContext
from agents.orchestrator import SupplyChainOrchestrator
from llm.client import GatewayLLMClient
from guardrails.input_guardrails import InputGuardrail
from guardrails.output_guardrails import OutputGuardrails
from fallbacks.deterministic_fallback import DeterministicFallbackEngine
from simulator.what_if_simulator import WhatIfSimulator

class SupplyChainAssistant:
    def __init__(self):
        self.context = SupplyChainContext.get_instance()
        self.orchestrator = SupplyChainOrchestrator(self.context)
        self.llm_client = GatewayLLMClient()
        self.input_guardrail = InputGuardrail()
        self.output_guardrails = OutputGuardrails()
        self.fallback_engine = DeterministicFallbackEngine()
        self.simulator = WhatIfSimulator(self.context)

    def process_query(self, query: str, force_fallback: bool = False) -> Dict[str, Any]:
        """Processes query through the complete end-to-end pipeline."""
        start_time = time.time()

        # 1. INPUT GUARDRAIL
        input_check = self.input_guardrail.validate(query)
        if not input_check["is_valid"]:
            return {
                "query": query,
                "answer": f"**Query Rejected by Input Guardrail:** {input_check['rejection_reason']}",
                "risk_level": "LOW",
                "agents_involved": [],
                "agent_trace": [],
                "agent_outputs": {},
                "handoffs": [],
                "evidence": [],
                "recommendations": [],
                "ml_predictions": {},
                "forecast": {},
                "anomalies": [],
                "knowledge_context": [],
                "guardrails": {
                    "input_valid": False,
                    "schema_valid": False,
                    "grounded": False,
                    "hallucination_detected": False,
                    "numeric_consistency": False,
                    "rejection_reason": input_check["rejection_reason"]
                },
                "evaluation": {"grounding_score": 0.0, "factual_consistency": 0.0, "hallucination_rate": 0.0},
                "llm": {"used": False, "model": settings.MODEL_NAME, "fallback_used": False, "fallback_reason": None},
                "what_if_simulation": None,
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "status": "rejected"
            }

        sanitized_query = input_check["sanitized_query"]

        # 2. WHAT-IF SIMULATION DETECTION
        simulation_data = None
        sim_match = re.search(r"(?:sup-\d{3}|apex|redstar|harborview|pacific)", sanitized_query, re.IGNORECASE)
        days_match = re.search(r"(\d+)\s*(?:day|days)", sanitized_query, re.IGNORECASE)
        if ("what happens" in sanitized_query.lower() or "simulate" in sanitized_query.lower()) and sim_match:
            sup_candidate = sim_match.group(0).upper()
            if not sup_candidate.startswith("SUP-"):
                # Map name to ID
                for p in self.context.supplier_profiles:
                    if sup_candidate.lower() in p["supplier_name"].lower():
                        sup_candidate = p["supplier_id"]
                        break
            if not sup_candidate.startswith("SUP-"):
                sup_candidate = "SUP-023"
            
            added_days = int(days_match.group(1)) if days_match else 7
            simulation_data = self.simulator.simulate_supplier_delay(sup_candidate, added_days)

        # 3. LANGGRAPH MULTI-AGENT ORCHESTRATION & A2A HANDOFFS
        state = self.orchestrator.execute(sanitized_query)
        agent_outputs = state.get("agent_outputs", {})
        ins_out = agent_outputs.get("insight_agent", {})
        rec_out = agent_outputs.get("recommendation_agent", {})
        del_out = agent_outputs.get("delivery_risk_agent", {})
        dmd_out = agent_outputs.get("demand_agent", {})

        overall_risk = ins_out.get("overall_supply_chain_risk", "MEDIUM")
        evidence = ins_out.get("consolidated_evidence", [])
        recommendations = rec_out.get("recommendations", [])

        # Extract ML predictions & forecast summaries
        ml_preds = {
            "delivery_risk_probability": del_out.get("ml_model_predicted_late_prob", 0.0) if del_out else 0.0,
            "delivery_model_f1": self.context.delivery_model.metrics.get("f1_score", 0.0),
            "anomaly_detector_f1": self.context.anomaly_detector.metrics.get("f1_score", 0.0)
        }
        forecast_summary = {
            "target_product": dmd_out.get("target_product_id") if dmd_out else None,
            "projected_demand": dmd_out.get("total_projected_demand") if dmd_out else None,
            "evaluation_metrics": dmd_out.get("evaluation_metrics", {}) if dmd_out else {}
        }

        # 4. LLM INTERPRETATION OR DETERMINISTIC FALLBACK
        llm_meta = {
            "used": False,
            "model": settings.MODEL_NAME,
            "fallback_used": False,
            "fallback_reason": None
        }

        if force_fallback:
            print("[Assistant] Fallback explicitly forced.")
            llm_res = self.fallback_engine.generate_fallback_response(sanitized_query, state, reason="Forced deterministic fallback test")
            llm_meta["fallback_used"] = True
            llm_meta["fallback_reason"] = "Forced deterministic fallback test"
        else:
            try:
                llm_res = self.llm_client.generate_explanation(
                    query=sanitized_query,
                    structured_agent_results=agent_outputs,
                    knowledge_context=state.get("knowledge_context", []),
                    overall_risk=overall_risk
                )
                llm_meta["used"] = True
            except Exception as e:
                print(f"[Assistant] LLM call failed ({e}). Engaging deterministic fallback engine...")
                llm_res = self.fallback_engine.generate_fallback_response(sanitized_query, state, reason=str(e))
                llm_meta["fallback_used"] = True
                llm_meta["fallback_reason"] = str(e)

        # 5. OUTPUT GUARDRAILS (Grounding, Hallucination, Numeric Consistency, Schema)
        guardrail_res = self.output_guardrails.validate(llm_res, evidence, agent_outputs)

        # If LLM response failed guardrails, switch to deterministic fallback!
        if not guardrail_res["all_passed"] and not llm_meta["fallback_used"]:
            print(f"[Assistant] Guardrail violation detected! Fallback to deterministic results.")
            llm_res = self.fallback_engine.generate_fallback_response(
                sanitized_query, state, reason=f"Guardrail violation: Grounded={guardrail_res['grounded']}, Hallucination={guardrail_res['hallucination_detected']}, Numeric={guardrail_res['numeric_consistency']}"
            )
            llm_meta["fallback_used"] = True
            llm_meta["fallback_reason"] = "Guardrail violation in LLM text"
            guardrail_res = self.output_guardrails.validate(llm_res, evidence, agent_outputs)

        answer_text = llm_res.get("natural_language_answer", "")
        if simulation_data and "is_simulation" in simulation_data:
            answer_text += (
                f"\n\n### What-If Simulation Result (Supplier {simulation_data['scenario']['supplier_id']} +{simulation_data['scenario']['delay_days']} Days Delay)\n"
                f"- **Risk Level:** {simulation_data['risk_level']}\n"
                f"- **Affected Products:** {simulation_data['affected_products_count']}\n"
                f"- **Potential Stockouts Triggered:** {simulation_data['potential_stockouts_count']}\n"
                f"- **Average Inventory Coverage Drop:** {simulation_data['inventory_coverage_reduction_days']} Days of Supply\n"
                f"- **Estimated Financial Risk Exposure:** ${simulation_data['estimated_financial_exposure_usd']:,.2f}\n"
                f"- *Note: This calculation is a deterministic operational simulation based on historical consumption.*"
            )

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # Build Final Response conforming to Section 37 Contract
        response_contract = {
            "query": sanitized_query,
            "answer": answer_text,
            "risk_level": overall_risk,
            "agents_involved": state.get("active_agents", []),
            "agent_trace": state.get("agent_trace", []),
            "agent_outputs": agent_outputs,
            "handoffs": state.get("handoffs", []),
            "evidence": evidence[:8],
            "recommendations": recommendations,
            "ml_predictions": ml_preds,
            "forecast": forecast_summary,
            "anomalies": self.context.anomalies[:5],
            "knowledge_context": state.get("knowledge_context", []),
            "guardrails": {
                "input_valid": True,
                "schema_valid": guardrail_res["schema_valid"],
                "grounded": guardrail_res["grounded"],
                "hallucination_detected": guardrail_res["hallucination_detected"],
                "numeric_consistency": guardrail_res["numeric_consistency"]
            },
            "evaluation": {
                "grounding_score": guardrail_res["grounding_score"],
                "factual_consistency": guardrail_res["numeric_consistent_ratio"],
                "hallucination_rate": guardrail_res["hallucination_rate"]
            },
            "llm": llm_meta,
            "what_if_simulation": simulation_data,
            "latency_ms": latency_ms,
            "status": "success"
        }

        return response_contract
