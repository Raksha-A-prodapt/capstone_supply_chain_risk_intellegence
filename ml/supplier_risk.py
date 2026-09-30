"""
Supplier Risk Scoring Engine
Calculates transparent, deterministic risk scores and tiers for all suppliers
combining historical delivery performance, variability, anomalies, and ML predictions.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from config.settings import settings

class SupplierRiskScorer:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {
            "late_rate": settings.WEIGHT_LATE_RATE,
            "avg_delay": settings.WEIGHT_AVG_DELAY,
            "lead_time_var": settings.WEIGHT_LEAD_TIME_VAR,
            "anomaly_freq": settings.WEIGHT_ANOMALY_FREQ,
            "ml_prob": settings.WEIGHT_ML_PROB
        }

    def compute_risk_score(
        self,
        late_rate: float,
        avg_delay_days: float,
        lead_time_std: float,
        anomaly_rate: float,
        ml_delivery_risk_prob: float
    ) -> float:
        """
        Deterministic, transparent weighted scoring formula:
        Score = w1*(late_rate) + w2*norm(avg_delay) + w3*norm(lead_time_std) + w4*norm(anomaly_rate) + w5*(ml_prob)
        """
        norm_delay = min(1.0, avg_delay_days / 12.0)
        norm_std = min(1.0, lead_time_std / 8.0)
        norm_anomaly = min(1.0, anomaly_rate / 0.10)

        raw_score = (
            self.weights["late_rate"] * late_rate +
            self.weights["avg_delay"] * norm_delay +
            self.weights["lead_time_var"] * norm_std +
            self.weights["anomaly_freq"] * norm_anomaly +
            self.weights["ml_prob"] * ml_delivery_risk_prob
        )
        return float(np.clip(raw_score, 0.0, 1.0))

    def classify_risk_tier(self, score: float) -> str:
        if score >= settings.RISK_LEVEL_HIGH:
            return "CRITICAL"
        elif score >= settings.RISK_LEVEL_MEDIUM:
            return "HIGH"
        elif score >= settings.RISK_LEVEL_LOW:
            return "MEDIUM"
        else:
            return "LOW"

    def score_all_suppliers(
        self,
        df: pd.DataFrame,
        ml_probs: Optional[np.ndarray] = None,
        anomaly_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Computes comprehensive metrics and risk levels for every supplier."""
        if ml_probs is not None and "ml_pred_prob" not in df.columns:
            df = df.copy()
            df["ml_pred_prob"] = ml_probs
        elif "ml_pred_prob" not in df.columns:
            # Baseline proxy if ML probs not passed
            df["ml_pred_prob"] = df["sup_late_rate"]

        # Anomaly counts per supplier
        anomaly_counts = {}
        if anomaly_list:
            for anom in anomaly_list:
                sup = anom.get("supplier_id")
                if sup:
                    anomaly_counts[sup] = anomaly_counts.get(sup, 0) + 1

        supplier_results = []
        for sup_id, group in df.groupby("supplier_id"):
            sup_name = group["supplier_name"].iloc[0]
            total_orders = len(group)
            late_orders = int(group["late_order"].sum())
            late_rate = float(late_orders / total_orders)
            avg_delay = float(group["delay_days"].mean())
            lead_time_mean = float(group["lead_time_days"].mean())
            lead_time_std = float(group["lead_time_days"].std()) if len(group) > 1 else 1.0
            
            anom_count = anomaly_counts.get(sup_id, 0)
            anomaly_rate = float(anom_count / total_orders)
            avg_ml_prob = float(group["ml_pred_prob"].mean())

            risk_score = self.compute_risk_score(
                late_rate=late_rate,
                avg_delay_days=avg_delay,
                lead_time_std=lead_time_std,
                anomaly_rate=anomaly_rate,
                ml_delivery_risk_prob=avg_ml_prob
            )
            risk_level = self.classify_risk_tier(risk_score)

            # Products supplied by this supplier
            supplied_prods = list(group["product_id"].unique())

            supplier_results.append({
                "supplier_id": sup_id,
                "supplier_name": sup_name,
                "supplier_risk_score": round(risk_score, 3),
                "supplier_risk_level": risk_level,
                "total_orders": total_orders,
                "late_orders": late_orders,
                "late_delivery_rate": round(late_rate, 4),
                "avg_delay_days": round(avg_delay, 1),
                "lead_time_mean_days": round(lead_time_mean, 1),
                "lead_time_std_days": round(lead_time_std, 1),
                "anomaly_count": anom_count,
                "ml_delivery_risk_prob": round(avg_ml_prob, 3),
                "supplied_products_count": len(supplied_prods),
                "products_supplied": supplied_prods[:5],
                "scoring_weights_used": self.weights
            })

        # Sort with highest risk score first
        supplier_results.sort(key=lambda x: x["supplier_risk_score"], reverse=True)
        return supplier_results

    def get_supplier_profile(self, supplier_id: str, supplier_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        for s in supplier_list:
            if s["supplier_id"] == supplier_id or s["supplier_name"].lower() == supplier_id.lower():
                return s
        return None
