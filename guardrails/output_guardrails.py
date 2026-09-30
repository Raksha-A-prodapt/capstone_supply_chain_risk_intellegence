"""
Output Guardrails Validation Suite
Orchestrates schema validation, grounding checks, hallucination checks,
and numeric consistency across LLM and deterministic outputs.
"""

from typing import Dict, Any, List, Optional
from guardrails.grounding import GroundingGuardrail
from guardrails.hallucination import HallucinationDetector
from guardrails.numeric_consistency import NumericConsistencyGuardrail

class OutputGuardrails:
    def __init__(self):
        self.grounding = GroundingGuardrail()
        self.hallucination = HallucinationDetector()
        self.numeric = NumericConsistencyGuardrail()

    def validate(
        self,
        llm_output: Dict[str, Any],
        agent_evidence: List[str],
        agent_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Runs the complete battery of output guardrails."""
        # 1. Schema Validation
        has_answer = bool(llm_output.get("natural_language_answer"))
        has_summary = bool(llm_output.get("risk_assessment_summary"))
        schema_valid = has_answer and has_summary

        answer_text = llm_output.get("natural_language_answer", "")
        claims = llm_output.get("claims_made", [])
        if not claims and answer_text:
            claims = [s.strip() for s in answer_text.split(".") if len(s.strip()) > 10]

        # 2. Grounding Evaluation
        grounding_res = self.grounding.evaluate(claims, agent_evidence, agent_outputs)

        # 3. Hallucination Detection
        hallucination_res = self.hallucination.detect(answer_text, agent_outputs)

        # 4. Numeric Consistency Check
        numeric_res = self.numeric.verify(answer_text, agent_evidence, agent_outputs)

        # Overall Status
        passed_all = (
            schema_valid and 
            grounding_res["is_grounded"] and 
            not hallucination_res["hallucination_detected"] and 
            numeric_res["numeric_consistency"]
        )

        return {
            "all_passed": passed_all,
            "schema_valid": schema_valid,
            "grounded": grounding_res["is_grounded"],
            "grounding_score": grounding_res["grounding_score"],
            "hallucination_detected": hallucination_res["hallucination_detected"],
            "hallucination_rate": hallucination_res["hallucination_rate"],
            "numeric_consistency": numeric_res["numeric_consistency"],
            "numeric_consistent_ratio": numeric_res["consistent_ratio"],
            "details": {
                "grounding": grounding_res,
                "hallucination": hallucination_res,
                "numeric": numeric_res
            }
        }
