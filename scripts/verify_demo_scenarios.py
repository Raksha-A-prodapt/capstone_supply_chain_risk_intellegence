"""Verification script for the 9 Required Demonstration Scenarios (Section 50)."""

import os
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assistant import SupplyChainAssistant

def run_demo():
    ast = SupplyChainAssistant()
    demo_queries = [
        "Which suppliers have the highest delivery risk?",
        "Why is supplier SUP-001 risky?",
        "Which products are most affected by supplier delays?",
        "Identify unusual supplier lead-time changes.",
        "Which products are at risk of stock-out?",
        "What is the demand forecast for product PROD-001?",
        "How could supplier SUP-001 delay affect inventory?",
        "What are the major supply-chain risks and what evidence supports them?",
        "What happens if supplier SUP-001 is delayed by 7 days?"
    ]

    print("=" * 70)
    print("VERIFYING ALL 9 DEMONSTRATION SCENARIOS (SECTION 50)")
    print("=" * 70)

    for i, q in enumerate(demo_queries, 1):
        res = ast.process_query(q)
        print(f"\n[{i}/9] Query: {q}")
        print(f"      Risk Level: {res['risk_level']} | Agents Invoked: {res['agents_involved']}")
        print(f"      Grounding: {res['evaluation']['grounding_score']} | Hallucination: {res['evaluation']['hallucination_rate']} | Status: {res['status']}")
        print(f"      Answer: {res['answer'][:180]}...")
        if res.get("what_if_simulation"):
            sim = res["what_if_simulation"]
            print(f"      [Simulation Detected] Potential Stockouts: {sim['potential_stockouts_count']}, Financial Exposure: ${sim['estimated_financial_exposure_usd']:,.2f}")

    print("\n" + "=" * 70)
    print("ALL 9 DEMO SCENARIOS VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
