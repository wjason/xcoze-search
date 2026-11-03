#!/usr/bin/env python3
"""xcoze search: automatic public/keyed search; Python 3.10+, stdlib only."""
from __future__ import annotations

import argparse
from copy import copy, deepcopy
from datetime import datetime, timezone
import getpass
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import warnings

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from search_common import SearchError, RequestBudget, invalid, public_url, text_field, validate_site
from search_providers import REGISTRY, get_provider as get_key_provider
from public_providers import PUBLIC_REGISTRY, domain_matches
from search_routing import (ALL as ALL_REGISTRY, STRATEGIES, PLATFORMS, preferences,
                            validate_preferences, scoped_args, plan, public_plan)

VERSION = "0.4.0"
PROVIDERS = tuple(REGISTRY)
ALL_PROVIDERS = tuple(ALL_REGISTRY)
ENDPOINTS = {name: provider.endpoint for name, provider in ALL_REGISTRY.items() if provider.supports_search}
ENDPOINTS.update({name + "_fetch": p.fetch_endpoint for name, p in ALL_REGISTRY.items() if p.fetch_endpoint})
ENDPOINTS["fetch"] = REGISTRY["deepseek"].fetch_endpoint
ENV_KEYS = {name: p.env_keys for name, p in REGISTRY.items()}
KEY_URLS = {name: p.key_url for name, p in REGISTRY.items()}
MAX_RESPONSE = 16 * 1024 * 1024
CONFIG_SCHEMA = 2


def get_provider(name):
    if name in PUBLIC_REGISTRY:
        return PUBLIC_REGISTRY[name]
    return get_key_provider(name)


def validate_config(data):
    if (not isinstance(data, dict) or type(data.get("schema_version")) is not int
            or data["schema_version"] not in (1, CONFIG_SCHEMA)
            or not isinstance(data.get("providers"), dict)
            or any(not isinstance(k, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", k)
                   or not isinstance(v, dict) for k, v in data["providers"].items())
            or data.get("default_provider") not in (*ALL_PROVIDERS, None)):
        raise SearchError("invalid_config", "Unsupported or invalid config; original file has not been changed.")
    validate_preferences(data.get("search_preferences", {}))
    return data


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
        return {"schema_version": CONFIG_SCHEMA, "providers": {}}
    try:
        return validate_config(json.loads(path.read_text(encoding="utf-8")))
    except (ValueError, OSError, UnicodeError):
        raise SearchError("invalid_config", "Invalid local config; original file has not been changed.") from None


def save_config(data):
    validate_config(data)
    data = {**data, "schema_version": CONFIG_SCHEMA}
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


def migrate_config(config):
    if config["schema_version"] == CONFIG_SCHEMA:
        return {"ok": True, "operation": "migrate-config", "migrated": False, "schema_version": CONFIG_SCHEMA}
    source = config_path()
    backup = source.with_name("config.v1.backup.json")
    check_config_path(backup)
    # Exclusive backup: never replace an existing backup or follow its symlink.
    try:
        fd = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise SearchError("invalid_config", "Migration backup already exists; inspect it locally before retrying.") from None
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(source.read_bytes())
        save_config(config)
    except (OSError, SearchError):
        raise SearchError("invalid_config", "Migration failed; keep the original file and private backup for local recovery.") from None
    return {"ok": True, "operation": "migrate-config", "migrated": True,
            "schema_version": CONFIG_SCHEMA, "backup_created": True}


def validate_key(value):
    if not isinstance(value, str):
        raise SearchError("invalid_key", "API key must be non-empty ASCII without whitespace.")
    value = value.strip()
    if not value or not value.isascii() or any(c.isspace() or ord(c) < 33 or ord(c) == 127 for c in value):
        raise SearchError("invalid_key", "API key must be non-empty ASCII without whitespace.")
    return value


def credential(provider, config):
    if not get_provider(provider).requires_key:
        return "", "not_required"
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
    if requested in ALL_REGISTRY:
        return [requested]
    if requested == "both":
        return ["deepseek", "yuanbao"]  # Backward-compatible meaning, even with six providers.
    if requested == "all":
        selected = configured_providers(config)
        if not selected:
            raise SearchError("missing_api_key", "Configure at least one provider using setup.")
        return selected
    if "," in requested:
        selected = requested.split(",")
        if len(selected) != len(set(selected)) or any(p not in ALL_REGISTRY for p in selected):
            invalid("Use distinct registered provider names separated by commas.")
        return selected
    if requested != "auto":
        invalid("Unknown provider; use capabilities to list services.")
    preferred = config.get("default_provider")
    if preferred:
        credential(preferred, config)
        return [preferred]
    available = configured_providers(config)
    if not available:
        raise SearchError("missing_api_key", "Configure at least one provider using setup.")
    return [available[0]]


def validate_query(provider, query):
    get_provider(provider).validate_query(query)


def search_payload(provider, args):
    return get_provider(provider).search_payload(args)


def normalize(provider, raw, count):
    return get_provider(provider).normalize(raw, count)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def http_error(status):
    messages = {401: "API key is invalid or expired.", 402: "Provider account balance is insufficient.",
                403: "Access denied; check permissions or target-site policy.",
                404: "Endpoint or page content unavailable.", 429: "Rate limit reached; retry later.",
                432: "Provider plan usage limit reached.", 433: "Provider spending limit reached.",
                434: "Provider capacity is temporarily unavailable."}
    return SearchError("http_error", messages.get(status, "Provider returned HTTP %s." % status),
                       status=status, retryable=status in (408, 429, 434) or 500 <= status <= 599)


def request_api(operation, payload, key, *, timeout=30, retries=1, opener=None, sleep=time.sleep, budget=None):
    if operation not in ENDPOINTS or not 1 <= timeout <= 120 or retries not in (0, 1, 2):
        invalid("Invalid operation, timeout, or retry limit.")
    fetching = operation == "fetch" or operation.endswith("_fetch")
    name = "deepseek" if operation == "fetch" else operation.removesuffix("_fetch")
    provider = get_provider(name)
    transport = opener or urllib.request.build_opener(NoRedirect())
    req = provider.build_request(payload, validate_key(key) if provider.requires_key else "", VERSION, fetch=fetching)
    budget = budget or RequestBudget(retries + 1)
    for attempt in range(retries + 1):
        try:
            budget.consume(name)
        except SearchError as error:
            error.attempts = attempt
            raise
        wait = min(2 ** attempt, 8)
        try:
            with transport.open(req, timeout=timeout) as response:
                if response.status != 200:
                    if name == "duckduckgo" and response.status == 202:
                        raise SearchError("access_challenge", "DuckDuckGo returned an incomplete or verification response.",
                                          status=202, category="access")
                    raise http_error(response.status)
                raw = response.read(MAX_RESPONSE + 1)
            if len(raw) > MAX_RESPONSE:
                raise SearchError("response_too_large", "Provider response exceeds 16 MiB.")
            data = provider.decode_response(raw)
            provider.check_error(data)
            return data, attempt + 1
        except urllib.error.HTTPError as exc:
            error = http_error(exc.code)
            if not provider.requires_key and exc.code in (401, 403):
                error.category = "access"
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
        error.attempts = attempt + 1
        if not error.retryable or attempt == retries:
            raise error from None
        if wait > 10:
            later = SearchError("retry_later", "Server requires a longer wait; retry later.")
            later.attempts = attempt + 1
            raise later
        sleep(wait)
    raise AssertionError("unreachable")


def run_search(args, config, *, budget=None):
    if args.provider == "auto":
        return run_routed(args, config, budget=budget)
    # An explicit provider is a per-invocation override; free explicitly requested on this call is strict.
    if getattr(args, "strategy", None) == "free":
        plan(args, config, credential)
    args = scoped_args(args)
    providers = select_providers(args.provider, config)
    payloads = {p: search_payload(p, args) for p in providers}
    for p in providers:
        credential(p, config)  # Validate all selected keys before any network I/O.
    budget = budget or RequestBudget(getattr(args, "max_requests", 12))
    if budget.limit - budget.used < len(providers):
        raise SearchError("budget_exhausted", "Budget must allow at least one HTTP attempt per selected provider.")
    output = {"ok": True, "operation": "search", "version": VERSION,
              "retrieved_at": datetime.now(timezone.utc).isoformat(),
              "query": args.query, "providers": providers, "results": [], "errors": [], "requests": [],
              "facts_verified": False}
    for p in providers:
        started = time.monotonic()
        try:
            key, _ = credential(p, config)
            raw, attempts = request_api(p, payloads[p], key, timeout=args.timeout, retries=args.retries, budget=budget)
            try:
                rows, meta = normalize(p, raw, args.count)
                if getattr(args, "site", None):
                    rows = [r for r in rows if domain_matches(r["url"], args.site)]
                    meta["shown_count"] = len(rows)
            except SearchError as exc:
                exc.attempts = attempts
                raise
            output["results"].extend(rows)
            output["requests"].append({"provider": p, "ok": True, "attempts": attempts, **meta})
        except SearchError as exc:
            output["errors"].append({"provider": p, **exc.data()})
            output["requests"].append({"provider": p, "ok": False, "attempts": exc.attempts})
        output["requests"][-1]["elapsed_ms"] = round((time.monotonic() - started) * 1000, 2)
    output["ok"] = not output["errors"]
    output["complete"] = output["ok"]
    output["empty"] = not output["results"]
    output["partial"] = bool(output["errors"]) and any(r["ok"] for r in output["requests"])
    output["budget"] = budget.data()
    groups = {}
    for i, row in enumerate(output["results"]):
        parsed = urllib.parse.urlsplit(row["url"])
        canonical = urllib.parse.urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, parsed.query, ""))
        groups.setdefault(canonical, []).append(i)
    output["duplicate_groups"] = [indices for indices in groups.values() if len(indices) > 1]
    return output


def run_fetch(args, config, *, budget=None):
    if not public_url(args.url):
        invalid("Fetch requires a public HTTP(S) URL, <=8192 characters, without embedded credentials.")
    name = getattr(args, "provider", "auto")
    if name == "auto":
        return run_routed(args, config, budget=budget, fetch=True)
    if getattr(args, "strategy", None) == "free":
        plan(args, config, credential, fetch=True)
    provider = get_provider(name)
    if not provider.fetch_endpoint:
        raise SearchError("unsupported_operation", provider.label + " does not support fetch.")
    payload = provider.fetch_payload(args)
    key, _ = credential(name, config)
    budget = budget or RequestBudget(getattr(args, "max_requests", 3))
    operation = "fetch" if name == "deepseek" else name + "_fetch"
    raw, attempts = request_api(operation, payload, key, timeout=getattr(args, "timeout", 30),
                                retries=getattr(args, "retries", 1), budget=budget)
    try:
        data = provider.normalize_fetch(raw, args.url)
    except SearchError as error:
        error.attempts = attempts
        raise
    return {"ok": True, "operation": "fetch", "provider": name, "url": args.url, **data,
            "empty": not data["content"].strip(), "attempts": attempts, "budget": budget.data(),
            "provider_metadata": provider.metadata(raw, [], 0),
            "retrieved_at": datetime.now(timezone.utc).isoformat(), "facts_verified": False}


def run_routed(args, config, *, budget=None, fetch=False):
    route = plan(args, config, credential, fetch=fetch)
    scoped = scoped_args(args)
    budget = budget or RequestBudget(getattr(args, "max_requests", 3 if fetch else 12))
    started = time.monotonic()
    seconds = getattr(args, "max_seconds", 45)
    requests, errors, rows, content, duplicates = [], [], [], None, []
    for name in route["candidates"][:route["max_sources"]]:
        remaining = seconds - (time.monotonic() - started)
        if remaining < 1 or not budget.data()["remaining"]:
            errors.append({"provider": name, "code": "budget_exhausted", "category": "budget",
                           "message": "Time or HTTP attempt budget exhausted.", "attempts": 0})
            break
        one = copy(scoped)
        one.provider = name
        one.timeout = min(getattr(args, "timeout", 30), remaining)
        one.retries = 0  # Smart fallback uses a different allowed source, not repeated retries.
        call_started = time.monotonic()
        before = budget.used
        try:
            if fetch:
                output = run_fetch(one, config, budget=budget)
                usable = bool(output.get("content", "").strip()) or output.get("content_kind") == "discussion_item"
                requests.append({"provider": name, "ok": usable, "attempts": budget.used - before})
                if usable: content = output
            else:
                output = run_search(one, config, budget=budget)
                requests.extend(output["requests"])
                errors.extend(output["errors"])
                rows = output["results"]
                duplicates = output["duplicate_groups"]
                usable = bool(rows)
            if usable:
                requests[-1]["elapsed_ms"] = round((time.monotonic() - call_started) * 1000, 2)
                break
        except SearchError as exc:
            errors.append({"provider": name, **exc.data()})
            requests.append({"provider": name, "ok": False, "attempts": budget.used - before})
        requests[-1]["elapsed_ms"] = round((time.monotonic() - call_started) * 1000, 2)
        # An access challenge is not proof of no matches. No browser or challenge solver is launched.
    routing = {**public_plan(route), "attempted_providers": [r["provider"] for r in requests],
               "stop_reason": "usable_results" if rows or content else "no_usable_results_within_limits",
               "agent_action": "Assess relevance, freshness and primary sources; search a remaining candidate only for an evidence gap."}
    if content:
        return {**content, "routing": routing, "requests": requests, "errors": errors,
                "partial": bool(errors), "budget": budget.data()}
    return {"ok": bool(rows), "operation": "fetch" if fetch else "search", "version": VERSION,
            "retrieved_at": datetime.now(timezone.utc).isoformat(), "query": getattr(args, "query", None),
            "url": getattr(args, "url", None), "providers": [r["provider"] for r in requests],
            "results": rows, "requests": requests, "errors": errors, "routing": routing,
            "empty": not rows, "partial": bool(rows and errors), "complete": bool(rows),
            "duplicate_groups": duplicates, "facts_verified": False, "budget": budget.data()}


def update_preferences(args, config):
    updated = deepcopy(config)
    if getattr(args, "reset", False):
        updated.pop("search_preferences", None)
        updated.pop("default_provider", None)
    else:
        settings = preferences(updated)
        if args.strategy is not None: settings["strategy"] = args.strategy
        if args.max_sources is not None: settings["max_sources"] = args.max_sources
        disabled = set(settings["disabled_providers"])
        disabled.update(args.disable or [])
        disabled.difference_update(args.enable or [])
        settings["disabled_providers"] = sorted(disabled)
        updated["search_preferences"] = settings
        if args.provider == "auto": updated.pop("default_provider", None)
        elif args.provider: updated["default_provider"] = args.provider
    validate_config(updated)
    changing = args.reset or args.strategy is not None or args.max_sources is not None or args.provider or args.disable or args.enable
    if changing:
        if config["schema_version"] == 1 and config_path().exists(): migrate_config(config)
        save_config(updated)
    return {"ok": True, "operation": "preferences", "saved": bool(changing),
            "preferences": preferences(updated), "default_provider": updated.get("default_provider"),
            "message": "Per-request provider/strategy overrides take precedence; no network requests sent."}


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
            "schema_version": config["schema_version"], "migration_available": config["schema_version"] == 1,
            "providers": states, "preferences": preferences(config),
            "keyless": {p: {"requires_key": False, "search": a.supports_search, "fetch": bool(a.fetch_endpoint),
                             "search_verified": False} for p, a in PUBLIC_REGISTRY.items()},
            "default_strategy": preferences(config)["strategy"],
            "message": "Local inspection only; keyless access is not a connectivity check. Doctor performs live requests."}


def doctor(args, config):
    query_args = argparse.Namespace(provider=args.provider, query="人工智能", count=1, site=None,
                                    freshness=None, industry=None, mode=None, need_content=False,
                                    timeout=args.timeout, retries=0, max_requests=getattr(args, "max_requests", 12))
    result = run_search(query_args, config)
    checks = {}
    for p in result["providers"]:
        entry = next(r for r in result["requests"] if r["provider"] == p)
        verified = entry["ok"] and any(r["provider"] == p for r in result["results"])
        checks[p] = {**entry, "search_verified": verified}
    good = bool(checks) and all(x["search_verified"] for x in checks.values())
    return {"ok": good, "operation": "doctor", "providers": checks, "errors": result["errors"], "budget": result["budget"],
            "message": "Live search verified." if good else "Not all requested providers returned usable results."}


def gui_key_command(provider):
    """Build a local password dialog command. Arguments never contain a key."""
    if provider not in PROVIDERS:
        invalid("Unknown provider.")
    label = REGISTRY[provider].label
    message = ("请输入 " + label + " API Key。密钥将以权限保护的明文保存在本机。"
               "如已选择验证，保存后将执行一次可能计费的搜索。")
    if sys.platform == "darwin":
        script = '''try
    set response to display dialog "%s" default answer "" with hidden answer with title "xcoze search" buttons {"取消", "保存"} default button "保存" cancel button "取消" giving up after 300
    if gave up of response then return "cancelled"
    return "ok:" & text returned of response
on error number -128
    return "cancelled"
end try''' % message
        return ["/usr/bin/osascript", "-e", script], "framed"
    if sys.platform == "win32":
        # Native Windows PowerShell + WinForms; no third-party Python GUI package.
        script = r'''$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$form = New-Object System.Windows.Forms.Form
$form.Text = 'xcoze search'
$form.ClientSize = New-Object System.Drawing.Size(480, 180)
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$form.MinimizeBox = $false
$form.TopMost = $true
$label = New-Object System.Windows.Forms.Label
$label.Text = '%s'
$label.Location = New-Object System.Drawing.Point(15, 12)
$label.Size = New-Object System.Drawing.Size(450, 65)
$keyBox = New-Object System.Windows.Forms.TextBox
$keyBox.Location = New-Object System.Drawing.Point(15, 82)
$keyBox.Size = New-Object System.Drawing.Size(450, 25)
$keyBox.UseSystemPasswordChar = $true
$save = New-Object System.Windows.Forms.Button
$save.Text = '保存'
$save.Location = New-Object System.Drawing.Point(285, 130)
$save.DialogResult = [System.Windows.Forms.DialogResult]::OK
$cancel = New-Object System.Windows.Forms.Button
$cancel.Text = '取消'
$cancel.Location = New-Object System.Drawing.Point(375, 130)
$cancel.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
$form.Controls.AddRange(@($label, $keyBox, $save, $cancel))
$form.AcceptButton = $save
$form.CancelButton = $cancel
$form.Add_Shown({[void]$keyBox.Focus()})
try {
    if ($form.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        [Console]::Write('ok:' + $keyBox.Text)
    } else {
        [Console]::Write('cancelled')
    }
} finally {
    $keyBox.Clear()
    $form.Dispose()
}''' % message
        # Encode the script, not the secret, to avoid Windows PowerShell's ANSI
        # command-line parsing corrupting the Chinese labels on some systems.
        import base64
        encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
        return ["powershell.exe", "-NoProfile", "-STA", "-NonInteractive", "-EncodedCommand", encoded], "framed"
    if sys.platform.startswith("linux") and (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        executable = shutil.which("zenity")
        if executable:
            return [executable, "--entry", "--hide-text", "--title=xcoze search", "--text=" + message,
                    "--timeout=300"], "raw"
    raise SearchError("gui_unavailable", "No supported local desktop dialog. Use setup in your own visible terminal, or managed environment variables.")


def gui_key(provider):
    command, protocol = gui_key_command(provider)
    try:
        # Capture the dialog's output inside this process; never relay child
        # stdout/stderr, even on failure. No shell, clipboard, or key argument.
        reply = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, encoding="utf-8", timeout=310, check=False)
    except FileNotFoundError:
        raise SearchError("gui_unavailable", "Local dialog tool is unavailable; use your own visible terminal.") from None
    except subprocess.TimeoutExpired:
        raise SearchError("cancelled", "Local key input timed out; no changes saved.") from None
    except (OSError, UnicodeError):
        raise SearchError("gui_failed", "Local key dialog failed; no changes saved.") from None
    if protocol == "raw" and reply.returncode in (1, 5):
        raise SearchError("cancelled", "Local key input cancelled; no changes saved.")
    if reply.returncode:
        raise SearchError("gui_failed", "Local key dialog failed; no changes saved.")
    value = reply.stdout.rstrip("\r\n")
    if protocol == "framed":
        if value == "cancelled":
            raise SearchError("cancelled", "Local key input cancelled; no changes saved.")
        if not value.startswith("ok:"):
            raise SearchError("gui_failed", "Local key dialog returned an invalid response; no changes saved.")
        value = value[3:]
    return validate_key(value)


def setup(args, config):
    p = args.provider
    graphical = getattr(args, "gui", False)
    if not graphical and not sys.stdin.isatty():
        raise SearchError("interactive_required", "Run setup in your own visible terminal; never send keys through chat or pipes.")
    print("官方密钥入口 / Official key console: " + KEY_URLS[p], file=sys.stderr)
    if REGISTRY[p].setup_hint:
        print(REGISTRY[p].setup_hint, file=sys.stderr)
    print("密钥仅输入到本机隐藏输入框；将以权限保护的明文保存在用户配置目录。", file=sys.stderr)
    if graphical:
        key = gui_key(p)
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            try:
                key = validate_key(getpass.getpass(p + " API Key (hidden): "))
            except getpass.GetPassWarning:
                raise SearchError("interactive_required", "This terminal cannot hide input.") from None
    if config["schema_version"] == 1 and config_path().exists():
        migrate_config(config)  # Only after successful input; cancellation never migrates.
    config["providers"][p] = {**config["providers"].get(p, {}), "api_key": key}
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
    root = argparse.ArgumentParser(description="xcoze search: automatic keyless and keyed search for Agents")
    root.add_argument("--version", action="version", version=VERSION)
    sub = root.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Local-only credential status; never prints keys")
    sub.add_parser("migrate-config", help="Back up and explicitly migrate v1 config to v2")
    prefs = sub.add_parser("preferences", help="Show/save strategy without network calls or exposing keys")
    prefs.add_argument("--strategy", choices=STRATEGIES)
    prefs.add_argument("--provider", choices=("auto", *ALL_PROVIDERS))
    prefs.add_argument("--max-sources", type=int, choices=(1, 2, 3))
    prefs.add_argument("--disable", choices=ALL_PROVIDERS, action="append")
    prefs.add_argument("--enable", choices=ALL_PROVIDERS, action="append")
    prefs.add_argument("--reset", action="store_true")
    capabilities = sub.add_parser("capabilities", help="Offline provider capabilities, limits and key links")
    capabilities.add_argument("--provider", choices=ALL_PROVIDERS)
    configure = sub.add_parser("setup", help="Hidden local input: desktop dialog or user's visible terminal")
    configure.add_argument("--provider", required=True, choices=PROVIDERS)
    configure.add_argument("--gui", action="store_true", help="Open a local hidden-input dialog; safe to launch from an agent")
    configure.add_argument("--default", action="store_true", help="Make this the auto provider")
    configure.add_argument("--verify", action="store_true", help="Run one live search after saving (may be billed)")
    diagnose = sub.add_parser("doctor", help="One live search per selected provider (may be billed)")
    diagnose.add_argument("--provider", default="auto", help="Name, comma-separated names, auto, both (DeepSeek/Yuanbao), or all configured")
    search = sub.add_parser("search", help="Search; count is per provider, maximum 50")
    search.add_argument("query")
    search.add_argument("--provider", default="auto", help="Name, comma-separated names, auto, both (DeepSeek/Yuanbao), or all configured")
    search.add_argument("--count", type=int, default=10)
    search.add_argument("--site", help="One public domain; see each provider's supported semantics")
    search.add_argument("--platform", choices=tuple(PLATFORMS), help="Target platform; public-index coverage is not a native site search")
    search.add_argument("--need-content", action="store_true", help="Explicit page content: DeepSeek, Tavily or Exa")
    search.add_argument("--freshness", help="Provider-native time filter; see capabilities and providers.md")
    search.add_argument("--industry", choices=("gov", "news", "acad", "finance"), help="Yuanbao paid tiers")
    search.add_argument("--mode", type=int, choices=(0, 1, 2), help="Yuanbao paid tiers: web / vertical / mixed")
    search.add_argument("--start-date", help="Tavily/Exa: YYYY-MM-DD")
    search.add_argument("--end-date", help="Tavily/Exa: YYYY-MM-DD")
    search.add_argument("--country", help="Brave: country code")
    search.add_argument("--language", help="Brave: search language")
    search.add_argument("--extra-snippets", action="store_true", help="Brave: request additional snippets")
    search.add_argument("--include-answer", action="store_true", help="Tavily: explicit generated answer, separately returned")
    search.add_argument("--depth", help="Tavily: basic/advanced/fast/ultra-fast; default basic")
    fetch = sub.add_parser("fetch", help="Read a URL; auto prefers keyless readers, or specify a supported source")
    fetch.add_argument("url")
    fetch.add_argument("--provider", choices=("auto", *ALL_PROVIDERS), default="auto")
    for command in (search, fetch):
        command.add_argument("--strategy", choices=STRATEGIES, help="Override saved strategy for this invocation")
        command.add_argument("--max-sources", type=int, choices=(1, 2, 3), help="Auto: at most this many sources including fallbacks")
        command.add_argument("--max-seconds", type=int, choices=range(1, 301), metavar="1..300", default=45,
                             help="Auto: wall time budget; each request is clipped to remaining time")
        command.add_argument("--highlights", action="store_true", help="Exa: explicitly request excerpts")
        command.add_argument("--summary", action="store_true", help="Exa/Bocha search or Exa fetch: explicit summary")
    for command in (search, fetch, diagnose):
        command.add_argument("--max-requests", type=int, choices=range(1, 1001), metavar="1..1000", default=12 if command != fetch else 3,
                             help="Maximum HTTP attempts including retries in this invocation")
    for command in (search, fetch, diagnose):
        command.add_argument("--timeout", type=int, choices=range(1, 121), metavar="1..120", default=30)
    for command in (search, fetch):
        command.add_argument("--retries", type=int, choices=(0, 1, 2), default=1)
    sub.add_parser("plan", parents=[search], add_help=False, help="Preview a search route offline; uses local credential presence only")
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "capabilities":
            names = [args.provider] if args.provider else ALL_PROVIDERS
            print(json.dumps({"ok": True, "operation": "capabilities", "version": VERSION,
                              "providers": [get_provider(name).capabilities() for name in names]}, ensure_ascii=False, indent=2))
            return 0
        config = read_config()
        if args.command == "migrate-config":
            result = migrate_config(config)
        elif args.command == "status":
            result = status(config)
        elif args.command == "preferences":
            result = update_preferences(args, config)
        elif args.command == "plan":
            result = {"ok": True, "operation": "plan", "network_requests": 0,
                      "routing": public_plan(plan(args, config, credential))}
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
        return 130 if exc.code == "cancelled" else 2 if exc.code == "missing_api_key" else 1
    except (KeyboardInterrupt, EOFError):
        print('{"ok":false,"error":{"code":"cancelled","message":"Cancelled."}}', file=sys.stderr)
        return 130
    except (OSError, UnicodeError):
        print('{"ok":false,"error":{"code":"local_io_error","message":"Local I/O failed."}}', file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
