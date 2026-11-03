"""Synthetic provider contracts and backwards-compatible multi-source execution."""
from contextlib import redirect_stdout, redirect_stderr
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import urllib.parse

from test_search import QueueTransport, args, ds, yb

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/xcoze_search.py"
spec = importlib.util.spec_from_file_location("multi_search", SCRIPT)
x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)


def tavily():
    return {"results": [{"title": "Tavily source", "url": "https://example.com/a", "content": "excerpts",
                         "raw_content": "page", "score": .8, "published_date": "2026-10-01", "future": 42}],
            "request_id": "fixture-t", "usage": {"credits": 1}, "answer": "generated answer"}


def exa():
    return {"results": [{"title": "Exa source", "url": "https://example.com/a", "text": "page",
                         "summary": "summary", "highlights": ["excerpt"], "publishedDate": "2026-10-01T00:00:00Z"}],
            "requestId": "fixture-e", "costDollars": {"total": .001}, "warnings": [], "future": "kept"}


def brave():
    return {"query": {"original": "fixture"}, "web": {"results": [
        {"title": "Brave source", "url": "https://example.com/a", "description": "snippet",
         "extra_snippets": ["second excerpt"], "age": "yesterday", "page_age": "2026-10-01"}]}}


def bocha():
    return {"code": 200, "log_id": "fixture-b", "data": {"queryContext": {"originalQuery": "fixture"},
            "webPages": {"value": [{"name": "Bocha source", "url": "https://example.com/a", "snippet": "snippet",
            "summary": "summary", "siteName": "Example", "datePublished": "2026-10-01"}]}}}


FIXTURES = {"deepseek": ds, "yuanbao": yb, "tavily": tavily, "exa": exa, "brave": brave, "bocha": bocha}


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {"XDG_CONFIG_HOME": self.temp.name}, clear=True)
        self.environment.start()
        self.config = {"schema_version": 2, "providers": {name: {"api_key": "synthetic-" + name} for name in x.PROVIDERS}}

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()

    def test_registered_auth_methods_and_fixed_transport(self):
        for name, adapter in x.REGISTRY.items():
            with self.subTest(provider=name):
                transport = QueueTransport(FIXTURES[name]())
                payload = x.search_payload(name, args())
                x.request_api(name, payload, "synthetic-key", opener=transport)
                request = transport.requests[0]
                self.assertEqual(request.full_url.split("?", 1)[0], adapter.endpoint)
                self.assertEqual(request.get_method(), adapter.method)
                headers = {k.lower(): v for k, v in request.header_items()}
                self.assertEqual(headers[adapter.auth_header.lower()], adapter.auth_prefix + "synthetic-key")
                self.assertNotIn("synthetic-key", request.full_url)
                if name == "brave":
                    self.assertIsNone(request.data)
                    self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlsplit(request.full_url).query)["q"], ["test"])
                else:
                    self.assertIsInstance(json.loads(request.data), dict)

    def test_no_optional_generation_or_paid_content_requested_by_default(self):
        t = x.search_payload("tavily", args())
        self.assertFalse(t["include_answer"])
        self.assertFalse(t["include_raw_content"])
        self.assertFalse(t["auto_parameters"])
        self.assertEqual(t["search_depth"], "basic")
        self.assertNotIn("contents", x.search_payload("exa", args()))
        self.assertFalse(x.search_payload("bocha", args())["summary"])

    def test_tavily_domain_dates_and_explicit_content_answer(self):
        payload = x.search_payload("tavily", args(site="example.com", start_date="2026-10-01", end_date="2026-10-31",
                                                  need_content=True, include_answer=True, depth="advanced"))
        self.assertEqual(payload["include_domains"], ["example.com"])
        self.assertEqual(payload["start_date"], "2026-10-01")
        self.assertTrue(payload["filter_by_published_date"])
        self.assertEqual(payload["include_raw_content"], "markdown")
        self.assertTrue(payload["include_answer"])

    def test_exa_domain_dates_and_separate_content_options(self):
        payload = x.search_payload("exa", args(site="example.com", start_date="2026-10-01", end_date="2026-10-31",
                                               need_content=True, highlights=True, summary=True))
        self.assertEqual(payload["includeDomains"], ["example.com"])
        self.assertEqual(payload["startPublishedDate"], "2026-10-01T00:00:00.000Z")
        self.assertEqual(payload["endPublishedDate"], "2026-10-31T23:59:59.999Z")
        self.assertEqual(payload["contents"], {"text": True, "highlights": True, "summary": {"query": "test"}})

    def test_brave_country_language_freshness_and_extra_snippets(self):
        payload = x.search_payload("brave", args(country="gb", language="en", freshness="pw", extra_snippets=True))
        self.assertEqual(payload["country"], "GB")
        self.assertEqual(payload["search_lang"], "en")
        self.assertEqual(payload["freshness"], "pw")
        self.assertEqual(payload["extra_snippets"], "true")

    def test_bocha_native_time_filter_and_optional_summary(self):
        for freshness in ("oneWeek", "2026-10-01", "2026-10-01..2026-10-31"):
            payload = x.search_payload("bocha", args(freshness=freshness, summary=True))
            self.assertEqual(payload["freshness"], freshness)
            self.assertTrue(payload["summary"])

    def test_provider_limits_and_invalid_filters_rejected_before_transport(self):
        examples = [("tavily", args(count=21)), ("brave", args(count=21)),
                    ("brave", args(query="word " * 76)), ("brave", args(query="中" * 601)),
                    ("tavily", args(start_date="2026-02-30")), ("exa", args(start_date="2026-11-02", end_date="2026-10-01")),
                    ("bocha", args(freshness="2026-02-30")), ("brave", args(freshness="d7")),
                    ("brave", args(freshness="20261001to20261031")),
                    ("tavily", args(freshness="week", start_date="2026-10-01"))]
        with patch.object(x, "request_api") as request:
            for provider, flags in examples:
                flags.provider = provider
                with self.subTest(provider=provider, flags=flags), self.assertRaises(x.SearchError):
                    x.run_search(flags, self.config)
            request.assert_not_called()

    def test_unsupported_multi_provider_options_fail_before_any_network(self):
        with patch.object(x, "request_api") as request:
            for flags in (args(provider="tavily,brave", need_content=True), args(provider="bocha", site="example.com"),
                          args(provider="deepseek,exa", start_date="2026-10-01")):
                with self.assertRaises(x.SearchError):
                    x.run_search(flags, self.config)
            request.assert_not_called()

    def test_normalized_text_types_and_native_metadata_are_preserved(self):
        t_rows, t_meta = x.normalize("tavily", tavily(), 5)
        self.assertEqual(t_rows[0]["snippet"], "excerpts")
        self.assertEqual(t_rows[0]["content"], "page")
        self.assertEqual(t_rows[0]["provider_fields"]["future"], 42)
        self.assertEqual(t_meta["usage"], {"credits": 1})
        self.assertEqual(t_meta["generated_answer"], "generated answer")
        e_rows, e_meta = x.normalize("exa", exa(), 5)
        self.assertEqual(e_rows[0]["highlights"], ["excerpt"])
        self.assertEqual(e_rows[0]["summary"], "summary")
        self.assertEqual(e_rows[0]["content"], "page")
        self.assertEqual(e_meta["cost"]["reported"]["total"], .001)
        self.assertEqual(e_meta["provider_metadata"]["future"], "kept")
        for name, fixture in (("brave", brave()), ("bocha", bocha())):
            rows, meta = x.normalize(name, fixture, 5)
            self.assertEqual(rows[0]["content"], "")
            self.assertEqual(rows[0]["content_kind"], "search_summary")
            self.assertIsNone(meta["cost"])
        self.assertEqual(x.normalize("brave", brave(), 5)[0][0]["extra_snippets"], ["second excerpt"])

    def test_exa_ignored_constraints_and_corrupt_fields_are_errors(self):
        raw = exa()
        raw["warnings"] = [{"code": "IGNORED_FIELD", "path": "/startPublishedDate"}]
        with self.assertRaises(x.SearchError) as caught:
            x.normalize("exa", raw, 5)
        self.assertEqual(caught.exception.code, "constraint_not_applied")
        for name, field in (("exa", "highlights"), ("tavily", "content")):
            raw = FIXTURES[name]()
            raw["results"][0][field] = {"bad": "shape"}
            with self.assertRaises(x.SearchError):
                x.normalize(name, raw, 5)

    def test_empty_results_are_not_malformed_responses(self):
        for name, data in (("tavily", {"results": []}), ("exa", {"results": []}),
                           ("brave", {"query": {"original": "empty"}}),
                           ("bocha", {"code": 200, "data": {"queryContext": {}}})):
            self.assertEqual(x.normalize(name, data, 5)[0], [])
            with self.assertRaises(x.SearchError):
                x.normalize(name, {}, 5)

    def test_bocha_business_error_redaction_and_retry(self):
        transport = QueueTransport({"code": 429, "msg": "synthetic-sensitive"}, bocha())
        _, attempts = x.request_api("bocha", {}, "synthetic", opener=transport, sleep=lambda _: None)
        self.assertEqual(attempts, 2)
        with self.assertRaises(x.SearchError) as caught:
            x.request_api("bocha", {}, "synthetic", opener=QueueTransport({"code": 401, "msg": "synthetic-sensitive"}))
        self.assertNotIn("synthetic-sensitive", str(caught.exception))
        self.assertEqual(caught.exception.category, "authentication")

    def test_legacy_both_and_auto_do_not_expand_after_new_keys(self):
        self.assertEqual(x.select_providers("both", self.config), ["deepseek", "yuanbao"])
        self.assertEqual(x.select_providers("auto", self.config), ["deepseek"])
        self.assertEqual(x.select_providers("all", self.config), list(x.PROVIDERS))
        self.assertEqual(x.select_providers("exa,tavily,brave", self.config), ["exa", "tavily", "brave"])
        self.config["default_provider"] = "exa"
        self.assertEqual(x.select_providers("auto", self.config), ["exa"])
        del self.config["providers"]["exa"]
        with self.assertRaises(x.SearchError):
            x.select_providers("auto", self.config)
        for name in ("unknown", "exa,exa", "exa,unknown"):
            with self.assertRaises(x.SearchError):
                x.select_providers(name, self.config)

    def test_multi_provider_requires_all_credentials_up_front(self):
        del self.config["providers"]["brave"]
        with patch.object(x, "request_api") as request:
            with self.assertRaises(x.SearchError):
                x.run_search(args(provider="exa,tavily,brave"), self.config)
            request.assert_not_called()

    def test_three_sources_preserve_order_duplicates_and_partial_results(self):
        transport = QueueTransport(exa(), urllib.error.HTTPError("", 401, "", {}, io.BytesIO()), brave())
        with patch.object(x.urllib.request, "build_opener", return_value=transport):
            result = x.run_search(args(provider="exa,tavily,brave", retries=0), self.config)
        self.assertFalse(result["ok"])
        self.assertTrue(result["partial"])
        self.assertEqual([r["provider"] for r in result["results"]], ["exa", "brave"])
        self.assertEqual(result["duplicate_groups"], [[0, 1]])
        self.assertEqual(result["budget"]["attempts"], 3)
        self.assertEqual(result["requests"][1]["attempts"], 1)

    def test_budget_counts_retries_and_never_exceeds_limit(self):
        transport = QueueTransport(urllib.error.HTTPError("", 429, "", {}, io.BytesIO()), exa(), tavily())
        with patch.object(x.urllib.request, "build_opener", return_value=transport), patch.object(x, "time") as clock:
            clock.monotonic.return_value = 1
            # A real request_api default sleep can wait one second; use retries=0 in other tests.
            result = x.run_search(args(provider="exa,tavily", max_requests=2, retries=1), self.config)
        self.assertEqual(len(transport.requests), 2)
        self.assertEqual(result["budget"]["attempts"], 2)
        self.assertEqual(result["errors"][0]["code"], "budget_exhausted")
        self.assertTrue(result["partial"])

    def test_insufficient_initial_budget_is_rejected_without_network(self):
        with patch.object(x, "request_api") as request:
            with self.assertRaises(x.SearchError) as caught:
                x.run_search(args(provider="exa,tavily", max_requests=1), self.config)
            self.assertEqual(caught.exception.code, "budget_exhausted")
            request.assert_not_called()

    def test_successful_http_with_malformed_results_still_accounts_attempt(self):
        with patch.object(x.urllib.request, "build_opener", return_value=QueueTransport({"unexpected": True})):
            result = x.run_search(args(provider="exa", retries=0), self.config)
        self.assertFalse(result["ok"])
        self.assertEqual(result["requests"][0]["attempts"], 1)
        self.assertEqual(result["budget"]["attempts"], 1)

    def test_extraction_success_failures_and_canonical_url(self):
        url = "https://example.com/a"
        responses = {"tavily": {"results": [{"url": url + "/", "raw_content": "page"}], "failed_results": [], "usage": {"credits": 1}},
                     "exa": exa()}
        for provider, raw in responses.items():
            with patch.object(x.urllib.request, "build_opener", return_value=QueueTransport(raw)):
                output = x.run_fetch(args(provider=provider, url=url, highlights=False, summary=False), self.config)
            self.assertEqual(output["content"], "page")
            self.assertEqual(output["provider"], provider)
            self.assertEqual(output["budget"]["attempts"], 1)
        failures = {"tavily": {"results": [], "failed_results": [{"url": url, "error": "synthetic-sensitive"}]},
                    "exa": {"results": exa()["results"], "statuses": [{"status": "error", "error": {"tag": "bad"}}]}}
        for provider, raw in failures.items():
            with patch.object(x.urllib.request, "build_opener", return_value=QueueTransport(raw)):
                with self.assertRaises(x.SearchError) as caught:
                    x.run_fetch(args(provider=provider, url=url), self.config)
            self.assertEqual(caught.exception.code, "extraction_failed")
            self.assertEqual(caught.exception.attempts, 1)
            self.assertNotIn("synthetic-sensitive", str(caught.exception))

    def test_fetch_has_no_provider_fallback_and_rejects_unsupported_options(self):
        for provider in ("brave", "bocha", "yuanbao"):
            with patch.object(x, "request_api") as request:
                with self.assertRaises(x.SearchError):
                    x.run_fetch(args(provider=provider, url="https://example.com/a"), self.config)
                request.assert_not_called()
        with self.assertRaises(x.SearchError):
            x.run_fetch(args(provider="tavily", url="https://example.com/a", summary=True), self.config)

    def test_v1_read_is_non_mutating_and_migration_preserves_unknown_fields(self):
        path = x.config_path()
        path.parent.mkdir(mode=0o700)
        data = {"schema_version": 1, "providers": {"deepseek": {"api_key": "synthetic-old", "future": 3},
                "future-provider": {"api_key": "synthetic-future"}}, "default_provider": "deepseek", "custom": 42}
        path.write_text(json.dumps(data), encoding="utf-8")
        path.chmod(0o600)
        before = path.read_bytes()
        config = x.read_config()
        self.assertTrue(x.status(config)["migration_available"])
        self.assertEqual(path.read_bytes(), before)
        result = x.migrate_config(config)
        self.assertTrue(result["migrated"])
        saved = x.read_config()
        self.assertEqual(saved, {**data, "schema_version": 2})
        backup = path.with_name("config.v1.backup.json")
        self.assertEqual(backup.read_bytes(), before)
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o600)
        self.assertFalse(x.migrate_config(saved)["migrated"])

    def test_future_or_invalid_config_and_failed_migration_leave_original_untouched(self):
        path = x.config_path()
        path.parent.mkdir(mode=0o700)
        path.write_text('{"schema_version":99,"providers":{}}', encoding="utf-8")
        path.chmod(0o600)
        before = path.read_bytes()
        with self.assertRaises(x.SearchError):
            x.read_config()
        self.assertEqual(path.read_bytes(), before)
        data = {"schema_version": 1, "providers": {"deepseek": {"api_key": "synthetic-old"}}}
        path.write_text(json.dumps(data), encoding="utf-8")
        before = path.read_bytes()
        with patch.object(x.os, "replace", side_effect=OSError("fixture failure")):
            with self.assertRaises(x.SearchError):
                x.migrate_config(data)
        self.assertEqual(path.read_bytes(), before)

    def test_migration_never_overwrites_existing_backup(self):
        path = x.config_path()
        path.parent.mkdir(mode=0o700)
        path.write_text('{"schema_version":1,"providers":{}}', encoding="utf-8")
        path.chmod(0o600)
        backup = path.with_name("config.v1.backup.json")
        backup.write_text("prior backup", encoding="utf-8")
        backup.chmod(0o600)
        with self.assertRaises(x.SearchError):
            x.migrate_config(x.read_config())
        self.assertEqual(backup.read_text(), "prior backup")

    def test_setup_migrates_only_after_input_and_keeps_private_original_backup(self):
        path = x.config_path()
        path.parent.mkdir(mode=0o700)
        data = {"schema_version": 1, "providers": {"deepseek": {"api_key": "synthetic-old", "future": 42}}}
        original = json.dumps(data).encode()
        path.write_bytes(original)
        path.chmod(0o600)
        with patch.object(x, "gui_key", side_effect=x.SearchError("cancelled", "Cancelled")), \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(x.main(["setup", "--provider", "exa", "--gui"]), 130)
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(path.with_name("config.v1.backup.json").exists())
        with patch.object(x, "gui_key", return_value="synthetic-replacement"), \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(x.main(["setup", "--provider", "deepseek", "--gui"]), 0)
        saved = x.read_config()
        self.assertEqual(saved["schema_version"], 2)
        self.assertEqual(saved["providers"]["deepseek"], {"api_key": "synthetic-replacement", "future": 42})
        self.assertEqual(path.with_name("config.v1.backup.json").read_bytes(), original)

    def test_reported_cost_and_usage_are_unknown_when_not_returned(self):
        for name in ("deepseek", "yuanbao", "brave", "bocha"):
            _, metadata = x.normalize(name, FIXTURES[name](), 5)
            self.assertIsNone(metadata["usage"])
            self.assertIsNone(metadata["cost"])

    def test_capabilities_work_offline_even_with_unreadable_config(self):
        with patch.object(x, "read_config", side_effect=AssertionError("must not read credentials")), \
                redirect_stdout(io.StringIO()) as out:
            self.assertEqual(x.main(["capabilities"]), 0)
        data = json.loads(out.getvalue())
        self.assertEqual({p["provider"] for p in data["providers"]}, set(x.ALL_PROVIDERS))
        self.assertEqual(sum(p["requires_key"] for p in data["providers"]), 6)
        self.assertTrue(next(p for p in data["providers"] if p["provider"] == "exa")["fetch"])
        self.assertFalse(next(p for p in data["providers"] if p["provider"] == "brave")["fetch"])

    def test_new_key_setup_is_hidden_and_status_never_reports_live_verification(self):
        for name in ("tavily", "exa", "brave", "bocha"):
            with patch.object(x, "gui_key", return_value="synthetic-new"), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(x.main(["setup", "--provider", name, "--gui"]), 0)
        states = x.status(x.read_config())["providers"]
        self.assertTrue(all(states[name]["configured"] for name in ("tavily", "exa", "brave", "bocha")))
        self.assertFalse(any(value["search_verified"] for value in states.values()))
        self.assertNotIn("synthetic-new", json.dumps(states))


if __name__ == "__main__":
    unittest.main()
