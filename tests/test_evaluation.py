"""Offline regression corpus validation and shared-budget evaluation behavior."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

from test_providers import exa, tavily
from test_search import QueueTransport

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/evaluate.py"
spec = importlib.util.spec_from_file_location("search_evaluate", SCRIPT)
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


class EvaluationTests(unittest.TestCase):
    def test_extraction_plan_is_separate_and_rejects_search_only_services(self):
        corpus = evaluation.load_cases(SCRIPT.parents[1] / "evaluations/queries.json")
        with patch.object(evaluation.search, "read_config", side_effect=AssertionError("must not read credentials")):
            report = evaluation.execute(corpus, ["deepseek", "tavily", "exa"], operation="fetch")
            self.assertEqual(report["planned_logical_requests"], 9)
            self.assertEqual(report["evaluation_operation"], "fetch")
            with self.assertRaises(evaluation.search.SearchError):
                evaluation.execute(corpus, ["brave"], operation="fetch")

    def test_extraction_evaluation_records_counts_not_page_text_and_shares_budget(self):
        corpus = {"fetches": [{"id": "one", "url": "https://example.com/a", "expected_terms": ["page"]},
                              {"id": "two", "url": "https://example.com/b", "expected_terms": []}]}
        config = {"schema_version": 2, "providers": {"exa": {"api_key": "synthetic-key"}, "tavily": {"api_key": "synthetic-key"}}}
        transport = QueueTransport(exa(), {"results": [{"url": "https://example.com/a", "raw_content": "page"}], "failed_results": []})
        with patch.object(evaluation.search, "read_config", return_value=config), \
                patch.dict(evaluation.search.os.environ, {}, clear=True), \
                patch.object(evaluation.search.urllib.request, "build_opener", return_value=transport):
            report = evaluation.execute(corpus, ["exa", "tavily"], operation="fetch", live=True, max_requests=2)
        self.assertEqual(report["completed_cases"], 1)
        self.assertFalse(report["complete"])
        self.assertEqual(report["budget"]["attempts"], 2)
        check = report["cases"][0]["checks"][0]
        self.assertEqual(check["content_characters"], 4)
        self.assertEqual(check["expected_term_matches"], ["page"])
        self.assertNotIn("content", check)
        self.assertNotIn("synthetic-key", str(report))

    def test_checked_in_bilingual_corpus_plans_without_credentials_or_network(self):
        corpus = evaluation.load_cases(SCRIPT.parents[1] / "evaluations/queries.json")
        with patch.object(evaluation.search, "read_config", side_effect=AssertionError("must not read credentials")), \
                patch.object(evaluation.search, "request_api", side_effect=AssertionError("must not call network")):
            report = evaluation.execute(corpus, list(evaluation.search.PROVIDERS))
        self.assertTrue(report["ok"])
        self.assertEqual(report["planned_logical_requests"], 72)
        self.assertEqual(report["budget"]["attempts"], 0)
        self.assertFalse(report["facts_verified"])
        self.assertEqual({case["language"] for case in corpus["queries"]}, {"en", "zh"})

    def test_live_evaluation_obeys_shared_budget_and_does_not_save_raw_response(self):
        corpus = {"as_of": "2026-11-02", "queries": [
            {"id": "one", "query": "fixture", "category": "test", "expected_domains": ["example.com"]},
            {"id": "two", "query": "second", "category": "test", "expected_domains": []}]}
        config = {"schema_version": 2, "providers": {"exa": {"api_key": "synthetic-key"}, "tavily": {"api_key": "synthetic-key"}}}
        transport = QueueTransport(exa(), tavily())
        with patch.object(evaluation.search, "read_config", return_value=config), \
                patch.dict(evaluation.search.os.environ, {}, clear=True), \
                patch.object(evaluation.search.urllib.request, "build_opener", return_value=transport):
            report = evaluation.execute(corpus, ["exa", "tavily"], live=True, max_requests=2)
        self.assertFalse(report["complete"])
        self.assertEqual(report["completed_cases"], 1)
        self.assertEqual(len(transport.requests), 2)
        self.assertEqual(report["budget"]["scope"], "evaluation_run")
        self.assertTrue(report["cases"][0]["sources"][0]["expected_domain_match"])
        self.assertNotIn("synthetic-key", str(report))
        self.assertNotIn("generated answer", str(report))


if __name__ == "__main__":
    unittest.main()
