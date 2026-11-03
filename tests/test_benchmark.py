"""Offline benchmark safeguards and conservative mismatch signals."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

from test_search import QueueTransport, ds
from search_quality import obvious_mismatch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('benchmark', ROOT / 'scripts/benchmark.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class BenchmarkTests(unittest.TestCase):
    def test_default_plan_never_reads_credentials_or_connects(self):
        for name, cells in [('smart-cases.json', 18), ('smart-holdout.json', 6)]:
            corpus = b.load_cases(ROOT / 'evaluations' / name)
            with patch.object(b.search, 'read_config', side_effect=AssertionError('no credentials')), \
                    patch.object(b.search, 'request_api', side_effect=AssertionError('no network')):
                result = b.execute(corpus)
            self.assertEqual(result['plan']['cells'], cells)
            self.assertEqual(result['network_requests'], 0)
            self.assertFalse(result['semantic_quality_assessed'])

    def test_native_date_constraints_and_explicit_deepseek_query_are_distinct(self):
        case = b.load_cases(ROOT / 'evaluations/smart-cases.json')['cases'][4]
        native = b.query_args(case, 'smart')
        direct = b.query_args(case, 'deepseek')
        self.assertEqual(native.start_date, '2026-10-27')
        self.assertIsNone(direct.start_date)
        self.assertIn('after:2026-10-27', direct.query)
        self.assertEqual(native.intent, 'current')

    def test_live_budget_and_observed_billing_exclude_empty_success(self):
        corpus = {'cases': [{'id': 'one', 'query': 'test'}, {'id': 'two', 'query': 'test'},
                            {'id': 'three', 'query': 'test'}],
                  'price_reference': {'deepseek_usd_per_successful_request': .00075}}
        config = {'schema_version': 2, 'providers': {'deepseek': {'api_key': 'synthetic-only'}}}
        transport = QueueTransport(ds(), {'results': []})
        with patch.object(b.search, 'read_config', return_value=config), \
                patch.dict(b.search.os.environ, {}, clear=True), \
                patch.object(b.search.urllib.request, 'build_opener', return_value=transport):
            report = b.execute(corpus, live=True, modes=('deepseek',), max_requests=2)
        self.assertFalse(report['ok'])
        self.assertEqual(report['budget']['attempts'], 2)
        self.assertEqual(report['cost']['deepseek_successes'], 1)
        self.assertEqual(report['cost']['estimated_known_search_cost'], .00075)
        self.assertNotIn('synthetic-only', str(report))
        self.assertIsNone(report['model_cost_usd'])

    def test_comparison_rotates_modes_without_parallel_competition(self):
        corpus = {'cases': [{'id': str(i), 'query': 'test'} for i in range(3)]}
        order = []
        def fake(case, mode, config, budget, **kw):
            order.append(mode)
            budget.consume('synthetic')
            return {'id': case['id'], 'mode': mode, 'ok': True, 'elapsed_ms': 1, 'receipts': []}
        with patch.object(b.search, 'read_config', return_value={}), patch.object(b, 'run_cell', side_effect=fake):
            report = b.execute(corpus, live=True, max_requests=9)
        self.assertEqual(order, ['free', 'deepseek', 'smart', 'deepseek', 'smart', 'free', 'smart', 'free', 'deepseek'])
        self.assertTrue(report['ok'])

    def test_mismatch_is_zero_overlap_only_and_skips_short_or_nonlatin_queries(self):
        bad = [{'title': 'Windows Get Help', 'url': 'https://microsoft.com/help'}]
        good = [{'title': 'TaskGroup semantics', 'url': 'https://docs.python.org/'}]
        self.assertTrue(obvious_mismatch('Python asyncio TaskGroup', bad))
        self.assertFalse(obvious_mismatch('Python asyncio TaskGroup', good))
        self.assertFalse(obvious_mismatch('Python', bad))
        self.assertFalse(obvious_mismatch('今天的天气', bad))
        self.assertFalse(obvious_mismatch('Node.js LTS', [{'title': 'Nodejs LTS'}]))
        self.assertFalse(obvious_mismatch('site:python.org Python', bad))


if __name__ == '__main__':
    unittest.main()
