"""
FastAPI Route Definitions
Provides clean, typed endpoints for supply-chain risk queries, supplier profiling,
inventory monitoring, anomaly tracking, forecasting, evaluation, and what-if simulation.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from config.settings import settings
from agents.context import SupplyChainContext
from assistant import SupplyChainAssistant
from simulator.what_if_simulator import WhatIfSimulator

router = APIRouter(prefix="/api")

# Models
class QueryRequest(BaseModel):
    query: str
    force_fallback: bool = False

class SimulateRequest(BaseModel):
    supplier_id: str
    delay_days: int = 7

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

# Lazy load assistant instance
_assistant: Optional[SupplyChainAssistant] = None
def get_assistant() -> SupplyChainAssistant:
    global _assistant
    if _assistant is None:
        _assistant = SupplyChainAssistant()
    return _assistant

@router.post("/query")
def process_query(payload: QueryRequest) -> Dict[str, Any]:
    """Processes natural language supply chain questions with multi-agent intelligence."""
    assistant = get_assistant()
    return assistant.process_query(payload.query, force_fallback=payload.force_fallback)

@router.get("/suppliers")
def get_suppliers() -> List[Dict[str, Any]]:
    """Returns scored suppliers ranked by overall risk score."""
    ctx = SupplyChainContext.get_instance()
    return ctx.supplier_profiles

@router.get("/suppliers/{supplier_id}")
def get_supplier_detail(supplier_id: str) -> Dict[str, Any]:
    """Returns detailed performance profile for a specific supplier."""
    ctx = SupplyChainContext.get_instance()
    sup = ctx.supplier_scorer.get_supplier_profile(supplier_id, ctx.supplier_profiles)
    if not sup:
        raise HTTPException(status_code=404, detail=f"Supplier {supplier_id} not found")
    
    # Recent orders sample
    recent_orders = ctx.df[ctx.df["supplier_id"] == sup["supplier_id"]].tail(20).to_dict(orient="records")
    for o in recent_orders:
        for k, v in o.items():
            if hasattr(v, "strftime"):
                o[k] = v.strftime("%Y-%m-%d")

    return {
        "profile": sup,
        "recent_orders": recent_orders
    }

@router.get("/orders")
def get_orders(
    limit: int = Query(50, ge=1, le=500),
    supplier_id: Optional[str] = None,
    late_only: bool = False
) -> List[Dict[str, Any]]:
    """Returns historical order records with optional supplier filtering."""
    ctx = SupplyChainContext.get_instance()
    df = ctx.df
    if supplier_id:
        df = df[df["supplier_id"] == supplier_id]
    if late_only:
        df = df[df["late_order"] == 1]

    records = df.tail(limit).to_dict(orient="records")
    for r in records:
        for k, v in r.items():
            if hasattr(v, "strftime"):
                r[k] = v.strftime("%Y-%m-%d")
    return records

@router.get("/inventory")
def get_inventory(limit: int = Query(25, ge=1, le=100)) -> List[Dict[str, Any]]:
    """Returns inventory risk evaluations and deterministic reorder quantities."""
    ctx = SupplyChainContext.get_instance()
    return ctx.critical_inventories[:limit]

@router.get("/anomalies")
def get_anomalies(limit: int = Query(50, ge=1, le=200)) -> List[Dict[str, Any]]:
    """Returns operational lead-time and volume anomalies detected by Isolation Forest."""
    ctx = SupplyChainContext.get_instance()
    return ctx.anomalies[:limit]

@router.get("/forecasts")
def get_forecasts(
    product_id: str = Query("PROD-001"),
    horizon: int = Query(30, ge=7, le=90)
) -> Dict[str, Any]:
    """Generates demand forecast for a product and returns MAE, RMSE, and MAPE."""
    ctx = SupplyChainContext.get_instance()
    return ctx.demand_forecaster.forecast_product(product_id=product_id, horizon_days=horizon)

@router.get("/evaluation")
def get_evaluation() -> Dict[str, Any]:
    """Returns the latest system-wide evaluation report."""
    report_file = settings.REPORTS_DIR / "evaluation_report.json"
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Evaluation report has not been generated yet.")

@router.post("/search")
def semantic_search(payload: SearchRequest) -> List[Dict[str, Any]]:
    """Performs cosine vector search across supply-chain knowledge base."""
    ctx = SupplyChainContext.get_instance()
    return ctx.semantic_search.search(payload.query, top_k=payload.top_k)

@router.post("/simulate")
def run_what_if_simulation(payload: SimulateRequest) -> Dict[str, Any]:
    """Performs deterministic What-If simulation of a supplier disruption."""
    ctx = SupplyChainContext.get_instance()
    sim = WhatIfSimulator(ctx)
    return sim.simulate_supplier_delay(supplier_id=payload.supplier_id, added_delay_days=payload.delay_days)

@router.get("/health")
def health_check() -> Dict[str, Any]:
    """System health status and telemetry."""
    ctx = SupplyChainContext.get_instance()
    return {
        "status": "healthy",
        "dataset_records": len(ctx.df),
        "gateway_url": settings.GATEWAY_URL,
        "models_loaded": {
            "delivery_classifier": ctx.delivery_model.pipeline is not None,
            "anomaly_detector": ctx.anomaly_detector.iso_forest is not None,
            "demand_forecaster": ctx.demand_forecaster.model is not None
        },
        "knowledge_chunks_indexed": len(ctx.semantic_search.chunks)
    }
