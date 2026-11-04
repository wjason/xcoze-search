"""Offline feed contracts: no credentials, history or keyword-search substitution."""
from contextlib import redirect_stdout
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from test_search import x, args, QueueTransport
from public_trends import TRENDING, TREND_PROVIDERS, run_trending
import public_access


BILI = {"code": 0, "timestamp": 1793829600, "list": [
    {"keyword": "ad", "show_name": "Paid", "stat_datas": {"is_commercial": "1"}},
    {"keyword": "Python 教程", "show_name": "Python 教程", "heat_score": 20, "pos": 2,
     "stat_datas": {"is_commercial": "0"}}]}
ZHIHU = {"data": [{"target": {"title_area": {"text": "A question"},
    "link": {"url": "https://www.zhihu.com/question/123"},
    "excerpt_area": {"text": "<p>An excerpt</p>"}, "metrics_area": {"text": "100 万热度"}},
    "feed_specific": {"answer_count": 5}}]}
V2EX = [{"id": 123, "title": "A topic", "created": 1767225600, "replies": 8,
         "node": {"name": "python"}, "content": "Must not be returned as a read body",
         "member": {"email": "not-shipped@example.com"}}]
FIXTURES = {"bilibili": BILI, "zhihu": ZHIHU, "v2ex": V2EX}


class TrendingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"XDG_CACHE_HOME": self.tmp.name}, clear=True)
        self.env.start()

    def tearDown(self):
        self.env.stop(); self.tmp.cleanup()

    def test_each_feed_one_keyless_request_no_config_no_browser_no_cookie(self):
        for platform, fixture in FIXTURES.items():
            with self.subTest(platform=platform):
                transport = QueueTransport(fixture)
                with patch.object(x.urllib.request, "build_opener", return_value=transport), \
                     patch.object(x, "read_config", side_effect=AssertionError("no config")), \
                     patch.object(x, "credential", side_effect=AssertionError("no key")), \
                     patch.object(x, "run_browser_search", side_effect=AssertionError("no browser")), \
                     redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(x.main(["trending", "--platform", platform]), 0)
                data = json.loads(out.getvalue())
                self.assertEqual(data["operation"], "trending")
                self.assertEqual(data["budget"]["attempts"], 1)
                self.assertEqual(data["execution_summary"]["keyed_api_attempts"], 0)
                self.assertEqual(data["execution_summary"]["browser_navigation_attempts"], 0)
                self.assertFalse(data["facts_verified"])
                self.assertFalse(data["metadata"]["snapshot_complete"])
                self.assertIsNone(data["metadata"]["cost"])
                self.assertEqual(data["results"][0]["content_kind"], "trending_item")
                self.assertEqual(data["results"][0]["content"], "")
                req = transport.requests[0]
                self.assertIsNone(req.get_header("Authorization"))
                self.assertIsNone(req.get_header("Cookie"))

    def test_bilibili_ads_removed_without_reranking_or_inventing_publication(self):
        rows, meta = TRENDING["bilibili"].normalize(BILI, 10)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["rank"], 2)
        self.assertIsNone(rows[0]["published_at"])
        self.assertEqual(rows[0]["provider_fields"]["heat_score"], 20)
        self.assertEqual(rows[0]["provider_fields"]["destination_kind"], "platform_search")
        self.assertIn("keyword=Python", rows[0]["url"])
        self.assertEqual(meta["upstream_updated_at"], 1793829600)

    def test_zhihu_question_excerpt_is_not_answer_or_arbitrary_url(self):
        p = TRENDING["zhihu"]
        rows, _ = p.normalize(ZHIHU, 2)
        self.assertEqual(rows[0]["snippet"], "An excerpt")
        self.assertFalse(rows[0]["provider_fields"]["answers_fetched"])
        self.assertIsNone(rows[0]["published_at"])
        malformed = json.loads(json.dumps(ZHIHU))
        malformed["data"][0]["target"]["link"]["url"] = "https://evil.example/question/123"
        with self.assertRaises(x.SearchError): p.normalize(malformed, 2)

    def test_v2ex_created_time_and_reply_count_do_not_claim_body_or_replies_read(self):
        p = TRENDING["v2ex"]
        rows, _ = p.normalize(p.decode_response(json.dumps(V2EX).encode()), 10)
        row = rows[0]
        self.assertEqual(row["published_at"], "2026-01-01T00:00:00+00:00")
        self.assertFalse(row["provider_fields"]["body_fetched"])
        self.assertFalse(row["provider_fields"]["replies_fetched"])
        self.assertNotIn("member", row["provider_fields"])
        self.assertNotIn("Must not be returned", json.dumps(rows))

    def test_unknown_shape_and_error_responses_are_not_successful_empty_feeds(self):
        for p in TRENDING.values():
            with self.assertRaises(x.SearchError): p.decode_response(b'<html>Login</html>')
            with self.assertRaises(x.SearchError): p.normalize({}, 10)
            with self.assertRaises(x.SearchError): p.build_request({}, "synthetic-key", "test")
            with self.assertRaises(x.SearchError): p.check_error({"code": -412, "message": "private text"})
        with self.assertRaises(x.SearchError):
            TRENDING["bilibili"].normalize({"list": [{"keyword": "", "show_name": ""}]}, 10)

    def test_valid_empty_array_stays_empty_and_count_validation_precedes_network(self):
        raw = {"bilibili": {"list": []}, "zhihu": {"data": []}, "v2ex": {"items": []}}
        for name, p in TRENDING.items():
            self.assertEqual(p.normalize(raw[name], 10)[0], [])
        for count in (0, 51, True):
            with patch.object(x, "request_api", side_effect=AssertionError("no network")):
                with self.assertRaises(x.SearchError):
                    run_trending(args(platform="zhihu", count=count), x.request_api, "test")

    def test_malformed_records_after_transport_still_count_the_http_attempt(self):
        with patch.object(x.urllib.request, "build_opener", return_value=QueueTransport({"data": [{}]})):
            with self.assertRaises(x.SearchError) as caught:
                run_trending(args(platform="zhihu"), x.request_api, "test")
        self.assertEqual(caught.exception.attempts, 1)

    def test_platform_index_links_distinguish_profiles_from_notes_and_posts(self):
        self.assertEqual(x.platform_item_type("xiaohongshu", "https://www.xiaohongshu.com/user/profile/123"), "user_profile")
        self.assertEqual(x.platform_item_type("xiaohongshu", "https://www.xiaohongshu.com/explore/123"), "note_link")
        self.assertEqual(x.platform_item_type("weibo", "https://weibo.com/123/AbCd"), "post_link")
        self.assertEqual(x.platform_item_type("weibo", "https://weibo.com/example"), "profile_or_landing_page")
        self.assertIsNone(x.platform_item_type("xiaohongshu", "https://example.com/explore/123"))
        body = {"results": [{"title": "Profile", "url": "https://www.xiaohongshu.com/user/profile/123"}]}
        with patch.object(x.urllib.request, "build_opener", return_value=QueueTransport(body)):
            data = x.run_search(args(provider="deepseek", platform="xiaohongshu"),
                                {"providers": {"deepseek": {"api_key": "synthetic-only"}}})
        self.assertEqual(data["results"][0]["platform_item_type"], "user_profile")

    def test_feed_cannot_be_used_as_keyword_source_or_silently_replace_weibo_search(self):
        self.assertTrue(all(not p.supports_search for p in TREND_PROVIDERS.values()))
        self.assertTrue(all(p.capabilities()["search_scope"] == "none_trending_only" for p in TREND_PROVIDERS.values()))
        route = x.plan(args(platform="zhihu"), {"providers": {}}, x.credential)
        self.assertNotIn("zhihu-trending", route["candidates"])
        self.assertNotIn("weibo", TRENDING)
        with patch.object(x, "request_api", side_effect=AssertionError("no network")):
            with self.assertRaises(x.SearchError):
                run_trending(args(platform="weibo"), x.request_api, "test")
        catalog = {r["platform"]: r for r in x.platform_catalog()["platforms"]}
        self.assertTrue(catalog["zhihu"]["native_trending"])
        self.assertEqual(catalog["zhihu"]["coverage"], "public_index_only")
        self.assertFalse(catalog["weibo"]["native_trending"])

    def test_denied_feed_pauses_and_next_call_sends_no_http(self):
        transport = QueueTransport(urllib.error.HTTPError("", 403, "", {}, io.BytesIO(b"not-logged")))
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            with self.assertRaises(x.SearchError) as first:
                run_trending(args(platform="zhihu"), x.request_api, "test")
            with self.assertRaises(x.SearchError) as second:
                run_trending(args(platform="zhihu"), x.request_api, "test")
        self.assertEqual(first.exception.status, 403)
        self.assertEqual(first.exception.attempts, 1)
        self.assertEqual(second.exception.code, "source_cooldown")
        self.assertEqual(second.exception.attempts, 0)
        self.assertEqual(len(transport.requests), 1)
        self.assertGreater(public_access.pause_status("zhihu-trending")["retry_after_seconds"], 0)


if __name__ == "__main__":
    unittest.main()
