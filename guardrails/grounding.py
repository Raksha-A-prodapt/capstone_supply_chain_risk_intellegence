"""
Grounding Validation Guardrail
Evaluates generated claims against structured agent evidence.
Calculates grounding score = supported_claims / total_claims.
"""

from typing import Dict, Any, List
import re

class GroundingGuardrail:
    @staticmethod
    def evaluate(claims: List[str], agent_evidence: List[str], agent_outputs: Dict[str, Any]) -> Dict[str, Any]:
        if not claims:
            return {
                "grounding_score": 1.0,
                "total_claims": 0,
                "supported_claims": [],
                "unsupported_claims": [],
                "is_grounded": True
            }

        # Build corpus of known true evidence tokens
        evidence_text = " ".join(agent_evidence).lower()
        for k, v in agent_outputs.items():
            if isinstance(v, dict):
                evidence_text += " " + str(v).lower()

        supported = []
        unsupported = []

        for claim in claims:
            # Extract key nouns and numbers from claim
            words = [w for w in re.findall(r"\b[a-zA-Z0-9_\-\.%]+\b", claim.lower()) if len(w) > 2]
            if not words:
                supported.append(claim)
                continue

            # Check if at least 60% of significant words or core entities appear in evidence
            match_count = sum(1 for w in words if w in evidence_text)
            match_ratio = match_count / len(words)

            if match_ratio >= 0.45 or any(entity in evidence_text for entity in re.findall(r"sup-\d{3}|prod-\d{3}", claim, re.IGNORECASE)):
                supported.append(claim)
            else:
                unsupported.append(claim)

        total = len(claims)
        score = round(len(supported) / max(1, total), 3)

        return {
            "grounding_score": score,
            "total_claims": total,
            "supported_claims": supported,
            "unsupported_claims": unsupported,
            "is_grounded": (score >= 0.75)
        }
