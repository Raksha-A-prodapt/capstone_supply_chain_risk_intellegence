"""
Evaluation Benchmark Dataset
Contains test queries with ground-truth expected agents, target entities,
risk types, and expected factual metrics.
"""

from typing import List, Dict, Any

EVALUATION_DATASET: List[Dict[str, Any]] = [
    {
        "id": "Q01",
        "query": "Which suppliers have a high risk of delivery delays?",
        "expected_primary_agent": "supplier_risk_agent",
        "expected_agents": ["supplier_risk_agent", "delivery_risk_agent", "insight_agent", "recommendation_agent"],
        "expected_entities": ["SUP-023", "SUP-021"],
        "expected_risk_level": "CRITICAL",
        "category": "SUPPLIER_RISK"
    },
    {
        "id": "Q02",
        "query": "Why is supplier SUP-023 risky and what is their late delivery rate?",
        "expected_primary_agent": "supplier_risk_agent",
        "expected_agents": ["supplier_risk_agent", "delivery_risk_agent", "insight_agent", "recommendation_agent"],
        "expected_entities": ["SUP-023"],
        "expected_risk_level": "HIGH",
        "category": "SUPPLIER_INVESTIGATION"
    },
    {
        "id": "Q03",
        "query": "Which products are most affected by supplier disruptions and at risk of stock-out?",
        "expected_primary_agent": "inventory_risk_agent",
        "expected_agents": ["inventory_risk_agent", "supplier_risk_agent", "delivery_risk_agent", "insight_agent", "recommendation_agent"],
        "expected_entities": [],
        "expected_risk_level": "CRITICAL",
        "category": "INVENTORY_STOCKOUT"
    },
    {
        "id": "Q04",
        "query": "Identify unusual changes in supplier lead times and delivery anomalies.",
        "expected_primary_agent": "delivery_risk_agent",
        "expected_agents": ["delivery_risk_agent", "supplier_risk_agent", "insight_agent", "recommendation_agent"],
        "expected_entities": [],
        "expected_risk_level": "HIGH",
        "category": "ANOMALY_DETECTION"
    },
    {
        "id": "Q05",
        "query": "What is the demand forecast for product PROD-001?",
        "expected_primary_agent": "demand_agent",
        "expected_agents": ["demand_agent", "inventory_risk_agent", "insight_agent", "recommendation_agent"],
        "expected_entities": ["PROD-001"],
        "expected_risk_level": "LOW",
        "category": "DEMAND_FORECAST"
    },
    {
        "id": "Q06",
        "query": "How could a delay from supplier SUP-001 affect inventory availability?",
        "expected_primary_agent": "supplier_risk_agent",
        "expected_agents": ["supplier_risk_agent", "delivery_risk_agent", "insight_agent", "recommendation_agent"],
        "expected_entities": ["SUP-001"],
        "expected_risk_level": "LOW",
        "category": "SUPPLIER_IMPACT"
    },
    {
        "id": "Q07",
        "query": "What are the major supply chain risks and what evidence supports them?",
        "expected_primary_agent": "insight_agent",
        "expected_agents": ["supplier_risk_agent", "delivery_risk_agent", "inventory_risk_agent", "demand_agent", "insight_agent", "recommendation_agent"],
        "expected_entities": [],
        "expected_risk_level": "CRITICAL",
        "category": "CROSS_DOMAIN_RISK"
    },
    {
        "id": "Q08",
        "query": "What happens if supplier SUP-023 is delayed by 7 days?",
        "expected_primary_agent": "supplier_risk_agent",
        "expected_agents": ["supplier_risk_agent", "delivery_risk_agent", "inventory_risk_agent", "insight_agent", "recommendation_agent"],
        "expected_entities": ["SUP-023"],
        "expected_risk_level": "CRITICAL",
        "category": "WHAT_IF_SIMULATION"
    },
    {
        "id": "Q09",
        "query": "Which carriers and 3PL routes have the highest delivery delays?",
        "expected_primary_agent": "delivery_risk_agent",
        "expected_agents": ["delivery_risk_agent", "supplier_risk_agent", "insight_agent", "recommendation_agent"],
        "expected_entities": [],
        "expected_risk_level": "HIGH",
        "category": "LOGISTICS_RISK"
    },
    {
        "id": "Q10",
        "query": "Which suppliers should be investigated based on recent performance?",
        "expected_primary_agent": "supplier_risk_agent",
        "expected_agents": ["supplier_risk_agent", "delivery_risk_agent", "insight_agent", "recommendation_agent"],
        "expected_entities": ["SUP-023", "SUP-021"],
        "expected_risk_level": "CRITICAL",
        "category": "SUPPLIER_AUDIT"
    }
]
