"""
TruthGuard Hybrid Vector & Sparse BM25 Retrieval Engine
Combines semantic similarity with exact BM25 keyword matching (crucial for numbers, acronyms, and section IDs).
"""

import math
import re
from typing import List, Dict, Any, Tuple

class HybridVectorStore:
    def __init__(self):
        self.documents: Dict[str, dict] = {}
        self.doc_tokens: Dict[str, List[str]] = {}
        self.df: Dict[str, int] = {}  # Document frequency for BM25
        self.total_docs: int = 0
        self.avg_doc_len: float = 0.0

    def _tokenize(self, text: str) -> List[str]:
        # Lowercase, retain alphanumeric and currency/percentage/metric symbols
        tokens = re.findall(r'\b[a-zA-Z0-9_\-\$\%]+|\$[0-9,]+|\d+(?:mg|w|ghz|hours?|years?)', text.lower())
        return tokens

    def add_document(self, doc: dict) -> None:
        doc_id = doc["id"]
        self.documents[doc_id] = doc
        combined_text = f"{doc.get('title', '')} {doc.get('category', '')} {doc.get('content', '')}"
        tokens = self._tokenize(combined_text)
        self.doc_tokens[doc_id] = tokens
        self.total_docs = len(self.documents)

        # Recompute DF and avg doc len
        self._reindex()

    def add_documents(self, docs: List[dict]) -> None:
        for d in docs:
            self.add_document(d)

    def _reindex(self) -> None:
        self.df.clear()
        total_len = 0
        for doc_id, tokens in self.doc_tokens.items():
            total_len += len(tokens)
            unique_terms = set(tokens)
            for t in unique_terms:
                self.df[t] = self.df.get(t, 0) + 1

        self.avg_doc_len = (total_len / self.total_docs) if self.total_docs > 0 else 1.0

    def _bm25_score(self, query_tokens: List[str], doc_id: str, k1: float = 1.5, b: float = 0.75) -> float:
        tokens = self.doc_tokens.get(doc_id, [])
        doc_len = len(tokens)
        if doc_len == 0 or self.total_docs == 0:
            return 0.0

        # Term counts in document
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1

        score = 0.0
        for q in query_tokens:
            if q in tf:
                doc_freq = self.df.get(q, 0)
                # Robertson-Sparck Jones IDF
                idf = math.log(((self.total_docs - doc_freq + 0.5) / (doc_freq + 0.5)) + 1.0)
                term_freq = tf[q]
                numerator = term_freq * (k1 + 1.0)
                denominator = term_freq + k1 * (1.0 - b + b * (doc_len / self.avg_doc_len))
                score += idf * (numerator / denominator)
        return score

    def _semantic_overlap(self, query_tokens: List[str], doc_id: str) -> float:
        tokens = set(self.doc_tokens.get(doc_id, []))
        if not tokens or not query_tokens:
            return 0.0
        q_set = set(query_tokens)
        intersection = q_set.intersection(tokens)
        return len(intersection) / math.sqrt(len(q_set) * len(tokens))

    def search(self, query: str, top_k: int = 5, category_filter: str = None) -> List[dict]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        results = []
        for doc_id, doc in self.documents.items():
            if category_filter and doc.get("category") != category_filter:
                continue

            bm25 = self._bm25_score(query_tokens, doc_id)
            sem = self._semantic_overlap(query_tokens, doc_id)
            # Weighted hybrid fusion
            hybrid_score = (0.65 * bm25) + (0.35 * sem * 10.0)

            if hybrid_score > 0.05:
                results.append({
                    "id": doc_id,
                    "doc_id": doc_id,
                    "title": doc.get("title", ""),
                    "category": doc.get("category", ""),
                    "version": doc.get("version", "1.0"),
                    "effective_date": doc.get("effective_date", ""),
                    "content": doc.get("content", ""),
                    "author": doc.get("author", ""),
                    "score": round(hybrid_score, 4),
                    "bm25_score": round(bm25, 4),
                    "semantic_score": round(sem, 4)
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
