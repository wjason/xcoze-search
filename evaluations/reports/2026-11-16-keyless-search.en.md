# Keyless documentation search and fallback checks

[简体中文](2026-11-16-keyless-search.md) | **English**

2026-11-16, Beijing time. This update adds official Python, pandas and SQLAlchemy static indexes, MDN site search and a lightweight 360 HTML fallback. None requires a user key, host search or a browser. See the [per-question data and probes](2026-11-16-keyless-search.data.json).

## Focused cases

| Method | Cases | Outcome |
|---|---|---|
| Official Sphinx indexes | Python TaskGroup, Path.read_text, tomllib.loads; pandas read_csv dtype; SQLAlchemy select/join | 5/5 located expected documentation pages in the top five |
| MDN site search | AbortController signal, Promise.allSettled | 2/2 located expected API documentation |
| 360 HTML Chinese scopes | Vehicle purchase tax, annual report, Zhihu asyncio, Xiaohongshu museum branch, Weibo AI, Bilibili rebase, NBS GDP, NEA offshore wind | 6/8 returned scoped candidates passing local topic checks; annual-report and museum-branch cases failed |

Documentation searches took about 0.3–1.1 seconds, MDN 0.4–1.0 seconds and 360 Chinese samples 0.9–2.3 seconds, including local pacing. Some community candidates were profiles or platform search pages, not read posts, comments or videos.

Five original pages from Python, pandas, SQLAlchemy, MDN and NBS were also read. All returned content containing the required topic or API markers. This confirms page/topic correspondence, not every claim, version or date. Static results use `documentation_index` and do not impersonate body summaries.

## 100 questions without Exa

Both runs used the same [100 questions](../agent-search-cases-v3.json), free mode, five results and an eight-second per-source timeout. Both Exa routes, user keys, host search and local browsers were disabled. Existing cooldowns were retained between runs. The baseline used the earlier routing behavior; the second run used final code.

| Metric | Before | After |
|---|---:|---:|
| Returned candidates | 60/100 | 67/100 |
| Expected domain in top five | 57/99 | 65/99 |
| Median retrieval time | 477 ms | 433 ms |
| P95 | 2,239 ms | 2,111 ms |
| Exa requests, keyed API requests, browser navigations | All 0 | All 0 |

Upstream conditions differed, so these changes are not an accuracy gain or stable performance guarantee. Parallel hit a real quota limit on its eleventh baseline request. The second run retained that cooldown and later made ten requests after natural recovery. Its first 360 request redirected to CAPTCHA; detection paused the source after one request without following or retrying.

The second run retrieved Python TaskGroup, tomllib, ExceptionGroup, pandas merge and two MDN questions directly from documentation sources. Other sources still had empty or restricted results. Kubernetes CPU requests/limits, Go context and Rust OnceLock remained gaps when general fallbacks were unavailable. General search services remain necessary.

Intermediate runs exposed two issues: static-index word forms missed `one_to_one`, and release/version queries could select the current documentation index. Final code adds limited suffix matching, keeps release queries on web search and skips fixed indexes when requested versions cannot be guaranteed. The final 100-question run followed these fixes.

## Public entry-point screening

Each entry point received one English documentation query and one Chinese scoped query. A page response alone is not a usable result:

| Entry point | Observation | Decision |
|---|---|---|
| 360 HTML | Related results in small samples; CAPTCHA redirect after batching | Limited fallback, 15-minute challenge cooldown |
| Google HTML | JavaScript page without extractable organic results | No HTTP adapter |
| Yahoo | HTTP 500 / 403 | Not integrated |
| Brave HTML | HTTP 429 | Not integrated |
| Baidu HTML / JSON | Verification redirect | Not integrated; no bypass |
| Sogou | Verification page | Not integrated |
| Mojeek | Verification page | Not integrated |
| Ecosia | HTTP 403 | Not integrated |
| Qwant | No organic HTML results; public JSON route returned 403 | Not integrated |
| Mwmbl v2 | Zero results on both scoped questions | Deferred for later checks |
| Bing HTML | Returned off-topic, out-of-scope results | No new HTML adapter; existing RSS retained |
| Stract | Tested search path returned HTTP 404 | Not integrated |

[Mozilla documents MDN's search design](https://hacks.mozilla.org/2021/03/how-mdns-site-search-works/). Sphinx adapters read public JSON indexes without executing JavaScript. [Mwmbl's developer page](https://developer.mwmbl.org/) describes its anonymous endpoint and quota; these misses do not establish failure on all queries. Adapters are independently implemented without copied third-party search-project code.

## Reproduce

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v3.json --modes free --keyless --without-exa --browser off --live --limit 100 --max-requests 300 --timeout 8 --count 5 --output /tmp/xcoze-no-exa.json
python3 scripts/xcoze_search.py search 'asyncio TaskGroup exception cancellation' --platform python-docs --strategy free --browser off
python3 scripts/xcoze_search.py search 'merge validate one_to_one' --platform pandas-docs --strategy free --browser off
python3 scripts/xcoze_search.py search 'AbortSignal.timeout' --platform mdn --strategy free --browser off
```

Do not clear real cooldowns, rotate identities around quotas or call paid APIs to improve a score. Domain hits measure source coverage; results and timings can differ across dates.
