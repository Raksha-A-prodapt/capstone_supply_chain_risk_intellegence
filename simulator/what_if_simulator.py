"""
What-If Risk Impact Simulator
Simulates operational cascading impacts when a specific supplier experiences a delay disruption.
Propagates delay -> delivery -> inventory depletion -> stock-out risk -> financial business impact.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from agents.context import SupplyChainContext

class WhatIfSimulator:
    def __init__(self, context: Optional[SupplyChainContext] = None):
        self.context = context or SupplyChainContext.get_instance()

    def simulate_supplier_delay(self, supplier_id: str, added_delay_days: int = 7) -> Dict[str, Any]:
        """Performs deterministic what-if cascading simulation."""
        df = self.context.df
        supplier_orders = df[df["supplier_id"] == supplier_id]

        if supplier_orders.empty:
            return {
                "error": f"Supplier {supplier_id} not found in database.",
                "scenario": {"supplier_id": supplier_id, "delay_days": added_delay_days}
            }

        supplier_name = supplier_orders["supplier_name"].iloc[0]
        affected_orders_count = len(supplier_orders.tail(50)) # active simulated window
        total_order_value = float(supplier_orders.tail(50)["order_value"].sum())

        # Determine products supplied
        unique_products = list(supplier_orders["product_id"].unique())
        affected_products_detail = []
        stockouts_caused = 0

        total_coverage_reduction = 0.0

        for p_id in unique_products:
            p_records = df[df["product_id"] == p_id]
            if p_records.empty:
                continue

            base_eval = self.context.inventory_analyzer.analyze_product_inventory(p_records)
            current_inv = base_eval["current_inventory"]
            daily_demand = base_eval["daily_demand"]
            base_dos = base_eval["days_of_supply"]

            # Simulated depletion over additional delay
            inventory_depletion = daily_demand * added_delay_days
            simulated_inv = max(0, int(current_inv - inventory_depletion))
            simulated_dos = round(simulated_inv / daily_demand, 1)
            coverage_drop = round(base_dos - simulated_dos, 1)
            total_coverage_reduction += coverage_drop

            # Projected stockout date shift
            new_days_to_stockout = max(0, int(np.floor(simulated_inv / daily_demand)))
            new_stockout_date = (datetime.now() + timedelta(days=new_days_to_stockout)).strftime("%Y-%m-%d")

            is_stockout = simulated_inv <= (daily_demand * 2.0)
            if is_stockout:
                stockouts_caused += 1

            new_roq = self.context.inventory_analyzer.calculate_reorder_quantity(
                current_inventory=simulated_inv,
                daily_demand=daily_demand,
                lead_time_days=base_eval["lead_time_days"] + added_delay_days,
                safety_stock=base_eval["safety_stock"]
            )

            affected_products_detail.append({
                "product_id": p_id,
                "product_name": base_eval["product_name"],
                "baseline_inventory": current_inv,
                "simulated_inventory": simulated_inv,
                "baseline_days_of_supply": base_dos,
                "simulated_days_of_supply": simulated_dos,
                "coverage_reduction_days": coverage_drop,
                "new_projected_stockout_date": new_stockout_date,
                "stockout_triggered": is_stockout,
                "revised_reorder_quantity": new_roq,
                "simulated_risk_level": "CRITICAL" if simulated_dos <= 4.0 else ("HIGH" if simulated_dos <= 10.0 else "MEDIUM")
            })

        avg_coverage_reduction = round(total_coverage_reduction / max(1, len(unique_products)), 1)

        # Financial impact estimation
        # Direct delayed order value + potential stockout penalty (estimated at $150 per stockout day)
        penalty_estimate = round(stockouts_caused * added_delay_days * 350.0 + (total_order_value * 0.05), 2)

        # Risk level determination
        if stockouts_caused >= 3 or added_delay_days >= 14:
            simulated_risk_level = "CRITICAL"
        elif stockouts_caused >= 1 or added_delay_days >= 7:
            simulated_risk_level = "HIGH"
        else:
            simulated_risk_level = "MEDIUM"

        evidence = [
            f"Simulated +{added_delay_days} days delay on Supplier {supplier_id} ({supplier_name}).",
            f"Directly impacts {len(unique_products)} product lines across {affected_orders_count} purchase orders.",
            f"Average product inventory coverage drops by {avg_coverage_reduction} Days of Supply.",
            f"Triggers {stockouts_caused} immediate stockout critical events across downstream inventory.",
            f"Estimated operational and financial risk exposure: ${penalty_estimate:,.2f}."
        ]

        assumptions = [
            f"Daily customer demand remains consistent during the {added_delay_days}-day disruption window.",
            "No alternative secondary supplier allocations were enacted prior to simulated delay.",
            "Material consumption continues at the 30-day baseline moving average."
        ]

        return {
            "simulation_type": "WHAT_IF_SUPPLIER_DISRUPTION",
            "scenario": {
                "supplier_id": supplier_id,
                "supplier_name": supplier_name,
                "delay_days": added_delay_days
            },
            "risk_level": simulated_risk_level,
            "affected_products_count": len(unique_products),
            "affected_orders_count": affected_orders_count,
            "potential_stockouts_count": stockouts_caused,
            "inventory_coverage_reduction_days": avg_coverage_reduction,
            "estimated_financial_exposure_usd": penalty_estimate,
            "affected_products_detail": affected_products_detail,
            "evidence": evidence,
            "assumptions": assumptions,
            "is_simulation": True
        }
