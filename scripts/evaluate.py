#!/usr/bin/env python3
"""Plan or explicitly run the public-source regression corpus with an HTTP budget."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.parse

import xcoze_search as search

ROOT = Path(__file__).resolve().parents[1]


def load_cases(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or data.get("schema_version") != 1
            or not isinstance(data.get("queries"), list) or not data["queries"]):
        raise ValueError("Invalid evaluation corpus.")
    ids = set()
    for case in data["queries"]:
        if (not isinstance(case, dict) or not isinstance(case.get("id"), str) or case["id"] in ids
                or not isinstance(case.get("query"), str) or not case["query"].strip()
                or not isinstance(case.get("expected_domains"), list)
                or any(not isinstance(d, str) for d in case["expected_domains"])):
            raise ValueError("Invalid or duplicate evaluation case.")
        ids.add(case["id"])
    fetches = data.get("fetches", [])
    if not isinstance(fetches, list):
        raise ValueError("Invalid extraction corpus.")
    fetch_ids = set()
    for case in fetches:
        if (not isinstance(case, dict) or not isinstance(case.get("id"), str) or case["id"] in fetch_ids
                or not search.public_url(case.get("url")) or not isinstance(case.get("expected_terms"), list)
                or any(not isinstance(term, str) for term in case["expected_terms"])):
            raise ValueError("Invalid extraction case.")
        fetch_ids.add(case["id"])
    return data


def execute(corpus, providers, *, live=False, limit=12, count=3, max_requests=24, operation="search"):
    if operation == "fetch":
        return execute_fetch(corpus, providers, live=live, limit=limit, max_requests=max_requests)
    cases = corpus["queries"][:limit]
    for provider in providers:
        for case in cases:
            search.search_payload(provider, query_args(case["query"], providers, count))
    report = {"operation": "evaluation", "evaluation_operation": "search", "live": live, "corpus_as_of": corpus.get("as_of"),
              "started_at": datetime.now(timezone.utc).isoformat(), "providers": providers,
              "query_count": len(cases), "facts_verified": False, "cases": [],
              "notice": "Expected-domain matches are review hints, not factual-accuracy or quality scores."}
    budget = search.RequestBudget(max_requests)
    if not live:
        planned = len(cases) * len(providers)
        report.update(ok=True, planned_logical_requests=planned, would_stop_early=planned > max_requests, budget=budget.data())
        return report
    config = search.read_config()
    for provider in providers:
        search.credential(provider, config)
    complete = True
    for case in cases:
        if budget.limit - budget.used < len(providers):
            complete = False
            break
        result = search.run_search(query_args(case["query"], providers, count), config, budget=budget)
        sources = []
        for row in result["results"]:
            domain = urllib.parse.urlsplit(row["url"]).hostname.lower()
            expected = case["expected_domains"]
            match = any(domain == d or domain.endswith("." + d) for d in expected) if expected else None
            sources.append({"provider": row["provider"], "url": row["url"], "domain": domain,
                            "expected_domain_match": match, "content_kind": row["content_kind"]})
        report["cases"].append({"id": case["id"], "category": case.get("category"), "ok": result["ok"],
                                 "sources": sources, "requests": [{key: item.get(key) for key in
                                 ("provider", "ok", "attempts", "elapsed_ms", "request_id", "usage", "cost")}
                                 for item in result["requests"]],
                                 "error_codes": [error["code"] for error in result["errors"]]})
    report.update(ok=complete and all(case["ok"] for case in report["cases"]),
                  complete=complete, completed_cases=len(report["cases"]), budget=budget.data())
    report["budget"]["scope"] = "evaluation_run"
    return report


def execute_fetch(corpus, providers, *, live=False, limit=12, max_requests=24):
    cases = corpus.get("fetches", [])[:limit]
    if not cases:
        raise ValueError("No extraction cases in corpus.")
    for name in providers:
        adapter = search.get_provider(name)
        if not adapter.fetch_endpoint:
            raise search.SearchError("unsupported_operation", adapter.label + " does not support fetch.")
        for case in cases:
            adapter.fetch_payload(argparse.Namespace(url=case["url"], highlights=False, summary=False))
    budget = search.RequestBudget(max_requests)
    planned = len(cases) * len(providers)
    report = {"operation": "evaluation", "evaluation_operation": "fetch", "live": live,
              "corpus_as_of": corpus.get("as_of"), "started_at": datetime.now(timezone.utc).isoformat(),
              "providers": providers, "case_count": len(cases), "facts_verified": False, "cases": [],
              "notice": "Nonempty content and term matches are extraction checks, not factual-accuracy scores."}
    if not live:
        report.update(ok=True, planned_logical_requests=planned, would_stop_early=planned > max_requests, budget=budget.data())
        return report
    config = search.read_config()
    for provider in providers:
        search.credential(provider, config)
    complete = True
    for case in cases:
        if budget.limit - budget.used < len(providers):
            complete = False
            break
        checks = []
        for provider in providers:
            args = argparse.Namespace(url=case["url"], provider=provider, highlights=False, summary=False, timeout=30, retries=0)
            started = search.time.monotonic()
            try:
                response = search.run_fetch(args, config, budget=budget)
                metadata = response["provider_metadata"]
                checks.append({"provider": provider, "ok": response["ok"] and not response["empty"],
                               "resolved_url": response.get("resolved_url", case["url"]),
                               "content_characters": len(response["content"]),
                               "summary_characters": len(response.get("summary", "")),
                               "highlight_count": len(response.get("highlights", [])),
                               "expected_term_matches": [term for term in case["expected_terms"] if term in response["content"]],
                               "attempts": response["attempts"], "usage": metadata["usage"], "cost": metadata["cost"]})
            except search.SearchError as error:
                checks.append({"provider": provider, "ok": False, "error_code": error.code, "attempts": error.attempts})
            checks[-1]["elapsed_ms"] = round((search.time.monotonic() - started) * 1000, 2)
        report["cases"].append({"id": case["id"], "url": case["url"], "ok": all(c["ok"] for c in checks), "checks": checks})
    report.update(ok=complete and all(case["ok"] for case in report["cases"]), complete=complete,
                  completed_cases=len(report["cases"]), budget=budget.data())
    report["budget"]["scope"] = "evaluation_run"
    return report


def query_args(query, providers, count):
    return argparse.Namespace(query=query, provider=",".join(providers), count=count, site=None,
                              need_content=False, freshness=None, industry=None, mode=None, timeout=30, retries=0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=ROOT / "evaluations/queries.json")
    parser.add_argument("--provider", default="deepseek", help="Explicit provider name(s), separated by commas")
    parser.add_argument("--operation", choices=("search", "fetch"), default="search")
    parser.add_argument("--live", action="store_true", help="Send corpus queries to the selected providers; may incur charges")
    parser.add_argument("--limit", type=int, choices=range(1, 101), default=12)
    parser.add_argument("--count", type=int, choices=range(1, 21), default=3)
    parser.add_argument("--max-requests", type=int, choices=range(1, 1001), default=24)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        providers = args.provider.split(",")
        if len(providers) != len(set(providers)) or any(p not in search.REGISTRY for p in providers):
            raise ValueError("Specify distinct registered provider names.")
        report = execute(load_cases(args.corpus), providers, live=args.live, limit=args.limit,
                         count=args.count, max_requests=args.max_requests, operation=args.operation)
    except search.SearchError as error:
        print(json.dumps({"ok": False, "error": error.data()}, ensure_ascii=False))
        return 1
    except (ValueError, OSError, UnicodeError):
        print('{"ok":false,"error":{"code":"invalid_evaluation","message":"Check corpus and local output path."}}')
        return 1
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(encoded, encoding="utf-8")
        except OSError:
            print('{"ok":false,"error":{"code":"output_write_failed","message":"Could not write evaluation report."}}')
            return 1
    print(encoded, end="")
    return 0 if report["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
