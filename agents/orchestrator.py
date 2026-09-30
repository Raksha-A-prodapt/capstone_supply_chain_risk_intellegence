"""
LangGraph Multi-Agent Orchestrator
Coordinates dynamic routing, executes specialist agents in a state graph,
records explicit A2A handoff payloads, and logs complete execution traces.
"""

import time
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END

from agents.state import OrchestratorState, AgentHandoff
from agents.context import SupplyChainContext
from agents.supplier_risk_agent import SupplierRiskAgent
from agents.delivery_risk_agent import DeliveryRiskAgent
from agents.inventory_risk_agent import InventoryRiskAgent
from agents.demand_agent import DemandAgent
from agents.insight_agent import InsightAgent
from agents.recommendation_agent import RecommendationAgent

class SupplyChainOrchestrator:
    def __init__(self, context: Optional[SupplyChainContext] = None):
        self.context = context or SupplyChainContext.get_instance()
        self.supplier_agent = SupplierRiskAgent(self.context)
        self.delivery_agent = DeliveryRiskAgent(self.context)
        self.inventory_agent = InventoryRiskAgent(self.context)
        self.demand_agent = DemandAgent(self.context)
        self.insight_agent = InsightAgent()
        self.recommendation_agent = RecommendationAgent()

        self.graph = self._build_graph()

    def classify_and_extract(self, query: str) -> Dict[str, Any]:
        """Classifies intent and extracts entities deterministically."""
        q = query.lower()

        # Extract entities
        suppliers = re.findall(r"sup-\d{3}", q, re.IGNORECASE)
        products = re.findall(r"prod-\d{3}", q, re.IGNORECASE)
        suppliers = [s.upper() for s in suppliers]
        products = [p.upper() for p in products]

        # Named supplier matching
        for p in self.context.supplier_profiles:
            if p["supplier_name"].lower() in q and p["supplier_id"] not in suppliers:
                suppliers.append(p["supplier_id"])

        # Determine routing query type
        if "what happens" in q or "simulate" in q or "delayed by" in q:
            query_type = "SIMULATION"
            active_agents = ["supplier_risk_agent", "delivery_risk_agent", "inventory_risk_agent", "insight_agent", "recommendation_agent"]
        elif "forecast" in q or "demand" in q:
            query_type = "DEMAND_FORECAST"
            active_agents = ["demand_agent", "inventory_risk_agent", "insight_agent", "recommendation_agent"]
        elif "inventory" in q or "stock" in q or "shortage" in q or "availability" in q:
            query_type = "INVENTORY_RISK"
            active_agents = ["inventory_risk_agent", "supplier_risk_agent", "delivery_risk_agent", "insight_agent", "recommendation_agent"]
        elif "supplier" in q or "lead time" in q or "lead-time" in q:
            query_type = "SUPPLIER_RISK"
            active_agents = ["supplier_risk_agent", "delivery_risk_agent", "insight_agent", "recommendation_agent"]
        elif "delay" in q or "delivery" in q or "carrier" in q or "route" in q:
            query_type = "DELIVERY_RISK"
            active_agents = ["delivery_risk_agent", "supplier_risk_agent", "insight_agent", "recommendation_agent"]
        else:
            query_type = "GENERAL_RISK"
            # Full 6-agent pipeline
            active_agents = [
                "supplier_risk_agent",
                "delivery_risk_agent",
                "inventory_risk_agent",
                "demand_agent",
                "insight_agent",
                "recommendation_agent"
            ]

        return {
            "query_type": query_type,
            "target_entities": {
                "suppliers": suppliers,
                "products": products
            },
            "active_agents": active_agents
        }

    def _record_handoff(self, state: OrchestratorState, from_agent: str, to_agent: str, payload_keys: List[str], summary: str):
        if "handoffs" not in state:
            state["handoffs"] = []
        state["handoffs"].append({
            "from_agent": from_agent,
            "to_agent": to_agent,
            "payload_keys": payload_keys,
            "summary": summary,
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3]
        })

    # Node wrappers with explicit A2A handoffs
    def node_supplier(self, state: OrchestratorState) -> OrchestratorState:
        if "supplier_risk_agent" in state.get("active_agents", []):
            try:
                state = self.supplier_agent.run(state)
                # A2A Handoff to Delivery Agent
                self._record_handoff(
                    state,
                    from_agent="Supplier Risk Agent",
                    to_agent="Delivery Risk Agent",
                    payload_keys=["supplier_profiles", "highest_risk_supplier", "weights_used"],
                    summary=f"Transferred supplier risk profile for {state['agent_outputs']['supplier_risk_agent'].get('highest_risk_supplier')} to Delivery Risk Agent."
                )
            except Exception as e:
                self._log_agent_error(state, "Supplier Risk Agent", str(e))
        return state

    def node_delivery(self, state: OrchestratorState) -> OrchestratorState:
        if "delivery_risk_agent" in state.get("active_agents", []):
            try:
                state = self.delivery_agent.run(state)
                # A2A Handoff to Inventory Agent
                self._record_handoff(
                    state,
                    from_agent="Delivery Risk Agent",
                    to_agent="Inventory Risk Agent",
                    payload_keys=["late_order_rate", "avg_delay_days", "carrier_performance"],
                    summary=f"Transferred delivery delay metrics ({state['agent_outputs']['delivery_risk_agent'].get('avg_delay_days')}d delay) to Inventory Risk Agent."
                )
            except Exception as e:
                self._log_agent_error(state, "Delivery Risk Agent", str(e))
        return state

    def node_inventory(self, state: OrchestratorState) -> OrchestratorState:
        if "inventory_risk_agent" in state.get("active_agents", []):
            try:
                state = self.inventory_agent.run(state)
                # A2A Handoff to Demand or Insight
                self._record_handoff(
                    state,
                    from_agent="Inventory Risk Agent",
                    to_agent="Demand Agent / Insight Agent",
                    payload_keys=["product_inventory_details", "critical_stockouts_count"],
                    summary=f"Transferred stockout exposure ({state['agent_outputs']['inventory_risk_agent'].get('critical_stockouts_count')} critical SKUs) downstream."
                )
            except Exception as e:
                self._log_agent_error(state, "Inventory Risk Agent", str(e))
        return state

    def node_demand(self, state: OrchestratorState) -> OrchestratorState:
        if "demand_agent" in state.get("active_agents", []):
            try:
                state = self.demand_agent.run(state)
                # A2A Handoff to Insight Agent
                self._record_handoff(
                    state,
                    from_agent="Demand Agent",
                    to_agent="Insight Agent",
                    payload_keys=["total_projected_demand", "evaluation_metrics"],
                    summary=f"Passed 30-day forecast projection for {state['agent_outputs']['demand_agent'].get('target_product_id')} to Insight Agent."
                )
            except Exception as e:
                self._log_agent_error(state, "Demand Agent", str(e))
        return state

    def node_insight(self, state: OrchestratorState) -> OrchestratorState:
        if "insight_agent" in state.get("active_agents", []):
            try:
                state = self.insight_agent.run(state)
                # A2A Handoff to Recommendation Agent
                self._record_handoff(
                    state,
                    from_agent="Insight Agent",
                    to_agent="Recommendation Agent",
                    payload_keys=["overall_supply_chain_risk", "causal_risk_chains"],
                    summary=f"Passed consolidated causal risk chains and {state['agent_outputs']['insight_agent'].get('overall_supply_chain_risk')} system risk to Recommendation Agent."
                )
            except Exception as e:
                self._log_agent_error(state, "Insight Agent", str(e))
        return state

    def node_recommendation(self, state: OrchestratorState) -> OrchestratorState:
        if "recommendation_agent" in state.get("active_agents", []):
            try:
                state = self.recommendation_agent.run(state)
            except Exception as e:
                self._log_agent_error(state, "Recommendation Agent", str(e))
        return state

    def _log_agent_error(self, state: OrchestratorState, agent_name: str, error_msg: str):
        if "agent_trace" not in state:
            state["agent_trace"] = []
        state["agent_trace"].append({
            "step": len(state["agent_trace"]) + 1,
            "agent_name": agent_name,
            "status": "ERROR",
            "latency_ms": 0.0,
            "summary": f"Failed with error: {error_msg}. Recovered via fault-tolerant bypass.",
            "data_points_analyzed": 0
        })

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(OrchestratorState)

        builder.add_node("supplier_node", self.node_supplier)
        builder.add_node("delivery_node", self.node_delivery)
        builder.add_node("inventory_node", self.node_inventory)
        builder.add_node("demand_node", self.node_demand)
        builder.add_node("insight_node", self.node_insight)
        builder.add_node("recommendation_node", self.node_recommendation)

        builder.set_entry_point("supplier_node")
        builder.add_edge("supplier_node", "delivery_node")
        builder.add_edge("delivery_node", "inventory_node")
        builder.add_edge("inventory_node", "demand_node")
        builder.add_edge("demand_node", "insight_node")
        builder.add_edge("insight_node", "recommendation_node")
        builder.add_edge("recommendation_node", END)

        return builder.compile()

    def execute(self, query: str) -> OrchestratorState:
        """Executes full state-based multi-agent workflow."""
        meta = self.classify_and_extract(query)

        # Retrieve relevant semantic knowledge from vector store
        knowledge_context = self.context.semantic_search.search(query, top_k=2)

        initial_state: OrchestratorState = {
            "query": query,
            "query_type": meta["query_type"],
            "target_entities": meta["target_entities"],
            "active_agents": meta["active_agents"],
            "agent_trace": [],
            "handoffs": [],
            "agent_outputs": {},
            "knowledge_context": knowledge_context,
            "status": "IN_PROGRESS"
        }

        # Execute LangGraph workflow
        final_state = self.graph.invoke(initial_state)
        final_state["status"] = "COMPLETED"
        return final_state
