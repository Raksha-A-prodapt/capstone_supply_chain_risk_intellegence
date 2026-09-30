"""
Input Guardrails
Validates user queries against prompt injection, off-topic requests,
empty strings, and malicious payload attacks.
"""

import re
from typing import Dict, Any, Tuple

INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"disregard (all )?prior commands",
    r"system prompt",
    r"jailbreak",
    r"you are now a",
    r"dan mode",
    r"override security",
    r"<script>",
    r"drop table"
]

class InputGuardrail:
    @staticmethod
    def validate(query: str) -> Dict[str, Any]:
        clean_q = query.strip()
        
        # 1. Empty / Whitespace check
        if not clean_q or len(clean_q) < 3:
            return {
                "is_valid": False,
                "sanitized_query": clean_q,
                "rejection_reason": "Query is too short or empty. Please ask a supply-chain risk question."
            }

        if len(clean_q) > 600:
            return {
                "is_valid": False,
                "sanitized_query": clean_q[:600],
                "rejection_reason": "Query exceeds maximum allowed length of 600 characters."
            }

        # 2. Prompt Injection detection
        for pat in INJECTION_PATTERNS:
            if re.search(pat, clean_q, re.IGNORECASE):
                return {
                    "is_valid": False,
                    "sanitized_query": clean_q,
                    "rejection_reason": "Query rejected by security guardrail: Malicious prompt injection pattern detected."
                }

        # 3. Off-Topic detection (basic heuristic)
        off_topic_keywords = ["recipe", "poem", "joke", "weather in paris", "horoscope", "celebrity"]
        for kw in off_topic_keywords:
            if kw in clean_q.lower():
                return {
                    "is_valid": False,
                    "sanitized_query": clean_q,
                    "rejection_reason": "Query is off-topic. The assistant only processes supply-chain risk, supplier performance, inventory, and logistics queries."
                }

        return {
            "is_valid": True,
            "sanitized_query": clean_q,
            "rejection_reason": None
        }
