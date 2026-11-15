"""Official documentation and lightweight public HTML search invariants."""
import json
import os
from pathlib import Path
import tempfile
import unittest
import urllib.error
import io
from unittest.mock import patch

from test_search import x, args, QueueTransport
from documentation_search import OfficialDocs, MDN
from public_access import pause_status
from public_providers import PUBLIC_REGISTRY


def index():
    return {'docnames': ['library/asyncio-task', 'library/asyncio-eventloop'],
            'titles': ['Coroutines and tasks', 'Event loop'],
            'terms': {'asyncio': [0, 1], 'taskgroup': 0}, 'titleterms': {},
            'objects': {'asyncio': [[0, 0, 1, '', 'TaskGroup']] +
                        [[1, 0, 1, '', 'unrelated' + str(i)] for i in range(60)]}}


def wire(data):
    return ('Search.setIndex(' + json.dumps(data) + ');').encode()


def html_rows():
    return '''<ul class="result"><li class="res-list"><h3 class="res-title">
    <a data-mdurl="https://www.cninfo.com.cn/report.html">新能源车购置税公告</a></h3>
    <p><span data-result-summary>新能源汽车 购置税</span></p></li>
    <li class="res-list"><h3 class="res-title"><a data-mdurl="https://evil.example/cninfo.com.cn">新能源汽车</a></h3></li></ul>'''.encode()


class KeylessSearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'XDG_CACHE_HOME': self.tmp.name}, clear=True)
        self.env.start()

    def tearDown(self):
        self.env.stop(); self.tmp.cleanup()

    def test_official_index_query_stays_local_and_symbols_beat_common_modules(self):
        source = OfficialDocs()
        query = args(query='Python asyncio TaskGroup exception cancellation documentation', site='docs.python.org')
        payload = source.search_payload(query)
        req = source.build_request(payload, 'synthetic-do-not-send', 'test')
        self.assertEqual(req.full_url, 'https://docs.python.org/3/searchindex.js')
        self.assertNotIn('TaskGroup', req.full_url)
        self.assertIsNone(req.get_header('Authorization'))
        rows, meta = source.normalize_search(source.decode_response(wire(index())), query)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]['url'].endswith('asyncio-task.html#asyncio.TaskGroup'))
        self.assertEqual(rows[0]['content_kind'], 'documentation_index')
        self.assertFalse(meta['query_sent_to_source'])
        self.assertFalse(meta['page_body_read'])
        self.assertNotIn('objects', meta['provider_metadata'])
        self.assertIsNone(rows[0]['published_at'])

    def test_legacy_sphinx_index_is_supported_without_executing_javascript(self):
        data = index(); data['objects'] = {'asyncio': {'TaskGroup': [0, 0, 1, '']}}
        rows, _ = OfficialDocs().normalize_search(data, args(query='asyncio.TaskGroup', site='docs.python.org'))
        self.assertIn('#asyncio.TaskGroup', rows[0]['url'])
        for raw in (b'Search.setIndex({});doSomething()', b'<html>login</html>', b'evil()'):
            with self.assertRaises(x.SearchError): OfficialDocs().decode_response(raw)

    def test_documentation_scope_and_index_paths_are_validated(self):
        source = OfficialDocs()
        with self.assertRaises(x.SearchError): source.search_payload(args(site='evil.example'))
        self.assertEqual(source.search_payload(args(site='docs.python.org', language='en')), {'site': 'docs.python.org'})
        for provider in (source, MDN()):
            with self.assertRaises(x.SearchError): provider.search_payload(args(site='docs.python.org' if provider.name == 'docs' else 'developer.mozilla.org', language='zh'))
        for value in ('../../private', 'https://evil.example/a'):
            data = index(); data['docnames'][0] = value
            with self.assertRaises(x.SearchError):
                source.normalize_search(data, args(query='TaskGroup', site='docs.python.org'))
        data = index(); data['terms']['taskgroup'] = [-1]
        with self.assertRaises(x.SearchError):
            source.normalize_search(data, args(query='TaskGroup', site='docs.python.org'))

    def test_static_index_suffixes_preserve_parameter_matches(self):
        data = {'docnames': ['reference/api/pandas.merge'], 'titles': ['pandas.merge'],
                'terms': {'merg': 0, 'one_to_on': 0}, 'titleterms': {}, 'objects': {}}
        rows, _ = OfficialDocs().normalize_search(data, args(query='pandas merge validate one_to_one documentation', site='pandas.pydata.org'))
        self.assertEqual(len(rows), 1)
        self.assertIn('one_to_one', rows[0]['snippet'])

    def test_version_and_release_queries_do_not_silently_use_the_current_index(self):
        with self.assertRaises(x.SearchError):
            OfficialDocs().search_payload(args(query='Python 3.11 TaskGroup', site='docs.python.org'))
        with patch('search_routing.browser_available', return_value=False):
            route = x.plan(args(query='Python 3.15 latest release official', intent='reference'), {'providers': {}}, x.credential)
        self.assertNotIn('docs', route['candidates'])

    def test_real_fetch_arguments_do_not_enter_documentation_query_inference(self):
        arguments = x.parser().parse_args(['fetch', 'https://example.com/article'])
        route = x.plan(arguments, {'providers': {}}, x.credential, fetch=True)
        self.assertEqual(route['candidates'][0], 'jina')
        self.assertNotIn('docs', route['candidates'])

    def test_mdn_maps_original_links_and_rejects_other_destinations(self):
        source = MDN()
        good = {'documents': [{'title': 'AbortController', 'mdn_url': '/en-US/docs/Web/API/AbortController', 'summary': 'Controller'}]}
        rows, _ = source.normalize(good, 5)
        self.assertEqual(rows[0]['url'], 'https://developer.mozilla.org/en-US/docs/Web/API/AbortController')
        self.assertEqual(rows[0]['snippet'], 'Controller')
        self.assertEqual(rows[0]['content'], '')
        for path in ('//evil.example/', 'https://evil.example/', '/api/private'):
            good['documents'][0]['mdn_url'] = path
            with self.assertRaises(x.SearchError): source.normalize(good, 5)

    def test_so360_organic_cards_exclude_ads_hidden_content_and_navigation(self):
        source = PUBLIC_REGISTRY['so360']
        body = b'''<a data-mdurl="https://navigation.example">Navigation</a>
        <div id="m-spread-left">''' + html_rows() + b'''</div>
        <div hidden>''' + html_rows() + b'''</div>''' + html_rows()
        rows, _ = source.normalize(source.decode_response(body), 5)
        self.assertEqual(len(rows), 2)
        self.assertIsNone(rows[0]['published_at'])
        self.assertEqual(rows[0]['snippet'], '新能源汽车 购置税')
        self.assertNotIn('so.com/link', rows[0]['url'])
        with self.assertRaises(x.SearchError): source.decode_response(b'<html>loading</html>')
        self.assertEqual(source.decode_response('抱歉，未找到相关搜索结果'.encode())['results'], [])

    def test_both_mcp_sources_disabled_reaches_http_without_paid_or_browser_calls(self):
        config = {'providers': {p: {'api_key': 'synthetic-only'} for p in x.PROVIDERS},
                  'search_preferences': {'disabled_providers': ['exa-free', 'parallel-free']}}
        transport = QueueTransport(html_rows())
        with patch('search_routing.browser_available', return_value=True), \
                patch.object(x, 'run_browser_search', side_effect=AssertionError('browser started')), \
                patch.object(x.urllib.request, 'build_opener', return_value=transport):
            out = x.run_search(args(query='新能源汽车 购置税', site='cninfo.com.cn', strategy='free'), config)
        self.assertTrue(out['ok'])
        self.assertEqual(out['providers'], ['so360'])
        self.assertEqual(len(out['results']), 1)
        self.assertEqual(len(transport.requests), 1)
        self.assertIsNone(transport.requests[0].get_header('Authorization'))
        self.assertEqual(out['execution_summary']['keyed_api_attempts'], 0)

    def test_free_default_uses_parallel_and_targeted_docs_before_exa(self):
        config = {'providers': {}}
        with patch('search_routing.browser_available', return_value=True):
            route = x.plan(args(strategy='free'), config, x.credential)
            self.assertEqual(route['execution_candidates'], ['parallel-free', 'exa-free', 'so360'])
            for site in ('docs.python.org', 'pandas.pydata.org', 'docs.sqlalchemy.org'):
                route = x.plan(args(query='TaskGroup', site=site, strategy='free'), config, x.credential)
                self.assertEqual(route['execution_candidates'][0], 'docs')
            route = x.plan(args(query='AbortController', platform='mdn'), config, x.credential)
            self.assertEqual(route['execution_candidates'][0], 'mdn')
            route = x.plan(args(query='中文 新闻', site='example.com', strategy='free'), config, x.credential)
            self.assertEqual(route['execution_candidates'], ['parallel-free', 'exa-free', 'so360'])

    def test_official_index_succeeds_when_both_mcp_sources_are_disabled(self):
        transport = QueueTransport(wire(index()))
        config = {'providers': {}, 'search_preferences': {'disabled_providers': ['exa-free', 'parallel-free']}}
        with patch('search_routing.browser_available', return_value=False), \
                patch.object(x.urllib.request, 'build_opener', return_value=transport):
            out = x.run_search(args(query='TaskGroup', site='docs.python.org', strategy='free'), config)
        self.assertTrue(out['ok'])
        self.assertEqual(out['providers'], ['docs'])
        self.assertEqual(out['budget']['attempts'], 1)

    def test_so360_verification_pauses_source_without_retrying(self):
        transport = QueueTransport('安全验证 请输入验证码'.encode())
        with self.assertRaises(x.SearchError) as caught:
            x.request_api('so360', {'q': 'query'}, '', retries=2, opener=transport)
        self.assertEqual(caught.exception.code, 'access_challenge')
        self.assertEqual(len(transport.requests), 1)
        self.assertIsNotNone(pause_status('so360'))
        route = x.plan(args(strategy='free'), {'providers': {}}, x.credential)
        self.assertNotIn('so360', route['candidates'])

    def test_so360_rejects_city_overlap_without_the_requested_museum_branch(self):
        from search_quality import filter_site_html
        weak = {'title': '上海三日游', 'url': 'https://www.xiaohongshu.com/explore/123', 'snippet': '上海工艺美术博物馆'}
        good = {**weak, 'title': '上海博物馆东馆参观', 'snippet': '东馆预约'}
        rows, dropped = filter_site_html('上海博物馆 东馆', [weak, good])
        self.assertEqual(rows, [good]); self.assertEqual(dropped, 1)

    def test_so360_captcha_redirect_pauses_without_following_or_leaking_tokens(self):
        error = urllib.error.HTTPError('https://www.so.com/s', 302, '',
                                      {'Location': 'https://qcaptcha.so.com/?tk=synthetic-private'}, io.BytesIO())
        transport = QueueTransport(error)
        with self.assertRaises(x.SearchError) as caught:
            x.request_api('so360', {'q': 'query'}, '', retries=2, opener=transport)
        self.assertEqual(caught.exception.code, 'access_challenge')
        self.assertEqual(len(transport.requests), 1)
        self.assertIsNotNone(pause_status('so360'))
        self.assertNotIn('synthetic-private', str(caught.exception))


if __name__ == '__main__': unittest.main()
