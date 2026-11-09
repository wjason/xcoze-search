#!/usr/bin/env python3
"""Bounded, explicitly live comparison of free / DeepSeek / default Smart retrieval."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from unittest.mock import patch

import xcoze_search as search

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODES = ("free", "deepseek", "smart")
MODES = DEFAULT_MODES + ("browser",)


def load_cases(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = data.get("cases")
    if (data.get("schema_version") != 1 or not isinstance(cases, list) or not cases
            or any(not isinstance(c, dict) or not isinstance(c.get("id"), str)
                   or not isinstance(c.get("query"), str) or not c["query"].strip() for c in cases)
            or len({c["id"] for c in cases}) != len(cases)):
        raise ValueError("Invalid benchmark corpus.")
    return data


def query_args(case, mode, *, count=5, timeout=15):
    argv = ["search", case["query"], "--count", str(count), "--timeout", str(timeout),
            "--retries", "0", "--max-seconds", str(timeout * 2 + 1)]
    if case.get("platform"): argv.extend(["--platform", case["platform"]])
    if case.get("intent"): argv.extend(["--intent", case["intent"]])
    for field in ("language", "site"):
        if case.get(field): argv.extend(["--" + field, case[field]])
    if mode == "browser":
        argv.extend(["--provider", "browser", "--strategy", "free"])
    elif mode == "deepseek":
        argv.extend(["--provider", "deepseek"])
        if case.get("deepseek_query"): argv[1] = case["deepseek_query"]
    else:
        argv.extend(["--strategy", mode])
    if mode != "deepseek":
        for field in ("start_date", "end_date"):
            if case.get(field): argv.extend(["--" + field.replace("_", "-"), case[field]])
    return search.parser().parse_args(argv)


def run_cell(case, mode, config, budget, *, count=5, timeout=15, keyless=False, without_exa=False):
    args = query_args(case, mode, count=count, timeout=timeout)
    original = search.request_api
    receipts = []

    def trace(operation, payload, key, **kwargs):
        # Never retain or print the key, payload or raw provider response.
        name = "deepseek" if operation == "fetch" else operation.removesuffix("_fetch")
        if without_exa and name in ("exa", "exa-free"):
            raise AssertionError("Outage benchmark rejected Exa dispatch before transmission.")
        if (keyless or mode in ("free", "browser")) and (search.get_provider(name).requires_key or key):
            raise AssertionError("Free benchmark rejected a keyed API before transmission.")
        started = time.perf_counter()
        try:
            raw, attempts = original(operation, payload, key, **kwargs)
        except search.SearchError as exc:
            receipts.append({"source": operation, "ok": False, "attempts": exc.attempts,
                             "error_code": exc.code, "http_status": exc.status,
                             "billable_success": None if operation == "deepseek" and exc.code in (
                                 "invalid_response", "response_too_large") else False,
                             "elapsed_ms": round((time.perf_counter() - started) * 1000, 2)})
            raise
        receipts.append({"source": operation, "ok": True, "attempts": attempts,
                         "billable_success": bool(raw.get("results")) if operation == "deepseek" else False,
                         "elapsed_ms": round((time.perf_counter() - started) * 1000, 2)})
        return raw, attempts

    started = time.perf_counter()
    search.request_api = trace
    def no_key_credential(provider, unused_config):
        if search.get_provider(provider).requires_key:
            raise search.SearchError("missing_api_key", "Keyed providers disabled for this benchmark.")
        return "", "not_required"

    try:
        if keyless:
            with patch.object(search, "credential", side_effect=no_key_credential):
                result = search.run_search(args, config, budget=budget)
        else:
            result = search.run_search(args, config, budget=budget)
    except search.SearchError as exc:
        result = {"ok": False, "results": [], "errors": [exc.data()], "requests": []}
    finally:
        search.request_api = original
    elapsed = round((time.perf_counter() - started) * 1000, 2)
    rows = []
    for item in result.get("results", []):
        rows.append({k: item.get(k) for k in ("provider", "rank", "title", "url", "published_at", "content_kind")})
        text = "\n".join(str(item.get(k) or "") for k in ("snippet", "summary", "content"))
        if item.get("highlights"): text += "\n" + "\n".join(item["highlights"])
        rows[-1].update(evidence_text=text[:1800], evidence_truncated=len(text) > 1800)
    return {"id": case["id"], "mode": mode, "query_sent": args.query, "ok": result["ok"],
            "expected_provider_returned": (any(r["provider"] == case["expected_provider"] for r in rows)
                                           if case.get("expected_provider") else None),
            "elapsed_ms": elapsed, "receipts": receipts, "sources": rows,
            "routing": result.get("routing"), "errors": result.get("errors", []),
            "execution_summary": result.get("execution_summary"),
            "requests": [{k: r[k] for k in ("provider", "ok", "attempts", "elapsed_ms", "execution",
                         "browser_engine", "browser_navigation_attempts", "browser_commands", "browser_cleanup_verified",
                         "dropped_irrelevant_count", "shown_count", "returned_count",
                         "browser_failure_stage", "browser_explicit_no_matches", "browser_stage_timings_ms") if k in r}
                         for r in result.get("requests", [])],
            "semantic_quality_assessed": False}


def execute(corpus, *, live=False, modes=DEFAULT_MODES, rounds=1, limit=6, count=5,
            max_requests=36, timeout=15, progress=None, keyless=False, without_exa=False):
    if not modes or len(set(modes)) != len(modes) or any(m not in MODES for m in modes):
        raise ValueError("Choose distinct free, deepseek, smart and/or explicit browser diagnostic modes.")
    if keyless and "deepseek" in modes:
        raise ValueError("Keyless benchmark cannot include DeepSeek mode.")
    if not 1 <= rounds <= 3 or not 1 <= limit <= 100 or not 1 <= count <= 10 or not 1 <= timeout <= 60:
        raise ValueError("Invalid benchmark limits.")
    cases = corpus["cases"][:limit]
    for case in cases:
        for mode in modes: query_args(case, mode, count=count, timeout=timeout)
    budget = search.RequestBudget(max_requests)
    report = {"operation": "benchmark", "version": search.VERSION, "live": live,
              "started_at": datetime.now(timezone.utc).isoformat(), "corpus_as_of": corpus.get("as_of"),
              "modes": list(modes), "keyless": keyless, "without_exa": without_exa,
              "rounds": rounds, "count": count, "timeout_seconds": timeout,
              "cases": cases, "cells": [], "semantic_quality_assessed": False,
              "scope": "retrieval only; process startup, final-answer generation and validation reads excluded",
              "price_reference": corpus.get("price_reference"), "model_cost_usd": None,
              "plan": {"cells": len(cases) * len(modes) * rounds,
                       "max_requests": max_requests, "max_sources_per_auto_call": 3}}
    if not live:
        return {**report, "ok": True, "budget": budget.data(), "network_requests": 0}
    config = {"schema_version": 2, "providers": {}} if keyless else search.read_config()
    # Benchmark default Smart without altering saved user preferences or credentials.
    disabled = ["exa-free", "exa"] if without_exa else []
    config = {**config, "search_preferences": {"strategy": "smart", "max_sources": 3, "disabled_providers": disabled}}
    for iteration in range(rounds):
        for index, case in enumerate(cases):
            rotation = (index + iteration) % len(modes)
            order = modes[rotation:] + modes[:rotation]
            for mode in order:
                if not budget.data()["remaining"]: break
                cell = run_cell(case, mode, config, budget, count=count, timeout=timeout,
                                keyless=keyless, without_exa=without_exa)
                cell["round"] = iteration + 1
                report["cells"].append(cell)
                if progress: progress({k: cell[k] for k in ("id", "mode", "ok", "elapsed_ms")})
    unit = corpus.get("price_reference", {}).get("deepseek_usd_per_successful_request")
    charged = sum(r.get("billable_success") is True for c in report["cells"] for r in c["receipts"])
    unknown = sum(r.get("billable_success") is None for c in report["cells"] for r in c["receipts"])
    return {**report, "ok": len(report["cells"]) == report["plan"]["cells"],
            "completed_at": datetime.now(timezone.utc).isoformat(), "budget": budget.data(),
            "cost": {"kind": "estimate_from_observed_billable_successes_not_invoice", "currency": "USD",
                     "deepseek_successes": charged, "unknown_billable_attempts": unknown,
                     "estimated_known_search_cost": round(charged * unit, 8) if unit is not None else None}}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--corpus", type=Path, default=ROOT / "evaluations/smart-cases.json")
    p.add_argument("--modes", default="free,deepseek,smart")
    p.add_argument("--live", action="store_true", help="Send public queries; DeepSeek/Smart may incur charges")
    p.add_argument("--keyless", action="store_true", help="Do not read config or environment keys; reject keyed API dispatch")
    p.add_argument("--without-exa", action="store_true", help="Simulate both Exa routes being unavailable for this benchmark")
    p.add_argument("--rounds", type=int, default=1)
    p.add_argument("--limit", type=int, default=6)
    p.add_argument("--max-requests", type=int, default=36)
    p.add_argument("--timeout", type=int, default=15)
    p.add_argument("--count", type=int, default=5)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        report = execute(load_cases(args.corpus), modes=tuple(args.modes.split(",")), live=args.live,
                         rounds=args.rounds, limit=args.limit, count=args.count, max_requests=args.max_requests, timeout=args.timeout,
                         keyless=args.keyless, without_exa=args.without_exa,
                         progress=lambda item: print(json.dumps(item, ensure_ascii=False), flush=True))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError, search.SearchError):
        print('{"ok":false,"error":"Check benchmark corpus, config and limits; no secret details retained."}')
        return 1
    print(json.dumps({"ok": report["ok"], "output": str(args.output), "budget": report["budget"], "cost": report.get("cost")}))
    return 0 if report["ok"] else 4


if __name__ == "__main__": raise SystemExit(main())
