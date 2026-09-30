"""
Multi-Agent Shared State Definition
Defines the state structure passed through the LangGraph orchestrator and A2A handoff bus.
"""

from typing import Dict, Any, List, Optional, TypedDict

class AgentExecutionTrace(TypedDict):
    step: int
    agent_name: str
    status: str
    latency_ms: float
    summary: str
    data_points_analyzed: int

class AgentHandoff(TypedDict):
    from_agent: str
    to_agent: str
    payload_keys: List[str]
    summary: str
    timestamp: str

class OrchestratorState(TypedDict, total=False):
    query: str
    query_type: str
    target_entities: Dict[str, List[str]]
    active_agents: List[str]
    agent_trace: List[AgentExecutionTrace]
    handoffs: List[AgentHandoff]
    agent_outputs: Dict[str, Any]
    knowledge_context: List[Dict[str, Any]]
    final_result: Dict[str, Any]
    llm_meta: Dict[str, Any]
    guardrails: Dict[str, Any]
    evaluation: Dict[str, Any]
    status: str
    error: Optional[str]
