"""
Critical Acceptance Criteria Test: Deterministic Fallback Verification (Section 44)
Tests that when LLM is disabled / times out / fails, the system continues to
return a valid, rich, structured response with verified evidence and fallback status.
"""

import pytest
from assistant import SupplyChainAssistant

def test_critical_llm_failure_acceptance_criteria():
    """
    SECTION 44 CRITICAL ACCEPTANCE CRITERION:
    Disable/fake the LLM, send 'Which suppliers have the highest delivery risk?',
    assert the system returns a valid answer.
    """
    assistant = SupplyChainAssistant()

    # Force fallback (simulates total LLM outage / timeout)
    result = assistant.process_query(
        query="Which suppliers have the highest delivery risk?",
        force_fallback=True
    )

    # 1. System must return success status
    assert result is not None
    assert result["status"] == "success"

    # 2. Answer must not be blank
    assert len(result["answer"]) > 100
    assert "SUP-023" in result["answer"] or "CRITICAL" in result["answer"]

    # 3. Fallback flags must be clearly reported
    assert result["llm"]["fallback_used"] is True
    assert result["llm"]["fallback_reason"] is not None

    # 4. Deterministic evidence and recommendations must still be populated
    assert len(result["evidence"]) > 0
    assert len(result["recommendations"]) > 0

    # 5. Guardrails must reflect valid deterministic execution
    assert result["guardrails"]["schema_valid"] is True
    assert result["guardrails"]["hallucination_detected"] is False

    print("\n[PASSED] Critical Section 44 Failure Test Succeeded!")
