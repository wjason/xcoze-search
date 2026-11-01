#!/usr/bin/env python3
"""xcoze search: direct official search APIs; Python 3.10+, stdlib only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import getpass
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import warnings

VERSION = "0.1.0"
PROVIDERS = ("deepseek", "yuanbao")
ENDPOINTS = {
    "deepseek": "https://api.deepseek.com/v1/tools/search",
    "yuanbao": "https://api.wsa.cloud.tencent.com/SearchPro",
    "fetch": "https://api.deepseek.com/v1/tools/fetch",
}
ENV_KEYS = {"deepseek": ("DEEPSEEK_API_KEY",),
            "yuanbao": ("YUANBAO_API_KEY", "TENCENTCLOUD_WSA_APIKEY")}
KEY_URLS = {"deepseek": "https://platform.deepseek.com/api_keys",
            "yuanbao": "https://console.cloud.tencent.com/wsapi/index"}
MAX_RESPONSE = 16 * 1024 * 1024


class SearchError(Exception):
    def __init__(self, code, message, *, status=None, retryable=False):
        super().__init__(message)
        self.code, self.status, self.retryable = code, status, retryable

    def data(self):
        return {"code": self.code, "message": str(self), "http_status": self.status}


def invalid(message):
    raise SearchError("invalid_input", message)


def config_path():
    configured_root = os.environ.get("XDG_CONFIG_HOME")
    try:
        root = Path(configured_root) if configured_root is not None else Path.home() / ".config"
    except RuntimeError:
        raise SearchError("invalid_config", "Cannot determine home directory; set an absolute XDG_CONFIG_HOME.") from None
    if not root.is_absolute():
        raise SearchError("unsafe_config", "XDG_CONFIG_HOME must be absolute.")
    return root / "xcoze-search" / "config.json"


def check_config_path(path):
    if path.is_symlink() or path.parent.is_symlink():
        raise SearchError("unsafe_config", "Config file and dedicated directory must not be symlinks.")
    if os.name == "posix":
        for entry in (path.parent, path):
            if entry.exists() and stat.S_IMODE(entry.stat().st_mode) & 0o077:
                raise SearchError("unsafe_config", "Config directory/file require private permissions (700/600).")


def read_config():
    path = config_path()
    check_config_path(path)
    if not path.exists():
        return {"schema_version": 1, "providers": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if (not isinstance(data, dict) or data.get("schema_version") != 1
                or not isinstance(data.get("providers"), dict)
                or any(k not in PROVIDERS or not isinstance(v, dict)
                       for k, v in data["providers"].items())
                or data.get("default_provider") not in (*PROVIDERS, None)):
            raise ValueError
        return data
    except (ValueError, OSError, UnicodeError):
        raise SearchError("invalid_config", "Invalid local config; repair or remove it in your own terminal.") from None


def save_config(data):
    path = config_path()
    check_config_path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=".config-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return path


def validate_key(value):
    if not isinstance(value, str):
        raise SearchError("invalid_key", "API key must be non-empty ASCII without whitespace.")
    value = value.strip()
    if not value or not value.isascii() or any(c.isspace() or ord(c) < 33 or ord(c) == 127 for c in value):
        raise SearchError("invalid_key", "API key must be non-empty ASCII without whitespace.")
    return value


def credential(provider, config):
    for env in ENV_KEYS[provider]:
        if os.environ.get(env, "").strip():
            return validate_key(os.environ[env]), "environment:" + env
    stored = config["providers"].get(provider, {}).get("api_key")
    if stored is not None:
        return validate_key(stored), "local_config"
    raise SearchError("missing_api_key", "Configure %s with setup or its API key environment variable." % provider)


def configured_providers(config):
    found = []
    for provider in PROVIDERS:
        try:
            credential(provider, config)
            found.append(provider)
        except SearchError as exc:
            if exc.code != "missing_api_key":
                raise
    return found


def select_providers(requested, config):
    if requested in PROVIDERS:
        return [requested]
    if requested == "both":
        return list(PROVIDERS)
    preferred = config.get("default_provider")
    if preferred:
        credential(preferred, config)  # Never silently switch away from the chosen default.
        return [preferred]
    available = configured_providers(config)
    if not available:
        raise SearchError("missing_api_key", "Configure at least one provider using setup.")
    return [available[0]]  # Stable documented order: deepseek, yuanbao.


def validate_query(provider, query):
    if not isinstance(query, str) or not query.strip():
        invalid("Query must not be empty.")
    if provider == "deepseek" and len(query) > 128:
        invalid("DeepSeek query is limited to 128 Unicode characters; split it into shorter queries.")
    if provider == "yuanbao" and len(query.encode("utf-8")) > 1500:
        invalid("Yuanbao query is limited here to 1500 UTF-8 bytes; split it into shorter queries.")


def validate_site(site):
    if not site:
        return
    if len(site) > 253 or not re.fullmatch(r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,63}", site):
        invalid("--site requires one public domain, e.g. example.com (use punycode for IDNs).")


def search_payload(provider, args):
    validate_query(provider, args.query)
    if type(args.count) is not int or not 1 <= args.count <= 50:
        invalid("--count must be 1..50 per provider.")
    validate_site(args.site)
    if provider == "deepseek":
        if args.freshness or args.industry or args.mode is not None:
            invalid("--freshness/--industry/--mode are Yuanbao-only. Use DeepSeek query operators separately.")
        query = args.query + (" site:" + args.site if args.site else "")
        validate_query(provider, query)
        return {"query": query, "count": args.count, "need_content": args.need_content}
    if args.need_content:
        invalid("--need-content is DeepSeek-only; Yuanbao dynamic summaries are not full page content.")
    payload = {"Query": args.query}
    # Omit paid-tier options at their baseline defaults to support Yuanbao lite accounts.
    if args.count > 10:
        payload["Cnt"] = int(math.ceil(args.count / 10) * 10)
    if args.site:
        payload["Site"] = args.site
    if args.freshness:
        match = re.fullmatch(r"([dmy])(\d+)", args.freshness)
        if not match or not 1 <= int(match[2]) <= {"d": 30, "m": 12, "y": 5}[match[1]]:
            invalid("--freshness supports d1..d30, m1..m12, y1..y5.")
        payload["Freshness"] = args.freshness
    if args.industry:
        if args.industry not in ("gov", "news", "acad", "finance"):
            invalid("Invalid Yuanbao industry.")
        payload["Industry"] = args.industry
    if args.mode is not None:
        if type(args.mode) is not int or args.mode not in (0, 1, 2):
            invalid("--mode must be 0, 1, or 2.")
        payload["Mode"] = args.mode
    return payload


def public_url(url):
    try:
        parsed = urllib.parse.urlsplit(url)
        if (len(url) > 8192 or parsed.scheme not in ("https", "http") or not parsed.hostname
                or parsed.username is not None or parsed.password is not None
                or any(c.isspace() or ord(c) < 32 for c in url)):
            return False
        parsed.port
        host = parsed.hostname.lower().rstrip(".")
        if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
            return False
        try:
            return ipaddress.ip_address(host).is_global
        except ValueError:
            return "." in host
    except (ValueError, TypeError):
        return False


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def http_error(status):
    messages = {401: "API key is invalid or expired.", 402: "Provider account balance is insufficient.",
                403: "Access denied; check permissions or target-site policy.",
                404: "Endpoint or page content unavailable.", 429: "Rate limit reached; retry later."}
    return SearchError("http_error", messages.get(status, "Provider returned HTTP %s." % status),
                       status=status, retryable=status in (408, 429) or 500 <= status <= 599)


def provider_error(code):
    root = code.split(".")[0] if isinstance(code, str) else ""
    messages = {"InternalError": "Yuanbao internal error.",
                "RequestLimitExceeded": "Yuanbao rate limit exceeded.",
                "UnauthorizedOperation": "Yuanbao API key invalid or not authorized.",
                "ResourceNotFound": "Enable Yuanbao Search in the Tencent Cloud console.",
                "ResourceUnavailable": "Yuanbao unavailable; check account balance and service status.",
                "InvalidParameter": "Yuanbao rejected a parameter; check account tier and options.",
                "InvalidParameterValue": "Yuanbao rejected a parameter value."}
    # Do not echo arbitrary provider messages or unknown codes (may contain secrets/input).
    safe_code = code if root in messages and re.fullmatch(r"[A-Za-z0-9_.]{1,100}", code) else "provider_error"
    return SearchError(safe_code, messages.get(root, "Provider returned an application error."),
                       retryable=root in ("InternalError", "RequestLimitExceeded"))


def request_api(operation, payload, key, *, timeout=30, retries=1, opener=None, sleep=time.sleep):
    if operation not in ENDPOINTS or not 1 <= timeout <= 120 or retries not in (0, 1, 2):
        invalid("Invalid operation, timeout, or retry limit.")
    transport = opener or urllib.request.build_opener(NoRedirect())
    req = urllib.request.Request(ENDPOINTS[operation],
                                 data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                                 headers={"Authorization": "Bearer " + validate_key(key),
                                          "Content-Type": "application/json; charset=utf-8",
                                          "User-Agent": "xcoze-search/" + VERSION}, method="POST")
    for attempt in range(retries + 1):
        wait = min(2 ** attempt, 8)
        try:
            with transport.open(req, timeout=timeout) as response:
                if response.status != 200:
                    raise http_error(response.status)
                raw = response.read(MAX_RESPONSE + 1)
            if len(raw) > MAX_RESPONSE:
                raise SearchError("response_too_large", "Provider response exceeds 16 MiB.")
            try:
                data = json.loads(raw)
            except (ValueError, UnicodeError):
                raise SearchError("invalid_response", "Provider returned invalid JSON.") from None
            if not isinstance(data, dict):
                raise SearchError("invalid_response", "Expected a JSON object.")
            if operation == "yuanbao":
                body = data.get("Response")
                if isinstance(body, dict) and "Error" in body:
                    err = body["Error"]
                    raise provider_error(err.get("Code") if isinstance(err, dict) else None)
                if "Error" in data:
                    err = data["Error"]
                    raise provider_error(err.get("Code") if isinstance(err, dict) else None)
            elif "error" in data:
                raise SearchError("provider_error", "Provider returned an application error.")
            return data, attempt + 1
        except urllib.error.HTTPError as exc:
            error = http_error(exc.code)
            retry_after = exc.headers.get("Retry-After", "") if exc.headers else ""
            exc.close()
            try:
                wait = max(wait, float(retry_after))
            except ValueError:
                pass
        except (urllib.error.URLError, TimeoutError, OSError):
            error = SearchError("network_error", "Network/TLS failure or timeout.", retryable=True)
        except SearchError as exc:
            error = exc
        if not error.retryable or attempt == retries:
            raise error from None
        if wait > 10:
            raise SearchError("retry_later", "Server requires a longer wait; retry later.")
        sleep(wait)
    raise AssertionError("unreachable")


def text_field(item, name, *, optional=False):
    value = item.get(name)
    if value is None and optional:
        return ""
    if not isinstance(value, str):
        raise SearchError("invalid_response", "Invalid provider text field: " + name)
    return value


def normalize(provider, raw, count):
    body = raw if provider == "deepseek" else raw.get("Response")
    name = "results" if provider == "deepseek" else "Pages"
    if not isinstance(body, dict) or not isinstance(body.get(name), list):
        raise SearchError("invalid_response", "Expected provider result array: " + name)
    results = []
    for rank, item in enumerate(body[name], 1):
        if provider == "yuanbao" and isinstance(item, str):
            try:
                item = json.loads(item)
            except ValueError:
                raise SearchError("invalid_response", "Yuanbao Pages contains invalid JSON.") from None
        if not isinstance(item, dict):
            raise SearchError("invalid_response", "Result must be an object.")
        title, url = text_field(item, "title"), text_field(item, "url")
        if not public_url(url):
            raise SearchError("invalid_response", "Result URL is not a public HTTP(S) URL.")
        is_ds = provider == "deepseek"
        # Yuanbao content is a dynamic summary, never presented as fetched page content.
        result = {"provider": provider, "rank": rank, "title": title, "url": url,
                  "snippet": text_field(item, "snippet" if is_ds else "passage", optional=True),
                  "summary": text_field(item, "summary" if is_ds else "content", optional=True),
                  "content": text_field(item, "content", optional=True) if is_ds else "",
                  "content_kind": "page_content" if is_ds and item.get("content") else "search_summary",
                  "published_at": item.get("date") or None,
                  "site_name": item.get("site_name" if is_ds else "site") or None,
                  "score": item.get("rerank_score" if is_ds else "score"),
                  "score_scale": "deepseek_0_3" if is_ds else "yuanbao_0_1",
                  "authority": item.get("authority" if is_ds else "authority_level"),
                  "authority_scale": "deepseek_-1_4" if is_ds else "yuanbao_0_5",
                  "provider_fields": item}
        results.append(result)
    metadata = {"request_id": body.get("RequestId") if provider == "yuanbao" else None,
                "account_tier": body.get("Version") if provider == "yuanbao" else None,
                "provider_message": body.get("Msg") if provider == "yuanbao" else None,
                "returned_count": len(results), "shown_count": min(len(results), count)}
    return results[:count], metadata


def run_search(args, config):
    providers = select_providers(args.provider, config)
    # Validate all requests before ANY network I/O, including incompatible both-provider flags.
    payloads = {p: search_payload(p, args) for p in providers}
    if len(providers) == 2:
        for p in providers:
            credential(p, config)  # Explicit both requires both credentials; no silent single-provider search.
    output = {"ok": True, "operation": "search", "version": VERSION,
              "retrieved_at": datetime.now(timezone.utc).isoformat(),
              "query": args.query, "providers": providers, "results": [], "errors": [], "requests": [],
              "facts_verified": False}
    for p in providers:
        try:
            key, _ = credential(p, config)
            raw, attempts = request_api(p, payloads[p], key, timeout=args.timeout, retries=args.retries)
            rows, meta = normalize(p, raw, args.count)
            output["results"].extend(rows)
            output["requests"].append({"provider": p, "ok": True, "attempts": attempts, **meta})
        except SearchError as exc:
            output["errors"].append({"provider": p, **exc.data()})
            output["requests"].append({"provider": p, "ok": False})
    output["ok"] = not output["errors"]
    output["complete"] = output["ok"]
    output["empty"] = not output["results"]
    output["partial"] = bool(output["errors"]) and any(r["ok"] for r in output["requests"])
    # Retain source versions and provider order. No cross-provider score sorting or destructive deduplication.
    groups = {}
    for i, row in enumerate(output["results"]):
        parsed = urllib.parse.urlsplit(row["url"])
        canonical = urllib.parse.urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, parsed.query, ""))
        groups.setdefault(canonical, []).append(i)
    output["duplicate_groups"] = [indices for indices in groups.values() if len(indices) > 1]
    return output


def run_fetch(args, config):
    if not public_url(args.url):
        invalid("Fetch requires a public HTTP(S) URL, <=8192 characters, without embedded credentials.")
    key, _ = credential("deepseek", config)
    raw, attempts = request_api("fetch", {"url": args.url}, key, timeout=args.timeout, retries=args.retries)
    title, content = text_field(raw, "title"), text_field(raw, "content")
    return {"ok": True, "operation": "fetch", "provider": "deepseek", "url": args.url,
            "title": title, "content": content, "empty": not content.strip(), "attempts": attempts,
            "retrieved_at": datetime.now(timezone.utc).isoformat(), "facts_verified": False}


def status(config):
    states = {}
    for p in PROVIDERS:
        try:
            _, source = credential(p, config)
            states[p] = {"configured": True, "credential_source": source, "search_verified": False}
        except SearchError as exc:
            states[p] = {"configured": False, "search_verified": False, "error": exc.data()}
    return {"ok": all(s.get("error", {}).get("code", "missing_api_key") == "missing_api_key" for s in states.values()),
            "operation": "status", "version": VERSION, "default_provider": config.get("default_provider"),
            "providers": states, "message": "Local inspection only; doctor performs a live billable search."}


def doctor(args, config):
    query_args = argparse.Namespace(provider=args.provider, query="人工智能", count=1, site=None,
                                    freshness=None, industry=None, mode=None, need_content=False,
                                    timeout=args.timeout, retries=0)
    result = run_search(query_args, config)
    checks = {}
    for p in result["providers"]:
        entry = next(r for r in result["requests"] if r["provider"] == p)
        verified = entry["ok"] and any(r["provider"] == p for r in result["results"])
        checks[p] = {**entry, "search_verified": verified}
    good = all(x["search_verified"] for x in checks.values())
    return {"ok": good, "operation": "doctor", "providers": checks, "errors": result["errors"],
            "message": "Live search verified." if good else "Not all requested providers returned usable results."}


def setup(args, config):
    p = args.provider
    # setup deliberately emits no input or key value; only the user types in their own terminal.
    if not sys.stdin.isatty():
        raise SearchError("interactive_required", "Run setup in your own visible terminal; never send keys through chat or pipes.")
    print("官方密钥入口 / Official key console: " + KEY_URLS[p], file=sys.stderr)
    if p == "yuanbao":
        print("先开通元宝搜索，再在概览 > 服务 API KEY 方式创建密钥（不是腾讯云 SecretKey）。", file=sys.stderr)
    print("密钥仅输入到本机隐藏输入框；将以权限保护的明文保存在用户配置目录。", file=sys.stderr)
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        try:
            key = validate_key(getpass.getpass(p + " API Key (hidden): "))
        except getpass.GetPassWarning:
            raise SearchError("interactive_required", "This terminal cannot hide input.") from None
    config["providers"][p] = {"api_key": key}
    if args.default:
        config["default_provider"] = p
    path = save_config(config)
    print("已保存 / Saved: " + str(path), file=sys.stderr)
    if any(os.environ.get(env, "").strip() for env in ENV_KEYS[p]):
        print("提示：现有环境变量优先于刚保存的密钥；验证将使用实际生效的凭据。", file=sys.stderr)
    if args.verify:
        # Verify the effective credential, so success matches subsequent searches.
        return doctor(argparse.Namespace(provider=p, timeout=30), config)
    return {"ok": True, "operation": "setup", "provider": p, "search_verified": False,
            "message": "Saved locally; run doctor for live verification (may incur API charges)."}


def parser():
    root = argparse.ArgumentParser(description="xcoze search: DeepSeek + Tencent Yuanbao official APIs")
    root.add_argument("--version", action="version", version=VERSION)
    sub = root.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Local-only credential status; never prints keys")
    configure = sub.add_parser("setup", help="Hidden input in the user's visible terminal")
    configure.add_argument("--provider", required=True, choices=PROVIDERS)
    configure.add_argument("--default", action="store_true", help="Make this the auto provider")
    configure.add_argument("--verify", action="store_true", help="Run one live search after saving (may be billed)")
    diagnose = sub.add_parser("doctor", help="One live search per selected provider (may be billed)")
    diagnose.add_argument("--provider", choices=(*PROVIDERS, "auto", "both"), default="auto")
    search = sub.add_parser("search", help="Search; count is per provider, maximum 50")
    search.add_argument("query")
    search.add_argument("--provider", choices=(*PROVIDERS, "auto", "both"), default="auto")
    search.add_argument("--count", type=int, default=10)
    search.add_argument("--site", help="One public domain; applies to Yuanbao web results only")
    search.add_argument("--need-content", action="store_true", help="DeepSeek only")
    search.add_argument("--freshness", help="Yuanbao only: d7 / m3 / y1")
    search.add_argument("--industry", choices=("gov", "news", "acad", "finance"), help="Yuanbao paid tiers")
    search.add_argument("--mode", type=int, choices=(0, 1, 2), help="Yuanbao paid tiers: web / vertical / mixed")
    fetch = sub.add_parser("fetch", help="Fetch page Markdown with DeepSeek (requires its key)")
    fetch.add_argument("url")
    for command in (search, fetch, diagnose):
        command.add_argument("--timeout", type=int, choices=range(1, 121), metavar="1..120", default=30)
    for command in (search, fetch):
        command.add_argument("--retries", type=int, choices=(0, 1, 2), default=1)
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        config = read_config()
        if args.command == "status":
            result = status(config)
        elif args.command == "setup":
            result = setup(args, config)
        elif args.command == "doctor":
            result = doctor(args, config)
        elif args.command == "fetch":
            result = run_fetch(args, config)
        else:
            result = run_search(args, config)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 4
    except SearchError as exc:
        print(json.dumps({"ok": False, "error": exc.data()}, ensure_ascii=False), file=sys.stderr)
        return 2 if exc.code == "missing_api_key" else 1
    except (KeyboardInterrupt, EOFError):
        print('{"ok":false,"error":{"code":"cancelled","message":"Cancelled."}}', file=sys.stderr)
        return 130
    except (OSError, UnicodeError):
        print('{"ok":false,"error":{"code":"local_io_error","message":"Local I/O failed."}}', file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
