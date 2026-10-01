"""
Inventory Risk & Stock-out Deterministic Analytics
Calculates inventory coverage, stockout probabilities, projected depletion dates,
and recommended reorder quantities using strict deterministic operations research formulas.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from config.settings import settings

class InventoryRiskAnalyzer:
    def __init__(self, z_score: float = None):
        # Default 95% service level = 1.65 standard deviations
        self.z_score = z_score or settings.SAFETY_STOCK_Z

    def calculate_reorder_quantity(
        self,
        current_inventory: int,
        daily_demand: float,
        lead_time_days: int,
        safety_stock: int
    ) -> int:
        """
        Deterministic Reorder Quantity Formula:
        ROQ = max(0, ceil(expected_demand_during_lead_time + safety_stock - current_inventory))
        """
        expected_demand_during_lt = daily_demand * lead_time_days
        target_inventory = expected_demand_during_lt + safety_stock
        roq = max(0, int(np.ceil(target_inventory - current_inventory)))
        return roq

    def analyze_product_inventory(self, df_product_records: pd.DataFrame) -> Dict[str, Any]:
        """Performs inventory risk analysis for a product's latest state."""
        if df_product_records.empty:
            return {"error": "No records found for product."}

        latest_record = df_product_records.sort_values(by="order_date").iloc[-1]
        product_id = latest_record["product_id"]
        product_name = latest_record["product_name"]
        current_inventory = int(latest_record["inventory_level"])
        reorder_point = int(latest_record["reorder_point"])#point reaches where new order to be placed
        
        # Recent demand dynamics (last 30 orders/records)
        recent_demands = df_product_records["demand"].tail(30)
        avg_demand_monthly = float(recent_demands.mean())
        daily_demand = max(0.5, avg_demand_monthly / 30.0)
        demand_std = float(recent_demands.std()) if len(recent_demands) > 1 else (daily_demand * 0.2)

        # Lead time dynamics
        recent_lead_times = df_product_records["lead_time_days"].tail(30)
        avg_lead_time = max(5, int(np.round(recent_lead_times.mean())))
        lead_time_std = float(recent_lead_times.std()) if len(recent_lead_times) > 1 else 2.0

        # Safety Stock formula: Z * sqrt( (Avg_LT * Demand_Var^2) + (Avg_Demand^2 * LT_Var^2) )
        safety_stock = int(np.ceil(
            self.z_score * np.sqrt(
                (avg_lead_time * (demand_std / 30.0)**2) + ((daily_demand**2) * (lead_time_std**2))
            )
        ))
        safety_stock = max(20, safety_stock)

        # Days of Supply (Inventory Coverage)
        days_of_supply = round(current_inventory / daily_demand, 1)

        # Projected Stockout Date
        # If we keep selling at the current daily demand and 
        # don't receive new stock, when will our inventory reach zero?
        current_date = datetime.now()
        days_to_stockout = max(0, int(np.floor(current_inventory / daily_demand)))
        projected_stockout_date = (current_date + timedelta(days=days_to_stockout)).strftime("%Y-%m-%d")

        # Deterministic Reorder Quantity
        recommended_reorder_qty = self.calculate_reorder_quantity(
            current_inventory=current_inventory,
            daily_demand=daily_demand,
            lead_time_days=avg_lead_time,
            safety_stock=safety_stock
        )

        # Risk Classification
        if days_of_supply <= 5.0 or current_inventory == 0:
            risk_level = "CRITICAL"
            stockout_probability = 0.95
        elif days_of_supply <= avg_lead_time or current_inventory < reorder_point:
            risk_level = "HIGH"
            stockout_probability = 0.75
        elif days_of_supply <= (avg_lead_time + 7):
            risk_level = "MEDIUM"
            stockout_probability = 0.35
        else:
            risk_level = "LOW"
            stockout_probability = 0.08

        return {
            "product_id": product_id,
            "product_name": product_name,
            "current_inventory": current_inventory,
            "daily_demand": round(daily_demand, 2),
            "reorder_point": reorder_point,
            "days_of_supply": days_of_supply,
            "safety_stock": safety_stock,
            "lead_time_days": avg_lead_time,
            "projected_stockout_date": projected_stockout_date,
            "days_until_stockout": days_to_stockout,
            "stockout_probability": stockout_probability,
            "recommended_reorder_quantity": recommended_reorder_qty,
            "risk_level": risk_level,
            "reorder_required": current_inventory <= reorder_point
        }

    def scan_critical_inventory(self, df: pd.DataFrame, limit: int = 15) -> List[Dict[str, Any]]:
        """Scans the latest inventory state across all products and returns high/critical risks."""
        risks = []
        for prod_id, group in df.groupby("product_id"):
            analysis = self.analyze_product_inventory(group)
            if "error" not in analysis and analysis["risk_level"] in ["CRITICAL", "HIGH", "MEDIUM"]:
                risks.append(analysis)

        # Sort with CRITICAL and lowest days of supply first
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        risks.sort(key=lambda x: (severity_order.get(x["risk_level"], 4), x["days_of_supply"]))
        return risks[:limit]
