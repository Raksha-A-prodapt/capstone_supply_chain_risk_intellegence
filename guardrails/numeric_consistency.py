"""
Numeric Consistency Guardrail
Compares numbers in natural language generated text against deterministic
source-of-truth outputs to prevent factual numerical drift.
"""

import re
from typing import Dict, Any, List, Set

class NumericConsistencyGuardrail:
    @staticmethod
    def _extract_numbers(text: str) -> List[float]:
        # Extract integers, floats, percentages
        clean_text = text.replace(",", "")
        matches = re.findall(r"\b\d+(?:\.\d+)?%?", clean_text)
        nums = []
        for m in matches:
            try:
                if m.endswith("%"):
                    nums.append(float(m[:-1]))
                else:
                    nums.append(float(m))
            except ValueError:
                pass
        return nums

    @classmethod
    def verify(cls, generated_text: str, agent_evidence: List[str], agent_outputs: Dict[str, Any]) -> Dict[str, Any]:
        text_numbers = cls._extract_numbers(generated_text)
        
        # Build truth numbers from evidence and outputs
        truth_str = " ".join(agent_evidence) + " " + str(agent_outputs)
        truth_numbers = set(cls._extract_numbers(truth_str))

        if not text_numbers:
            return {
                "numeric_consistency": True,
                "consistent_ratio": 1.0,
                "unverified_numbers": []
            }

        unverified = []
        consistent_count = 0

        for n in text_numbers:
            # Check if exact number or approximately equal (within 5%) exists in ground truth
            matched = any(abs(n - tn) <= max(0.2, 0.05 * tn) for tn in truth_numbers)
            # Standard conversational numbers (e.g. 1, 2, 3, 24, 30, 365) are exempt
            if matched or n in [1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 14.0, 30.0, 90.0, 100.0]:
                consistent_count += 1
            else:
                unverified.append(n)

        ratio = round(consistent_count / len(text_numbers), 3)
        is_consistent = (ratio >= 0.80)

        return {
            "numeric_consistency": is_consistent,
            "consistent_ratio": ratio,
            "total_numbers_checked": len(text_numbers),
            "unverified_numbers": unverified[:5]
        }
