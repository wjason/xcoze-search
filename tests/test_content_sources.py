"""Fixed feeds, finite policy search and original-post reading; offline fixtures only."""
from contextlib import redirect_stdout
import http.client
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from test_search import x, args, QueueTransport
from content_sources import FEEDS, GovCN, CommunityReader, html_text, parse_timestamp
import public_access

RSS = b'''<rss version="2.0"><channel><title>Fixture</title>
<item><title>Energy policy</title><link>https://example.com/a</link><description>&lt;p&gt;Notice&lt;/p&gt;</description><pubDate>Wed, 4 Nov 2026 16:30:00 GMT</pubDate></item>
<item><title>Duplicate</title><link>https://example.com/a#section</link></item>
<item><title>Unknown date</title><link>https://example.com/b</link></item></channel></rss>'''
ATOM = b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Updated only</title><link href="https://example.com/a"/><updated>2026-11-05T00:00:00Z</updated></entry></feed>'''
GOV = [{"TITLE": "Energy policy", "URL": "https://www.gov.cn/zhengce/example.htm", "DOCRELPUBTIME": "2026-11-01"},
       {"TITLE": "Other", "URL": "https://www.gov.cn/zhengce/other.htm", "DOCRELPUBTIME": "2026-10-01"}]
TOPIC = {"id": 123, "title": "Example topic", "reply_count": 5, "post_stream": {"posts": [
    {"post_number": 2, "cooked": "This is a reply"},
    {"post_number": 1, "cooked": '<p>Original <a href="https://example.com/docs">docs</a></p><pre>  code\n    indented</pre>'}]}}


class ContentSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"XDG_CACHE_HOME": self.tmp.name}, clear=True); self.env.start()
    def tearDown(self): self.env.stop(); self.tmp.cleanup()

    def test_feed_one_keyless_http_no_config_browser_or_semantic_search(self):
        transport = QueueTransport(RSS)
        with patch.object(x.urllib.request, "build_opener", return_value=transport), \
             patch.object(x, "read_config", side_effect=AssertionError("no config")), \
             patch.object(x, "run_browser_search", side_effect=AssertionError("no browser")), \
             redirect_stdout(io.StringIO()) as output:
            self.assertEqual(x.main(["feed", "--source", "cns-scroll", "--query", "energy", "--count", "5"]), 0)
        data = json.loads(output.getvalue())
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["budget"]["attempts"], 1)
        self.assertEqual(data["execution_summary"]["keyed_api_attempts"], 0)
        self.assertTrue(data["metadata"]["window_only"])
        self.assertFalse(data["metadata"]["historical_search"])
        self.assertEqual(data["results"][0]["content_kind"], "feed_excerpt")
        self.assertEqual(data["results"][0]["content"], "")
        self.assertIsNone(transport.requests[0].get_header("Authorization"))
        self.assertIsNone(transport.requests[0].get_header("Cookie"))

    def test_date_filter_uses_beijing_day_unknown_dates_excluded_and_urls_deduplicated(self):
        a=x.parser().parse_args(["feed","--source","bbc-world","--start-date","2026-11-05","--end-date","2026-11-05"])
        with patch.object(x.urllib.request,"build_opener",return_value=QueueTransport(RSS)):
            d=x.run_feed(a,x.request_api,x.VERSION)
        self.assertEqual(len(d["results"]),1)
        self.assertEqual(d["metadata"]["duplicate_urls_removed"],1)
        self.assertEqual(d["metadata"]["unknown_dates_excluded"],1)
        self.assertEqual(d["results"][0]["published_at"],"2026-11-04T16:30:00+00:00")
        self.assertIsNone(parse_timestamp("Wed, 4 Nov 2026 16:30:00"))

    def test_atom_updated_is_not_publication_and_html_or_doctype_is_not_empty_feed(self):
        p=FEEDS["cns-scroll"]
        row=p.records(p.decode_response(ATOM))[0]
        self.assertIsNone(row["published_at"])
        self.assertIsNotNone(row["provider_fields"]["updated_at"])
        for raw in (b'<html>Log in</html>', b'<!DOCTYPE rss><rss><channel/></rss>', '<!DOCTYPE rss><rss><channel/></rss>'.encode('utf-16'), b'<?xml version="1.0" encoding="unknown-encoding"?><rss><channel/></rss>'):
            with self.assertRaises(x.SearchError):p.decode_response(raw)
        self.assertEqual(p.records(p.decode_response(b'<rss><channel/></rss>')),[])

    def test_invalid_date_is_rejected_before_feed_http(self):
        with patch.object(x,"request_api",side_effect=AssertionError("no network")):
            a=x.parser().parse_args(["feed","--source","cns-scroll","--start-date","2026-02-30"])
            with self.assertRaises(x.SearchError):x.run_feed(a,x.request_api,x.VERSION)

    def test_govcn_native_first_with_key_and_local_filter_does_not_relax_dates(self):
        a=args(query="Energy",platform="govcn",strategy="free",start_date="2026-11-01",end_date="2026-11-02")
        cfg={"providers":{"deepseek":{"api_key":"synthetic-only"}}}
        route=x.plan(a,cfg,x.credential)
        self.assertEqual(route["candidates"][0],"govcn")
        with patch.object(x.urllib.request,"build_opener",return_value=QueueTransport(GOV)):
            d=x.run_search(a,cfg)
        self.assertEqual(len(d["results"]),1)
        self.assertEqual(d["results"][0]["content_kind"],"official_policy_index")
        self.assertEqual(d["results"][0]["rank"],1)
        self.assertEqual(d["requests"][0]["source_row_count"],2)
        with self.assertRaises(x.SearchError):GovCN().records({"items":[{**GOV[0],"URL":"https://evil.example/a"}]})

    def test_community_reader_prefers_native_and_only_original_not_first_returned_reply(self):
        a=args(url="https://discuss.python.org/t/slug/123",strategy="free",max_characters=1000)
        self.assertEqual(x.plan(a,{"providers":{}},x.credential,fetch=True)["candidates"][0],"community")
        with patch.object(x.urllib.request,"build_opener",return_value=QueueTransport(TOPIC)):
            d=x.run_fetch(a,{"providers":{}})
        self.assertEqual(d["provider"],"community")
        self.assertIn("Original",d["content"])
        self.assertIn("https://example.com/docs",d["content"])
        self.assertIn("    indented",d["content"])
        self.assertNotIn("This is a reply",d["content"])
        self.assertTrue(d["comments_fetched"])
        self.assertFalse(d["comments_included"])
        self.assertEqual(d["source_attached_replies"],1)
        self.assertFalse(d["thread_complete"])
        self.assertEqual(d["content_kind"],"community_original_post")

    def test_community_rejects_reply_targets_arbitrary_hosts_ports_and_wrong_topic_identity(self):
        p=CommunityReader()
        for url in ("https://discuss.python.org/t/123/2","https://discuss.python.org/t/slug/123/2",
                    "https://discuss.python.org/t/123#post_2","https://discuss.python.org/t/123?api_key=no",
                    "https://evil.example/t/123","https://discuss.python.org:444/t/123"):
            with self.assertRaises(x.SearchError):p.fetch_payload(args(url=url))
        self.assertEqual(p.fetch_payload(args(url="https://discuss.python.org/t/123/1"))["id"],"123")
        with self.assertRaises(x.SearchError):p.normalize_fetch(TOPIC,"https://discuss.python.org/t/124")
        hidden=json.loads(json.dumps(TOPIC));hidden['post_stream']['posts'][1]['hidden']=True
        with self.assertRaises(x.SearchError):p.normalize_fetch(hidden,"https://discuss.python.org/t/123")

    def test_v2ex_body_is_original_plain_text_and_cutoff_is_explicit(self):
        raw=[{"id":123,"title":"Example","content":"x"*2000,"replies":20}]
        a=args(provider="community",url="https://www.v2ex.com/t/123",max_characters=1000)
        with patch.object(x.urllib.request,"build_opener",return_value=QueueTransport(raw)):
            d=x.run_fetch(a,{"providers":{}})
        self.assertEqual(len(d["content"]),1000)
        self.assertTrue(d["truncated"])
        self.assertFalse(d["comments_fetched"])

    def test_access_denial_stops_reader_fanout_and_cooldown_is_per_host(self):
        denied=urllib.error.HTTPError("",403,"",{},io.BytesIO())
        transport=QueueTransport(denied)
        a=args(url="https://www.v2ex.com/t/123",strategy="free")
        with patch.object(x.urllib.request,"build_opener",return_value=transport):
            d=x.run_fetch(a,{"providers":{}})
            later=x.run_fetch(a,{"providers":{}})
        self.assertFalse(d["ok"])
        self.assertEqual(d["budget"]["attempts"],1)
        self.assertEqual(later["budget"]["attempts"],0)
        self.assertEqual(len(transport.requests),1)
        self.assertIsNone(public_access.pause_status("community-python"))
        self.assertIsNotNone(public_access.pause_status("community-v2ex"))

    def test_incomplete_http_body_is_a_counted_redacted_network_failure(self):
        with patch.object(x.urllib.request,"build_opener",return_value=QueueTransport(http.client.IncompleteRead(b'private partial body'))):
            with self.assertRaises(x.SearchError) as caught:x.request_api('cns-scroll',{},'',retries=0)
        self.assertEqual(caught.exception.code,'network_error')
        self.assertEqual(caught.exception.attempts,1)
        self.assertNotIn('private',str(caught.exception))

    def test_keyless_401_does_not_blame_a_missing_or_invalid_user_key(self):
        denied=urllib.error.HTTPError('',401,'',{},io.BytesIO())
        with patch.object(x.urllib.request,'build_opener',return_value=QueueTransport(denied)):
            with self.assertRaises(x.SearchError) as caught:x.request_api('jina_fetch',{'url':'https://example.com'},'',retries=0)
        self.assertEqual(caught.exception.category,'access')
        self.assertIn('no user API key was sent',str(caught.exception))


if __name__ == '__main__':unittest.main()

class ChinaOfficialIndexTests(unittest.TestCase):
    def test_official_html_parsing_and_literal_window(self):
        from public_providers import PUBLIC_REGISTRY
        fixtures = {
            'ndrc': ('https://www.ndrc.gov.cn/xxgk/zcfb/tz/202611/t20261104_1408591.html', '生态政策', '2026/11/04'),
            'nbs': ('https://www.stats.gov.cn/sj/zxfb/202611/t20261103_1965738.html', '价格数据', '2026-11-04'),
            'nea': ('http://www.nea.gov.cn/20261102/af04409304d44bfb89c9880f55b70dff/c.html', '能源公告', '2026-11-02'),
        }
        for name, (url, title, day) in fixtures.items():
            with self.subTest(source=name):
                p = PUBLIC_REGISTRY[name]
                html = ('<html><ul><li><a href="' + url + '">' + title + '</a><div><ul><li>'
                        '<a href="https://evil.example/202611/t20261104_1.html">相关解读</a></li></ul></div>'
                        '<span>' + day + '</span></li></ul></html>').encode()
                raw = p.decode_response(html)
                args_match = x.parser().parse_args(['search', title[:2], '--provider', name, '--strategy', 'free'])
                rows, meta = p.normalize_search(raw, args_match)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]['title'], title)
                self.assertEqual(rows[0]['published_at'], day.replace('/', '-'))
                self.assertTrue(rows[0]['url'].startswith('https://'))
                self.assertEqual(rows[0]['content_kind'], 'official_index')
                self.assertFalse(meta['historical_search'])
                self.assertNotIn('list_items', meta.get('provider_metadata', {}))
                args_miss = x.parser().parse_args(['search', '不存在', '--provider', name, '--strategy', 'free'])
                self.assertEqual(p.normalize_search(raw, args_miss)[0], [])
                with self.assertRaises(x.SearchError): p.records(p.decode_response(b'<html>unrelated</html>'))

    def test_missing_display_date_is_not_inferred_from_url(self):
        from public_providers import PUBLIC_REGISTRY
        p = PUBLIC_REGISTRY['nea']
        html = b'<html><li><a href="https://www.nea.gov.cn/20261102/af04409304d44bfb89c9880f55b70dff/c.html">Energy</a></li></html>'
        rows = p.records(p.decode_response(html))
        self.assertIsNone(rows[0]['published_at'])

class ChinaPublicBatchTests(unittest.TestCase):
    def test_eleven_public_index_shapes_and_safe_source_urls(self):
        from public_providers import PUBLIC_REGISTRY
        cases = {
            'miit': ('/zwgk/zcwj/wjfb/tz/art/2026/art_0e076dfcb9854ee2be816c49b053184e.html', '工业标准', '2026-11-03', 'li'),
            'mee': ('/ywdt/xwfb/202610/t20261029_1184815.shtml', '环境质量', '2026-10-29', 'li'),
            'mem': ('/xw/yjglbgzdt/202610/t20261022_736602.shtml', '自然灾害', '2026-10-22', 'li'),
            'pbc': ('/diaochatongjisi/116219/116225/2026110416143085995/index.html', '金融统计', '2026-11-04', 'tr'),
            'ggzy': ('/information/deal/html/a/610000/9001/20261105/0061ee692d32122e479e8bedf64f9774a964.html', '项目公告', '2026-11-05', 'li'),
            'mofcom': ('/syxwfb/art/2026/art_2d11cc8218d248a3b4c98ea465781427.html', '商务资讯', '2026-11-01', 'li'),
            'csrc': ('/csrc/c100028/c7668092/content.shtml', '证券监管', '2026-11-01', 'li'),
            'ccgp': ('/cggg/dfgg/zbgg/202611/t20261105_27630401.htm', '采购项目', '2026-11-05', 'li'),
            'cas': ('//www.cas.cn/../../syky/202611/t20261105_5123509.shtml', '科学发现', '2026-11-05', 'li'),
            'cgs': ('/ywdt/ddyw/202611/t20261104_871443.html', '地质调查', '2026-11-04', 'li'),
            'xinhua': ('/20261105/17dfbf4604f14ddc8ce41be818763986/c.html', '中国新闻', '2026-11-05', 'li'),
        }
        for name, (path, title, day, tag) in cases.items():
            with self.subTest(source=name):
                p = PUBLIC_REGISTRY[name]
                html = ('<html><' + tag + '><a href="' + path + '">' + title + '<span>' + day + '</span></a></' + tag + '></html>').encode()
                row = p.records(p.decode_response(html))[0]
                self.assertEqual(row['title'], title)
                self.assertEqual(row['published_at'], day)
                self.assertEqual(urllib.parse.urlsplit(row['url']).hostname, p.content_host)
                self.assertNotIn('/../', row['url'])
                self.assertEqual(row['content_kind'], 'official_index')
                self.assertFalse(p.capabilities()['historical_search'])
                with self.assertRaises(x.SearchError):
                    p.records(p.decode_response(b'<html><li><a href="https://evil.example/fake">fake</a></li></html>'))

    def test_hk_data_is_a_feed_not_full_catalog_search(self):
        p = FEEDS['hk-data']
        self.assertEqual(p.endpoint, 'https://data.gov.hk/filestore/feeds/data_rss_en.xml')
        rows = p.records(p.decode_response(RSS))
        self.assertEqual(rows[0]['content_kind'], 'feed_excerpt')
        self.assertFalse(p.supports_search)

class ChinaIndexScopedRoutingTests(unittest.TestCase):
    def test_public_index_scopes_are_declared_without_claiming_native_access(self):
        from search_routing import PLATFORMS, platform_catalog
        expected = {'china-data':'data.stats.gov.cn', 'cma-data':'data.cma.cn', 'china-weather':'weather.com.cn',
                    'cninfo':'cninfo.com.cn', 'sse':'sse.com.cn', 'szse':'szse.cn', 'bse':'bse.cn',
                    'china-standards':'openstd.samr.gov.cn', 'china-laws':'flk.npc.gov.cn', 'cnsa':'cnsa.gov.cn',
                    'scidb':'scidb.cn', 'ceic':'ceic.ac.cn', 'nmefc':'nmefc.cn', 'hko':'hko.gov.hk'}
        for name, domain in expected.items():
            with self.subTest(platform=name):
                self.assertEqual(PLATFORMS[name], domain)
                row = platform_catalog(name)['platforms'][0]
                self.assertEqual(row['coverage'], 'public_index_only')
                self.assertIsNone(row['native_provider'])
                self.assertFalse(row['live_verified'])
                route = x.plan(args(query='test', platform=name, strategy='free'), {'providers': {}}, x.credential)
                self.assertFalse(any(x.ALL_REGISTRY[p].requires_key for p in route['candidates']))
                site_route = x.plan(args(query='test', site=domain, strategy='free'), {'providers': {}}, x.credential)
                self.assertEqual(route['candidates'], site_route['candidates'])
                self.assertEqual(route['payloads'], site_route['payloads'])
