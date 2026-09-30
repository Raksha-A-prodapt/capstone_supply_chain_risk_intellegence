"""
Global Supply Chain Analytics Context
Loads and caches preprocessed dataset, trained ML models, and vector search engine
for low-latency multi-agent execution.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd
from config.settings import settings
from data.preprocessing import DataPreprocessor
from ml.delivery_risk import DeliveryRiskModel
from ml.anomaly_detection import SupplyChainAnomalyDetector
from ml.forecasting import DemandForecaster
from ml.inventory_risk import InventoryRiskAnalyzer
from ml.supplier_risk import SupplierRiskScorer
from semantic_search.search import SemanticSearchEngine

class SupplyChainContext:
    _instance: Optional["SupplyChainContext"] = None

    def __init__(self):
        print("Initializing SupplyChainContext...")
        self.preprocessor = DataPreprocessor()
        self.df, self.quality_report = self.preprocessor.prepare_data()

        self.delivery_model = DeliveryRiskModel()
        self.delivery_model.load()

        self.anomaly_detector = SupplyChainAnomalyDetector()
        self.anomaly_detector.load()

        self.demand_forecaster = DemandForecaster()
        self.demand_forecaster.load()

        self.inventory_analyzer = InventoryRiskAnalyzer()
        self.supplier_scorer = SupplierRiskScorer()

        self.semantic_search = SemanticSearchEngine()
        self.semantic_search.build_index()

        # Precompute anomalies and supplier scores for instant lookup
        self.anomalies = self.anomaly_detector.detect_anomalies(self.df, max_results=100)
        self.supplier_profiles = self.supplier_scorer.score_all_suppliers(
            self.df,
            anomaly_list=self.anomalies
        )
        self.critical_inventories = self.inventory_analyzer.scan_critical_inventory(self.df, limit=25)
        print("SupplyChainContext initialization complete!")

    @classmethod
    def get_instance(cls) -> "SupplyChainContext":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
