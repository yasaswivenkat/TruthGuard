"""
TruthGuard Retriever Agent
Pulls candidate passages relevant to the query with hybrid dense/sparse search and temporal metadata.
"""

from typing import List, Dict, Any
from backend.core.vector_store import HybridVectorStore

class RetrieverAgent:
    def __init__(self, vector_store: HybridVectorStore):
        self.vector_store = vector_store

    def run(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Retrieves top candidate passages and extracts temporal spans.
        """
        passages = self.vector_store.search(query=query, top_k=top_k)

        # Group by category and extract distinct dates
        dates = sorted(list(set(p["effective_date"] for p in passages if p["effective_date"])))
        has_temporal_span = len(dates) > 1

        return {
            "query": query,
            "passages_count": len(passages),
            "passages": passages,
            "dates_detected": dates,
            "has_temporal_span": has_temporal_span,
            "retrieval_strategy": "Hybrid Dense-Sparse (BM25 + Semantic Cosine)"
        }
