import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.agents.orchestrator import TruthGuardOrchestrator

class TestTruthGuardAgents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus_path = os.path.join(BASE_DIR, "backend", "data", "sample_corpus.json")
        cls.orchestrator = TruthGuardOrchestrator(corpus_path=corpus_path)

    def test_01_corpus_ingestion(self):
        """Verifies all benchmark contradictory documents are indexed."""
        docs = self.orchestrator.vector_store.documents
        self.assertGreaterEqual(len(docs), 8)
        self.assertIn("DOC-TIME-001", docs)
        self.assertIn("DOC-TIME-002", docs)

    def test_02_temporal_dag_supersedence(self):
        """Verifies that 2025 Addendum (DOC-TIME-002) supersedes 2023 SLA (DOC-TIME-001)."""
        tg = self.orchestrator.temporal_graph
        is_old, superseding = tg.is_superseded("DOC-TIME-001")
        self.assertTrue(is_old)
        self.assertIn("DOC-TIME-002", superseding)
        self.assertTrue(tg.does_supersede("DOC-TIME-002", "DOC-TIME-001"))

    def test_03_critic_detects_contradiction(self):
        """Verifies that Critic actively identifies monetary cap & MTTR contradictions."""
        query = "What is the penalty compensation and MTTR response window for Tier-1 Network Outage?"
        res = self.orchestrator.process_query(query)
        critic = res["critic_findings"]

        self.assertTrue(critic["has_conflict"])
        self.assertTrue(critic["has_staleness"])
        self.assertEqual(critic["verdict"], "CHALLENGE_RAISED")
        self.assertGreater(len(critic["contradictions"]), 0)

    def test_04_resolution_applies_temporal_supersedence(self):
        """Verifies that Resolution Step determines the canonical active policy with provenance."""
        query = "What is the Tier-1 Network Outage compensation cap?"
        res = self.orchestrator.process_query(query)

        self.assertEqual(res["resolution_type"], "TEMPORAL_SUPERSEDENCE_APPLIED")
        self.assertIn("$25,000", res["final_answer"])
        self.assertIn("SUPERSEDED", res["final_answer"])
        self.assertGreaterEqual(res["confidence_score"], 0.90)

    def test_05_unresolvable_ambiguity_transparent_dissent(self):
        """Verifies that simultaneous conflicting circulars without DAG hierarchy trigger transparent ambiguity."""
        query = "What is the maximum allowed power limit for Band 78 private 5G in suburban campuses?"
        res = self.orchestrator.process_query(query)

        self.assertEqual(res["resolution_type"], "TRANSPARENT_DISSENT_SURFACED")
        self.assertIn("UNRESOLVABLE ENTERPRISE CONFLICT DETECTED", res["final_answer"])
        self.assertIn("200 Watts", res["final_answer"])
        self.assertIn("400 Watts", res["final_answer"])
        self.assertEqual(res["confidence_score"], 0.50)

    def test_06_benchmark_suite_evaluation(self):
        """Verifies automated execution of 4-case benchmark conflict suite with 100% accuracy."""
        report = self.orchestrator.run_benchmark_suite()
        self.assertEqual(report["total_cases"], 4)
        self.assertEqual(report["passed_cases"], 4)
        self.assertEqual(report["accuracy_rate"], 100.0)
        self.assertEqual(report["hallucination_compromise_rate"], 0.0)

if __name__ == "__main__":
    unittest.main()
