"""Unit tests for Data Preprocessing and Feature Engineering."""

import pytest
import pandas as pd
from data.preprocessing import DataPreprocessor

def test_data_quality_and_features():
    preprocessor = DataPreprocessor()
    df, report = preprocessor.prepare_data()

    assert df is not None
    assert len(df) >= 100_000
    assert report["data_quality_status"] == "PASSED"
    assert report["duplicate_orders"] == 0
    assert report["invalid_dates"] == 0

    # Verify analytical feature creation
    required_features = [
        "fulfillment_rate", "expected_lead_time", "lead_time_variance",
        "days_of_supply", "is_below_reorder_point", "sup_late_rate",
        "carrier_late_rate", "order_value"
    ]
    for feat in required_features:
        assert feat in df.columns, f"Missing feature: {feat}"
