# Official documentation and Chinese site-search checks

[简体中文](2026-11-16-native-search.md) | **English**

2026-11-16, Beijing time. This update adds Kubernetes, Go and Rust documentation retrieval, CNINFO disclosures and National Bureau of Statistics site search. The new routes need no user key, Exa, Parallel, host search or browser. [Per-question results, original checks and failures](2026-11-16-native-search.data.json)

## Focused retrieval

| Entry point | Cases | Expected page position in the top five |
|---|---|---|
| Kubernetes official navigation | CPU requests/limits and memory; probes; volume reclaim; NetworkPolicy | 2, 1, 1, 1 |
| Go standard-library symbol search | WithCancelCause; Server.Shutdown; Decoder.DisallowUnknownFields; errors.Is | All 1 |
| Rust standard-library items | OnceLock; PoisonError; HashMap | All 1 |
| CNINFO | Moutai 2024 annual report; listed-company reports; CATL 2025 report | Related disclosures returned; both named-company reports at 1 |
| NBS site search | GDP; September 2026 CPI; October 2026 PMI | NBS publications returned; CPI title matches the requested month after correction |

All 17 focused cases returned candidates meeting those location criteria. Documentation retrieval was mostly 0.2–1.2 seconds; Chinese site search about 0.3–2.4 seconds, with one NBS request around seven seconds. Timings include local pacing and exclude answer generation and original-page reading.

Kubernetes matches navigation titles and links rather than using Pagefind full-text search; its resource-management target ranked second. Rust locates a type before its methods without inventing method anchors. Go retains only results carrying the standard-library badge, excluding third-party packages from official API results.

## Originals and dates

Sixteen originals were checked: eleven technical pages, three NBS pages and the first pages of two annual-report PDFs. Required API/topic markers were found. Moutai's first page confirmed the issuer, 2024 and annual report. CATL's result was the Traditional Chinese Hong Kong report: the cover shows code 3750, search metadata preserves `03750`, and the reporting year is 2025. It was not identified as an A-share report.

Metadata preserves security codes, markets and publication dates. Reporting years differ from publication dates; statistical periods differ from NBS webpage dates. Checks cover the required pages, markers and report covers, not complete-report or statistical-figure audits.

## 100 questions with Exa and Parallel disabled

Both runs used the same [100 questions](../agent-search-cases-v3.json), free mode, five results and an eight-second per-source timeout. Both Exa routes, Parallel, keyed services and browsers were disabled. Baseline routing came from `136e015`, with the same updated benchmark harness used for both versions. The final run retained baseline cooldowns. Host search did not participate.

| Metric | Before | Final replay |
|---|---:|---:|
| Returned candidates | 56/100 | 65/100 |
| Expected domain in top five | 55/99 | 63/99 |
| Median retrieval time | 374 ms | 370 ms |
| P95 | 2,328 ms | 1,719 ms |
| API HTTP attempts | 105 | 103 |
| Exa / Parallel / keyed requests / browser navigations | All 0 | All 0 |

The Kubernetes, Go and Rust gap questions now retrieved their expected official pages. Moutai's report question found the target PDF, while NBS questions used site search. Domain hits measure source coverage, not answer accuracy. Network conditions, cooldowns and index updates affect reproduction; intermediate runs and failures remain in the data file.

Thirty-five questions still returned no candidates, including some law/standards sites, community indexes, public data and other official documentation. This update addresses the listed targets, not stable unlimited free web search.

## Corrections from live checks

- Bare `Shutdown` initially selected `syscall.Shutdown`. Package and receiver context now produces `http.Server.Shutdown`; JSON Decoder methods received the same correction.
- CNINFO title-only search missed the annual-report query. Its public full-text index works; listed-company queries use public equity categories to avoid fund and bond reports.
- October CPI initially outranked a September question. Clearly conflicting title months are now excluded, followed by topic-based title ordering. Comparison months in excerpts do not replace title periods.
- Fixed documentation indexes cannot guarantee a requested version. Unsupported version, language and date constraints exclude a source or fail explicitly.

## Scope and reproduction

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v3.json --modes free --keyless --without-exa --without-parallel --browser off --live --limit 100 --max-requests 300 --timeout 8 --count 5 --output /tmp/xcoze-native-100.json
```

Adapters are independently implemented against public navigation, item and search interfaces: [Kubernetes documentation](https://kubernetes.io/docs/concepts/), [Go search help](https://pkg.go.dev/search-help), [Rust standard-library items](https://doc.rust-lang.org/std/all.html), [CNINFO](https://www.cninfo.com.cn/) and [NBS search](https://www.stats.gov.cn/search/s?qt=%E5%9B%BD%E5%86%85%E7%94%9F%E4%BA%A7%E6%80%BB%E5%80%BC). See [Chinese site search](../../references/china-site-search.en.md) for the NBS-selected third-party backend and limits.

China's central government full-site search page was also inspected, but its request protocol is not yet adapted and does not count as a new working entry point. The existing recent-listing adapter retains its original scope.
