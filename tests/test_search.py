"""Offline contract tests: synthetic fixtures, never live keys or production requests."""
import argparse
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
import urllib.request

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "xcoze_search.py"
spec = importlib.util.spec_from_file_location("xcoze_search", SCRIPT)
x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)


def ds(url="https://example.com/a", content="page", summary="ds summary"):
    return {"results": [{"title": "Title", "url": url, "snippet": "snippet", "summary": summary,
                         "content": content, "date": None, "rerank_score": 2.5}]}


def yb(summary="dynamic summary"):
    return {"Response": {"Pages": [json.dumps({"title": "Title Y", "url": "https://example.com/a#section",
                                               "passage": "passage", "content": summary, "score": .9})],
                         "Version": "standard", "RequestId": "synthetic-request"}}


def args(**kw):
    values = dict(query="test", provider="auto", count=5, site=None, need_content=False,
                  freshness=None, industry=None, mode=None, timeout=1, retries=0)
    values.update(kw)
    return argparse.Namespace(**values)


class Reply:
    status = 200
    def __init__(self, data):
        self.data = data if isinstance(data, bytes) else json.dumps(data).encode()
    def __enter__(self): return self
    def __exit__(self, *exc): pass
    def read(self, n): return self.data[:n]


class QueueTransport:
    def __init__(self, *responses):
        self.responses, self.requests = list(responses), []
    def open(self, req, timeout):
        self.requests.append(req)
        item = self.responses.pop(0)
        if isinstance(item, Exception): raise item
        return Reply(item)


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"XDG_CONFIG_HOME": self.tmp.name}, clear=True)
        self.env.start()
        self.config = {"schema_version": 1, "providers": {
            "deepseek": {"api_key": "synthetic-ds"}, "yuanbao": {"api_key": "synthetic-yb"}}}
    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_bearer_and_fixed_official_endpoints(self):
        for p in x.PROVIDERS:
            transport = QueueTransport(ds() if p == "deepseek" else yb())
            x.request_api(p, {"query": "test"}, "synthetic-key", opener=transport)
            req = transport.requests[0]
            self.assertEqual(req.full_url, x.ENDPOINTS[p])
            self.assertEqual(req.get_header("Authorization"), "Bearer synthetic-key")
            self.assertEqual(req.get_method(), "POST")

    def test_redirect_handler_blocks_key_forwarding(self):
        req = urllib.request.Request(x.ENDPOINTS["deepseek"])
        self.assertIsNone(x.NoRedirect().redirect_request(req, None, 302, "", {}, "https://evil.example"))
        transport = QueueTransport(urllib.error.HTTPError(req.full_url, 302, "", {}, io.BytesIO(b"secret")))
        with self.assertRaises(x.SearchError):
            x.request_api("deepseek", {}, "synthetic", opener=transport)
        self.assertEqual(len(transport.requests), 1)

    def test_retryable_status_bounded(self):
        transport = QueueTransport(urllib.error.HTTPError("", 429, "", {}, io.BytesIO()), ds())
        sleeps = []
        data, attempts = x.request_api("deepseek", {}, "synthetic", opener=transport, sleep=sleeps.append)
        self.assertEqual(attempts, 2)
        self.assertEqual(len(sleeps), 1)
        self.assertIn("results", data)

    def test_auth_and_balance_are_not_retried_or_leaked(self):
        for status in (401, 402):
            transport = QueueTransport(urllib.error.HTTPError("", status, "synthetic-key", {}, io.BytesIO(b"synthetic-key")))
            with self.assertRaises(x.SearchError) as caught:
                x.request_api("deepseek", {}, "synthetic-key", retries=2, opener=transport)
            self.assertNotIn("synthetic-key", str(caught.exception))
            self.assertEqual(len(transport.requests), 1)

    def test_retry_after_does_not_create_long_wait(self):
        transport = QueueTransport(urllib.error.HTTPError("", 429, "", {"Retry-After": "60"}, io.BytesIO()))
        with self.assertRaises(x.SearchError) as caught:
            x.request_api("deepseek", {}, "synthetic", opener=transport)
        self.assertEqual(caught.exception.code, "retry_later")

    def test_yuanbao_http200_business_error_not_success(self):
        transport = QueueTransport({"Response": {"Error": {"Code": "UnauthorizedOperation", "Message": "synthetic-key"}}})
        with self.assertRaises(x.SearchError) as caught:
            x.request_api("yuanbao", {}, "synthetic", opener=transport)
        self.assertEqual(caught.exception.code, "UnauthorizedOperation")
        self.assertNotIn("synthetic-key", str(caught.exception))

    def test_yuanbao_rate_limit_retries(self):
        transport = QueueTransport({"Response": {"Error": {"Code": "RequestLimitExceeded"}}}, yb())
        _, attempts = x.request_api("yuanbao", {}, "synthetic", opener=transport, sleep=lambda _: None)
        self.assertEqual(attempts, 2)

    def test_bad_or_oversize_response(self):
        for data in (b"not json", b"[]", b"x" * (x.MAX_RESPONSE + 1)):
            with self.assertRaises(x.SearchError):
                x.request_api("deepseek", {}, "synthetic", opener=QueueTransport(data))

    def test_mapping_and_summary_boundary(self):
        rows, meta = x.normalize("yuanbao", yb(), 5)
        self.assertEqual(rows[0]["snippet"], "passage")
        self.assertEqual(rows[0]["summary"], "dynamic summary")
        self.assertEqual(rows[0]["content"], "")
        self.assertEqual(rows[0]["content_kind"], "search_summary")
        self.assertEqual(meta["request_id"], "synthetic-request")
        self.assertIsNone(rows[0]["published_at"])
        self.assertNotEqual(rows[0]["score_scale"], x.normalize("deepseek", ds(), 5)[0][0]["score_scale"])

    def test_yuanbao_object_entry_and_lite_optional_fields(self):
        raw = {"Response": {"Pages": [{"title": "t", "url": "https://example.com", "passage": "p"}]}}
        rows, _ = x.normalize("yuanbao", raw, 1)
        self.assertEqual(rows[0]["summary"], "")
        self.assertEqual(rows[0]["provider_fields"]["passage"], "p")

    def test_corrupt_page_is_not_silently_dropped(self):
        for raw in ({"Response": {"Pages": ["not JSON"]}}, {"Response": {"Pages": [3]}}, {}):
            with self.assertRaises(x.SearchError): x.normalize("yuanbao", raw, 1)

    def test_query_limits_and_payloads(self):
        with self.assertRaises(x.SearchError): x.search_payload("deepseek", args(query="中" * 129))
        with self.assertRaises(x.SearchError): x.search_payload("yuanbao", args(query="中" * 501))
        with self.assertRaises(x.SearchError): x.search_payload("deepseek", args(query="a" * 128, site="example.com"))
        self.assertEqual(x.search_payload("yuanbao", args()), {"Query": "test"})
        self.assertEqual(x.search_payload("yuanbao", args(count=11))["Cnt"], 20)
        self.assertEqual(x.search_payload("deepseek", args(site="example.com"))["query"], "test site:example.com")

    def test_cross_provider_flags_fail_before_network(self):
        with patch.object(x, "request_api") as request:
            for flags in ({"need_content": True}, {"freshness": "d7"}, {"mode": 1}):
                with self.assertRaises(x.SearchError): x.run_search(args(provider="both", **flags), self.config)
            request.assert_not_called()

    def test_bad_filters_rejected(self):
        for flags in ({"site": "https://example.com"}, {"freshness": "d31"}, {"freshness": "y6"}, {"count": 0}):
            with self.assertRaises(x.SearchError): x.search_payload("yuanbao", args(**flags))

    def test_auto_default_and_no_silent_fallback(self):
        self.assertEqual(x.select_providers("auto", self.config), ["deepseek"])
        self.config["default_provider"] = "yuanbao"
        self.assertEqual(x.select_providers("auto", self.config), ["yuanbao"])
        del self.config["providers"]["yuanbao"]
        with self.assertRaises(x.SearchError): x.select_providers("auto", self.config)
        with patch.object(x, "request_api", side_effect=x.http_error(401)) as request:
            result = x.run_search(args(provider="deepseek"), self.config)
            self.assertFalse(result["ok"])
            self.assertEqual(request.call_count, 1)

    def test_both_requires_both_keys_before_network(self):
        del self.config["providers"]["yuanbao"]
        with patch.object(x, "request_api") as request:
            with self.assertRaises(x.SearchError): x.run_search(args(provider="both"), self.config)
            request.assert_not_called()

    def test_both_preserves_duplicate_versions(self):
        with patch.object(x, "request_api", side_effect=[(ds(), 1), (yb(), 1)]):
            result = x.run_search(args(provider="both"), self.config)
        self.assertTrue(result["ok"])
        self.assertEqual(result["duplicate_groups"], [[0, 1]])
        self.assertEqual(len(result["results"]), 2)
        self.assertNotEqual(result["results"][0]["summary"], result["results"][1]["summary"])

    def test_partial_and_empty_are_distinct(self):
        with patch.object(x, "request_api", side_effect=[(ds(), 1), x.http_error(401)]):
            result = x.run_search(args(provider="both"), self.config)
        self.assertFalse(result["ok"])
        self.assertTrue(result["partial"])
        self.assertFalse(result["empty"])
        with patch.object(x, "request_api", return_value=({"results": []}, 1)):
            result = x.run_search(args(provider="deepseek"), self.config)
        self.assertTrue(result["ok"])
        self.assertTrue(result["empty"])
        self.assertFalse(result["partial"])

    def test_fetch_url_and_provider_boundary(self):
        for url in ("file:///tmp/a", "http://127.0.0.1/a", "http://localhost/a", "https://user:pass@example.com"):
            with patch.object(x, "request_api") as request:
                with self.assertRaises(x.SearchError): x.run_fetch(argparse.Namespace(url=url), self.config)
                request.assert_not_called()
        del self.config["providers"]["deepseek"]
        with self.assertRaises(x.SearchError):
            x.run_fetch(argparse.Namespace(url="https://example.com/a"), self.config)

    def test_doctor_empty_is_not_verified(self):
        with patch.object(x, "request_api", return_value=({"results": []}, 1)):
            result = x.doctor(argparse.Namespace(provider="deepseek", timeout=1), self.config)
        self.assertFalse(result["ok"])
        self.assertFalse(result["providers"]["deepseek"]["search_verified"])

    def test_status_offline_redacted_and_env_precedence(self):
        os.environ["YUANBAO_API_KEY"] = "synthetic-primary"
        os.environ["TENCENTCLOUD_WSA_APIKEY"] = "synthetic-alias"
        self.assertEqual(x.credential("yuanbao", self.config), ("synthetic-primary", "environment:YUANBAO_API_KEY"))
        with patch.object(x, "request_api") as request:
            result = x.status(self.config)
            request.assert_not_called()
        self.assertNotIn("synthetic", json.dumps(result))
        self.assertFalse(result["providers"]["yuanbao"]["search_verified"])

    def test_config_roundtrip_permissions_and_symlinks(self):
        path = x.save_config(self.config)
        self.assertEqual(x.read_config(), self.config)
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
            path.chmod(0o644)
            with self.assertRaises(x.SearchError): x.read_config()
            path.chmod(0o600)
            saved = path.with_name("backup.json")
            path.rename(saved)
            path.symlink_to(saved)
            with self.assertRaises(x.SearchError): x.read_config()

    def test_setup_rejects_captured_input_without_saving(self):
        with patch.object(x.sys.stdin, "isatty", return_value=False):
            with self.assertRaises(x.SearchError):
                x.setup(argparse.Namespace(provider="deepseek", default=False, verify=False), self.config)
        self.assertFalse(x.config_path().exists())

    def test_cli_missing_credentials_and_no_key_echo(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = x.main(["search", "test"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(err.getvalue())["error"]["code"], "missing_api_key")
        self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
