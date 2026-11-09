# Search regression corpus

[简体中文](README.md) | **English**

Corpus date: 2026-11-02. `queries.json` contains 12 Chinese/English search queries and three extraction URLs, covering technical docs, original standards, content types, dated news, versions, and conflicting information. It supports reproduction, result comparison, and manual reading; it is not a universal accuracy benchmark.

## Agent search question set

The [100-question set](agent-search-cases-v3.en.json) preserves the first 20 questions and adds 10 questions in each of eight groups. The groups cover public policy, freshness, technical docs, packages, research, communities, public data, and disambiguation. Chinese and English versions share case IDs, queries and search constraints.

The [100-question baseline](reports/2026-11-09-100-question-baseline.en.md) records the free run, six targeted retests and six Smart spot checks. The [20-question report](reports/2026-11-09-agent-search.en.md) contains the original-source review.

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v3.en.json --modes free --keyless --limit 100 --max-requests 300 --output /tmp/xcoze-100-plan.json
```

This plans 100 free-mode searches without sending requests. Use a small Smart sample to check fallback without keys. To measure a baseline, add `--live` and use a separate output file. Preserve the date constraints and record the run time for rolling windows. Use the per-case criteria to review the top five results, then label each case verified, partial or missed. Use expected domains to locate evidence and open the original pages to check the actual claim or date.

## Public source checks

The [GitHub Actions workflow](https://github.com/wjason/xcoze-search/actions/workflows/source-check.yml) runs weekly on Mondays at 11:23 Beijing time and can be started manually. Its run summary lists each action and differences from the November 5 snapshot. The JSON artifact is retained for 90 days. On November 9, [a local check](reports/2026-11-09-public-source-check.json) covered 75 actions. It recorded 67 passes, 5 limited and 3 with no hits. The workflow checks search, reading, feeds, trends and site scopes. API-key services and local browser engines remain separate checks.

```bash
python3 evaluations/check_sources.py --live --output /tmp/xcoze-source-check.json --summary /tmp/xcoze-source-summary.md
```

Omit `--live` for a local plan with no requests. Each action gets up to one attempt and follows source cooldowns.

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

## Open-source and competitor-study checks

The [dated study](reports/2026-11-03-open-sources.en.md) covers nine adapters, Agent Reach and a long-reading correction. Use open-source-cases.json with --modes free --limit 10 --count 3 in benchmark.py; default is offline, --live connects. expected_provider_returned indicates a native provider returned rows, not a correct answer.

## Exa quota failure injection

```bash
python3 scripts/evaluate_fallback.py --output ../fallback-offline.json
python3 scripts/evaluate_fallback.py --live-api --live-browser --output ../fallback-live.json
```

Default HTTP/browser execution is simulated, with synthetic keys for six providers and no credential-file reads. --live-api sends one anonymous API query; --live-browser launches one real browser path after injected API failures. The guard rejects keyed requests before transmission. ok means routing safety assertions passed; live_browser_usable separately reports actual browser availability and may be false. Simulated recovery is not real retrieval success. See the [observed report](reports/2026-11-03-fallback.en.md).

## Live browser acceptance (v0.7.1)

```bash
python3 scripts/evaluate_browser.py --live --output ../browser-live.json
```

Explicit --live is required. All search pages/HTTP responses are real. Synthetic in-memory keys and temporary cache avoid user credential files/saved preference changes; a pre-transmission guard rejects keyed APIs. Three docs/statistical-release/filing-reproduction tasks plus a GitHub coverage probe run, followed by a real DDG-to-browser route with Exa/Bing temporarily disabled in test preferences. Successful DDG evidence without browser execution does not pass the browser-fallback check.

accepted indicates an expected source/topic and acknowledged close, not factual accuracy. The GitHub coverage probe is required:false and remains a failed coverage check when empty; overall ok must not hide it. Overall ok requires the three core tasks, real automatic recovery and zero keyed attempts. Every failure remains reported. Public indexes/network conditions may change. Keep the historical [quota report](reports/2026-11-03-fallback.en.md) separate from [real browser evidence](reports/2026-11-03-browser.en.md).

## Six-task comparison and independent 360 probes (v0.7.2)

```bash
python3 scripts/benchmark.py --corpus evaluations/browser-comparison-cases.json --output ../comparison-plan.json
python3 scripts/benchmark.py --live --corpus evaluations/browser-comparison-cases.json --max-requests 36 --output ../comparison.json
python3 scripts/benchmark.py --live --corpus evaluations/browser-comparison-cases.json --modes browser --max-requests 6 --output ../browser-probe.json
python3 scripts/benchmark.py --live --corpus evaluations/browser-comparison-scoped.json --limit 4 --max-requests 24 --output ../scoped.json
```

The default three modes remain; browser is an explicit free diagnostic, never automatically added. Free/browser guards reject keyed APIs before transmission. Live runs use normal config/cache state without clearing limits, rotate mode order and run serially. Scoped/short variants change query conditions and cannot be claimed as unchanged-query algorithm gains. Overall ok means planned cells ran, even if individual cells fail/return no matches or insufficient evidence. Local evidence is bounded to 1800 characters; missing text after clipping does not establish absence in the full response. Remove bodies before publication and review source/time/answer support manually. Keyed calls may cost money; browser requires an existing installation. Model cost is unknown.

The [bilingual report](reports/2026-11-03-comparison.en.md) retains stages, natural Exa recovery and unresolved English coverage; it is not blinded accuracy or a stable latency ranking.
