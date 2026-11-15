"""Native documentation and Chinese site-search contracts, without network or keys."""
import copy
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from test_search import x, args, QueueTransport
from native_search import NavigationDocs, GoDocs, CninfoSearch, StatisticsSearch
from public_access import pause_status


KUBE = b'''<a href="/docs/concepts/configuration/manage-resources-containers/">Resource Management for Pods and Containers</a>
<a href="/docs/concepts/services-networking/network-policies/">Network Policies</a>
<a href="https://evil.example/docs/concepts/">Network Policy ingress</a>'''
RUST = b'''<a href="sync/struct.OnceLock.html">sync::OnceLock</a>
<a href="sync/struct.Mutex.html">sync::Mutex</a>
<a href="sync/poison/struct.Mutex.html">sync::poison::Mutex</a>'''
GO = b'''<div class="SearchSnippet"><div><h2><a href="/context#WithCancelCause" data-test-id="snippet-title">WithCancelCause</a></h2>
<span class="go-Chip">standard library</span></div></div>
<div class="SearchSnippet"><a href="/github.com/example/pkg#WithCancelCause" data-test-id="snippet-title">WithCancelCause</a><p>standard library compatibility</p></div>
<div class="SearchSnippet"><a href="/fakepkg#WithCancelCause" data-test-id="snippet-title">WithCancelCause</a></div>'''
CNINFO = {'totalRecordNum': 1, 'announcements': [{'announcementTitle': '<em>某公司</em>：2024年度报告',
          'adjunctUrl': 'finalpage/2025-04-03/123456.PDF', 'announcementTime': 1743609600000,
          'secCode': '600000', 'secName': '某公司', 'announcementId': '123456'}]}
STATS = {'ok': True, 'totalHits': 1, 'resultDocs': [{'data': {
    'titleO': '2026年三季度国内生产总值初步核算', 'url': 'https://www.stats.gov.cn/sj/test.html',
    'summary': '前三季度<em>国内生产总值</em>数据', 'docDate': '2026-10-20', 'myValues': {'unused': 'large raw object'}}}]}


class NativeSearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'XDG_CACHE_HOME': self.tmp.name}, clear=True); self.env.start()

    def tearDown(self):
        self.env.stop(); self.tmp.cleanup()

    def test_navigation_uses_published_links_and_never_fabricates_method_anchors(self):
        p = NavigationDocs()
        rows, meta = p.normalize_search(p.decode_response(RUST), args(query='Rust std OnceLock get_or_init documentation', site='doc.rust-lang.org'))
        self.assertEqual([r['url'] for r in rows], ['https://doc.rust-lang.org/std/sync/struct.OnceLock.html'])
        self.assertFalse(meta['query_sent_to_source'])
        self.assertFalse(meta['page_body_read'])
        self.assertIsNone(rows[0]['published_at'])
        self.assertEqual(rows[0]['content_kind'], 'documentation_index')
        rows, _ = p.normalize_search(p.decode_response(RUST), args(query='Mutex', site='doc.rust-lang.org'))
        self.assertTrue(rows[0]['url'].endswith('/sync/struct.Mutex.html'))

    def test_kubernetes_compound_symbol_and_unknown_topic(self):
        p = NavigationDocs(); raw = p.decode_response(KUBE)
        rows, _ = p.normalize_search(raw, args(query='Kubernetes NetworkPolicy ingress egress', site='kubernetes.io'))
        self.assertIn('network-policies', rows[0]['url'])
        self.assertFalse(any('evil.example' in r['url'] for r in rows))
        rows, _ = p.normalize_search(raw, args(query='unrelated_unique_token', site='kubernetes.io'))
        self.assertEqual(rows, [])
        with self.assertRaises(x.SearchError): p.normalize_search(p.decode_response(b'<html>empty shell</html>'), args(query='CPU', site='kubernetes.io'))

    def test_documentation_scope_versions_and_unsupported_filters_fail_before_requests(self):
        for source, site in ((NavigationDocs(), 'kubernetes.io'), (GoDocs(), 'pkg.go.dev')):
            for kwargs in ({'site': 'evil.example'}, {'site': site, 'query': 'v1.34 version docs'}, {'site': site, 'start_date': '2026-11-01'}, {'site': site, 'language': 'zh'}):
                with self.subTest(source=source.name, kwargs=kwargs), self.assertRaises(x.SearchError): source.search_payload(args(**kwargs))

    def test_go_symbol_keeps_package_and_receiver(self):
        p = GoDocs()
        cases = [('Go context WithCancelCause Cause pkg.go.dev', 'context.WithCancelCause'),
                 ('Go net/http Server Shutdown documentation', 'http.Server.Shutdown'),
                 ('Go encoding/json Decoder DisallowUnknownFields documentation', 'json.Decoder.DisallowUnknownFields'),
                 ('Go errors Is As documentation', 'errors.Is'), ('http.Server.Shutdown', 'http.Server.Shutdown')]
        for query, expected in cases:
            with self.subTest(query=query): self.assertEqual(p.build_search(args(query=query))['q'], expected)

    def test_go_requires_standard_library_badge_and_rejects_empty_shells(self):
        p = GoDocs(); rows, _ = p.normalize(p.decode_response(GO), 5)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['url'], 'https://pkg.go.dev/context#WithCancelCause')
        self.assertEqual(p.decode_response(b'<h1>No symbols found</h1>')['results'], [])
        with self.assertRaises(x.SearchError): p.decode_response(b'<script>SearchSnippet</script>')

    def test_cninfo_preserves_disclosure_date_and_pdf_identity(self):
        p = CninfoSearch(); rows, meta = p.normalize(CNINFO, 5)
        self.assertEqual(rows[0]['published_at'], '2025-04-03')
        self.assertEqual(rows[0]['provider_fields']['security_code'], '600000')
        self.assertEqual(rows[0]['content'], '')
        self.assertFalse(meta['provider_metadata']['pagination_fetched'])
        payload = p.build_search(args(query='上市公司 年度报告'))
        self.assertEqual(payload['searchkey'], '年度报告')
        self.assertNotIn('fund', payload['type'].split(','))
        self.assertEqual(p.normalize({'totalRecordNum': 0, 'announcements': None}, 5)[0], [])
        for path in ('https://evil.example/a.PDF', 'finalpage/2025-04-03/../private.PDF'):
            data = copy.deepcopy(CNINFO); data['announcements'][0]['adjunctUrl'] = path
            with self.assertRaises(x.SearchError): p.normalize(data, 5)

    def test_statistics_publication_date_is_not_statistical_period_or_raw_backend_object(self):
        p = StatisticsSearch(); rows, meta = p.normalize(STATS, 5)
        self.assertEqual(rows[0]['published_at'], '2026-10-20')
        self.assertEqual(rows[0]['snippet'], '前三季度国内生产总值数据')
        self.assertNotIn('myValues', str(rows) + str(meta))
        for field, value in (('url', 'https://evil.example/stats.gov.cn'), ('docDate', '2026-99-99')):
            data = copy.deepcopy(STATS); data['resultDocs'][0]['data'][field] = value
            with self.assertRaises(x.SearchError): p.normalize(data, 5)
        with self.assertRaises(x.SearchError): p.normalize({'ok': False, 'msg': 'private diagnostic'}, 5)

    def test_statistics_month_uses_title_period_not_comparison_text_or_release_day(self):
        data = copy.deepcopy(STATS)
        data['resultDocs'][0]['data'].update(titleO='2026年10月份居民消费价格', summary='与2026年9月份相比', docDate='2026-11-09')
        correct = copy.deepcopy(data['resultDocs'][0]); correct['data'].update(titleO='2026年9月份居民消费价格', docDate='2026-10-14')
        unrelated = copy.deepcopy(correct); unrelated['data']['titleO'] = '2026年9月份能源生产情况'
        data['resultDocs'].extend([unrelated, correct])
        rows, meta = StatisticsSearch().normalize_search(data, args(query='2026年9月 居民消费价格 2026年10月14日', count=1))
        self.assertEqual(rows[0]['title'], '2026年9月份居民消费价格')
        self.assertEqual(rows[0]['published_at'], '2026-10-14')
        self.assertEqual(meta['excluded_conflicting_title_period_count'], 1)

    def test_all_four_adapters_send_no_credentials_and_keep_fixed_destinations(self):
        for p, site in ((NavigationDocs(), 'doc.rust-lang.org'), (GoDocs(), 'pkg.go.dev'), (CninfoSearch(), 'cninfo.com.cn'), (StatisticsSearch(), 'stats.gov.cn')):
            query = args(query='OnceLock' if p.name == 'site-docs' else 'context.WithCancelCause' if p.name == 'go-docs' else '年度报告', site=site)
            payload = p.search_payload(query); req = p.build_request(payload, 'synthetic-private-key', 'test')
            self.assertIsNone(req.get_header('Authorization'))
            self.assertNotIn('synthetic-private-key', req.full_url + str(req.data))
            if p.name == 'site-docs': self.assertEqual(req.full_url, 'https://doc.rust-lang.org/std/all.html')
            if p.name == 'nbs-search':
                self.assertEqual(req.get_method(), 'POST')
                self.assertIn(b'siteCode=bm36000002', req.data)

    def test_auto_native_paths_work_with_both_mcp_routes_disabled_and_all_paid_keys_present(self):
        config = {'providers': {p: {'api_key': 'synthetic-only'} for p in x.PROVIDERS},
                  'search_preferences': {'disabled_providers': ['exa', 'exa-free', 'parallel-free'], 'browser': 'off'}}
        for platform, source, response in (('rust-docs', 'site-docs', RUST), ('kubernetes-docs', 'site-docs', KUBE),
                                           ('go-docs', 'go-docs', GO), ('cninfo', 'cninfo', CNINFO), ('nbs', 'nbs-search', STATS)):
            query = 'OnceLock' if platform == 'rust-docs' else 'NetworkPolicy' if platform == 'kubernetes-docs' else 'context.WithCancelCause' if platform == 'go-docs' else '年度报告'
            with self.subTest(platform=platform), patch.object(x.urllib.request, 'build_opener', return_value=QueueTransport(response)), \
                    patch.dict(os.environ, {'XDG_CACHE_HOME': self.tmp.name + '/' + platform}), \
                    patch.object(x, 'run_browser_search', side_effect=AssertionError('browser')):
                out = x.run_search(args(query=query, platform=platform, strategy='free'), config)
            self.assertTrue(out['ok']); self.assertEqual(out['providers'], [source])
            self.assertEqual(out['execution_summary']['keyed_api_attempts'], 0)

    def test_native_access_denial_is_paused_and_does_not_expose_service_body(self):
        transport = QueueTransport(urllib.error.HTTPError('', 403, '', {}, io.BytesIO(b'synthetic-private')))
        with self.assertRaises(x.SearchError) as caught: x.request_api('cninfo', {'searchkey': 'query'}, '', retries=2, opener=transport)
        self.assertEqual(len(transport.requests), 1)
        self.assertNotIn('synthetic-private', str(caught.exception))
        self.assertIsNotNone(pause_status('cninfo'))
        route = x.plan(args(platform='cninfo', strategy='free'), {'providers': {}}, x.credential)
        self.assertNotIn('cninfo', route['candidates'])


if __name__ == '__main__': unittest.main()
