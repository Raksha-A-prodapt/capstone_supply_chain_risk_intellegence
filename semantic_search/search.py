"""
Semantic Search & Vector Indexer
Indexes knowledge base documents, generates embeddings,
and retrieves relevant supply-chain SOP and SLA contexts using cosine similarity.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from config.settings import settings
from semantic_search.embeddings import GatewayEmbeddingClient

class SemanticSearchEngine:
    def __init__(self, docs_dir: Optional[Path] = None, index_file: Optional[Path] = None):
        self.docs_dir = docs_dir or settings.DOCS_DIR
        self.index_file = index_file or (settings.BASE_DIR / "knowledge_base" / "embeddings" / "kb_vectors.json")
        self.embedding_client = GatewayEmbeddingClient()
        self.chunks: List[Dict[str, Any]] = []
        self.vectors: np.ndarray = np.array([])

    def build_index(self, force_rebuild: bool = False):
        """Extracts chunks from documents and indexes their embeddings."""
        if not force_rebuild and self.load_index():
            print(f"Loaded existing semantic index with {len(self.chunks)} chunks.")
            return

        print("Building Semantic Search Index from knowledge documents...")
        os.makedirs(self.docs_dir, exist_ok=True)
        chunks = []

        for file_path in self.docs_dir.glob("*.md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split by markdown headers
            sections = content.split("## ")
            doc_title = sections[0].replace("#", "").strip()

            for sec in sections[1:]:
                lines = sec.strip().split("\n")
                sec_title = lines[0].strip()
                sec_body = "\n".join(lines[1:]).strip()
                if sec_body:
                    chunks.append({
                        "doc_title": doc_title,
                        "section_title": sec_title,
                        "file_name": file_path.name,
                        "text": f"[{doc_title} - {sec_title}]\n{sec_body}"
                    })

        if not chunks:
            print("[Warning] No document chunks found to index.")
            return

        print(f"Embedding {len(chunks)} chunks using Gateway text-embedding-3-small...")
        texts = [c["text"] for c in chunks]
        embeddings = [self.embedding_client.get_embedding(t) for t in texts]

        self.chunks = chunks
        self.vectors = np.array(embeddings, dtype=np.float32)

        # Save index to disk
        os.makedirs(self.index_file.parent, exist_ok=True)
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump({
                "chunks": self.chunks,
                "vectors": self.vectors.tolist()
            }, f, indent=2)

        print(f"Semantic index saved to {self.index_file} ({len(self.chunks)} chunks).")

    def load_index(self) -> bool:
        """Loads precomputed vectors from disk if available."""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.chunks = data["chunks"]
                self.vectors = np.array(data["vectors"], dtype=np.float32)
                return True
            except Exception as e:
                print(f"[Warning] Failed loading index: {e}")
                return False
        return False

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves top_k relevant knowledge snippets for query."""
        if len(self.chunks) == 0:
            self.build_index()

        if len(self.chunks) == 0:
            return []

        query_vec = np.array(self.embedding_client.get_embedding(query), dtype=np.float32)
        norm_q = np.linalg.norm(query_vec)
        if norm_q > 0:
            query_vec = query_vec / norm_q

        # Cosine similarities
        norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized_vectors = self.vectors / norms
        sims = np.dot(normalized_vectors, query_vec)

        top_indices = np.argsort(sims)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "doc_title": self.chunks[idx]["doc_title"],
                "section": self.chunks[idx]["section_title"],
                "file": self.chunks[idx]["file_name"],
                "text": self.chunks[idx]["text"],
                "similarity_score": round(float(sims[idx]), 4)
            })

        return results

if __name__ == "__main__":
    engine = SemanticSearchEngine()
    engine.build_index(force_rebuild=True)
    sample_res = engine.search("What happens if supplier delays by 7 days?")
    print("\nSample Search Results:")
    for r in sample_res:
        print(f"[{r['similarity_score']}] {r['doc_title']} -> {r['section']}")
