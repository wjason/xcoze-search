"""Public energy/procurement contracts, including deliberately untrusted responses."""
import copy
import io
import json
import os
import tempfile
import unittest
import urllib.error
import urllib.parse
from unittest.mock import patch

from test_search import x, args, QueueTransport
from industry_search import EnergyArchive, TradingSearch, CSGNotices, classify
from public_access import pause_status

ENERGY = {'datasource': [
    {'showTitle': '新型储能政策', 'publishUrl': '../20250912/a/c.html', 'publishTime': '2025-09-12 10:00:00', 'summary': ''},
    {'title': '<a>旧储能政策</a>', 'publishUrl': 'http://zfxxgk.nea.gov.cn/auto/a.htm', 'publishTime': '2024-01-01 00:00:00'},
    {'title': '储能外部链接', 'publishUrl': 'https://evil.example/nea.gov.cn/a.htm', 'publishTime': '2025-01-01'},
]}
TRADING = {'code': 200, 'data': {'records': [
    {'title': '储能设备采购公告', 'url': '/information/deal/html/a/440000/0201/20261101/a.html',
     'publishTime': '2026-11-01', 'province': '440000', 'provinceText': '广东省',
     'businessTypeText': '政府采购', 'informationType': '0201', 'informationTypeText': '采购/资审公告',
     'tenderProjectCode': None, 'deadline': None},
], 'total': 1, 'current': 1, 'pages': 1}}
CSG = b'''<html><ul><li><span>2026-11-01</span><a class="Blue">Example Grid</a>
<a href="/zbgg/123.jhtml">Storage tender</a></li></ul></html>'''


class IndustrySearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'XDG_CACHE_HOME': self.tmp.name}, clear=True); self.env.start()

    def tearDown(self): self.env.stop(); self.tmp.cleanup()

    def test_energy_uses_published_snapshot_filters_dates_and_keeps_unknown_effective_date(self):
        p = EnergyArchive()
        rows, meta = p.normalize_search(ENERGY, args(query='储能', start_date='2025-01-01', end_date='2025-12-31'))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['published_at'], '2025-09-12')
        self.assertEqual(rows[0]['url'], 'https://www.nea.gov.cn/20250912/a/c.html')
        self.assertFalse(meta['archive_complete']); self.assertFalse(meta['query_sent_to_source'])
        self.assertFalse(rows[0]['provider_fields']['page_body_read'])
        rows, _ = p.normalize_search(ENERGY, args(query='旧储能'))
        self.assertTrue(rows[0]['url'].startswith('http://zfxxgk.nea.gov.cn/'))
        self.assertEqual(p.build_search(args(query='全社会用电量'))['section'], 'releases')
        with self.assertRaises(x.SearchError): p.normalize_search({'datasource': [{}]}, args())

    def test_all_requests_have_fixed_destinations_and_never_send_keys(self):
        for p, query in ((EnergyArchive(), args()), (TradingSearch(), args()), (CSGNotices(), args())):
            req = p.build_request(p.search_payload(query), 'synthetic-secret', 'test')
            self.assertNotIn('synthetic-secret', req.full_url + str(req.data))
            self.assertIsNone(req.get_header('Authorization'))
            self.assertIsNone(req.get_header('Cookie'))
        p = EnergyArchive()
        req = p.build_request(p.build_search(args(query='private-query', energy_section='releases')), '', 'test')
        self.assertNotIn('private-query', req.full_url)
        with self.assertRaises(x.SearchError): p.build_request({'section': 'https://evil.example'}, '', 'test')

    def test_energy_statistical_title_variant_keeps_the_original_date_constraint(self):
        raw = {'datasource': [{'title': '2025年1-9月份全国电力工业统计数据',
               'publishUrl': 'https://www.nea.gov.cn/20251026/a/c.html', 'publishTime': '2025-10-26'}]}
        p = EnergyArchive(); query = args(query='全国电力统计数据', energy_section='releases', start_date='2025-10-01', end_date='2025-10-31')
        rows, meta = p.normalize_search(raw, query)
        self.assertEqual(len(rows), 1); self.assertTrue(meta['query_rewritten_for_matching'])
        self.assertEqual(query.query, '全国电力统计数据')
        query.start_date = '2026-10-01'; query.end_date = '2026-10-31'
        self.assertEqual(p.normalize_search(raw, query)[0], [])

    def test_trading_custom_dates_source_region_and_stage_are_not_silently_dropped(self):
        p = TradingSearch(); a = args(query='储能', business='government', notice_type='tender',
                                     start_date='2026-10-01', end_date='2026-11-16', region='广东省')
        payload = p.search_payload(a)
        self.assertEqual((payload['DEAL_TIME'], payload['DEAL_STAGE'], payload['DEAL_PROVINCE']), ('06', '0201', '440000'))
        self.assertEqual(payload['TIMEBEGIN'], '2026-10-01')
        req = p.build_request(payload, '', 'test')
        self.assertEqual(req.get_method(), 'POST')
        self.assertEqual(urllib.parse.parse_qs(req.data.decode())['FINDTXT'], ['储能'])
        for fields in ({'start_date': '2026-10-01'}, {'notice_type': 'tender'},
                       {'business': 'engineering', 'notice_type': 'contract'}, {'region': '虚构省'},
                       {'trading_source': 'central', 'region': '广东'}, {'page': 101}):
            with self.subTest(fields=fields), self.assertRaises(x.SearchError): p.search_payload(args(**fields))

    def test_trading_checks_server_filters_and_drops_fulltext_only_matches(self):
        p = TradingSearch(); raw = copy.deepcopy(TRADING)
        for changes in ({'title': '粮食仓储能力提升项目'}, {'province': '110000'}, {'publishTime': '2025-11-01'},
                        {'informationType': '0202'}, {'businessTypeText': '工程建设'}):
            raw['data']['records'].append({**raw['data']['records'][0], **changes})
        rows, meta = p.normalize_search(raw, args(query='储能', region='广东', business='government', notice_type='tender',
                                                start_date='2026-10-01', end_date='2026-11-16'))
        self.assertEqual(len(rows), 1); self.assertEqual(meta['excluded_by_constraints'], 5)
        fields = rows[0]['provider_fields']
        self.assertIsNone(fields['deadline']); self.assertIsNone(fields['buyer']); self.assertIsNone(fields['open_for_bidding'])
        self.assertFalse(fields['deadline_verified']); self.assertFalse(meta['pagination_fetched'])

    def test_trading_external_links_invalid_dates_and_challenges_fail_without_leaking(self):
        p = TradingSearch()
        with self.assertRaises(x.SearchError) as wrong_page:
            p.normalize_search(TRADING, args(page=2))
        self.assertEqual(wrong_page.exception.code, 'constraint_not_applied')
        for changes in ({'url': 'https://evil.example/ggzy.gov.cn'}, {'publishTime': '2026-99-01'}):
            raw = copy.deepcopy(TRADING); raw['data']['records'][0].update(changes)
            with self.assertRaises(x.SearchError): p.normalize_search(raw, args())
        for code in (829, 800):
            raw = {'code': code, 'captchaToken': 'synthetic-private-token', 'captchaImage': 'private-image'}
            t = QueueTransport(raw)
            with patch.dict(os.environ, {'XDG_CACHE_HOME': self.tmp.name + '/' + str(code)}), self.assertRaises(x.SearchError) as caught:
                x.request_api('ggzy-search', p.build_search(args()), '', opener=t, retries=2)
            self.assertEqual(len(t.requests), 1)
            self.assertNotIn('synthetic-private-token', str(caught.exception))

    def test_csg_preserves_list_dates_publisher_and_bounded_page(self):
        html = '''<html><ul><li><span>2026-11-01</span><span class="num"><i>1</i></span><a class="Blue">云南电网公司</a>
        <a href="/zbhxrgs/123.jhtml">储能项目中标公告</a></li>
        <li><span>2026-11-01</span><a href="/zbhxrgs/124.jhtml">储能项目中标候选人公示</a></li>
        <li><a href="https://evil.example/zbgg/125.jhtml">储能招标公告</a></li></ul></html>'''
        p = CSGNotices(); rows, meta = p.normalize_search(p.decode_response(html), args(query='储能', notice_type='award', page=2))
        self.assertEqual(len(rows), 1); self.assertEqual(rows[0]['provider_fields']['publisher'], '云南电网公司')
        self.assertEqual(rows[0]['published_at'], '2026-11-01')
        self.assertEqual(rows[0]['provider_fields']['notice_stage'], 'award')
        self.assertFalse(meta['site_keyword_search']); self.assertFalse(meta['pagination_fetched'])
        req = p.build_request(p.build_search(args(page=2)), '', 'test')
        self.assertEqual(req.full_url, 'https://www.bidding.csg.cn/zbgg/index_2.jhtml')
        self.assertFalse(p.normalize_search(p.decode_response(html), args(query='不存在', notice_type='award'))[0])
        for body in ('<html>访问过于频繁 synthetic-private</html>', '<html>empty shell</html>'):
            with self.assertRaises(x.SearchError): p.decode_response(body)

    def test_notice_classification_does_not_mislabel_awards_or_cancellations(self):
        for title, expected in (('储能项目公开招标中标公告', 'award'), ('采购项目中标候选人公示', 'candidate'),
                                ('采购项目招标中止公告', 'cancel'), ('招标公告澄清', 'correction')):
            self.assertEqual(classify(title), expected)

    def test_platform_routes_use_independent_public_adapters_with_mcp_and_paid_sources_blocked(self):
        config = {'providers': {p: {'api_key': 'synthetic-only'} for p in x.PROVIDERS},
                  'search_preferences': {'disabled_providers': ['exa', 'exa-free', 'parallel-free'], 'browser': 'off'}}
        for platform, provider, response, extra in (
            ('nea', 'nea-archive', ENERGY, {}),
            ('government-procurement', 'ggzy-search', TRADING, {'notice_type': 'tender'}),
            ('ggzy', 'ggzy-search', TRADING, {})):
            with self.subTest(platform=platform), patch.object(x.urllib.request, 'build_opener', return_value=QueueTransport(response)), \
                    patch.dict(os.environ, {'XDG_CACHE_HOME': self.tmp.name + '/' + platform}), \
                    patch.object(x, 'run_browser_search', side_effect=AssertionError('browser')):
                out = x.run_search(args(query='储能', platform=platform, strategy='free', **extra), config)
            self.assertTrue(out['ok']); self.assertEqual(out['providers'], [provider])
            self.assertEqual(out['execution_summary']['keyed_api_attempts'], 0)
        route = x.plan(args(query='储能', platform='government-procurement', notice_type='tender'), config, x.credential)
        self.assertEqual(route['payloads']['ggzy-search']['DEAL_CLASSIFY'], '02')
        with self.assertRaises(x.SearchError): x.plan(args(platform='government-procurement', business='engineering'), config, x.credential)

    def test_public_denial_pauses_source_and_automatic_planning_skips_it(self):
        t = QueueTransport(urllib.error.HTTPError('', 403, '', {}, io.BytesIO(b'synthetic-private')))
        with self.assertRaises(x.SearchError): x.request_api('csg', {'channel': 'zbgg', 'page': 1}, '', opener=t, retries=2)
        self.assertEqual(len(t.requests), 1); self.assertIsNotNone(pause_status('csg'))
        route = x.plan(args(query='储能', platform='csg', strategy='free'), {'providers': {}}, x.credential)
        self.assertNotIn('csg', route['candidates'])
        t = QueueTransport('<html>您的访问过于频繁 synthetic-private</html>'.encode())
        with self.assertRaises(x.SearchError) as caught: x.request_api('ccgp', {}, '', opener=t, retries=2)
        self.assertEqual(caught.exception.code, 'access_challenge')
        self.assertNotIn('synthetic-private', str(caught.exception)); self.assertIsNotNone(pause_status('ccgp'))


if __name__ == '__main__': unittest.main()
