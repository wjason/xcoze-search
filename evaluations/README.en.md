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
- The earlier six-keyed-service regression ran offline plans and synthetic-response checks, not live quality evaluations of the four new services. Keep corpus versions and evaluation dates when adding query sets.

## Smart same-task comparison

The [2026-11-03 report](reports/2026-11-03.en.md) covers six baseline/revised tasks and two Chinese holdouts. [Public data](reports/2026-11-03.data.json) retains metrics, URLs and manual reviews only.

```bash
python3 scripts/benchmark.py --output ../smart-plan.json
python3 scripts/benchmark.py --live --limit 6 --max-requests 36 --output ../smart-live.json
python3 scripts/benchmark.py --live --corpus evaluations/smart-holdout.json --limit 2 --max-requests 12 --output ../holdout-live.json
```

Default is an offline plan without credential reads. --live sends public queries and may incur DeepSeek/Smart charges. Runs share an actual HTTP budget, use zero retries and rotate order. Smart uses in-memory default preferences without saving config. Explicit DeepSeek HN queries use recorded date operators; native routes use date fields.

Local live reports retain up to 1800 evidence characters per result, possibly truncated: do not publish them directly. Retain only URLs, metrics and manual reviews after privacy/copyright review. Cost estimates count raw nonempty DeepSeek successes at the dated corpus price, not an invoice; model cost is unknown. ok means scheduled cells executed, not useful evidence; semantic_quality_assessed defaults false. Token/domain hits are not manual fact checks. Dated answers are historical snapshots; refresh the corpus and save new reports for later runs.
