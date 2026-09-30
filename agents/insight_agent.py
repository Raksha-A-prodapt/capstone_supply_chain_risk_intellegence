"""
Agent 5: Supply Chain Insight Agent (Consolidation Layer)
Consolidates analytical outputs from specialist agents, synthesizes cross-domain causal chains,
correlates supplier bottlenecks with downstream inventory depletion, and establishes the overall risk picture.
"""

import time
from typing import Dict, Any, List, Optional
from agents.state import OrchestratorState

class InsightAgent:
    def __init__(self):
        self.agent_name = "Supply Chain Insight Agent"

    def run(self, state: OrchestratorState) -> OrchestratorState:
        start_time = time.time()
        agent_outputs = state.get("agent_outputs", {})

        sup_out = agent_outputs.get("supplier_risk_agent")
        del_out = agent_outputs.get("delivery_risk_agent")
        inv_out = agent_outputs.get("inventory_risk_agent")
        dmd_out = agent_outputs.get("demand_agent")

        causal_chains = []
        consolidated_evidence = []
        identified_risks = []

        # 1. Gather all upstream evidence
        for agent_key, out in agent_outputs.items():
            if isinstance(out, dict) and "evidence" in out:
                consolidated_evidence.extend(out["evidence"])

        # 2. Correlate Supplier and Delivery Risk
        highest_risk_supplier = None
        supplier_risk_level = "LOW"
        if sup_out and sup_out.get("supplier_profiles"):
            top_sup = sup_out["supplier_profiles"][0]
            highest_risk_supplier = top_sup["supplier_id"]
            supplier_risk_level = top_sup["supplier_risk_level"]

            if top_sup["supplier_risk_level"] in ["HIGH", "CRITICAL"]:
                identified_risks.append({
                    "domain": "Supplier Performance",
                    "severity": top_sup["supplier_risk_level"],
                    "description": f"Supplier {top_sup['supplier_id']} exhibits severe operational instability with {top_sup['late_delivery_rate']:.1%} late delivery rate and {top_sup['avg_delay_days']} days average delay."
                })

        # 3. Correlate Delivery Bottlenecks with Inventory
        delivery_risk_level = del_out.get("delivery_risk_level", "LOW") if del_out else "LOW"
        inventory_risk_level = inv_out.get("inventory_risk_level", "LOW") if inv_out else "LOW"

        if del_out and del_out.get("delivery_risk_level") in ["HIGH", "CRITICAL"]:
            identified_risks.append({
                "domain": "Logistics & Delivery",
                "severity": del_out["delivery_risk_level"],
                "description": f"Transit delays are elevated ({del_out['avg_delay_days']} days delay on late orders). ML models predict {del_out['ml_model_predicted_late_prob']:.1%} forward delay probability."
            })

        # 4. Formulate explicit Causal Chains (Supplier -> Delivery -> Inventory -> Stock-Out)
        if highest_risk_supplier and inv_out and inv_out.get("product_inventory_details"):
            critical_prods = [p for p in inv_out["product_inventory_details"] if p["risk_level"] in ["CRITICAL", "HIGH"]]
            if critical_prods:
                target_p = critical_prods[0]
                causal_chains.append({
                    "chain_type": "SUPPLIER_TO_STOCKOUT_CASCADE",
                    "root_cause": f"Elevated delivery delays from supplier {highest_risk_supplier} ({supplier_risk_level} risk)",
                    "transmission": f"Inbound transit delay propagates into warehouse replenishment gap ({del_out.get('avg_delay_days', 5.0) if del_out else 5.0} days average delay)",
                    "impact": f"Inventory for {target_p['product_id']} ({target_p['product_name']}) dropped to {target_p['days_of_supply']} days of supply",
                    "ultimate_risk": f"Projected stock-out on {target_p['projected_stockout_date']} unless {target_p['recommended_reorder_quantity']:,} units are replenished immediately.",
                    "evidence_grounding": [
                        f"Supplier {highest_risk_supplier} late rate: {sup_out['supplier_profiles'][0]['late_delivery_rate']:.1%}" if sup_out else "Supplier metrics",
                        f"Product {target_p['product_id']} coverage: {target_p['days_of_supply']} DOS",
                        f"Deterministic ROQ: {target_p['recommended_reorder_quantity']} units"
                    ]
                })

        # Determine overall consolidated risk level
        levels = [supplier_risk_level, delivery_risk_level, inventory_risk_level]
        if "CRITICAL" in levels:
            overall_system_risk = "CRITICAL"
        elif "HIGH" in levels:
            overall_system_risk = "HIGH"
        elif "MEDIUM" in levels:
            overall_system_risk = "MEDIUM"
        else:
            overall_system_risk = "LOW"

        output_payload = {
            "status": "SUCCESS",
            "overall_supply_chain_risk": overall_system_risk,
            "identified_risks": identified_risks,
            "causal_risk_chains": causal_chains,
            "risk_interconnectivity": "HIGH_CORRELATION" if causal_chains else "INDEPENDENT_FACTORS",
            "consolidated_evidence": consolidated_evidence,
            "summary": (
                f"Multi-agent synthesis identifies an overall {overall_system_risk} risk state. "
                f"Root vulnerabilities stem from supplier performance ({supplier_risk_level}) and logistics dwell, "
                f"directly threatening stock-out exposure across {len(inv_out.get('product_inventory_details', [])) if inv_out else 0} active SKUs."
            )
        }

        latency = round((time.time() - start_time) * 1000, 2)

        if "agent_outputs" not in state:
            state["agent_outputs"] = {}
        state["agent_outputs"]["insight_agent"] = output_payload

        if "agent_trace" not in state:
            state["agent_trace"] = []
        state["agent_trace"].append({
            "step": len(state["agent_trace"]) + 1,
            "agent_name": self.agent_name,
            "status": "SUCCESS",
            "latency_ms": latency,
            "summary": f"Synthesized findings across specialist agents. Overall risk: {overall_system_risk}. Formed {len(causal_chains)} causal risk chains.",
            "data_points_analyzed": len(consolidated_evidence)
        })

        return state
