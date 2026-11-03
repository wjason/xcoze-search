# Six real tasks: free, DeepSeek, Smart and 360 fallback

[简体中文](2026-11-03-comparison.md) | **English**

Sampled 2026-11-03; release/installed acceptance 2026-11-04 Beijing time. Baseline v0.7.1 (`c307eee`), changes released as v0.7.2. [Redacted data](2026-11-03-comparison.data.json) retains 75 stage cells, source URLs, attempts and failures, without bodies, keys, cookies or auth headers. Development stages sometimes shared a 0.7.1 version label despite different code/network conditions. The earlier [browser acceptance](2026-11-03-browser.en.md) remains unchanged.

## Findings

Keep APIs primary and 360 as emergency leads. Healthy anonymous Exa retrieved English primary documentation quickly; a real anonymous limit changed later cells. This does not establish generally poor free-API quality. 360 supplied Chinese-news leads, while official-domain scope improved primary-source location. Some summaries still required body reading and older records were mixed in.

360 did not supply the expected English primary docs or either GitHub repository in these probes, even after official-site/short-query variants. Native GitHub was more direct and faster. Smart's RSS complement under Exa limits added no useful evidence here; it now skips that weak complement while preserving failure fallback and configured/Exa complements. Complements after usable evidence receive at most a 3-second request timeout.

This is limited manual source/time review, not blinded accuracy or a lasting provider ranking. HTTP success, nonempty output and an official-domain hit do not establish an answer.

## Corpus and method

Six questions were frozen before the first round:

| Category | Need | Query |
|---|---|---|
| Chinese news | October 2026 manufacturing PMI/change; original release | 2026年10月 制造业 PMI 国家统计局 |
| Chinese news | Q1–Q3 2026 renewable additions/share | 2026年前三季度 可再生能源 新增装机 国家能源局 |
| English docs | PostgreSQL 18 uuidv7 ordering/shift | PostgreSQL 18 uuidv7 shift interval documentation |
| English docs | Rust Mutex poisoning and PoisonError::into_inner | Rust std Mutex poisoning PoisonError into_inner documentation |
| GitHub | Official Microsoft MarkItDown and PDF extras | markitdown; platform=github |
| GitHub | Official Microsoft Playwright and browser support | playwright; platform=github |

Baseline and core-fix rounds ran free/DeepSeek/Smart serially with rotated order, count=5 and zero retries. Separate same-query 360, four official-site, two short-query and focused checks followed. Official domains were independently verified; those variants are not blind discovery or unchanged-query algorithm gains.

Only DeepSeek had a key. Smart used temporary default preferences without saving changes. Free/browser guards rejected keyed API dispatch. Responses were real, with no pause reset. The second Exa request really reported an application-level anonymous limit; later automatic plans skipped it. Normal calls succeeded after natural cooldown expiry.

Times cover retrieval including browser close, excluding process startup, model query/final-answer generation, independent reference browsing and reading. Local evidence was bounded to 1800 characters; absence after clipping does not establish absence in the full response. Published data removes bodies; literal signals only aid review.

## Same-query observations

Initially, free renewable search returned calendars in about 0.57 seconds; PostgreSQL returned home/download pages in about 0.48 seconds. Neither supported the question. Some entered Smart complements. The first explicit DeepSeek PMI call had a network failure, retained in the data.

This table is the **core per-row-fix same-query round**, under Exa limits and before later DDG-pause/complement-timeout revisions. One observation per cell, seconds; not a final-version latency promise.

| Task | Free | DeepSeek | Smart | Evidence review |
|---|---:|---:|---:|---|
| PMI | 5.40 | 0.51 | 1.03 | Media leads; original query did not consistently locate the original release |
| Renewables | 6.56 | 0.45 | 1.01 | Free snippets insufficient; keyed modes had current figures through media |
| PostgreSQL UUID | 10.24 | 0.40 | 1.08 | Free third-party material; keyed function/shift leads still require distinguishing official mail from formal v18 docs |
| Rust Mutex | 9.15, rejected | 0.50 | 0.84 | Free rows lacked requested code identifiers; keyed modes found official Mutex docs and other material |
| MarkItDown | 0.22 | 0.98 | 0.74 | Native search directly locates the official repository; PDF extras still require README reading |
| Playwright | 0.27 | 1.41 | 0.70 | Native description supplies browser leads; DeepSeek includes official README snapshots and other repositories |

Rejecting irrelevant evidence can lower apparent success counts without solving coverage. Literal/code/time filters do not verify assertions; semantic APIs and native metadata are outside these lexical rules.

## Independent 360 and scoped variants

Direct 360 times for the six original queries were about 7.84, 6.15, 5.23, 7.41, 3.60 and 4.63 seconds. Chinese queries had related media leads, including 2023/half-year pollution for renewables. Neither English query found the expected primary docs; both GitHub queries explicitly had no matches. Six successful DOM operations are not six effective retrievals.

Adding independently verified official domains produced these observations:

| Task/scope | Free | DeepSeek | Smart before tail cap | Review |
|---|---:|---:|---:|---|
| PMI, stats.gov.cn | 4.36 | 0.66 | 1.03 | Original release and requested figures available |
| Renewables, nea.gov.cn | 4.17 | 0.76 | 1.14 | Current conference/transcript entries; body reading needed for both figures |
| UUID, postgresql.org | 4.89, empty | 0.66 | 0.98 | 360 miss; keyed official mail/attachments/related pages still need the formal function documentation |
| Mutex, doc.rust-lang.org | 5.15, empty | 0.55 | 0.91 | 360 miss; keyed modes locate official Mutex docs |

Concise English rewrites also had no matches. The final v0.7.2 date-path smoke took about 4.03 seconds and retained two current NEA entries, excluding an older compact-date path.

Reference verification used the [NBS release](https://www.stats.gov.cn/zwfwck/sjfb/202610/t20261031_1965718.html), [NEA material](https://www.nea.gov.cn/20261030/28a6f818b9f843a995952940301590bd/c.html), [PostgreSQL 18 UUID docs](https://www.postgresql.org/docs/18/functions-uuid.html), [Rust Mutex](https://doc.rust-lang.org/std/sync/struct.Mutex.html), [MarkItDown](https://github.com/microsoft/markitdown) and [Playwright](https://github.com/microsoft/playwright). A known reference URL was never retroactively counted as retrieved by a mode.

## Final changes and checks

- Experimental rows reject obvious Chinese mismatch, missing queried code identifiers and explicit year/some month/half-year conflicts, including compact date paths. Retain ranks and count removals. False rejection/missed conflicts remain possible; the Agent still checks versions, dates and support.
- DDG verification pauses 15 minutes; later plans skip it. Query-specific browser relevance failure no longer pauses the entire source, allowing a task-budgeted rewrite while challenges still stop.
- GitHub does not reserve a browser slot ahead of native/general APIs. Explicit browser choice remains; source caps still apply.
- A successful primary is complemented only by another configured service or Exa. Real controlled-preference checks with Exa temporarily disabled in memory took about 0.65/0.43 seconds for PMI/Rust, each with one DeepSeek HTTP and no RSS/browser. This was not presented as a real quota error.
- Healthy Exa complements later produced a 6.86-second Smart tail. Automatic complements after usable evidence now cap their request timeout at 3 seconds. A final Rust observation took about 1.57 seconds with two APIs, no browser and successful complement; this is not a hard latency guarantee. Explicit sources and lower budgets remain.
- After natural Exa cooldown expiry, the original free Rust query retrieved official Mutex/PoisonError sources in about **1.44 seconds**, with **zero browser launches**. Healthy free APIs and exhausted-quota browser paths must be assessed separately.

149 offline tests cover free isolation, filtering/ranks, DDG pauses, GitHub slots, complement eligibility and the 3-second cap. They verify behavior boundaries, without replacing live evidence or closing English free-coverage gaps.

## Cost and limits

The report covers 75 cells, 85 observable API HTTP attempts and 26 browser navigations. Resource subrequests are unknown, not merged into an invented HTTP total. There were 34 nonempty DeepSeek successes and one initial DeepSeek network failure. At the [official Search rate checked on November 3](https://api-docs.deepseek.com/guides/search/#billing) of USD 0.75 per 1000 successful requests, known search cost is estimated at **USD 0.02550**, not reconciled to an invoice. Free/browser keyed API attempts were **zero**. Model/host/local-compute costs are unknown; independent reference browsing and later installed-package smoke are outside this ledger.

Browser close sometimes took about 5.4–5.6 seconds; an exhausted-source free path reached about 12.52 seconds total. Shutdown time was included and cleanup acknowledgment retained. Network/index/cache conditions vary; this is not multi-network or real Windows/Linux browser acceptance.

An independent installed v0.7.2 smoke located MarkItDown through native GitHub, then read the repository body through anonymous Exa after Jina failed. It took about 1.77 seconds, returning 20202 characters including PDF-extra information, with one search and two reading API attempts, no keyed call and no browser. This is outside the preceding sample ledger.

The current choice is quality-first APIs with keys, healthy keyless APIs without them, and 360 emergency leads. Use verified official scope and native GitHub search. Keyless English primary-document coverage under Exa limits remains unfinished work.

## Reproduce

```bash
python3 scripts/benchmark.py --corpus evaluations/browser-comparison-cases.json --output ../plan.json
python3 scripts/benchmark.py --live --corpus evaluations/browser-comparison-cases.json --max-requests 36 --output ../comparison.json
python3 scripts/benchmark.py --live --corpus evaluations/browser-comparison-cases.json --modes browser --max-requests 6 --output ../browser.json
python3 scripts/benchmark.py --live --corpus evaluations/browser-comparison-scoped.json --limit 4 --max-requests 24 --output ../scoped.json
python3 -m unittest discover -s tests -q
```

Default execution only plans offline. --live reads normal configuration and uses the network; DeepSeek/Smart may incur charges. Remove evidence bodies before public sharing. Service limits change later runs; do not clear pauses to force matching results. Runner ok means planned cells executed, not all questions answered correctly.
