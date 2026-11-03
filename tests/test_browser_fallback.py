"""Quota failure injection, strict free routing, lazy browsers and bounded local execution."""
from contextlib import redirect_stdout
import io
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import urllib.error

from test_search import x, args, ds, QueueTransport
from test_routing import EXA, RSS
import browser_search as browser
import public_access

QUOTA = {'jsonrpc': '2.0', 'id': 1, 'result': {'isError': True, 'content': [
    {'type': 'text', 'text': 'Exa free MCP rate limit reached. synthetic-private-body'}]}}
BAD_RSS = RSS.replace(b'Python', b'Windows Help').replace(b'python.org', b'microsoft.com')
CHALLENGE = b'<form id="challenge-form">verify you are human</form>'
PAGE = {'url': 'https://www.bing.com/search?q=Python', 'title': 'Python search', 'challenge': False, 'text': 'Results',
        'results': [{'title': 'Python asyncio TaskGroup documentation', 'url': 'https://docs.python.org/3/library/asyncio-task.html', 'snippet': 'TaskGroup cancellation'}]}


def browser_result(*a, **kw):
    return {'results': PAGE['results'], 'browser_engine': 'bing', 'browser_navigation_attempts': 1,
            'browser_commands': 4, 'browser_http_requests': None, 'browser_cleanup_verified': True}


class FallbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'XDG_CONFIG_HOME': self.tmp.name, 'XDG_CACHE_HOME': self.tmp.name}, clear=True)
        self.env.start()
        self.available = patch('search_routing.browser_available', return_value=True); self.available.start()
        self.config = {'schema_version': 2, 'providers': {p: {'api_key': 'synthetic-only'} for p in x.PROVIDERS}}
    def tearDown(self):
        self.available.stop(); self.env.stop(); self.tmp.cleanup()

    def test_healthy_free_api_never_starts_browser_even_with_all_paid_keys(self):
        transport = QueueTransport(EXA)
        with patch.object(x.urllib.request, 'build_opener', return_value=transport), patch.object(x, 'run_browser_search') as local:
            out = x.run_search(args(strategy='free'), self.config)
        self.assertTrue(out['ok']); self.assertEqual(out['providers'], ['exa-free']); local.assert_not_called()
        self.assertEqual(out['budget']['attempts'], 1)
        self.assertIsNone(transport.requests[0].get_header('Authorization'))

    def test_healthy_smart_primary_uses_configured_api_and_no_browser(self):
        transport = QueueTransport(ds())
        with patch.object(x.urllib.request, 'build_opener', return_value=transport), patch.object(x, 'run_browser_search') as local:
            out = x.run_search(args(), self.config)
        self.assertTrue(out['ok']); self.assertEqual(out['providers'], ['deepseek']); local.assert_not_called()

    def test_exa_quota_and_irrelevant_feed_reach_browser_without_any_paid_http(self):
        for message in ('Daily request limit reached', 'Insufficient credits', 'Too many requests'):
            with self.assertRaises(x.SearchError) as caught:
                x.get_provider('exa-free').decode_response(json.dumps({'jsonrpc':'2.0','id':1,'result':{'isError':True,'content':[{'type':'text','text':message}]}}).encode())
            self.assertEqual(caught.exception.code, 'source_rate_limited')
        transport = QueueTransport(QUOTA, BAD_RSS)
        with patch.object(x.urllib.request, 'build_opener', return_value=transport), patch.object(x, 'run_browser_search', side_effect=browser_result) as local:
            out = x.run_search(args(query='Python asyncio TaskGroup', strategy='free'), self.config)
        self.assertTrue(out['ok']); self.assertTrue(out['partial'])
        self.assertEqual(out['providers'], ['exa-free', 'bing', 'browser'])
        self.assertEqual(out['budget']['attempts'], 2)
        self.assertEqual(out['requests'][-1]['attempts'], 0)
        self.assertEqual(out['requests'][-1]['browser_navigation_attempts'], 1)
        self.assertEqual(out['errors'][0]['code'], 'source_rate_limited')
        self.assertIsNone(out['errors'][0]['http_status'])  # MCP application error is not a wire HTTP 429.
        self.assertNotIn('synthetic-private-body', str(out))
        self.assertEqual(local.call_count, 1)
        for request in transport.requests:
            self.assertIsNone(request.get_header('Authorization'))
            self.assertIn(__import__('urllib.parse', fromlist=['urlsplit']).urlsplit(request.full_url).hostname,
                          ('mcp.exa.ai', 'www.bing.com'))
        self.assertIsNotNone(public_access.pause_status('exa-free'))

    def test_quota_pause_skips_next_exa_request_and_expiry_allows_probe(self):
        clock = [100.0]
        with patch.object(public_access.time, 'time', side_effect=lambda: clock[0]):
            transport = QueueTransport(QUOTA, BAD_RSS)
            with patch.object(x.urllib.request, 'build_opener', return_value=transport), patch.object(x, 'run_browser_search', side_effect=browser_result):
                x.run_search(args(query='Python asyncio TaskGroup', strategy='free'), self.config)
            route = x.plan(args(strategy='free'), self.config, x.credential)
            self.assertNotIn('exa-free', route['candidates'])
            self.assertEqual(route['skipped_unavailable'][0]['retry_after_seconds'], 900)
            transport = QueueTransport(BAD_RSS, CHALLENGE)
            with patch.object(x.urllib.request, 'build_opener', return_value=transport), patch.object(x, 'run_browser_search', side_effect=browser_result):
                out = x.run_search(args(query='Python asyncio TaskGroup', strategy='free'), self.config)
            self.assertEqual(out['providers'], ['bing', 'duckduckgo', 'browser'])
            clock[0] = 1001
            self.assertIn('exa-free', x.plan(args(strategy='free'), self.config, x.credential)['candidates'])

    def test_http_429_honors_retry_after_without_retry_or_raw_error_body(self):
        error = urllib.error.HTTPError('', 429, 'private', {'Retry-After': '120'}, io.BytesIO(b'private'))
        transport = QueueTransport(error); budget = x.RequestBudget(3)
        with patch.object(x.urllib.request, 'build_opener', return_value=transport):
            with self.assertRaises(x.SearchError) as caught:
                x.request_api('exa-free', {'tool': 'web_search_exa', 'arguments': {}}, '', retries=2, budget=budget)
        self.assertEqual(len(transport.requests), 1); self.assertEqual(budget.used, 1)
        self.assertGreater(public_access.pause_status('exa-free')['retry_after_seconds'], 115)
        self.assertNotIn('private', str(caught.exception))

    def test_reference_api_evidence_is_retained_if_complement_exhausted_no_browser(self):
        transport = QueueTransport(ds(), QUOTA)
        with patch.object(x.urllib.request, 'build_opener', return_value=transport), patch.object(x, 'run_browser_search') as local:
            out = x.run_search(args(query='Python documentation'), self.config)
        self.assertTrue(out['ok']); self.assertTrue(out['partial']); local.assert_not_called()
        self.assertEqual(out['providers'], ['deepseek', 'exa-free'])

    def test_browser_absent_or_disabled_does_not_install_or_reach_paid_services(self):
        for browser_flags, present in (({'browser': 'off'}, True), ({}, False)):
            with self.subTest(flags=browser_flags), tempfile.TemporaryDirectory() as cache, \
                    patch.dict(os.environ, {'XDG_CACHE_HOME': cache}), \
                    patch('search_routing.browser_available', return_value=present):
                transport = QueueTransport(QUOTA, BAD_RSS, CHALLENGE)
                with patch.object(x.urllib.request, 'build_opener', return_value=transport), patch.object(x, 'run_browser_search') as local:
                    out = x.run_search(args(query='Python asyncio TaskGroup', strategy='free', **browser_flags), self.config)
                self.assertFalse(out['ok']); local.assert_not_called()
                self.assertTrue(all(not x.get_provider(p).requires_key for p in out['providers']))
                self.assertEqual(out['budget']['attempts'], 3)

    def test_source_http_and_time_limits_can_prevent_browser_launch(self):
        for flags in ({'max_sources': 1}, {'max_requests': 1}):
            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as cache, patch.dict(os.environ, {'XDG_CACHE_HOME': cache}):
                transport = QueueTransport(QUOTA)
                with patch.object(x.urllib.request, 'build_opener', return_value=transport), patch.object(x, 'run_browser_search') as local:
                    out = x.run_search(args(strategy='free', **flags), self.config)
                self.assertFalse(out['ok']); local.assert_not_called()
        with patch.object(x.time, 'monotonic', side_effect=[0, 50]), patch.object(x, 'run_browser_search') as local:
            out = x.run_search(args(strategy='free', max_seconds=1), self.config)
        self.assertFalse(out['ok']); local.assert_not_called()

    def test_explicit_free_conflict_and_explicit_source_never_expand(self):
        all_route = x.plan(args(provider='all'), self.config, x.credential)
        self.assertEqual(all_route['execution_candidates'], all_route['candidates'])
        self.assertEqual(len(all_route['execution_candidates']), 6)
        with self.assertRaises(x.SearchError): x.plan(args(provider='deepseek', strategy='free'), self.config, x.credential)
        with self.assertRaises(x.SearchError): x.plan(args(provider='browser', browser='off'), self.config, x.credential)
        transport = QueueTransport(QUOTA)
        with patch.object(x.urllib.request, 'build_opener', return_value=transport), patch.object(x, 'run_browser_search') as local:
            out = x.run_search(args(provider='exa-free'), self.config)
        self.assertFalse(out['ok']); local.assert_not_called()

    def test_api_timeouts_are_capped_and_browser_preferences_do_not_touch_keys(self):
        def fake(*a, **kw):
            self.assertLessEqual(kw['timeout'], 8)
            return EXA['result']['structuredContent'], 1
        with patch.object(x, 'request_api', side_effect=fake), patch.object(x, 'run_browser_search') as local:
            x.run_search(args(strategy='free', timeout=30), self.config)
        local.assert_not_called()
        x.save_config(self.config)
        with redirect_stdout(io.StringIO()): self.assertEqual(x.main(['preferences', '--browser', 'off']), 0)
        self.assertEqual(x.read_config()['providers'], self.config['providers'])
        self.assertEqual(x.preferences(x.read_config())['browser'], 'off')
        self.config['default_provider'] = 'browser'
        self.assertEqual(x.plan(args(), self.config, x.credential)['execution_candidates'][0], 'browser')
        with patch.object(x, 'run_browser_search', side_effect=browser_result), patch.object(x, 'request_api') as api:
            out = x.run_search(args(), self.config)
        self.assertTrue(out['ok']); api.assert_not_called()


class LocalBrowserTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        minimum = {k: v for k, v in os.environ.items() if k in ('PATH', 'SystemRoot', 'SYSTEMROOT', 'WINDIR', 'HOME', 'USERPROFILE', 'TEMP', 'TMP')}
        self.env = patch.dict(os.environ, {**minimum, 'XDG_CACHE_HOME': self.tmp.name}, clear=True); self.env.start()
    def tearDown(self):
        self.env.stop(); self.tmp.cleanup()

    def test_private_lazy_session_fixed_commands_sanitized_environment_and_cleanup(self):
        calls = []
        def command(argv, **kw):
            calls.append((argv, kw))
            config = Path(argv[argv.index('--config') + 1])
            self.assertEqual(json.loads(config.read_text()), {})
            self.assertNotIn('synthetic-secret', str(kw['env']))
            self.assertNotIn('AGENT_BROWSER_AUTO_CONNECT', kw['env'])
            if 'open' in argv: return {'url': PAGE['url'], 'title': PAGE['title']}
            if 'eval' in argv: return {'result': PAGE}
            return {}
        with patch.object(browser.shutil, 'which', return_value='/safe/agent-browser'), \
                patch.object(browser, 'command', side_effect=command), \
                patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'synthetic-secret', 'EXA_API_KEY': 'synthetic-secret',
                                       'AGENT_BROWSER_PROVIDER': 'remote', 'AGENT_BROWSER_AUTO_CONNECT': '1'}):
            raw = browser.search({'query': 'Python $(touch /tmp/never-executed)', 'count': 3}, engine='bing')
        self.assertEqual(len(calls), 5); self.assertIn('close', calls[-1][0])
        self.assertTrue(raw['browser_cleanup_verified'])
        self.assertEqual(raw['browser_navigation_attempts'], 1)
        self.assertIsNone(raw['browser_http_requests'])
        self.assertTrue(calls[0][0][calls[0][0].index('--session') + 1].startswith('xcoze-search-'))
        self.assertEqual(calls[3][1]['input_text'], browser.EXTRACT)
        self.assertTrue(calls[1][1]['input_text'].startswith('setTimeout(() => location.assign('))
        self.assertNotIn('$(touch /tmp/never-executed)', calls[1][1]['input_text'])
        self.assertEqual(set(raw['browser_stage_timings_ms']), {'launch','navigate','wait','extract','close'})

    def test_challenge_stops_cools_down_and_never_switches_engine(self):
        calls = []
        def command(argv, **kw):
            calls.append(argv)
            if 'eval' in argv and kw.get('input_text') == browser.EXTRACT:
                return {'result': {**PAGE, 'url': 'https://www.google.com/sorry/index', 'results': [], 'challenge': True}}
            return {}
        with patch.object(browser.shutil, 'which', return_value='/safe/agent-browser'), patch.object(browser, 'command', side_effect=command):
            with self.assertRaises(x.SearchError) as caught:
                browser.search({'query': 'Python', 'count': 3}, engine='google')
            self.assertEqual(caught.exception.code, 'access_challenge')
            self.assertEqual(len(calls), 5)
            with self.assertRaises(x.SearchError) as paused:
                browser.search({'query': 'Python', 'count': 3}, engine='bing')
            self.assertEqual(paused.exception.code, 'source_cooldown')
            self.assertEqual(len(calls), 5)
        self.assertIsNotNone(public_access.pause_status('browser'))

    def test_unwrap_valid_links_and_reject_empty_shell_and_non_public_links(self):
        self.assertEqual(browser.unwrap_url('https://www.google.com/url?q=https%3A%2F%2Fpython.org'), 'https://python.org')
        self.assertEqual(browser.unwrap_url('http://127.0.0.1/private'), '')
        with self.assertRaises(x.SearchError): browser.parse_page({**PAGE, 'results': []}, 'bing')
        with self.assertRaises(x.SearchError): browser.parse_page({**PAGE, 'url': 'https://evil.example'}, 'bing')
        with self.assertRaises(x.SearchError) as caught: browser.parse_page({**PAGE, 'challenge': True}, 'bing')
        self.assertEqual(caught.exception.code, 'access_challenge')
        with self.assertRaises(x.SearchError) as caught:
            browser.parse_page({**PAGE, 'title': '安全验证', 'text': '请完成验证', 'results': []}, 'bing')
        self.assertEqual(caught.exception.code, 'access_challenge')

    def test_bounded_subprocess_failure_and_timeout_do_not_echo_output(self):
        env = browser.browser_environment()
        value = browser.command([sys.executable, '-c', 'import json; print(json.dumps({"success":True,"data":{"ok":1}}))'], env=env, deadline=time.monotonic()+5)
        self.assertEqual(value, {'ok': 1})
        with self.assertRaises(x.SearchError) as caught:
            browser.command([sys.executable, '-c', 'print("synthetic-secret")'], env=env, deadline=time.monotonic()+5)
        self.assertNotIn('synthetic-secret', str(caught.exception))
        with self.assertRaises(x.SearchError) as caught:
            browser.command([sys.executable, '-c', 'import time; time.sleep(5)'], env=env, deadline=time.monotonic()+.1)
        self.assertEqual(caught.exception.code, 'browser_timeout')

    def test_hidden_rows_wait_timeout_is_diagnosed_on_same_page(self):
        calls = []
        def fake(argv, **kw):
            calls.append(argv)
            if 'wait' in argv:
                raise x.SearchError('browser_timeout', 'Synthetic wait timeout')
            if 'eval' in argv and kw.get('input_text') == browser.EXTRACT:
                return {'result': {**PAGE, 'results': [], 'hidden_count': 10}}
            return {}
        with patch.object(browser.shutil, 'which', return_value='/safe/agent-browser'), patch.object(browser, 'command', side_effect=fake):
            with self.assertRaises(x.SearchError) as caught:
                browser.search({'query':'Python asyncio', 'count':3}, engine='bing')
        self.assertEqual(caught.exception.code, 'browser_results_hidden')
        self.assertEqual(caught.exception.browser_failure_stage, 'extract')
        self.assertEqual(caught.exception.browser_navigation_attempts, 1)
        self.assertTrue(caught.exception.browser_cleanup_verified)
        self.assertEqual(len(calls), 5)
        self.assertIsNotNone(public_access.pause_status('browser'))

    def test_360_target_urls_exclude_engine_cards_and_nonpublic_destinations(self):
        data = {**PAGE, 'url': 'https://www.so.com/s?q=Python', 'results': [
            *PAGE['results'], {'title':'AI answer', 'url':'https://ai.so.com/answer'},
            {'title':'Ad', 'url':'https://e.so.com/click'}, {'title':'Internal','url':'http://127.0.0.1/'}]}
        rows = browser.parse_page(data, '360')
        self.assertEqual(len(rows), 1); self.assertEqual(rows[0]['url'], PAGE['results'][0]['url'])
        with self.assertRaises(x.SearchError): browser.parse_page({**data,'url':'https://www.so.com/account'}, '360')
        with self.assertRaises(x.SearchError): browser.parse_page({**data,'url':'https://['}, '360')
        self.assertEqual(x.parser().parse_args(['search','query']).browser_engine, '360')

    def test_browser_chinese_mismatch_rejected_inside_cooldown_and_without_retry(self):
        from search_quality import obvious_mismatch
        self.assertTrue(obvious_mismatch('新能泰山 最新公告', [{'title':'ChatGPT release','url':'https://github.com/example'}], include_cjk=True))
        self.assertFalse(obvious_mismatch('新能泰山 最新公告', [{'title':'新能泰山三季报','url':'https://example.com'}], include_cjk=True))
        self.assertFalse(obvious_mismatch('上海天气', [{'title':'上海市天气预报','url':'https://example.com'}], include_cjk=True))
        def fake(argv, **kw):
            if kw.get('input_text') == browser.EXTRACT:
                return {'result': {**PAGE, 'results':[{'title':'ChatGPT news','url':'https://example.com'}]}}
            return {}
        with patch.object(browser.shutil, 'which', return_value='/safe/agent-browser'), patch.object(browser, 'command', side_effect=fake):
            with self.assertRaises(x.SearchError) as caught:
                browser.search({'query':'新能泰山 最新公告','count':3},engine='bing')
        self.assertEqual(caught.exception.code, 'irrelevant_results')
        self.assertIsNotNone(public_access.pause_status('browser'))

    def test_cli_timeout_and_navigation_errors_keep_stage_without_upstream_text(self):
        for detail, code in [('Wait timed out after 6000ms synthetic-secret','browser_timeout'),
                             ('Navigation failed: private-url','browser_navigation_failed')]:
            program = 'import json; print(json.dumps(' + repr({'success':False,'error':detail}) + '))'
            with self.assertRaises(x.SearchError) as caught:
                browser.command([sys.executable,'-c',program],env=browser.browser_environment(),deadline=time.monotonic()+5)
            self.assertEqual(caught.exception.code,code)
            self.assertNotIn('synthetic-secret',str(caught.exception));self.assertNotIn('private-url',str(caught.exception))

    def test_explicit_no_match_is_not_a_hidden_shell_or_failure_cooldown(self):
        page = {**PAGE, 'url':'https://www.so.com/s?q=test', 'results':[],
                'candidate_count':0, 'hidden_count':0, 'explicit_no_matches':True}
        self.assertEqual(browser.parse_page(page,'360'), [])
        def fake(argv, **kw):
            return {'result':page} if kw.get('input_text') == browser.EXTRACT else {}
        with patch.object(browser.shutil,'which',return_value='/safe/agent-browser'), patch.object(browser,'command',side_effect=fake):
            raw = browser.search({'query':'unlikely topic','count':3})
        self.assertEqual(raw['results'],[]); self.assertTrue(raw['browser_explicit_no_matches'])
        self.assertIsNone(public_access.pause_status('browser'))
        with self.assertRaises(x.SearchError): browser.parse_page({**page,'explicit_no_matches':False},'360')
        with self.assertRaises(x.SearchError): browser.parse_page({**page,'url':PAGE['url']},'bing')

    def test_live_evaluator_requires_explicit_opt_in_and_disables_only_named_sources(self):
        path = Path(__file__).resolve().parents[1] / 'scripts/evaluate_browser.py'
        spec = importlib.util.spec_from_file_location('evaluate_browser',path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with patch.object(sys,'argv',['evaluate_browser.py','--output','unused.json']), \
                patch.object(module,'execute',side_effect=AssertionError('no network')), \
                patch('sys.stderr',io.StringIO()), self.assertRaises(SystemExit) as caught:
            module.main()
        self.assertEqual(caught.exception.code,2)
        config = {'providers':{}, 'search_preferences':{'strategy':'free','disabled_providers':['exa-free','bing']}}
        with patch('search_routing.browser_available',return_value=True):
            route = x.plan(args(strategy='free'),config,x.credential)
        self.assertEqual(route['execution_candidates'],['duckduckgo','browser'])

    def test_fault_evaluator_default_is_fully_simulated_and_records_zero_paid_calls(self):
        path = Path(__file__).resolve().parents[1] / 'scripts/evaluate_fallback.py'
        spec = importlib.util.spec_from_file_location('evaluate_fallback', path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with patch.object(browser, 'command', side_effect=AssertionError('no real browser')):
            report = module.execute()
        self.assertTrue(report['ok'])
        self.assertFalse(report['live_api_requested']); self.assertFalse(report['live_browser_requested'])
        self.assertEqual(report['healthy_api_browser_starts'], 0)
        self.assertTrue(report['simulated_recovery_passed'])
        self.assertIsNone(report['live_browser_usable'])
        self.assertTrue(all(c['execution_summary']['keyed_api_attempts'] == 0 for c in report['cases']))


if __name__ == '__main__': unittest.main()
