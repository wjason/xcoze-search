"""No network: policy boundaries, public protocols, bounded automatic execution."""
import argparse
from contextlib import redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from test_search import x, args, ds, QueueTransport
from public_providers import PUBLIC_REGISTRY as FREE

RSS = b'<rss><channel><item><title>Python</title><link>https://docs.python.org/3/</link><description>Official docs</description></item></channel></rss>'
JINA = {"code": 200, "data": {"title": "Example", "url": "https://example.com", "content": "Public article text."}}
GH = {"items": [{"full_name": "python/cpython", "html_url": "https://github.com/python/cpython", "description": "Python"}], "incomplete_results": False}
HN = {"hits": [{"objectID": "123", "title": "Python", "url": "https://python.org", "created_at": "2026-11-01"}]}


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"XDG_CONFIG_HOME": self.tmp.name}, clear=True)
        self.env.start()
        self.config = {"schema_version": 2, "providers": {}}

    def tearDown(self):
        self.env.stop(); self.tmp.cleanup()

    def keyed(self):
        self.config["providers"]["deepseek"] = {"api_key": "synthetic-only"}

    def test_no_key_plan_is_free_and_does_not_create_config(self):
        route = x.plan(args(), self.config, x.credential)
        self.assertEqual(route["strategy"], "free")
        self.assertTrue(all(not x.get_provider(p).requires_key for p in route["candidates"]))
        self.assertFalse(x.config_path().exists())

    def test_key_selects_quality_and_saved_free_never_selects_keyed_source(self):
        self.keyed()
        self.assertEqual(x.plan(args(), self.config, x.credential)["candidates"][0], "deepseek")
        self.config["search_preferences"] = {"strategy": "free"}
        self.assertNotIn("deepseek", x.plan(args(), self.config, x.credential)["candidates"])

    def test_balanced_public_first_and_explicit_override_precedence(self):
        self.keyed(); self.config["search_preferences"] = {"strategy": "balanced"}
        route = x.plan(args(), self.config, x.credential)
        self.assertEqual(route["candidates"][0], "bing")
        self.assertIn("deepseek", route["candidates"])
        self.config["search_preferences"] = {"strategy": "free"}
        self.assertEqual(x.plan(args(provider="deepseek"), self.config, x.credential)["candidates"], ["deepseek"])
        with self.assertRaises(x.SearchError): x.plan(args(provider="deepseek", strategy="free"), self.config, x.credential)

    def test_platform_prefers_structured_public_source_even_with_key(self):
        self.keyed()
        for platform, source in (("github", "github"), ("hackernews", "hackernews")):
            route = x.plan(args(platform=platform), self.config, x.credential)
            self.assertEqual(route["candidates"][0], source)
        for platform, site in (("zhihu", "zhihu.com"), ("xiaohongshu", "xiaohongshu.com"), ("weibo", "weibo.com")):
            route = x.plan(args(platform=platform), self.config, x.credential)
            self.assertIn("site:" + site, route["payloads"]["deepseek"]["query"])
        with self.assertRaises(x.SearchError):
            x.plan(args(platform="zhihu", site="github.com"), self.config, x.credential)

    def test_constraint_matching_never_drops_requested_option(self):
        route = x.plan(args(start_date="2026-11-01", platform="hackernews"), self.config, x.credential)
        self.assertEqual(route["candidates"], ["hackernews"])
        self.assertIn("numericFilters", route["payloads"]["hackernews"])
        with self.assertRaises(x.SearchError): x.plan(args(freshness="d7"), self.config, x.credential)
        with self.assertRaises(x.SearchError): x.plan(args(count=0), self.config, x.credential)
        self.assertEqual(FREE["github"].capabilities()["time_filters"], [])

    def test_disabled_sources_and_bad_keys_do_not_enter_automatic_routes(self):
        self.keyed(); self.config["providers"]["deepseek"]["api_key"] = "bad key"
        route = x.plan(args(), self.config, x.credential)
        self.assertNotIn("deepseek", route["candidates"])
        self.config["search_preferences"] = {"disabled_providers": ["bing", "exa-free"]}
        self.assertEqual(x.plan(args(), self.config, x.credential)["candidates"], ["duckduckgo"])

    def test_preferences_save_reset_private_and_preserve_credentials(self):
        self.keyed(); x.save_config(self.config)
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(x.main(["preferences", "--strategy", "free", "--disable", "bing"]), 0)
        self.assertNotIn("synthetic-only", out.getvalue())
        saved = x.read_config()
        self.assertEqual(saved["providers"], self.config["providers"])
        self.assertEqual(saved["search_preferences"]["strategy"], "free")
        with redirect_stdout(io.StringIO()): self.assertEqual(x.main(["preferences", "--reset"]), 0)
        self.assertEqual(x.preferences(x.read_config())["strategy"], "smart")
        if os.name == "posix": self.assertEqual(x.config_path().stat().st_mode & 0o777, 0o600)

    def test_plan_cli_never_connects_or_prints_key(self):
        self.keyed(); x.save_config(self.config)
        with patch.object(x, "request_api") as request, redirect_stdout(io.StringIO()) as out:
            self.assertEqual(x.main(["plan", "latest Python"]), 0)
        request.assert_not_called()
        self.assertEqual(json.loads(out.getvalue())["network_requests"], 0)
        self.assertNotIn("synthetic-only", out.getvalue())
        with self.assertRaises(x.SearchError):
            x.plan(args(provider="all"), {"schema_version": 2, "providers": {}}, x.credential)

    def test_free_mode_executes_with_no_auth_even_when_key_is_configured(self):
        self.keyed()
        transport = QueueTransport(RSS)
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_search(args(strategy="free"), self.config)
        self.assertTrue(output["ok"])
        self.assertEqual(output["providers"], ["bing"])
        self.assertEqual(output["budget"]["attempts"], 1)
        self.assertIsNone(transport.requests[0].get_header("Authorization"))

    def test_quality_stops_after_usable_primary_and_recovery_is_reported(self):
        self.keyed()
        transport = QueueTransport(ds())
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_search(args(), self.config)
        self.assertTrue(output["ok"]); self.assertEqual(len(transport.requests), 1)
        transport = QueueTransport(urllib.error.HTTPError("", 402, "", {}, io.BytesIO()), RSS)
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_search(args(), self.config)
        self.assertTrue(output["ok"]); self.assertTrue(output["partial"])
        self.assertEqual(output["routing"]["attempted_providers"], ["deepseek", "bing"])
        self.assertEqual(output["errors"][0]["category"], "billing")

    def test_empty_results_fallback_but_do_not_claim_semantic_quality(self):
        self.keyed(); transport = QueueTransport({"results": []}, RSS)
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_search(args(), self.config)
        self.assertTrue(output["ok"])
        self.assertFalse(output["routing"]["semantic_quality_verified"])
        self.assertEqual(len(transport.requests), 2)

    def test_balanced_reaches_configured_api_within_default_two_source_limit(self):
        self.keyed()
        transport = QueueTransport(urllib.error.HTTPError("", 503, "", {}, io.BytesIO()), ds())
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_search(args(strategy="balanced"), self.config)
        self.assertTrue(output["ok"])
        self.assertEqual(output["routing"]["attempted_providers"], ["bing", "deepseek"])
        self.assertEqual(output["budget"]["attempts"], 2)

    def test_saved_free_fetch_never_reaches_keyed_api_after_reader_failure(self):
        self.keyed(); self.config["search_preferences"] = {"strategy": "free"}
        route = x.plan(args(url="https://example.com"), self.config, x.credential, fetch=True)
        self.assertNotIn("deepseek", route["candidates"])
        transport = QueueTransport(urllib.error.HTTPError("", 403, "", {}, io.BytesIO()),
                                   urllib.error.HTTPError("", 403, "", {}, io.BytesIO()))
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_fetch(args(url="https://example.com"), self.config)
        self.assertFalse(output["ok"])
        self.assertTrue(all(r.get_header("Authorization") is None for r in transport.requests))
        self.assertEqual(output["errors"][0]["category"], "access")

    def test_request_and_source_limits_stop_fallback_without_extra_calls(self):
        self.keyed()
        for flags in ({"max_requests": 1}, {"max_sources": 1}):
            transport = QueueTransport(urllib.error.HTTPError("", 503, "", {}, io.BytesIO()))
            with patch.object(x.urllib.request, "build_opener", return_value=transport):
                output = x.run_search(args(**flags), self.config)
            self.assertFalse(output["ok"]); self.assertEqual(len(transport.requests), 1)

    def test_deadline_clips_timeout_and_stops_next_source(self):
        self.keyed()
        ticks = iter([0, 0, 0, 0, 0, 0, 0, 50])
        with patch.object(x.time, "monotonic", side_effect=lambda: next(ticks, 50)), patch.object(x, "request_api", return_value=({"results": []}, 1)) as call:
            output = x.run_search(args(max_seconds=2), self.config)
        self.assertLessEqual(call.call_args.kwargs["timeout"], 2)
        self.assertFalse(output["ok"])

    def test_platform_scope_is_checked_on_returned_urls(self):
        self.keyed()
        with patch.object(x, "request_api", return_value=(ds(url="https://evil.example/zhihu.com"), 1)):
            output = x.run_search(args(provider="deepseek", platform="zhihu"), self.config)
        self.assertEqual(output["results"], [])

    def test_auto_fetch_is_keyless_and_has_no_paid_auth(self):
        self.keyed(); transport = QueueTransport(JINA)
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_fetch(args(url="https://example.com"), self.config)
        self.assertTrue(output["ok"]); self.assertEqual(output["provider"], "jina")
        self.assertIsNone(transport.requests[0].get_header("Authorization"))

    def test_preference_save_migrates_v1_with_private_backup(self):
        self.keyed(); original = {**self.config, "schema_version": 1}
        path = x.config_path(); path.parent.mkdir(mode=0o700)
        path.write_text(json.dumps(original)); path.chmod(0o600)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(x.main(["preferences", "--strategy", "balanced"]), 0)
        self.assertEqual(json.loads(path.with_name("config.v1.backup.json").read_text()), original)
        self.assertEqual(x.read_config()["providers"], original["providers"])

    def test_expired_time_budget_starts_no_further_request(self):
        self.keyed(); clock = [0]
        def empty(*a, **kw):
            kw["budget"].consume(a[0]); clock[0] = 3
            return {"results": []}, 1
        with patch.object(x.time, "monotonic", side_effect=lambda: clock[0]), patch.object(x, "request_api", side_effect=empty) as call:
            output = x.run_search(args(max_seconds=2), self.config)
        self.assertEqual(call.call_count, 1)
        self.assertEqual(output["budget"]["attempts"], 1)
        self.assertEqual(output["errors"][-1]["code"], "budget_exhausted")


class PublicProtocolTests(unittest.TestCase):
    def test_rss_and_html_do_not_treat_challenges_as_empty_success(self):
        data = FREE["bing"].decode_response(RSS)
        self.assertEqual(FREE["bing"].normalize(data, 5)[0][0]["snippet"], "Official docs")
        self.assertIsNone(FREE["bing"].normalize(data, 5)[0][0]["published_at"])
        for provider, body in (("bing", b'<html>captcha</html>'), ("duckduckgo", b'<form id="challenge-form">verify</form>')):
            with self.assertRaises(x.SearchError): FREE[provider].decode_response(body)

    def test_ddg_extracts_only_public_result_links(self):
        body = b'<a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fpython.org">Python <b>docs</b></a><a class="result__snippet">Read docs</a>'
        rows, _ = FREE["duckduckgo"].normalize(FREE["duckduckgo"].decode_response(body), 5)
        self.assertEqual(rows[0]["url"], "https://python.org")
        self.assertEqual(rows[0]["title"], "Python docs")
        self.assertEqual(rows[0]["snippet"], "Read docs")

    def test_mcp_sse_structured_text_and_application_errors(self):
        p = FREE["exa-free"]
        for body in ({"structuredContent": {"results": [{"title": "t", "url": "https://example.com", "highlights": ["excerpt"]}]}},
                     {"content": [{"type": "text", "text": "Title: t\nURL: https://example.com\nPublished: N/A\nAuthor: N/A\nHighlights:\nexcerpt"}]}):
            raw = ('event: message\ndata: ' + json.dumps({"jsonrpc": "2.0", "id": 1, "result": body}) + '\n\n').encode()
            rows, _ = p.normalize(p.decode_response(raw), 5)
            self.assertEqual(rows[0]["url"], "https://example.com")
        for msg in ({"id": 1, "error": {"message": "synthetic-secret"}}, {"id": 1, "result": {"isError": True}}):
            with self.assertRaises(x.SearchError) as caught: p.decode_response(json.dumps(msg).encode())
            self.assertNotIn("synthetic-secret", str(caught.exception))

    def test_github_results_and_readme_have_distinct_content_scope(self):
        p = FREE["github"]
        rows, _ = p.normalize(GH, 5)
        self.assertEqual(rows[0]["title"], "python/cpython")
        self.assertIsNone(rows[0]["published_at"])
        data = p.normalize_fetch({"encoding": "base64", "content": "IyBQeXRob24=", "name": "README.md"}, "https://github.com/python/cpython")
        self.assertEqual(data["content"], "# Python")
        self.assertEqual(data["content_kind"], "repository_readme")
        for url in ("https://github.com/a/b/blob/main/file", "https://evil.example/a/b", "https://github.com/a/.."):
            with self.assertRaises(x.SearchError): p.fetch_payload(args(url=url))

    def test_hn_preserves_discussion_and_outbound_article_separately(self):
        p = FREE["hackernews"]
        rows, _ = p.normalize(HN, 5)
        self.assertEqual(rows[0]["url"], "https://news.ycombinator.com/item?id=123")
        self.assertEqual(rows[0]["provider_fields"]["outbound_url"], "https://python.org")
        data = p.normalize_fetch({"id": 123, "title": "Python", "url": "https://python.org", "kids": [1, 2]}, "")
        self.assertEqual(data["comment_ids"], [1, 2]); self.assertFalse(data["comments_fetched"])
        self.assertEqual(data["content_kind"], "discussion_item")

    def test_jina_keyless_is_reader_only_and_rejects_blocked_or_empty_text(self):
        p = FREE["jina"]
        self.assertFalse(p.capabilities()["search"])
        for data in ({"code": 200, "data": {"content": ""}}, {"code": 200, "data": {"title": "Log in", "content": "Sign in"}}):
            with self.assertRaises(x.SearchError): p.normalize_fetch(data, "https://example.com")
        with self.assertRaises(x.SearchError): p.check_error({"code": 403, "message": "secret"})

    def test_keyless_auth_is_never_forwarded_and_requests_are_fixed_host(self):
        for name, p in FREE.items():
            if not p.supports_search: continue
            payload = p.search_payload(args())
            request = p.build_request(payload, "synthetic-do-not-send", "0.4.0")
            self.assertIsNone(request.get_header("Authorization"))
            self.assertNotIn("synthetic-do-not-send", request.full_url + str(request.data))
            self.assertTrue(request.full_url.startswith(p.endpoint))


if __name__ == "__main__": unittest.main()
