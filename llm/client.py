"""
OpenAI Gateway LLM Client
Connects to https://keygateway1.arshnivlabs.com/v1/chat/completions
Uses gpt-4o-mini to interpret structured deterministic agent results.
Includes timeout handling and fallback triggers.
"""

import json
import time
from typing import Dict, Any, List, Optional
import requests
import urllib3
from config.settings import settings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SYSTEM_PROMPT = """You are an expert AI Supply Chain Risk Intelligence Assistant.
Your primary role is to interpret and explain deterministically calculated supply-chain analytics,
ML predictions, and multi-agent risk findings to operational decision-makers.

CRITICAL INSTRUCTIONS:
1. NEVER invent, hallucinate, or alter any numbers, percentages, quantities, order counts, lead times, or risk scores.
2. Every number and entity mentioned in your response MUST come directly from the provided Structured Agent Results.
3. You must output strictly valid JSON matching the following schema:
{
  "natural_language_answer": "Concise, professional explanation of the supply chain risk and findings.",
  "risk_assessment_summary": "1-2 sentence executive summary of current risk exposure.",
  "key_findings": ["Point 1 with exact numbers", "Point 2 with exact numbers"],
  "claims_made": ["Claim 1 with metric", "Claim 2 with entity"]
}
Do NOT include markdown fences (```json ... ```) outside the JSON. Return raw valid JSON.
"""

class GatewayLLMClient:
    def __init__(self):
        self.gateway_url = settings.GATEWAY_URL
        self.learner_key = settings.LEARNER_KEY
        self.headers = {
            "Authorization": f"Bearer {self.learner_key}",
            "Content-Type": "application/json"
        }
        self.timeout = settings.LLM_TIMEOUT

    def generate_explanation(
        self,
        query: str,
        structured_agent_results: Dict[str, Any],
        knowledge_context: List[Dict[str, Any]],
        overall_risk: str
    ) -> Dict[str, Any]:
        """
        Sends structured agent results to Gateway gpt-4o-mini for natural language synthesis.
        """
        context_str = "\n".join([f"- [{k['doc_title']}]: {k['text'][:200]}..." for k in knowledge_context])
        
        # Build concise structured summary for prompt (do not dump giant unparsed data)
        prompt_payload = {
            "user_query": query,
            "overall_risk_level": overall_risk,
            "agent_findings": {
                k: {
                    "status": v.get("status"),
                    "evidence": v.get("evidence", [])[:4],
                    "metrics": {
                        mk: mv for mk, mv in v.items() 
                        if mk in ["late_order_rate", "avg_delay_days", "ml_model_predicted_late_prob", "highest_risk_supplier", "critical_stockouts_count", "total_projected_demand", "recommendations"]
                    }
                }
                for k, v in structured_agent_results.items()
            },
            "relevant_knowledge_base": context_str
        }

        user_content = (
            f"User Question: {query}\n\n"
            f"Deterministic Analytics Context:\n{json.dumps(prompt_payload, indent=2)}\n\n"
            f"Synthesize the natural language response in strict JSON format based ONLY on the evidence above."
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        url = f"{self.gateway_url}/v1/chat/completions"
        response = requests.post(
            url,
            headers=self.headers,
            json={"messages": messages, "temperature": 0.1},
            verify=settings.SSL_VERIFY,
            timeout=self.timeout
        )

        if response.status_code != 200:
            raise RuntimeError(f"Gateway returned HTTP {response.status_code}: {response.text}")

        data = response.json()
        raw_text = data["choices"][0]["message"]["content"].strip()

        # Clean potential markdown wrapping
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        parsed = json.loads(raw_text)
        return parsed
