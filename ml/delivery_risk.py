"""
Delivery Risk Machine Learning Model
Trains and evaluates a supervised classifier for predicting late delivery risk (late_order).
Calculates Precision, Recall, F1, ROC-AUC, PR-AUC, and Confusion Matrix.
"""

import os
from pathlib import Path
from typing import Dict, Any, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)
from config.settings import settings
from data.preprocessing import DataPreprocessor

class DeliveryRiskModel:
    def __init__(self, model_path: Path = None):
        self.model_path = model_path or (settings.MODELS_DIR / "delivery_risk_model.joblib")
        self.pipeline: Pipeline = None
        self.metrics: Dict[str, Any] = {}
        self.feature_cols = [
            "distance_km", "weight", "units_ordered", "expected_lead_time",
            "material_handling", "customs_procedure", "carrier_3pl",
            "sup_late_rate", "sup_avg_delay", "month", "day_of_week"
        ]
        self.categorical_cols = ["material_handling", "customs_procedure", "carrier_3pl"]
        self.numeric_cols = [
            "distance_km", "weight", "units_ordered", "expected_lead_time",
            "sup_late_rate", "sup_avg_delay", "month", "day_of_week"
        ]

    def build_pipeline(self) -> Pipeline:
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), self.numeric_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), self.categorical_cols)
            ]
        )
        classifier = HistGradientBoostingClassifier(
            max_iter=120,
            learning_rate=0.08,
            max_depth=6,
            random_state=42
        )
        return Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", classifier)
        ])

    def train_and_evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Trains the delivery risk model and computes evaluation metrics."""
        print("Training Delivery Risk Model...")
        X = df[self.feature_cols]
        y = df["late_order"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )

        self.pipeline = self.build_pipeline()
        self.pipeline.fit(X_train, y_train)

        # Predictions & Probabilities
        y_pred = self.pipeline.predict(X_test)
        y_prob = self.pipeline.predict_proba(X_test)[:, 1]

        # Calculate Evaluation Metrics
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        roc_auc = float(roc_auc_score(y_test, y_prob))
        pr_auc = float(average_precision_score(y_test, y_prob))
        cm = confusion_matrix(y_test, y_pred).tolist()

        self.metrics = {
            "model_type": "HistGradientBoostingClassifier",
            "test_samples": len(y_test),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "confusion_matrix": cm,
            "class_distribution": {
                "on_time": int(np.sum(y_test == 0)),
                "late": int(np.sum(y_test == 1))
            }
        }

        # Save model artifact
        os.makedirs(self.model_path.parent, exist_ok=True)
        joblib.dump({"pipeline": self.pipeline, "metrics": self.metrics}, self.model_path)
        print(f"Delivery Risk Model saved to {self.model_path}!")
        print(f"Metrics: F1={f1:.4f}, ROC-AUC={roc_auc:.4f}, PR-AUC={pr_auc:.4f}, Precision={prec:.4f}, Recall={rec:.4f}")

        return self.metrics

    def load(self) -> bool:
        if os.path.exists(self.model_path):
            artifact = joblib.load(self.model_path)
            self.pipeline = artifact["pipeline"]
            self.metrics = artifact["metrics"]
            return True
        return False

    def predict_risk(self, df_sample: pd.DataFrame) -> np.ndarray:
        """Returns delivery risk probability for given records."""
        if self.pipeline is None and not self.load():
            raise RuntimeError("Delivery risk model has not been trained or loaded.")
        X = df_sample[self.feature_cols]
        return self.pipeline.predict_proba(X)[:, 1]

if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    df, _ = preprocessor.prepare_data()
    model = DeliveryRiskModel()
    metrics = model.train_and_evaluate(df)
    print("Delivery Risk Evaluation:", metrics)
