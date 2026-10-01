"""
Input Guardrails
Validates user queries against prompt injection, off-topic requests,
empty strings, and malicious payload attacks.
"""

import re
from typing import Dict, Any
from guardrails.topic_classifier import SupplyChainTopicClassifier

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

OFF_TOPIC_REASON = (
    "Query is outside scope. Please ask about suppliers, deliveries, inventory, "
    "demand, logistics, or supply-chain risk."
)

class InputGuardrail:
    def __init__(self, topic_classifier=None):
        self.topic_classifier = topic_classifier or SupplyChainTopicClassifier()

    @staticmethod
    def _reject(query: str, reason: str) -> Dict[str, Any]:
        return {
            "is_valid": False,
            "sanitized_query": query,
            "rejection_reason": reason,
        }

    def validate(self, query: str) -> Dict[str, Any]:
        clean_q = query.strip()
        
        # 1. Empty / Whitespace check
        if not clean_q or len(clean_q) < 3:
            return self._reject(
                clean_q,
                "Query is too short or empty. Please ask a supply-chain risk question.",
            )

        if len(clean_q) > 600:
            return self._reject(
                clean_q[:600],
                "Query exceeds maximum allowed length of 600 characters.",
            )

        # 2. Prompt Injection detection
        for pat in INJECTION_PATTERNS:
            if re.search(pat, clean_q, re.IGNORECASE):
                return self._reject(
                    clean_q,
                    "Query rejected by security guardrail: Malicious prompt injection pattern detected.",
                )

        topic_check = self.topic_classifier.classify(clean_q)
        if not topic_check["is_in_scope"]:
            return self._reject(clean_q, topic_check["rejection_reason"] or OFF_TOPIC_REASON)

        return {
            "is_valid": True,
            "sanitized_query": clean_q,
            "rejection_reason": None
        }
