"""
Agent 1: Supplier Risk Analysis Agent
Responsible for analyzing supplier performance metrics, calculating late-delivery rates,
lead-time variability, anomaly frequencies, deterministic supplier risk scores,
and generating evidence-backed risk profiles.
"""

import time
from typing import Dict, Any, List, Optional
from agents.state import OrchestratorState
from agents.context import SupplyChainContext

class SupplierRiskAgent:
    def __init__(self, context: Optional[SupplyChainContext] = None):
        self.context = context or SupplyChainContext.get_instance()
        self.agent_name = "Supplier Risk Agent"

    def run(self, state: OrchestratorState) -> OrchestratorState:
        start_time = time.time()
        target_suppliers = state.get("target_entities", {}).get("suppliers", [])
        
        all_profiles = self.context.supplier_profiles
        selected_profiles = []

        if target_suppliers:
            # Filter for requested suppliers
            for s_id in target_suppliers:
                p = self.context.supplier_scorer.get_supplier_profile(s_id, all_profiles)
                if p:
                    selected_profiles.append(p)

        if not selected_profiles:
            # Return top high-risk suppliers by default
            selected_profiles = all_profiles[:5]

        # Extract specific evidence
        evidence = []
        for p in selected_profiles:
            evidence.append(
                f"Supplier {p['supplier_id']} ({p['supplier_name']}) has an overall risk score of {p['supplier_risk_score']} "
                f"({p['supplier_risk_level']}), late delivery rate of {p['late_delivery_rate']:.1%}, average delay of {p['avg_delay_days']} days, "
                f"lead-time std of {p['lead_time_std_days']} days, and {p['anomaly_count']} detected operational anomalies across {p['total_orders']} orders."
            )

        output_payload = {
            "status": "SUCCESS",
            "suppliers_analyzed": len(selected_profiles),
            "highest_risk_supplier": selected_profiles[0]["supplier_id"] if selected_profiles else None,
            "highest_risk_level": selected_profiles[0]["supplier_risk_level"] if selected_profiles else "LOW",
            "supplier_profiles": selected_profiles,
            "evidence": evidence,
            "weights_used": self.context.supplier_scorer.weights
        }

        latency = round((time.time() - start_time) * 1000, 2)
        
        # Update state
        if "agent_outputs" not in state:
            state["agent_outputs"] = {}
        state["agent_outputs"]["supplier_risk_agent"] = output_payload

        if "agent_trace" not in state:
            state["agent_trace"] = []
        state["agent_trace"].append({
            "step": len(state["agent_trace"]) + 1,
            "agent_name": self.agent_name,
            "status": "SUCCESS",
            "latency_ms": latency,
            "summary": f"Analyzed {len(selected_profiles)} suppliers. Highest risk: {selected_profiles[0]['supplier_id']} ({selected_profiles[0]['supplier_risk_level']})",
            "data_points_analyzed": sum(p["total_orders"] for p in selected_profiles)
        })

        return state
