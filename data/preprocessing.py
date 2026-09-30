"""
Data Preprocessing & Feature Engineering Pipeline
Handles data cleaning, quality validation, analytical feature creation,
and prepares datasets for ML modeling and multi-agent analytics.
"""

import os
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from config.settings import settings

class DataPreprocessor:
    def __init__(self, data_path: str = None):
        self.data_path = str(data_path or settings.DATA_PATH)
        self.quality_report: Dict[str, Any] = {}

    def load_and_validate(self) -> pd.DataFrame:
        """Loads data and runs quality checks."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")

        df = pd.read_csv(self.data_path)
        
        # Quality validation checks
        total_rows = len(df)
        null_counts = df.isnull().sum().to_dict()
        duplicate_orders = int(df["order_id"].duplicated().sum())

        # Date validations
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["expected_delivery_date"] = pd.to_datetime(df["expected_delivery_date"])
        df["actual_delivery_date"] = pd.to_datetime(df["actual_delivery_date"])

        invalid_dates = int((df["expected_delivery_date"] < df["order_date"]).sum())
        invalid_quantities = int((df["units_ordered"] <= 0).sum())
        invalid_inventory = int((df["inventory_level"] < 0).sum())

        self.quality_report = {
            "total_records": total_rows,
            "columns": list(df.columns),
            "missing_values": {k: int(v) for k, v in null_counts.items() if v > 0},
            "duplicate_orders": duplicate_orders,
            "invalid_dates": invalid_dates,
            "invalid_quantities": invalid_quantities,
            "invalid_inventory": invalid_inventory,
            "data_quality_status": "PASSED" if (duplicate_orders == 0 and invalid_dates == 0) else "WARNINGS_FOUND"
        }

        return df

    def feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Creates analytical features for delivery ML, inventory risk,
        anomaly detection, and supplier evaluation.
        """
        df = df.copy()

        # 1. Fulfillment metrics
        df["fulfillment_rate"] = np.round(df["units_received"] / (df["units_ordered"] + 1e-5), 4)
        df["order_shortage"] = np.maximum(0, df["units_ordered"] - df["units_received"])

        # 2. Lead time & delay indicators
        df["expected_lead_time"] = (df["expected_delivery_date"] - df["order_date"]).dt.days
        df["lead_time_variance"] = np.abs(df["lead_time_days"] - df["expected_lead_time"])
        df["delay_ratio"] = np.round(df["delay_days"] / (df["lead_time_days"] + 1e-5), 4)

        # 3. Inventory & Demand metrics
        # Daily demand rate (approximate 30-day base)
        df["daily_demand"] = np.maximum(0.5, df["demand"] / 30.0)
        # Days of Supply (Inventory Coverage)
        df["days_of_supply"] = np.round(df["inventory_level"] / df["daily_demand"], 1)
        # Reorder gap
        df["inventory_to_reorder_ratio"] = np.round(df["inventory_level"] / (df["reorder_point"] + 1e-5), 3)
        # Stock-out risk flag (deterministic)
        df["is_below_reorder_point"] = (df["inventory_level"] < df["reorder_point"]).astype(int)
        df["stockout_critical"] = (df["inventory_level"] <= (df["daily_demand"] * 3.0)).astype(int)

        # 4. Temporal Features
        df["month"] = df["order_date"].dt.month
        df["quarter"] = df["order_date"].dt.quarter
        df["day_of_week"] = df["order_date"].dt.dayofweek
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

        # 5. Financial metrics
        df["order_value"] = np.round(df["units_ordered"] * df["unit_cost"], 2)

        # 6. Supplier Aggregated Historical Features (pre-computed baselines)
        sup_stats = df.groupby("supplier_id").agg(
            sup_total_orders=("order_id", "count"),
            sup_late_rate=("late_order", "mean"),
            sup_avg_delay=("delay_days", "mean"),
            sup_lead_time_mean=("lead_time_days", "mean"),
            sup_lead_time_std=("lead_time_days", "std")
        ).reset_index()

        df = df.merge(sup_stats, on="supplier_id", how="left")

        # 7. Carrier Aggregated Features
        carrier_stats = df.groupby("carrier_3pl").agg(
            carrier_late_rate=("late_order", "mean"),
            carrier_avg_delay=("delay_days", "mean")
        ).reset_index()

        df = df.merge(carrier_stats, on="carrier_3pl", how="left")

        return df

    def get_quality_report(self) -> Dict[str, Any]:
        return self.quality_report

    def prepare_data(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Complete data pipeline execution."""
        df_raw = self.load_and_validate()
        df_featured = self.feature_engineering(df_raw)
        return df_featured, self.quality_report

if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    df, report = preprocessor.prepare_data()
    print("Preprocessing & Feature Engineering Complete!")
    print(f"Dataset shape: {df.shape}")
    print("Quality Report:", report)
    print("\nSample features:")
    print(df[["order_id", "supplier_id", "days_of_supply", "is_below_reorder_point", "sup_late_rate", "carrier_late_rate"]].head())
