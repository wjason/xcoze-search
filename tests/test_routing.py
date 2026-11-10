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
EXA = {"jsonrpc": "2.0", "id": 1, "result": {"structuredContent": {
    "results": [{"title": "Python", "url": "https://docs.python.org/3/", "text": "Official docs"}]}}}


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"XDG_CONFIG_HOME": self.tmp.name, "XDG_CACHE_HOME": self.tmp.name}, clear=True)
        self.env.start()
        self.browser = patch('search_routing.browser_available', return_value=False)
        self.browser.start()
        self.config = {"schema_version": 2, "providers": {}}

    def tearDown(self):
        self.browser.stop(); self.env.stop(); self.tmp.cleanup()

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
        self.assertEqual(route["candidates"][0], "exa-free")
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

    def test_github_keeps_api_slots_instead_of_reserving_browser(self):
        self.keyed()
        with patch('search_routing.browser_available', return_value=True):
            route = x.plan(args(query='markitdown',platform='github'),self.config,x.credential)
            self.assertEqual(route['execution_candidates'],['github','deepseek','exa-free'])
            self.assertEqual(route['browser_slot_policy'],'api_priority_for_github')
            free = x.plan(args(query='markitdown',platform='github',strategy='free'),self.config,x.credential)
            self.assertEqual(free['execution_candidates'],['github','exa-free','parallel-free'])
            generic = x.plan(args(query='example'),self.config,x.credential)
            self.assertEqual(generic['execution_candidates'],['deepseek','exa-free','browser'])
            explicit = x.plan(args(query='markitdown',platform='github',provider='browser'),self.config,x.credential)
            self.assertEqual(explicit['execution_candidates'],['browser'])
        transport = QueueTransport(urllib.error.HTTPError('',503,'',{},io.BytesIO()),ds(url='https://github.com/microsoft/markitdown'))
        with patch('search_routing.browser_available',return_value=True),patch.object(x.urllib.request,'build_opener',return_value=transport),patch.object(x,'run_browser_search') as local:
            result=x.run_search(args(query='markitdown',platform='github'),self.config)
        self.assertTrue(result['ok']);self.assertEqual(result['providers'],['github','deepseek']);local.assert_not_called()

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
        self.config["search_preferences"] = {"disabled_providers": ["bing", "exa-free", "parallel-free"]}
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
        transport = QueueTransport(EXA)
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_search(args(strategy="free"), self.config)
        self.assertTrue(output["ok"])
        self.assertEqual(output["providers"], ["exa-free"])
        self.assertEqual(output["budget"]["attempts"], 1)
        self.assertIsNone(transport.requests[0].get_header("Authorization"))

    def test_quality_stops_after_usable_primary_and_recovery_is_reported(self):
        self.keyed()
        transport = QueueTransport(ds())
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_search(args(), self.config)
        self.assertTrue(output["ok"]); self.assertEqual(len(transport.requests), 1)
        transport = QueueTransport(urllib.error.HTTPError("", 402, "", {}, io.BytesIO()), EXA)
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_search(args(), self.config)
        self.assertTrue(output["ok"]); self.assertTrue(output["partial"])
        self.assertEqual(output["routing"]["attempted_providers"], ["deepseek", "exa-free"])
        self.assertEqual(output["errors"][0]["category"], "billing")

    def test_empty_results_fallback_but_do_not_claim_semantic_quality(self):
        self.keyed(); transport = QueueTransport({"results": []}, EXA)
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
        self.assertEqual(output["routing"]["attempted_providers"], ["exa-free", "deepseek"])
        self.assertEqual(output["budget"]["attempts"], 2)

    def test_reference_quality_combines_sources_and_marks_duplicates(self):
        self.keyed()
        transport = QueueTransport(ds(url="https://docs.python.org/3/#section"), EXA)
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_search(args(query="Python documentation"), self.config)
        self.assertEqual(output["routing"]["intent"], "reference")
        self.assertTrue(output["routing"]["complementary_search"])
        self.assertEqual(output["providers"], ["deepseek", "exa-free"])
        self.assertEqual(output["duplicate_groups"], [[0, 1]])
        self.assertEqual([r["rank"] for r in output["results"]], [1, 1])

    def test_reference_skips_weak_complement_but_retains_failure_fallback(self):
        self.keyed();self.config['search_preferences']={'disabled_providers':['exa-free']}
        route=x.plan(args(query='Rust Mutex documentation'),self.config,x.credential)
        self.assertFalse(route['complementary_search'])
        transport=QueueTransport(ds())
        with patch.object(x.urllib.request,'build_opener',return_value=transport):
            out=x.run_search(args(query='Rust Mutex documentation'),self.config)
        self.assertTrue(out['ok']);self.assertEqual(out['providers'],['deepseek'])
        self.assertEqual(len(transport.requests),1)
        self.config['search_preferences']={'disabled_providers':['exa-free','parallel-free','bing']}
        body=b'<a class="result__a" href="https://example.com/rust">Rust Mutex reference</a>'
        transport=QueueTransport({'results':[]},body)
        with patch.object(x.urllib.request,'build_opener',return_value=transport):
            out=x.run_search(args(query='Rust Mutex documentation'),self.config)
        self.assertTrue(out['ok']);self.assertEqual(out['providers'],['deepseek','duckduckgo'])

    def test_healthy_primary_caps_only_automatic_complement_at_three_seconds(self):
        self.keyed();transport=QueueTransport(ds(),EXA);timeouts=[];original=transport.open
        def capture(request,timeout):
            timeouts.append(timeout);return original(request,timeout)
        transport.open=capture
        with patch.object(x.urllib.request,'build_opener',return_value=transport):
            out=x.run_search(args(query='Python documentation',timeout=30),self.config)
        self.assertTrue(out['ok']);self.assertEqual(len(timeouts),2)
        self.assertEqual(timeouts[0],8);self.assertLessEqual(timeouts[1],3)
        self.assertEqual(out['routing']['complementary_timeout_seconds'],3)

    def test_complement_failure_keeps_first_results_and_reports_partial(self):
        self.keyed()
        transport = QueueTransport(ds(), urllib.error.HTTPError("", 429, "", {}, io.BytesIO()))
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_search(args(query="latest Python", max_sources=3), self.config)
        self.assertTrue(output["ok"]); self.assertTrue(output["partial"])
        self.assertEqual(len(output["results"]), 1)
        self.assertEqual(output["errors"][0]["category"], "rate_limit")
        self.assertEqual(len(transport.requests), 2)

    def test_intent_limits_overrides_and_platform_avoid_unrequested_fanout(self):
        self.keyed()
        cases = [(args(query="latest Python", max_sources=1), ds()),
                 (args(query="latest Python", intent="general"), ds()),
                 (args(query="latest Python", provider="deepseek"), ds()),
                 (args(query="latest Python", platform="github"), GH),
                 (args(query="Python API", strategy="free"), EXA)]
        for arguments, response in cases:
            transport = QueueTransport(response)
            with self.subTest(args=arguments), patch.object(x.urllib.request, "build_opener", return_value=transport):
                output = x.run_search(arguments, self.config)
                self.assertTrue(output["ok"])
                self.assertEqual(len(transport.requests), 1)
        route = x.plan(args(query="普通问题", intent="current"), self.config, x.credential)
        self.assertEqual(route["intent"], "current")

    def test_scraped_topic_mismatch_falls_back_and_explicit_source_does_not_expand(self):
        bad = RSS.replace(b'Python', b'Windows help').replace(b'python.org', b'microsoft.com')
        self.config["search_preferences"] = {"disabled_providers": ["exa-free", "parallel-free"]}
        good = b'<a class="result__a" href="https://docs.python.org/3/">Python TaskGroup</a>'
        transport = QueueTransport(bad, good)
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_search(args(query="Python asyncio TaskGroup"), self.config)
        self.assertTrue(output["ok"]); self.assertTrue(output["partial"])
        self.assertEqual(output["providers"], ["bing", "duckduckgo"])
        self.assertEqual(output["errors"][0]["code"], "irrelevant_results")
        transport = QueueTransport(bad)
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            output = x.run_search(args(query="Python asyncio TaskGroup", provider="bing"), self.config)
        self.assertFalse(output["ok"]); self.assertEqual(len(transport.requests), 1)

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

    def test_chinese_rows_drop_noise_preserve_rank_and_reject_empty_complement(self):
        self.keyed()
        raw = '<rss><channel><item><title>2026 calendar</title><link>https://example.com/calendar</link></item><item><title>2026年可再生能源新增装机</title><link>https://example.com/energy</link></item></channel></rss>'.encode('utf-8')
        transport = QueueTransport(raw)
        with patch.object(x.urllib.request,'build_opener',return_value=transport):
            out=x.run_search(args(query='2026年 可再生能源 新增装机',provider='bing'),self.config)
        self.assertTrue(out['ok']);self.assertEqual(len(out['results']),1)
        self.assertEqual(out['results'][0]['rank'],2)
        self.assertEqual(out['requests'][0]['dropped_irrelevant_count'],1)
        self.assertEqual(out['requests'][0]['shown_count'],1)

    def test_ddg_real_challenge_protocol_pauses_later_routes_without_http(self):
        self.config['search_preferences']={'disabled_providers':['exa-free','parallel-free','bing']}
        transport=QueueTransport(b'<form id="challenge-form">verify you are human</form>')
        with patch.object(x.urllib.request,'build_opener',return_value=transport):
            out=x.run_search(args(strategy='free'),self.config)
        self.assertFalse(out['ok']);self.assertEqual(len(transport.requests),1)
        self.assertEqual(out['errors'][0]['code'],'access_challenge')
        with self.assertRaises(x.SearchError) as caught:
            x.plan(args(strategy='free'),self.config,x.credential)
        self.assertEqual(caught.exception.code,'no_compatible_provider')
        with patch('search_routing.browser_available',return_value=True):
            route=x.plan(args(strategy='free'),self.config,x.credential)
        self.assertEqual(route['execution_candidates'],['browser'])
        self.assertEqual(route['skipped_unavailable'][0]['provider'],'duckduckgo')

    def test_platform_scope_is_checked_on_returned_urls(self):
        self.keyed()
        with patch.object(x, "request_api", return_value=(ds(url="https://evil.example/zhihu.com"), 1)):
            output = x.run_search(args(provider="deepseek", platform="zhihu"), self.config)
        self.assertEqual(output["results"], [])

    def test_parallel_fallback_retrieves_scoped_excerpts_without_keys_or_browser(self):
        self.keyed()
        self.config['search_preferences'] = {'disabled_providers': ['exa-free', 'exa']}
        result = {'jsonrpc': '2.0', 'id': 1, 'result': {'structuredContent': {'results': [
            {'url': 'https://evil.example/docs.python.org', 'title': 'Impostor', 'excerpts': []},
            {'url': 'https://docs.python.org/3/library/asyncio-task.html', 'title': None,
             'excerpts': ['TaskGroup'], 'publish_date': 'invalid'},
        ], 'session_id': 'private-test-session'}}}
        transport = QueueTransport(('data: ' + json.dumps(result) + '\n\n').encode())
        query = args(query='Python TaskGroup', site='docs.python.org', strategy='free')
        with patch.object(x.urllib.request, 'build_opener', return_value=transport), \
                patch('search_routing.browser_available', return_value=True), \
                patch.object(x, 'run_browser_search') as browser:
            output = x.run_search(query, self.config)
        browser.assert_not_called()
        self.assertEqual(output['providers'], ['parallel-free'])
        request = transport.requests[0]
        self.assertIsNone(request.get_header('Authorization'))
        self.assertEqual(json.loads(request.data)['params']['arguments']['search_queries'],
                         ['Python TaskGroup site:docs.python.org'])
        self.assertEqual(len(output['results']), 1)
        self.assertEqual(output['results'][0]['content_kind'], 'excerpts')
        self.assertIsNone(output['results'][0]['published_at'])
        self.assertNotIn('private-test-session', str(output))

    def test_parallel_rate_limit_preserves_bing_and_pauses_next_plan(self):
        self.config['search_preferences'] = {'disabled_providers': ['exa-free']}
        quota = {'jsonrpc': '2.0', 'id': 1, 'result': {'isError': True, 'content': [
            {'type': 'text', 'text': 'Rate limit exceeded, raw private diagnostic'},
        ]}}
        transport = QueueTransport(quota, RSS)
        query = args(query='Python', strategy='free')
        with patch.object(x.urllib.request, 'build_opener', return_value=transport):
            output = x.run_search(query, self.config)
        self.assertEqual(output['providers'], ['parallel-free', 'bing'])
        self.assertTrue(output['ok'])
        self.assertEqual(output['errors'][0]['code'], 'source_rate_limited')
        self.assertNotIn('raw private diagnostic', str(output))
        route = x.plan(query, self.config, x.credential)
        self.assertEqual(route['candidates'][0], 'bing')
        self.assertEqual(route['skipped_unavailable'][0]['provider'], 'parallel-free')

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
            if p.method == "LOCAL_BROWSER": continue
            payload = p.search_payload(args(query="CN,SP.POP.TOTL" if name == "worldbank" else "2.5,day" if name == "usgs" else "wind"))
            request = p.build_request(payload, "synthetic-do-not-send", "0.4.0")
            self.assertIsNone(request.get_header("Authorization"))
            self.assertNotIn("synthetic-do-not-send", request.full_url + str(request.data))
            self.assertTrue(request.full_url.startswith(p.endpoint))


if __name__ == "__main__": unittest.main()
