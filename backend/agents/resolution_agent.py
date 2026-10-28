import hashlib
from typing import Dict, Any, List
from backend.core.temporal_graph import TemporalGraph

class ResolutionAgent:
    def __init__(self, temporal_graph: TemporalGraph):
        self.temporal_graph = temporal_graph

    def _hash_provenance(self, doc_id: str, content: str, date: str) -> str:
        payload = f"{doc_id}|{date}|{content}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:16]

    def run(self, 
            query: str, 
            draft_data: Dict[str, Any], 
            critic_data: Dict[str, Any], 
            retrieved_data: Dict[str, Any]) -> Dict[str, Any]:
        
        passages = retrieved_data.get("passages", [])
        contradictions = critic_data.get("contradictions", [])
        staleness_flags = critic_data.get("staleness_flags", [])

        conflicting_ids = set()
        for c in contradictions:
            conflicting_ids.add(c["doc_a"])
            conflicting_ids.add(c["doc_b"])

        if not conflicting_ids and staleness_flags:
            primary_id = passages[0]["id"] if passages else None
            primary_is_stale = any(s["doc_id"] == primary_id for s in staleness_flags)
            if primary_is_stale:
                for s in staleness_flags:
                    if s["doc_id"] == primary_id:
                        conflicting_ids.add(s["doc_id"])
                        for sup in s.get("superseded_by", []):
                            conflicting_ids.add(sup)

        if not conflicting_ids:
            primary_doc = passages[0] if passages else None
            return {
                "status": "CANONICAL_CONSENSUS",
                "resolution_type": "CANONICAL_CONSENSUS",
                "final_answer": draft_data.get("candidate_answer", ""),
                "canonical_document": primary_doc,
                "dissenting_positions": [],
                "confidence_score": 0.96,
                "provenance_chain": [
                    {
                        "doc_id": p["id"],
                        "title": p["title"],
                        "date": p["effective_date"],
                        "hash": self._hash_provenance(p["id"], p["content"], p["effective_date"]),
                        "status": "VALID_ACTIVE"
                    }
                    for p in passages
                ],
                "explanation": "All retrieved enterprise passages are consistent and verified."
            }

        target_ids = list(conflicting_ids)
        temporal_result = self.temporal_graph.resolve_temporal_precedence(target_ids)

        if temporal_result["status"] == "RESOLVED_PREVALENT":
            canonical = temporal_result["canonical"]
            superseded_items = temporal_result["superseded"]

            dissent_explanations = []
            for s in superseded_items:
                dissent_explanations.append(
                    f"Prior Document '{s['title']}' ({s['doc_id']}, effective {s['date']}) is SUPERSEDED by "
                    f"'{s['superseding_title']}' ({s['superseded_by']}, effective {s['superseding_date']})."
                )

            final_answer = (
                f"CANONICAL CURRENT POLICY (Effective {canonical['effective_date']}):\n"
                f"{canonical['content']}\n\n"
                f"TEMPORAL PROVENANCE & DISSENT AUDIT:\n"
                + "\n".join([f"• {e}" for e in dissent_explanations])
            )

            provenance_chain = []
            for p in passages:
                is_stale = any(s["doc_id"] == p["id"] for s in superseded_items)
                provenance_chain.append({
                    "doc_id": p["id"],
                    "title": p["title"],
                    "date": p["effective_date"],
                    "hash": self._hash_provenance(p["id"], p["content"], p["effective_date"]),
                    "status": "SUPERSEDED_DEPRECATED" if is_stale else "CANONICAL_ACTIVE"
                })

            return {
                "status": "RESOLVED_WITH_PROVENANCE",
                "resolution_type": "TEMPORAL_SUPERSEDENCE_APPLIED",
                "final_answer": final_answer,
                "canonical_document": canonical,
                "superseded_documents": superseded_items,
                "confidence_score": 0.94,
                "provenance_chain": provenance_chain,
                "explanation": (
                    f"Detected direct contradiction between versions. The conflict is successfully resolved "
                    f"because {canonical['id']} ({canonical['effective_date']}) legally supersedes prior iterations."
                )
            }

        elif temporal_result["status"] == "UNRESOLVED_AMBIGUITY":
            ambiguous_docs = temporal_result["ambiguous"]

            positions = []
            for doc in ambiguous_docs:
                positions.append(
                    f"• Position from '{doc['title']}' ({doc['id']}, effective {doc['effective_date']}):\n"
                    f"  \"{doc['content']}\""
                )

            final_answer = (
                "ATTENTION: UNRESOLVABLE ENTERPRISE CONFLICT DETECTED\n"
                "The enterprise corpus contains conflicting directives that cannot be resolved automatically "
                "because both documents hold valid status without a superseding precedence hierarchy.\n\n"
                "SURFACED CONFLICTING POSITIONS:\n"
                + "\n\n".join(positions) + "\n\n"
                "RECOMMENDATION: Manual compliance review or legal escalation required to clarify jurisdiction."
            )

            return {
                "status": "UNRESOLVED_AMBIGUITY",
                "resolution_type": "TRANSPARENT_DISSENT_SURFACED",
                "final_answer": final_answer,
                "canonical_document": None,
                "conflicting_positions": [
                    {
                        "doc_id": d["id"],
                        "title": d["title"],
                        "date": d["effective_date"],
                        "content": d["content"],
                        "author": d.get("author", "Regulatory Body"),
                        "position_summary": d["content"],
                        "hash": self._hash_provenance(d["id"], d["content"], d["effective_date"])
                    }
                    for d in ambiguous_docs
                ],
                "confidence_score": 0.50,
                "provenance_chain": [
                    {
                        "doc_id": p["id"],
                        "title": p["title"],
                        "date": p["effective_date"],
                        "hash": self._hash_provenance(p["id"], p["content"], p["effective_date"]),
                        "status": "CONFLICTING_UNRESOLVED"
                    }
                    for p in passages
                ],
                "explanation": (
                    "TruthGuard refuses to paper over this conflict with a false consensus. "
                    "Both conflicting positions have been surfaced with exact metadata and provenance."
                )
            }

        else:
            return {
                "status": "INDETERMINATE",
                "resolution_type": "NO_CANONICAL_ANSWER",
                "final_answer": "Unable to resolve query with available information.",
                "confidence_score": 0.20,
                "provenance_chain": [],
                "explanation": "Insufficient passage metadata to substantiate an authoritative response."
            }
