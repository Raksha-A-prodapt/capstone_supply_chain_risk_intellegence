"""
Training script for all ML Models
Prepares data, trains delivery risk classifier, anomaly detector, and demand forecaster,
and logs evaluation metrics.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.preprocessing import DataPreprocessor
from ml.delivery_risk import DeliveryRiskModel
from ml.anomaly_detection import SupplyChainAnomalyDetector
from ml.forecasting import DemandForecaster

def train_all_models():
    print("=" * 60)
    print("STARTING ML TRAINING & EVALUATION PIPELINE")
    print("=" * 60)

    # 1. Preprocess Data
    preprocessor = DataPreprocessor()
    df, quality_report = preprocessor.prepare_data()
    print(f"Data ready: {len(df):,} records.")

    # 2. Train Delivery Risk Model
    delivery_model = DeliveryRiskModel()
    delivery_metrics = delivery_model.train_and_evaluate(df)

    # 3. Train Anomaly Detection Model
    anomaly_detector = SupplyChainAnomalyDetector()
    anomaly_metrics = anomaly_detector.fit_and_evaluate(df)

    # 4. Train Demand Forecasting Model (with MAE, RMSE, MAPE)
    forecaster = DemandForecaster()
    forecast_metrics = forecaster.train_and_evaluate(df)

    print("\n" + "=" * 60)
    print("ALL MODELS TRAINED AND SAVED SUCCESSFULLY!")
    print("=" * 60)
    print("Delivery Model Metrics:", delivery_metrics)
    print("Anomaly Detection Metrics:", anomaly_metrics)
    print("Forecasting Metrics:", forecast_metrics)

    return {
        "delivery": delivery_metrics,
        "anomaly": anomaly_metrics,
        "forecasting": forecast_metrics
    }

if __name__ == "__main__":
    train_all_models()
