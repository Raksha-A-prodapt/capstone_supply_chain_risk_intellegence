"""
Anomaly Detection Model
Detects unusual lead times, unexpected delay surges, and order volume anomalies
using Isolation Forest and statistical Z-score profiling.
Calculates Precision, Recall, F1, and False-Positive Rate.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score
from config.settings import settings
# “anomaly” means an order whose delivery behavior looks unusually different from the normal pattern.


class SupplyChainAnomalyDetector:
    def __init__(self, model_path: Path = None):
        self.model_path = model_path or (settings.MODELS_DIR / "anomaly_detector.joblib")
        self.iso_forest: IsolationForest = None
        self.scaler: StandardScaler = None
        self.metrics: Dict[str, Any] = {}
        self.feature_cols = ["lead_time_days", "delay_days", "units_ordered", "lead_time_variance"]

    def fit_and_evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Trains Isolation Forest and calculates detection performance."""
        print("Training Anomaly Detection Model...")
        X = df[self.feature_cols].copy()
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        contamination = settings.ANOMALY_CONTAMINATION
        self.iso_forest = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42,
            n_jobs=-1
        )
        # 1 for normal, -1 for anomaly
        preds = self.iso_forest.fit_predict(X_scaled)
        is_anomaly_iso = (preds == -1).astype(int)

        # Statistical Z-score anomaly ground truth / benchmark:
        # A lead time is anomalous if it exceeds the supplier's mean by > 2.5 std
        z_scores = (df["lead_time_days"] - df["sup_lead_time_mean"]) / (df["sup_lead_time_std"] + 1e-5)
        is_anomaly_stat = ((z_scores > settings.LEAD_TIME_ANOMALY_Z) | (df["delay_days"] >= 18)).astype(int)

        # Compute evaluation metrics against statistical/injected anomalies
        prec = float(precision_score(is_anomaly_stat, is_anomaly_iso, zero_division=0))
        rec = float(recall_score(is_anomaly_stat, is_anomaly_iso, zero_division=0))
        f1 = float(f1_score(is_anomaly_stat, is_anomaly_iso, zero_division=0))
        
        # False Positive Rate: FP / (FP + TN)
        fp = int(np.sum((is_anomaly_iso == 1) & (is_anomaly_stat == 0)))
        tn = int(np.sum((is_anomaly_iso == 0) & (is_anomaly_stat == 0)))
        fpr = float(fp / (fp + tn + 1e-5))

        self.metrics = {
            "model_type": "IsolationForest",
            "contamination": contamination,
            "total_evaluated": len(df),
            "anomalies_detected": int(np.sum(is_anomaly_iso)),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "false_positive_rate": round(fpr, 4)
        }

        # Save model
        os.makedirs(self.model_path.parent, exist_ok=True)
        joblib.dump({"model": self.iso_forest, "scaler": self.scaler, "metrics": self.metrics}, self.model_path)
        print(f"Anomaly Detector saved to {self.model_path}!")
        print(f"Metrics: F1={f1:.4f}, Precision={prec:.4f}, Recall={rec:.4f}, FPR={fpr:.4f}")

        return self.metrics

    def load(self) -> bool:
        if os.path.exists(self.model_path):
            artifact = joblib.load(self.model_path)
            self.iso_forest = artifact["model"]
            self.scaler = artifact["scaler"]
            self.metrics = artifact["metrics"]
            return True
        return False

    def detect_anomalies(self, df: pd.DataFrame, max_results: int = 50) -> List[Dict[str, Any]]:
        """Identifies anomalies and formats them with explanatory details."""
        if self.iso_forest is None and not self.load():
            raise RuntimeError("Anomaly detector not initialized.")

        X = df[self.feature_cols].copy()
        X_scaled = self.scaler.transform(X)
        scores = self.iso_forest.decision_function(X_scaled)
        preds = self.iso_forest.predict(X_scaled)

        anomaly_indices = np.where(preds == -1)[0]
        # Sort by anomaly score ascending (most anomalous first)
        sorted_indices = anomaly_indices[np.argsort(scores[anomaly_indices])][:max_results]

        anomalies = []
        for idx in sorted_indices:
            row = df.iloc[idx]
            z = float((row["lead_time_days"] - row["sup_lead_time_mean"]) / (row["sup_lead_time_std"] + 1e-5))
            
            # Severity classification
            if z > 3.5 or row["delay_days"] >= 20:
                severity = "CRITICAL"
            elif z > 2.5 or row["delay_days"] >= 10:
                severity = "HIGH"
            else:
                severity = "MODERATE"

            anomalies.append({
                "order_id": row["order_id"],
                "supplier_id": row["supplier_id"],
                "supplier_name": row["supplier_name"],
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "order_date": str(row["order_date"].strftime("%Y-%m-%d") if hasattr(row["order_date"], "strftime") else row["order_date"]),
                "lead_time_days": int(row["lead_time_days"]),
                "expected_lead_time": int(row.get("expected_lead_time", row["lead_time_days"] - row["delay_days"])),
                "delay_days": int(row["delay_days"]),
                "units_ordered": int(row["units_ordered"]),
                "supplier_avg_lead_time": round(float(row["sup_lead_time_mean"]), 1),
                "z_score": round(z, 2),
                "anomaly_score": round(float(-scores[idx]), 3),
                "severity": severity,
                "reason": (
                    f"Severe lead time spike ({row['lead_time_days']} days vs baseline {row['sup_lead_time_mean']:.1f}d, z={z:.1f})"
                    if z > 2.0 else f"High delay spike ({row['delay_days']} days delayed)"
                )
            })

        return anomalies
