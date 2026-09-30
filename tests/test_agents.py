"""Unit tests for the Six Specialized Agents."""

import pytest
from agents.context import SupplyChainContext
from agents.supplier_risk_agent import SupplierRiskAgent
from agents.delivery_risk_agent import DeliveryRiskAgent
from agents.inventory_risk_agent import InventoryRiskAgent
from agents.demand_agent import DemandAgent
from agents.insight_agent import InsightAgent
from agents.recommendation_agent import RecommendationAgent

@pytest.fixture(scope="module")
def ctx():
    return SupplyChainContext.get_instance()

def test_all_six_specialist_agents(ctx):
    state = {
        "query": "Comprehensive supply chain risk test",
        "target_entities": {"suppliers": ["SUP-023"], "products": ["PROD-001"]},
        "active_agents": [
            "supplier_risk_agent", "delivery_risk_agent",
            "inventory_risk_agent", "demand_agent",
            "insight_agent", "recommendation_agent"
        ],
        "agent_trace": [],
        "handoffs": [],
        "agent_outputs": {}
    }

    # 1. Supplier Risk Agent
    sup_agent = SupplierRiskAgent(ctx)
    state = sup_agent.run(state)
    assert "supplier_risk_agent" in state["agent_outputs"]
    assert state["agent_outputs"]["supplier_risk_agent"]["status"] == "SUCCESS"

    # 2. Delivery Risk Agent
    del_agent = DeliveryRiskAgent(ctx)
    state = del_agent.run(state)
    assert "delivery_risk_agent" in state["agent_outputs"]
    assert state["agent_outputs"]["delivery_risk_agent"]["status"] == "SUCCESS"

    # 3. Inventory Risk Agent
    inv_agent = InventoryRiskAgent(ctx)
    state = inv_agent.run(state)
    assert "inventory_risk_agent" in state["agent_outputs"]
    assert state["agent_outputs"]["inventory_risk_agent"]["status"] == "SUCCESS"

    # 4. Demand Agent
    dmd_agent = DemandAgent(ctx)
    state = dmd_agent.run(state)
    assert "demand_agent" in state["agent_outputs"]
    assert state["agent_outputs"]["demand_agent"]["status"] == "SUCCESS"

    # 5. Supply Chain Insight Agent
    ins_agent = InsightAgent()
    state = ins_agent.run(state)
    assert "insight_agent" in state["agent_outputs"]
    assert state["agent_outputs"]["insight_agent"]["overall_supply_chain_risk"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    # 6. Risk Recommendation Agent
    rec_agent = RecommendationAgent()
    state = rec_agent.run(state)
    assert "recommendation_agent" in state["agent_outputs"]
    assert len(state["agent_outputs"]["recommendation_agent"]["recommendations"]) > 0
