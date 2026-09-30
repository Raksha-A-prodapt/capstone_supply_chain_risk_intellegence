"""
Multi-Agent Evaluation Runner
Executes the evaluation dataset across the complete multi-agent pipeline
and measures routing accuracy, success rate, grounding score, hallucination rate,
factual consistency, fallback frequency, and latency.
"""

import time
from typing import Dict, Any, List
import numpy as np
from assistant import SupplyChainAssistant
from evaluation.evaluation_dataset import EVALUATION_DATASET

def evaluate_all_agents(assistant: SupplyChainAssistant = None) -> Dict[str, Any]:
    ast = assistant or SupplyChainAssistant()
    
    results = []
    routing_matches = 0
    total_invocations = 0
    successful_invocations = 0
    grounding_scores = []
    hallucination_rates = []
    consistency_scores = []
    latencies = []
    fallback_count = 0

    print(f"Running evaluation benchmark on {len(EVALUATION_DATASET)} queries...")

    for item in EVALUATION_DATASET:
        t0 = time.time()
        res = ast.process_query(item["query"])
        elapsed = round((time.time() - t0) * 1000, 2)
        latencies.append(elapsed)

        # 1. Routing Evaluation: Was expected primary agent included?
        invoked_agents = res.get("agents_involved", [])
        primary_match = item["expected_primary_agent"] in invoked_agents
        if primary_match:
            routing_matches += 1

        # 2. Agent Execution Success Rate
        trace = res.get("agent_trace", [])
        for step in trace:
            total_invocations += 1
            if step["status"] == "SUCCESS":
                successful_invocations += 1

        # 3. Grounding & Hallucination
        eval_metrics = res.get("evaluation", {})
        g_score = eval_metrics.get("grounding_score", 1.0)
        h_rate = eval_metrics.get("hallucination_rate", 0.0)
        c_score = eval_metrics.get("factual_consistency", 1.0)

        grounding_scores.append(g_score)
        hallucination_rates.append(h_rate)
        consistency_scores.append(c_score)

        if res.get("llm", {}).get("fallback_used"):
            fallback_count += 1

        results.append({
            "id": item["id"],
            "query": item["query"],
            "category": item["category"],
            "expected_primary_agent": item["expected_primary_agent"],
            "agents_invoked": invoked_agents,
            "routing_success": primary_match,
            "risk_level": res.get("risk_level"),
            "grounding_score": g_score,
            "hallucination_rate": h_rate,
            "factual_consistency": c_score,
            "fallback_used": res.get("llm", {}).get("fallback_used", False),
            "latency_ms": elapsed
        })

    summary = {
        "total_test_queries": len(EVALUATION_DATASET),
        "routing_accuracy": round(routing_matches / len(EVALUATION_DATASET), 4),
        "agent_success_rate": round(successful_invocations / max(1, total_invocations), 4),
        "mean_grounding_score": round(float(np.mean(grounding_scores)), 4),
        "mean_hallucination_rate": round(float(np.mean(hallucination_rates)), 4),
        "mean_factual_consistency": round(float(np.mean(consistency_scores)), 4),
        "fallback_rate": round(fallback_count / len(EVALUATION_DATASET), 4),
        "average_latency_ms": round(float(np.mean(latencies)), 1),
        "total_agent_invocations": total_invocations,
        "successful_agent_invocations": successful_invocations,
        "sample_evaluations": results
    }

    return summary
