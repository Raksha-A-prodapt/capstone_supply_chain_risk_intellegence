"""
Embedding Client for OpenAI Gateway (text-embedding-3-small)
Communicates with https://keygateway1.arshnivlabs.com/v1/embeddings
Includes graceful offline fallback to avoid network blockage crashes.
"""

import os
import hashlib
from typing import List, Union
import requests
import urllib3
import numpy as np
from config.settings import settings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GatewayEmbeddingClient:
    def __init__(self):
        self.gateway_url = settings.GATEWAY_URL
        self.learner_key = settings.LEARNER_KEY
        self.headers = {
            "Authorization": f"Bearer {self.learner_key}",
            "Content-Type": "application/json"
        }
        self.cache: dict = {}

    def _fallback_embedding(self, text: str, dim: int = 1536) -> List[float]:
        """Deterministic pseudo-embedding if gateway is unreachable."""
        words = text.lower().split()
        vec = np.zeros(dim, dtype=np.float32)
        for w in words:
            h = int(hashlib.sha256(w.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            val = (h % 1000) / 1000.0 - 0.5
            vec[idx] += val
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def get_embedding(self, text: str) -> List[float]:
        """Gets 1536-dimensional vector embedding for text."""
        clean_text = text.strip()
        if not clean_text:
            return [0.0] * 1536
        if clean_text in self.cache:
            return self.cache[clean_text]

        try:
            url = f"{self.gateway_url}/v1/embeddings"
            response = requests.post(
                url,
                headers=self.headers,
                json={"input": clean_text},
                verify=settings.SSL_VERIFY,
                timeout=12
            )
            if response.status_code == 200:
                data = response.json()
                emb = data["data"][0]["embedding"]
                self.cache[clean_text] = emb
                return emb
            else:
                print(f"[Warning] Gateway embedding returned status {response.status_code}. Using fallback.")
                return self._fallback_embedding(clean_text)
        except Exception as e:
            print(f"[Warning] Gateway embedding error: {e}. Using deterministic fallback.")
            return self._fallback_embedding(clean_text)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.get_embedding(t) for t in texts]
