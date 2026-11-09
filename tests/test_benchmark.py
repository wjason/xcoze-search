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
    def test_outage_benchmark_blocks_exa_and_preserves_native_search(self):
        from test_open_sources import NPM
        corpus = {'cases': [{'id': 'one', 'query': '@example/tool', 'platform': 'npm'}]}
        transport = QueueTransport(NPM)
        with patch.object(b.search, 'read_config', side_effect=AssertionError('must not read config')), \
                patch.object(b.search.urllib.request, 'build_opener', return_value=transport):
            report = b.execute(corpus, live=True, modes=('free',), keyless=True, without_exa=True)
        self.assertTrue(report['without_exa'])
        self.assertEqual(report['cells'][0]['routing']['attempted_providers'], ['npm'])
        self.assertNotIn('exa-free', report['cells'][0]['routing']['candidates'])
        self.assertNotIn('exa', report['cells'][0]['routing']['candidates'])

    def test_keyless_smart_ignores_config_and_environment_keys(self):
        corpus = {'cases': [{'id': 'one', 'query': 'Python'}]}
        response = {'jsonrpc': '2.0', 'id': 1, 'result': {'structuredContent': {'results': [
            {'title': 'Python', 'url': 'https://python.org', 'text': 'Python'}]}}}
        with patch.object(b.search, 'read_config', side_effect=AssertionError('must not read config')), \
                patch.dict(b.search.os.environ, {'DEEPSEEK_API_KEY': 'synthetic-only'}), \
                patch.object(b.search.urllib.request, 'build_opener', return_value=QueueTransport(response)), \
                patch('search_routing.browser_available', return_value=False):
            report = b.execute(corpus, live=True, modes=('smart',), keyless=True, max_requests=3)
        self.assertTrue(report['cells'][0]['sources'])
        self.assertEqual(report['cells'][0]['receipts'][0]['source'], 'exa-free')
        self.assertNotIn('synthetic-only', str(report))
        with self.assertRaises(ValueError):
            b.execute(corpus, modes=('deepseek',), keyless=True)

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

    def test_strict_scraped_rows_require_code_topic_and_reject_wrong_year(self):
        from search_quality import filter_experimental
        query = 'PostgreSQL 18 uuidv7 shift interval documentation'
        weak = {'title':'PostgreSQL Downloads','url':'https://www.postgresql.org/download/'}
        good = {'title':'UUID functions','url':'https://www.postgresql.org/docs/18/functions-uuid.html','snippet':'uuidv7 uses a shift interval'}
        self.assertEqual(filter_experimental(query,[weak,good]),([good],1))
        old = {'title':'2023年前三季度可再生能源','url':'https://example.com/2023/','snippet':'新增装机'}
        current = {'title':'2026年前三季度可再生能源','url':'https://example.com/2026/','snippet':'新增装机'}
        self.assertEqual(filter_experimental('2026年前三季度 可再生能源 新增装机 国家能源局',[old,current]),([current],1))
        self.assertEqual(filter_experimental('国家能源局 可再生能源 新增装机',[{'title':'2026 Calendar','url':'https://example.com'}]),([],1))
        rust = {'title':'Rust Mutex','url':'https://doc.rust-lang.org/','snippet':'recover PoisonError with into_inner'}
        self.assertEqual(filter_experimental('Rust std Mutex PoisonError into_inner',[rust]),([rust],0))
        self.assertEqual(filter_experimental('2026年 可再生能源',[{'title':'可再生能源发布','url':'https://example.com/202309/t20230915_1.html'}]),([],1))
        self.assertEqual(filter_experimental('2026年10月 制造业 PMI',[{'title':'2026年9月制造业PMI','url':'https://example.com'}]),([],1))
        self.assertEqual(filter_experimental('2026年前三季度 可再生能源',[{'title':'2026年上半年可再生能源','url':'https://example.com'}]),([],1))
        self.assertEqual(filter_experimental('Node.js LTS',[{'title':'Nodejs LTS','url':'https://nodejs.org'}])[1],0)

    def test_free_benchmark_guard_rejects_paid_dispatch_before_transport(self):
        def faulty(args,config,budget):
            return b.search.request_api('deepseek',{},'synthetic-only',budget=budget)
        with patch.object(b.search,'run_search',side_effect=faulty), \
                patch.object(b.search.urllib.request,'build_opener',side_effect=AssertionError('must not reach transport')):
            with self.assertRaisesRegex(AssertionError,'rejected a keyed API'):
                b.run_cell({'id':'one','query':'test'},'free',{'providers':{}},b.search.RequestBudget(2))

    def test_explicit_browser_diagnostic_is_free_and_not_in_default_modes(self):
        case = {'id':'doc','query':'test'}
        browser = b.query_args(case,'browser')
        self.assertEqual(browser.provider,'browser'); self.assertEqual(browser.strategy,'free')
        self.assertEqual(b.execute({'cases':[case]})['modes'],['free','deepseek','smart'])

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
