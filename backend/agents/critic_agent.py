import re
from typing import List, Dict, Any, Tuple
from backend.core.temporal_graph import TemporalGraph

class CriticAgent:
    def __init__(self, temporal_graph: TemporalGraph):
        self.temporal_graph = temporal_graph
        self.metric_keywords = {
            "financial_cap": ["penalty", "compensation", "cap", "fee", "credit", "outage", "cost", "fine", "$"],
            "time_window": ["mttr", "hour", "response", "window", "time", "resolution", "outage"],
            "power_limit": ["power", "watt", "eirp", "limit", "radiated"],
            "dosage": ["dose", "dosage", "cardipril", "mg", "hypertension", "medication"],
            "retention_years": ["retention", "archive", "tape", "years", "logs", "retain", "privacy", "purge"]
        }

    def _extract_metric_values(self, text: str) -> Dict[str, str]:
        metrics = {}
        money = re.findall(r'\$[0-9,]+', text)
        if money:
            metrics["financial_cap"] = money[0]

        durations = re.findall(r'(\d+)\s*(?:hours?|hrs?|minutes?|days?)', text, re.I)
        if durations:
            metrics["time_window"] = durations[0]

        power = re.findall(r'(\d+)\s*(?:watts?|w)', text, re.I)
        if power:
            metrics["power_limit"] = power[0]

        dosage = re.findall(r'(\d+)\s*mg', text, re.I)
        if dosage:
            metrics["dosage"] = dosage[0]

        years = re.findall(r'(\d+)\s*years?', text, re.I)
        if years:
            metrics["retention_years"] = years[0]

        return metrics

    def _detect_passage_contradictions(self, passages: List[dict], query: str = "") -> List[dict]:
        contradictions = []
        n = len(passages)
        primary_cat = passages[0].get("category") if passages else None
        q_lower = query.lower() if query else ""

        for i in range(n):
            for j in range(i + 1, n):
                p1 = passages[i]
                p2 = passages[j]

                if primary_cat and (p1.get("category") != primary_cat or p2.get("category") != primary_cat):
                    continue

                m1 = self._extract_metric_values(p1["content"])
                m2 = self._extract_metric_values(p2["content"])

                common_metrics = set(m1.keys()).intersection(set(m2.keys()))
                for metric in common_metrics:
                    if q_lower and metric in self.metric_keywords:
                        if not any(k in q_lower for k in self.metric_keywords[metric]):
                            continue

                    val1 = m1[metric]
                    val2 = m2[metric]
                    if val1 != val2:
                        contradictions.append({
                            "type": "DIRECT_METRIC_CONTRADICTION",
                            "metric": metric,
                            "doc_a": p1["id"],
                            "doc_a_title": p1["title"],
                            "doc_a_date": p1["effective_date"],
                            "doc_a_val": val1,
                            "doc_b": p2["id"],
                            "doc_b_title": p2["title"],
                            "doc_b_date": p2["effective_date"],
                            "doc_b_val": val2,
                            "severity": "HIGH",
                            "description": f"Conflict detected on '{metric}': {p1['id']} specifies '{val1}', but {p2['id']} specifies '{val2}'."
                        })
        return contradictions

    def _check_staleness(self, passages: List[dict], contradictions: List[dict] = None) -> List[dict]:
        staleness_flags = []
        doc_ids = [p["id"] for p in passages]
        primary_cat = passages[0].get("category") if passages else None

        for p in passages:
            p_id = p["id"]
            if primary_cat and p.get("category") and p["category"] != primary_cat:
                continue

            is_old, superseding_list = self.temporal_graph.is_superseded(p_id)
            if is_old:
                present_superseding = [s for s in superseding_list if s in doc_ids]
                staleness_flags.append({
                    "doc_id": p_id,
                    "title": p["title"],
                    "date": p["effective_date"],
                    "is_stale": True,
                    "superseded_by": superseding_list,
                    "superseding_present_in_results": present_superseding,
                    "warning": f"Document {p_id} ({p['effective_date']}) is deprecated and superseded by {superseding_list}."
                })
        return staleness_flags

    def _audit_unsupported_claims(self, candidate_claims: List[str], passages: List[dict]) -> List[str]:
        unsupported = []
        combined_text = " ".join([p["content"] for p in passages]).lower()
        for claim in candidate_claims:
            clean_claim = claim.strip().lower()
            if clean_claim and clean_claim not in combined_text:
                unsupported.append(claim)
        return unsupported

    def run(self, draft_data: Dict[str, Any], retrieved_data: Dict[str, Any]) -> Dict[str, Any]:
        passages = retrieved_data.get("passages", [])
        candidate_claims = draft_data.get("claims", [])
        query = draft_data.get("query") or retrieved_data.get("query", "")

        contradictions = self._detect_passage_contradictions(passages, query=query)
        staleness_flags = self._check_staleness(passages, contradictions=contradictions)
        unsupported_claims = self._audit_unsupported_claims(candidate_claims, passages)

        has_conflict = len(contradictions) > 0
        has_staleness = len(staleness_flags) > 0
        has_hallucinations = len(unsupported_claims) > 0

        if has_conflict or has_staleness or has_hallucinations:
            verdict = "CHALLENGE_RAISED"
        else:
            verdict = "CONSENSUS_VERIFIED"

        return {
            "verdict": verdict,
            "has_conflict": has_conflict,
            "has_staleness": has_staleness,
            "has_hallucinations": has_hallucinations,
            "contradictions": contradictions,
            "staleness_flags": staleness_flags,
            "unsupported_claims": unsupported_claims,
            "adversarial_findings_count": len(contradictions) + len(staleness_flags) + len(unsupported_claims)
        }
