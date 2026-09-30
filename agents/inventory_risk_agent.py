"""
Agent 3: Inventory Risk Agent
Responsible for deterministic inventory risk evaluation, days of supply (inventory coverage),
stock-out date projection, supplier delay impact propagation, and deterministic reorder quantities.
"""

import time
from typing import Dict, Any, List, Optional
import pandas as pd
from agents.state import OrchestratorState
from agents.context import SupplyChainContext

class InventoryRiskAgent:
    def __init__(self, context: Optional[SupplyChainContext] = None):
        self.context = context or SupplyChainContext.get_instance()
        self.agent_name = "Inventory Risk Agent"

    def run(self, state: OrchestratorState) -> OrchestratorState:
        start_time = time.time()
        df = self.context.df

        target_products = state.get("target_entities", {}).get("products", [])
        
        # A2A handoff: If upstream Supplier Agent identified high-risk suppliers, check their supplied products!
        upstream_suppliers = []
        if "supplier_risk_agent" in state.get("agent_outputs", {}):
            sup_out = state["agent_outputs"]["supplier_risk_agent"]
            upstream_suppliers = [p["supplier_id"] for p in sup_out.get("supplier_profiles", [])]

        if not target_products and upstream_suppliers:
            # Gather products supplied by these risky suppliers
            sup_records = df[df["supplier_id"].isin(upstream_suppliers)]
            target_products = list(sup_records["product_id"].unique())[:5]

        product_evaluations = []
        if target_products:
            for p_id in target_products:
                p_records = df[df["product_id"] == p_id]
                if not p_records.empty:
                    eval_data = self.context.inventory_analyzer.analyze_product_inventory(p_records)
                    product_evaluations.append(eval_data)
        else:
            # Default to top critical inventory risks across the enterprise
            product_evaluations = self.context.critical_inventories[:6]

        # Determine overall inventory risk level
        risk_levels = [p["risk_level"] for p in product_evaluations]
        if "CRITICAL" in risk_levels:
            overall_inventory_risk = "CRITICAL"
        elif "HIGH" in risk_levels:
            overall_inventory_risk = "HIGH"
        elif "MEDIUM" in risk_levels:
            overall_inventory_risk = "MEDIUM"
        else:
            overall_inventory_risk = "LOW"

        # Construct deterministic evidence
        evidence = []
        for p in product_evaluations:
            evidence.append(
                f"Product {p['product_id']} ({p['product_name']}): Current inventory = {p['current_inventory']:,} units, "
                f"Coverage = {p['days_of_supply']} Days of Supply, Reorder Point = {p['reorder_point']:,}. "
                f"Projected stock-out date is {p['projected_stockout_date']} ({p['days_until_stockout']} days). "
                f"Deterministic recommended reorder quantity: {p['recommended_reorder_quantity']:,} units."
            )

        output_payload = {
            "status": "SUCCESS",
            "inventory_risk_level": overall_inventory_risk,
            "products_evaluated": len(product_evaluations),
            "critical_stockouts_count": sum(1 for p in product_evaluations if p["risk_level"] == "CRITICAL"),
            "high_risk_products_count": sum(1 for p in product_evaluations if p["risk_level"] in ["CRITICAL", "HIGH"]),
            "product_inventory_details": product_evaluations,
            "evidence": evidence,
            "formula_documentation": "ROQ = max(0, ceil(Daily_Demand * Lead_Time + Safety_Stock - Current_Inventory))"
        }

        latency = round((time.time() - start_time) * 1000, 2)

        if "agent_outputs" not in state:
            state["agent_outputs"] = {}
        state["agent_outputs"]["inventory_risk_agent"] = output_payload

        if "agent_trace" not in state:
            state["agent_trace"] = []
        state["agent_trace"].append({
            "step": len(state["agent_trace"]) + 1,
            "agent_name": self.agent_name,
            "status": "SUCCESS",
            "latency_ms": latency,
            "summary": f"Evaluated inventory for {len(product_evaluations)} products. Risk: {overall_inventory_risk}. Critical stockouts: {output_payload['critical_stockouts_count']}",
            "data_points_analyzed": len(product_evaluations)
        })

        return state
