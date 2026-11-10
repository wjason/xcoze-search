# Routing and platform scope

[简体中文](routing.md) | **English**

## Defaults and overrides

Normal questions trigger the Skill without a mode choice. Search defaults to provider auto. Precedence: explicit current source/strategy, saved preferences, then Smart. A named source overrides a saved mode; an explicit free strategy together with a keyed source is rejected.

Smart selects quality when a syntactically valid, enabled key exists, otherwise free. Format does not establish network access, balance or permissions. Quality without keys still uses keyless sources. Preferences only update local configuration, never keys or remote state; unknown config fields are retained.

| Strategy | General search candidate order |
|---|---|
| quality | First configured source, keyless Exa, other configured sources, then Parallel/Bing/DDG |
| balanced | Keyless Exa, configured sources, then Parallel/Bing/DDG |
| free | Keyless Exa, anonymous Parallel, Bing, DuckDuckGo; excludes keyed adapters |

GitHub repository/HN story targets prefer their platform adapters. A saved default may take priority; disabled sources stay excluded. Bootstrap order is transparent configuration policy, not a benchmark ranking. No persistent learned success history is implemented.

## Script and Agent responsibilities

The script preflights constraints. Incompatible auto candidates appear in skipped_incompatible without dropping time/site conditions. Explicit multi-source calls fail preflight if any selected source is incompatible. Native freshness expressions are not translated to another provider's different semantics; use supported start/end dates or separate Agent queries when appropriate.

Auto defaults to at most three sources (configurable 1–3; lower saved settings are retained) within 45 seconds by default. This is a scheduling budget, not a hard process deadline for DNS/network reads. Remaining time is checked before calls and each timeout is clipped accordingly; automatic sources have zero retries, and max-requests caps actual HTTP attempts. General tasks return on usable nonempty results. Quality reference/current general tasks may consult one more candidate and accumulate both result sets, retaining the first if the second fails. Successful GitHub/HN routes, explicit selections and free/balanced strategies do not force a complement. Failure history is retained. The Agent evaluates relevance, freshness, coverage and independence, then searches remaining compatible sources or revises queries only for evidence gaps. Script scores never replace fact checking.

The script does not accumulate time or currency across commands; the Agent must track task-wide calls. There is no quality guarantee, universal cross-provider score, real-time stock quote guarantee or index-delay promise. Successful fallback establishes access to results, not factual truth.

## Task intent and evidence checks

`--intent auto|general|reference|current` applies to this invocation, default auto. Latest/recent/current/LTS terms select current; official/pricing/docs/API terms select reference; other queries select general. The Agent should derive intent from the original question when a short query loses a time or primary-source requirement. Users need not choose intent. Intent does not relax constraints, enable disabled sources, cross free-mode boundaries or increase budgets.

`routing.intent`, `specialized_source` and `complementary_search` describe the policy; requests record actual attempts. Results retain per-source order without score comparison; duplicate URLs are marked. Two services may share an index and do not guarantee correctness.

Experimental Bing/DDG nonempty results with zero overlap against at least two informative Latin topic tokens produce irrelevant_results and may fall back. Short/non-Latin queries skip this signal; it is not a relevance classifier. Read current primary pages for prices, versions, rules and conflicting snippets; an official domain does not guarantee a fresh excerpt.

[Live tasks and tradeoffs](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03.en.md).

## Extended platforms

Wikipedia, Stack Exchange, arXiv, Crossref, npm, crates, GitLab, Europe PMC and Hugging Face prefer their public adapter for --platform or supported sites. Successful native routes do not force complements; unsupported dates/languages are still rejected/skipped in preflight. Offline platforms reads no keys and executes no tool. Added video/community scopes are public indexes only. See [open sources](open-sources.en.md) for parameters, local-tool cooperation and pacing.

## Platform coverage

| Target | Implemented | Not promised |
|---|---|---|
| GitHub | Public repository search and default README | Code search, private repositories, full Issue/PR adapters |
| HN | Algolia story search and official single-item reads | Automatically fetched comment trees or read outbound articles |
| Zhihu | Scoped public-index search | Arbitrary full answers, native search or comments |
| Xiaohongshu | Scoped public-index search | Logged-in ranking, image understanding, complete notes or comments |
| Weibo | Scoped public-index search | Official live trends or complete comments |

Returned URL hosts are checked for site scope; a domain in a URL path is not a match. Public indexes may have no relevant records. Existing authorized platform tools such as Agent Reach can complement site-specific tasks, but they are not dependencies; this package does not copy sessions or install browsers automatically.

## Reading and cost

Fetch auto tries GitHub README for repository-root links and the official interface for HN items. General URLs start with Jina Reader; configured Fetch-capable services take fallback priority when allowed, followed by Exa keyless MCP. The same source-count cap applies; unattempted candidates have no live verification status. Skip the script when the host already reads the page successfully.

Keyless is not entirely local: Bing, DuckDuckGo, Exa, Parallel, GitHub, Algolia/HN and Jina receive corresponding requests. Exa keyless and Jina Reader are limited-access commercial services. Free strategy guarantees no user-keyed service requests from this tool, not zero model/subscription/compute costs.

## Management examples

```bash
python3 scripts/xcoze_search.py preferences
python3 scripts/xcoze_search.py preferences --strategy free
python3 scripts/xcoze_search.py preferences --strategy balanced --max-sources 2
python3 scripts/xcoze_search.py preferences --provider deepseek
python3 scripts/xcoze_search.py preferences --disable duckduckgo
python3 scripts/xcoze_search.py preferences --enable duckduckgo
python3 scripts/xcoze_search.py preferences --reset
python3 scripts/xcoze_search.py plan 'industrial vision' --platform github
python3 scripts/xcoze_search.py search 'industrial vision' --provider yuanbao
```

Explicit sources never fall back outside their selection. Both and comma-list semantics remain. Auto and Fetch defaults changed in v0.4.0; pin a source to retain older deterministic behavior.

## Browser fallback and quota recovery

- APIs first by default. With a compatible browser, execution_candidates defaults to two API routes plus browser; without it, up to three APIs. Cap 2 means one API plus browser, cap 1 no fallback. A browser never complements existing API evidence. Explicit current/saved browser-source preference may override order.
- Auto API timeout caps at 8 seconds per source, browser work at 15 seconds clipped to remaining time/--timeout. The schedule is 45 seconds plus up to 6 seconds browser-close grace. Successful native APIs stop immediately. Quality reference/current retains up to two API result sets and keeps the first when a complement fails.
- Exa HTTP 429/503 honors Retry-After. JSON-RPC/tool quota errors become source_rate_limited without inventing wire HTTP status. Absent recovery guidance, pause 900 seconds then permit probing, not guaranteed reset. Search/Fetch share pause state. Auto skips and reports skipped_unavailable; explicit sources never expand.
- Browser challenges/abnormal navigation pause 900 seconds; shells/timeouts/execution failures 60. A held lock prevents concurrent fallback browsers. State contains timestamps/hashes, no results/keys. Normal queries read local state without online health checks.
- --browser off / preferences --browser off disable fallback; auto restores lazy use. Disabled browser stays excluded. Missing CLI triggers no install. Pauses, constraints and source/HTTP/time budgets may prevent browser use.
- Browser only supports general query/site; explicit unsupported dates/languages are not dropped. API budget unit is provider_api_http_attempts. Browser navigation/commands are separate and actual subrequest counts remain unknown.


- Exa transport failures and other HTTP 5xx responses pause the anonymous route for 60 seconds. Anonymous 401/403/404/410 pauses it for 15 minutes. Search and Fetch share the cooldown. Try a native source, an already known official URL, or permitted host web search for gaps in general coverage.

Parallel uses the documented legacy anonymous endpoint. Site-scoped results are checked locally, and returned text is labeled as excerpts. Limits enter the same cooldown policy as Exa. [100-question comparison](../evaluations/reports/2026-11-10-parallel-no-exa.en.md) · [Parallel documentation](https://docs.parallel.ai/integrations/mcp/search-mcp).

## Browser search results

360 is the default browser engine; --browser-engine explicitly selects Bing/Google. One selected engine, without probes/rotation. An anonymous session launches a blank page, schedules one navigation through a fixed script and waits for visible organic rows with nonempty titles, rather than page load. 360 destination URLs come from organic data-mdurl attributes; ads, AI answer cards and internal engine links are excluded.

Explicit no-match pages return an empty list and browser_explicit_no_matches:true, without failure cooldown or a claim of web-wide absence. Hidden rows produce browser_results_hidden, action timeouts remain browser_timeout and browser network pages produce browser_navigation_failed. These failures pause 60 seconds; challenges still pause 900. browser_failure_stage and browser_stage_timings_ms retain bounded stage/timing diagnostics for launch/navigation/wait/extraction/close, without page bodies or upstream error text. Conservative English/Chinese zero-topic-overlap rejection is not a semantic classifier.


## Source selection and result filtering

- 360 is a browser fallback; it does not start automatically when an API has returned usable results. Index coverage varies by search engine.
- GitHub does not reserve a browser slot: fill the existing three-source cap with native/general APIs in their original order. Lower caps, disabled sources and explicit browser selection remain. Browser may occupy a leftover slot when fewer APIs qualify; browser_slot_policy explains the plan.
- Quality reference/current complements only when the next candidate is configured/keyed or keyless Exa. If only Parallel/Bing/DDG/browser remains, stop on usable primary evidence, while keeping failure fallback. A complement after usable evidence receives at most a 3-second request timeout; primary APIs retain 8 seconds. Explicit multi-source calls keep their own limits. This is not a hard DNS/network deadline or SLA.
- RSS/HTML/browser rows reject obvious Chinese mismatch, missing queried code identifiers, conflicting explicit years and some month/half-year periods. Compact /YYYYMM/ release paths participate in year checks; missing dates stay unknown. dropped_irrelevant_count records removal and retained ranks stay original. Semantic APIs/native repository data are unaffected. This is not factual/version/full-date/semantic verification; false rejection and missed conflicts remain possible.
- DDG verification pauses for 900 seconds and automatic plans skip it locally, avoiding repeated HTTP. Browser topic rejection is query-specific and no longer pauses the source; shells/network timeouts/challenges keep their recovery rules.
- For requested primary sources with known official domains, the Agent should use --site and short queries. When an official page is not indexed, read an already located URL or follow verified official navigation rather than retrying the browser repeatedly.
