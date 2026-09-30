"""Unit tests for ML analytics models, anomaly detection, forecasting, and risk scoring."""

import pytest
import numpy as np
from agents.context import SupplyChainContext

@pytest.fixture(scope="module")
def ctx():
    return SupplyChainContext.get_instance()

def test_delivery_risk_model(ctx):
    model = ctx.delivery_model
    assert model.pipeline is not None
    assert model.metrics["roc_auc"] > 0.65
    assert model.metrics["f1_score"] > 0.40
    assert "confusion_matrix" in model.metrics

    # Test sample inference
    sample = ctx.df.tail(5)
    probs = model.predict_risk(sample)
    assert len(probs) == 5
    assert np.all((probs >= 0.0) & (probs <= 1.0))

def test_anomaly_detection_model(ctx):
    detector = ctx.anomaly_detector
    assert detector.iso_forest is not None
    assert detector.metrics["f1_score"] > 0.40
    assert detector.metrics["false_positive_rate"] < 0.05

    anomalies = ctx.anomalies
    assert len(anomalies) > 0
    assert "severity" in anomalies[0]
    assert "z_score" in anomalies[0]

def test_demand_forecasting_model(ctx):
    forecaster = ctx.demand_forecaster
    assert forecaster.model is not None
    assert "mape" in forecaster.metrics
    assert "mae" in forecaster.metrics
    assert "rmse" in forecaster.metrics
    assert forecaster.metrics["mape"] < 40.0 # Strict MAPE check

    # Forecast product
    fc = forecaster.forecast_product("PROD-001", horizon_days=30)
    assert len(fc["forecast_series"]) == 30
    assert fc["total_projected_demand"] > 0

def test_inventory_risk_deterministic_formula(ctx):
    analyzer = ctx.inventory_analyzer
    roq = analyzer.calculate_reorder_quantity(
        current_inventory=100,
        daily_demand=10.0,
        lead_time_days=14,
        safety_stock=50
    )
    # Expected demand during lead time = 10 * 14 = 140
    # Target = 140 + 50 = 190
    # ROQ = 190 - 100 = 90
    assert roq == 90

def test_supplier_risk_scoring(ctx):
    scorer = ctx.supplier_scorer
    profiles = ctx.supplier_profiles
    assert len(profiles) == 25
    assert profiles[0]["supplier_risk_score"] >= profiles[-1]["supplier_risk_score"]
    
    # Highest risk should be SUP-023 or SUP-021
    top_ids = [p["supplier_id"] for p in profiles[:3]]
    assert "SUP-023" in top_ids or "SUP-021" in top_ids
