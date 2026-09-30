"""
ML Models Evaluation Runner
Gathers and structures evaluation metrics for Delivery Risk, Anomaly Detection,
and Demand Forecasting models.
"""

from typing import Dict, Any
from agents.context import SupplyChainContext

def evaluate_all_models(context: SupplyChainContext = None) -> Dict[str, Any]:
    ctx = context or SupplyChainContext.get_instance()
    
    del_metrics = ctx.delivery_model.metrics
    anom_metrics = ctx.anomaly_detector.metrics
    fc_metrics = ctx.demand_forecaster.metrics

    return {
        "delivery_risk_model": {
            "name": "Delivery Risk Classifier",
            "algorithm": del_metrics.get("model_type", "HistGradientBoostingClassifier"),
            "f1_score": del_metrics.get("f1_score", 0.0),
            "roc_auc": del_metrics.get("roc_auc", 0.0),
            "pr_auc": del_metrics.get("pr_auc", 0.0),
            "precision": del_metrics.get("precision", 0.0),
            "recall": del_metrics.get("recall", 0.0),
            "test_samples": del_metrics.get("test_samples", 0),
            "confusion_matrix": del_metrics.get("confusion_matrix", []),
            "class_distribution": del_metrics.get("class_distribution", {})
        },
        "anomaly_detector": {
            "name": "Supply Chain Anomaly Detector",
            "algorithm": anom_metrics.get("model_type", "IsolationForest"),
            "f1_score": anom_metrics.get("f1_score", 0.0),
            "precision": anom_metrics.get("precision", 0.0),
            "recall": anom_metrics.get("recall", 0.0),
            "false_positive_rate": anom_metrics.get("false_positive_rate", 0.0),
            "total_records_analyzed": anom_metrics.get("total_evaluated", 0),
            "anomalies_flagged": anom_metrics.get("anomalies_detected", 0)
        },
        "demand_forecaster": {
            "name": "Demand Time Series Forecaster",
            "algorithm": fc_metrics.get("model_type", "HistGradientBoostingRegressor"),
            "mae": fc_metrics.get("mae", 0.0),
            "rmse": fc_metrics.get("rmse", 0.0),
            "mape": fc_metrics.get("mape", 0.0),
            "train_samples": fc_metrics.get("train_samples", 0),
            "test_samples": fc_metrics.get("test_samples", 0),
            "mean_test_demand": fc_metrics.get("mean_test_demand", 0.0)
        }
    }
