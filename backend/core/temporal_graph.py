"""
TruthGuard Temporal Knowledge Graph (TKG) & Version Lineage Engine
Constructs a Directed Acyclic Graph (DAG) linking parent policies, amendments, and supersedence chains.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

class TemporalGraph:
    def __init__(self):
        self.nodes: Dict[str, dict] = {}
        # edges[parent_id] = [child_ids that supersede parent]
        self.superseded_by_edges: Dict[str, List[str]] = {}
        # edges[child_id] = [parent_ids that child supersedes]
        self.supersedes_edges: Dict[str, List[str]] = {}

    def add_document(self, doc: dict) -> None:
        doc_id = doc["id"]
        self.nodes[doc_id] = {
            "id": doc_id,
            "title": doc.get("title", ""),
            "category": doc.get("category", ""),
            "version": doc.get("version", "1.0"),
            "effective_date": doc.get("effective_date", "1970-01-01"),
            "supersedes": doc.get("supersedes"),
            "superseded_by": doc.get("superseded_by"),
            "content": doc.get("content", ""),
            "author": doc.get("author", "")
        }
        if doc_id not in self.superseded_by_edges:
            self.superseded_by_edges[doc_id] = []
        if doc_id not in self.supersedes_edges:
            self.supersedes_edges[doc_id] = []

        # If doc explicitly declares it supersedes another
        parent_id = doc.get("supersedes")
        if parent_id:
            self.add_supersedence(child_id=doc_id, parent_id=parent_id)

        # If doc explicitly declares it is superseded by another
        child_id = doc.get("superseded_by")
        if child_id:
            self.add_supersedence(child_id=child_id, parent_id=doc_id)

    def add_supersedence(self, child_id: str, parent_id: str) -> None:
        if parent_id not in self.superseded_by_edges:
            self.superseded_by_edges[parent_id] = []
        if child_id not in self.superseded_by_edges[parent_id]:
            self.superseded_by_edges[parent_id].append(child_id)

        if child_id not in self.supersedes_edges:
            self.supersedes_edges[child_id] = []
        if parent_id not in self.supersedes_edges[child_id]:
            self.supersedes_edges[child_id].append(parent_id)

    def is_superseded(self, doc_id: str) -> Tuple[bool, List[str]]:
        """Returns True and the list of superseding documents if doc_id has been superseded."""
        children = self.superseded_by_edges.get(doc_id, [])
        return (len(children) > 0, children)

    def does_supersede(self, doc_a: str, doc_b: str) -> bool:
        """Checks if doc_a supersedes doc_b either directly or through transitive DAG traversal."""
        visited: Set[str] = set()
        queue = [doc_b]
        while queue:
            curr = queue.pop(0)
            if curr == doc_a:
                return True
            visited.add(curr)
            for child in self.superseded_by_edges.get(curr, []):
                if child not in visited:
                    queue.append(child)
        return False

    def get_lineage(self, doc_id: str) -> List[dict]:
        """Returns chronological provenance chain for a given document."""
        chain = []
        # Trace roots
        visited = set()
        def collect_roots(curr_id):
            parents = self.supersedes_edges.get(curr_id, [])
            if not parents:
                return [curr_id]
            res = []
            for p in parents:
                if p not in visited:
                    visited.add(p)
                    res.extend(collect_roots(p))
            return res

        roots = collect_roots(doc_id)
        # Trace forward from root to leaves
        walk_visited = set()
        walk_queue = list(roots)
        while walk_queue:
            node_id = walk_queue.pop(0)
            if node_id in self.nodes and node_id not in walk_visited:
                walk_visited.add(node_id)
                chain.append(self.nodes[node_id])
                for child in self.superseded_by_edges.get(node_id, []):
                    walk_queue.append(child)

        # Sort chronologically by effective date
        chain.sort(key=lambda x: x["effective_date"])
        return chain

    def resolve_temporal_precedence(self, doc_ids: List[str]) -> dict:
        """
        Given a list of candidate documents that might contradict each other,
        determines the canonical latest authoritative document and identifies superseded ones.
        """
        if not doc_ids:
            return {"canonical": None, "superseded": [], "ambiguous": []}

        docs = [self.nodes[d] for d in doc_ids if d in self.nodes]
        docs.sort(key=lambda d: d["effective_date"], reverse=True)

        # Check DAG supersedence
        superseded_docs = []
        active_candidates = []

        for d in docs:
            d_id = d["id"]
            # Is this doc superseded by any other in the candidate list?
            is_old = False
            for other in docs:
                if other["id"] != d_id and self.does_supersede(other["id"], d_id):
                    is_old = True
                    superseded_docs.append({
                        "doc_id": d_id,
                        "title": d["title"],
                        "date": d["effective_date"],
                        "superseded_by": other["id"],
                        "superseding_title": other["title"],
                        "superseding_date": other["effective_date"]
                    })
                    break
            if not is_old:
                active_candidates.append(d)

        # If exactly 1 active candidate remains, precedence is resolved deterministically!
        if len(active_candidates) == 1:
            return {
                "status": "RESOLVED_PREVALENT",
                "canonical": active_candidates[0],
                "superseded": superseded_docs,
                "ambiguous": []
            }
        elif len(active_candidates) > 1:
            # Check if active candidates have identical or overlapping dates without explicit hierarchy
            return {
                "status": "UNRESOLVED_AMBIGUITY",
                "canonical": None,
                "superseded": superseded_docs,
                "ambiguous": active_candidates
            }
        else:
            return {
                "status": "EMPTY",
                "canonical": None,
                "superseded": [],
                "ambiguous": []
            }
