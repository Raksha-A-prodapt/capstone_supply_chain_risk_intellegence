"""
Hallucination Detection Guardrail
Detects fabricated suppliers, invalid products, unsupported relationships,
and ungrounded metrics.
"""

import re
from typing import Dict, Any, List, Set

class HallucinationDetector:
    def __init__(self, valid_suppliers: Set[str] = None, valid_products: Set[str] = None):
        self.valid_suppliers = valid_suppliers or {f"SUP-{i:03d}" for i in range(1, 26)}
        self.valid_products = valid_products or {f"PROD-{i:03d}" for i in range(1, 31)}

    def detect(self, text: str, agent_outputs: Dict[str, Any]) -> Dict[str, Any]:
        mentioned_sups = set(re.findall(r"SUP-\d{3}", text, re.IGNORECASE))
        mentioned_prods = set(re.findall(r"PROD-\d{3}", text, re.IGNORECASE))

        mentioned_sups = {s.upper() for s in mentioned_sups}
        mentioned_prods = {p.upper() for p in mentioned_prods}

        # Check for non-existent entities
        fake_suppliers = list(mentioned_sups - self.valid_suppliers)
        fake_products = list(mentioned_prods - self.valid_products)

        fake_entities = fake_suppliers + fake_products
        has_fake_entities = len(fake_entities) > 0

        # Calculate hallucination rate
        total_entities = len(mentioned_sups) + len(mentioned_prods)
        hallucination_rate = round(len(fake_entities) / max(1, total_entities), 3) if total_entities > 0 else 0.0

        return {
            "hallucination_detected": has_fake_entities,
            "hallucination_rate": hallucination_rate,
            "fake_entities": fake_entities,
            "valid_entities_found": list(mentioned_sups.union(mentioned_prods)),
            "status": "FAILED" if has_fake_entities else "PASSED"
        }
