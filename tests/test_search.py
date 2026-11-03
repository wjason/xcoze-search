"""Offline contract tests: synthetic fixtures, never live keys or production requests."""
import argparse
from contextlib import redirect_stdout, redirect_stderr
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
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
        for p in ("deepseek", "yuanbao"):
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
            x.run_fetch(argparse.Namespace(url="https://example.com/a", provider="deepseek"), self.config)

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
        self.assertEqual(x.read_config(), {**self.config, "schema_version": 2})
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

    def test_explicit_config_root_does_not_require_home(self):
        with patch.object(x.Path, "home", side_effect=RuntimeError("Home unavailable")) as home:
            self.assertEqual(x.config_path(), Path(self.tmp.name) / "xcoze-search" / "config.json")
            home.assert_not_called()
            del os.environ["XDG_CONFIG_HOME"]
            with self.assertRaises(x.SearchError) as caught:
                x.config_path()
            self.assertEqual(caught.exception.code, "invalid_config")

    def test_setup_rejects_captured_input_without_saving(self):
        with patch.object(x.sys.stdin, "isatty", return_value=False):
            with self.assertRaises(x.SearchError):
                x.setup(argparse.Namespace(provider="deepseek", default=False, verify=False), self.config)
        self.assertFalse(x.config_path().exists())

    def test_gui_setup_saves_without_exposing_key_or_requiring_tty(self):
        secret = "synthetic-dialog-key"
        reply = subprocess.CompletedProcess([], 0, "ok:" + secret + "\n", "")
        out, err = io.StringIO(), io.StringIO()
        with patch.object(x.sys.stdin, "isatty", return_value=False), \
                patch.object(x, "gui_key_command", return_value=(["dialog-tool"], "framed")), \
                patch.object(x.subprocess, "run", return_value=reply) as launch, \
                patch.object(x, "request_api") as request, redirect_stdout(out), redirect_stderr(err):
            code = x.main(["setup", "--provider", "deepseek", "--gui", "--default"])
        self.assertEqual(code, 0)
        self.assertEqual(x.read_config()["providers"]["deepseek"]["api_key"], secret)
        self.assertEqual(x.read_config()["default_provider"], "deepseek")
        self.assertNotIn(secret, out.getvalue() + err.getvalue() + repr(launch.call_args))
        self.assertEqual(launch.call_args.kwargs["stdin"], subprocess.DEVNULL)
        self.assertEqual(launch.call_args.kwargs["stdout"], subprocess.PIPE)
        self.assertFalse(launch.call_args.kwargs.get("shell", False))
        request.assert_not_called()

    def test_gui_cancel_preserves_existing_file_and_never_verifies(self):
        path = x.save_config(self.config)
        before = path.read_bytes()
        reply = subprocess.CompletedProcess([], 0, "cancelled\n", "")
        with patch.object(x, "gui_key_command", return_value=(["dialog-tool"], "framed")), \
                patch.object(x.subprocess, "run", return_value=reply), \
                patch.object(x, "request_api") as request, redirect_stdout(io.StringIO()), \
                redirect_stderr(io.StringIO()):
            code = x.main(["setup", "--provider", "deepseek", "--gui", "--verify"])
        self.assertEqual(code, 130)
        self.assertEqual(path.read_bytes(), before)
        request.assert_not_called()

    def test_gui_failures_redact_child_output_and_timeout_payload(self):
        secret = "synthetic-sensitive-child-output"
        cases = [subprocess.CompletedProcess([], 2, secret, secret),
                 subprocess.CompletedProcess([], 0, secret, secret),
                 subprocess.TimeoutExpired(["dialog-tool"], 310, output=secret, stderr=secret),
                 FileNotFoundError(secret)]
        for reply in cases:
            out, err = io.StringIO(), io.StringIO()
            with self.subTest(kind=type(reply).__name__), \
                    patch.object(x, "gui_key_command", return_value=(["dialog-tool"], "framed")), \
                    patch.object(x.subprocess, "run", **({"side_effect": reply} if isinstance(reply, Exception)
                                                        else {"return_value": reply})), \
                    redirect_stdout(out), redirect_stderr(err):
                code = x.main(["setup", "--provider", "deepseek", "--gui"])
            self.assertNotEqual(code, 0)
            self.assertNotIn(secret, out.getvalue() + err.getvalue())
            self.assertFalse(x.config_path().exists())

    def test_gui_validation_rejects_empty_or_multiline_key_without_saving(self):
        for value in ("", "synthetic-key\ninjected"):
            reply = subprocess.CompletedProcess([], 0, "ok:" + value, "")
            with patch.object(x, "gui_key_command", return_value=(["dialog-tool"], "framed")), \
                    patch.object(x.subprocess, "run", return_value=reply), \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(x.main(["setup", "--provider", "yuanbao", "--gui"]), 1)
            self.assertFalse(x.config_path().exists())

    def test_gui_verify_uses_effective_environment_and_preserves_other_provider(self):
        x.save_config(self.config)
        os.environ["DEEPSEEK_API_KEY"] = "synthetic-environment-key"
        with patch.object(x, "gui_key", return_value="synthetic-new-key"), \
                patch.object(x, "request_api", return_value=(ds(), 1)) as request, \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = x.main(["setup", "--provider", "deepseek", "--gui", "--verify"])
        self.assertEqual(code, 0)
        self.assertEqual(request.call_args.args[2], "synthetic-environment-key")
        saved = x.read_config()
        self.assertEqual(saved["providers"]["deepseek"]["api_key"], "synthetic-new-key")
        self.assertEqual(saved["providers"]["yuanbao"], self.config["providers"]["yuanbao"])
        self.assertNotIn("default_provider", saved)

    def test_gui_failed_verification_is_reported_after_save(self):
        with patch.object(x, "gui_key", return_value="synthetic-new-key"), \
                patch.object(x, "request_api", side_effect=x.http_error(401)), \
                redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()):
            code = x.main(["setup", "--provider", "deepseek", "--gui", "--verify"])
        self.assertEqual(code, 4)
        self.assertFalse(json.loads(out.getvalue())["providers"]["deepseek"]["search_verified"])
        self.assertEqual(x.read_config()["providers"]["deepseek"]["api_key"], "synthetic-new-key")

    def test_gui_headless_environment_fails_without_launching(self):
        with patch.object(x.sys, "platform", "linux"), patch.object(x.subprocess, "run") as launch:
            with self.assertRaises(x.SearchError) as caught:
                x.gui_key("deepseek")
        self.assertEqual(caught.exception.code, "gui_unavailable")
        launch.assert_not_called()

    def test_gui_zenity_supports_masked_input_and_cancel(self):
        os.environ["DISPLAY"] = ":0"
        for returncode, output in ((0, "synthetic-linux-key\n"), (1, ""), (5, "")):
            with patch.object(x.sys, "platform", "linux"), patch.object(x.shutil, "which", return_value="/usr/bin/zenity"), \
                    patch.object(x.subprocess, "run", return_value=subprocess.CompletedProcess([], returncode, output, "")) as launch:
                if returncode:
                    with self.assertRaises(x.SearchError) as caught:
                        x.gui_key("yuanbao")
                    self.assertEqual(caught.exception.code, "cancelled")
                else:
                    self.assertEqual(x.gui_key("yuanbao"), "synthetic-linux-key")
                self.assertIn("--hide-text", launch.call_args.args[0])

    def test_cli_missing_credentials_and_no_key_echo(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = x.main(["search", "test", "--provider", "deepseek"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(err.getvalue())["error"]["code"], "missing_api_key")
        self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
