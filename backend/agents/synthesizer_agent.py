"""
TruthGuard Synthesizer Agent
Drafts initial candidate response from retrieved passages and tags candidate factual assertions.
"""

import re
from typing import List, Dict, Any

class SynthesizerAgent:
    def __init__(self):
        pass

    def _extract_claims(self, text: str) -> List[str]:
        """Extracts specific quantitative or policy claims from text."""
        claims = []
        # Find amounts, hours, wattages, dosages, years
        patterns = [
            r'\$[0-9,]+',
            r'\d+\s*(?:hours?|hrs?|minutes?|days?)',
            r'\d+\s*(?:mg|grams?|ml)',
            r'\d+\s*(?:watts?|w|ghz|mhz)',
            r'\d+\s*(?:years?)',
            r'(?:capped at|strictly capped at|restricted to|authorized for)\s*[^.,;]+'
        ]
        for p in patterns:
            matches = re.findall(p, text, re.IGNORECASE)
            claims.extend(matches)
        return list(set(claims))

    def run(self, query: str, retrieved_data: Dict[str, Any]) -> Dict[str, Any]:
        passages = retrieved_data.get("passages", [])
        if not passages:
            return {
                "candidate_answer": "No relevant passages were found in the enterprise corpus.",
                "claims": [],
                "primary_sources": [],
                "confidence_score": 0.0
            }

        primary_doc = passages[0]
        primary_id = primary_doc.get("id") or primary_doc.get("doc_id", "DOC-UNKNOWN")
        claims = self._extract_claims(primary_doc["content"])

        # Formulate synthesized candidate draft
        candidate_answer = (
            f"Based on {primary_doc['title']} ({primary_id}, effective {primary_doc['effective_date']}): "
            f"{primary_doc['content']}"
        )

        return {
            "candidate_answer": candidate_answer,
            "claims": claims,
            "primary_sources": [p.get("id") or p.get("doc_id") for p in passages],
            "initial_confidence": 0.75,
            "status": "DRAFT_READY_FOR_ADVERSARY"
        }
