# Search regression corpus

[简体中文](README.md) | **English**

Corpus date: 2026-11-02. `queries.json` contains 12 Chinese/English search queries and three extraction URLs, covering technical docs, original standards, content types, dated news, versions, and conflicting information. It supports reproduction, result comparison, and manual reading; it is not a universal accuracy benchmark.

## Plan without networking

```bash
python3 scripts/evaluate.py --provider deepseek,tavily,exa
python3 scripts/evaluate.py --operation fetch --provider deepseek,tavily,exa
```

No credentials are read and no HTTP requests are made. Output reports case counts, planned requests, and budget. would_stop_early:true means the selected combinations exceed the budget. There are 12 search cases, with one logical request per provider/case. No automatic query expansion or follow-up Fetch is performed. Extraction requires explicit --operation fetch and supports only DeepSeek/Tavily/Exa; search-only services are rejected.

## Explicit live execution

```bash
python3 scripts/evaluate.py --live --provider deepseek --limit 2 --count 3 --max-requests 2 --output ../evaluation-report.json
```

This sends corpus queries to selected providers and may incur charges. Configure credentials first. --max-requests is a shared HTTP-attempt limit for the entire evaluation. Live regression uses zero retries. If the next provider group cannot fit, execution stops with complete:false. The default budget is 24, adjustable from 1 to 1000.

Reports retain run time, case IDs, providers, source URLs, content types, elapsed time, attempts, reported usage/cost, and error codes. They do not contain keys, raw responses, full text, generated answers, or search history. Without --output, reports go only to stdout.

Extraction reports include text/summary character counts, highlight counts, and expected-term matches without saving page text. A match only establishes that a term occurred, not completeness or factual correctness.

## Manual review

- Check run date, failures, success rates, and early budget stops before comparing sources for the same query.
- expected_domains is a review hint; an empty list has no preset domains. A match does not prove correctness, and a miss does not prove a provider failed.
- Read original pages to check dates, versions, wording, and source relationships. Evaluate retrieval and extraction separately; snippets/summaries cannot be treated as full text.
- This work ran offline plans and synthetic-response checks, not live quality evaluations of the four new services. Keep corpus versions and evaluation dates when adding query sets.
