# Roadmap

[简体中文](TODO.md) | **English**

Updated 2026-11-04. Focus: Agent web search and source reading. Default automatic routing, public access without keys, quality-first with keys. Implementation, live access and search quality are recorded separately.

## v0.4.0: implemented

- [x] Smart selects quality with keys and free without keys; persistent quality/balanced/free preferences and per-call overrides.
- [x] Dependency-free Bing RSS, DuckDuckGo HTML and Exa keyless MCP search.
- [x] GitHub public repository/README adapters and HN story search/single-item reading.
- [x] Jina Reader and Exa keyless reading, with Fetch routed independently of search.
- [x] Scoped public-index search for Zhihu, Xiaohongshu and Weibo, URL-host checks and coverage boundaries.
- [x] Source/HTTP/time limits, preflight, fallback, offline plan and preference management.
- [x] Chinese/English instructions, setup, routing contracts and competitor implementation research.
- [x] Per-source local connectivity checks; successes and restrictions in [validation](VALIDATION.en.md) do not promise availability or accuracy.

## v0.5.0: measured routing revision

- [x] Exa-first keyless search, conservative experimental RSS/HTML mismatch fallback and bounded quality reference/current complements.
- [x] Current primary-page verification guidance and bilingual reproducible observations.

## v0.6.0: public indexes and platform scope

- [x] Nine public keyless native indexes, date/language/metadata semantics and live checks.
- [x] Offline platform catalog and existing-tool detection, separating public indexes from native actions.
- [x] Persistent pacing/backoff, bounded long reading, Agent Reach source study and observed same-task paths.

## v0.7.0: quota and lazy browser

- [x] Exa pause/skip and free-mode injection, with zero keyed attempts despite six synthetic keys.
- [x] Existing local agent-browser execution, one navigation, isolated session, budgets/close/cooldown and disable preference.
- [x] No browser on healthy APIs, separate execution accounting and truthful live failures.
- [x] v0.7.1 live acceptance on this machine: visible readiness, 360 organic/destination extraction, explicit no-match and stage diagnostics; three retrieval tasks and real API-to-browser recovery passed. [Evidence](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03-browser.en.md).
- [ ] Multi-network/multi-OS live acceptance; track Bing hidden/unrelated results and GitHub public-index misses without identity rotation or challenge solving.

## v0.7.2: live comparison and false-success fixes

- [x] Six-task multimode and independent 360 checks retaining real limits/failures/recovery. [Evidence](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03-comparison.en.md).
- [x] Per-row topic/code/explicit-time checks, DDG verification pause, GitHub API budget priority and bounded stronger complements.
- [ ] Improve keyless English primary-doc coverage under Exa limits; 360 did not close this gap, and third-party links are not substitutes.
- [ ] Continue multi-network/browser startup/close tail measurements with cleanup acknowledgment; do not hide shutdown time.

## P0: task quality and reliability

- [ ] Shared Chinese news/policy/docs/ecosystem/community/video tasks with blinded answer support, freshness and body/comment/subtitle evidence review before competitive claims.
- [ ] Evaluate Open Library, DBLP, Wikidata and Hugging Face datasets; distinguish current indexes from archival material and source count from utility.
- [ ] Evaluate optional platform execution adapters and action health, reusing authorized tools; browser search is wired; other platform-tool bridges remain discovery-only.


- [x] Initial six-task plus two-Chinese-holdout comparison of keyless/DeepSeek/Smart, with evidence/freshness review, timings and API estimates. [Report](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03.en.md); model cost and invoice reconciliation remain pending.
- [ ] Expand Chinese current-information cases; check feed relevance, platform coverage and unknown dates.
- [ ] Monitor GitHub anonymous quotas, DDG challenges, Exa keyless limits and network changes; no challenge bypass or identity rotation.
- [ ] Yuanbao real-account verification remains deferred because the user has no test key. Four additional keyed sources also retain separate real-account/quality verification work.
- [ ] Validate implicit invocation and native-tool cooperation on each host; updating this machine is not acceptance on all hosts.

## P1: user experience

- [ ] Manually accept real hidden-input dialogs on macOS/Windows/Linux: entry, save, cancel, timeout. Synthetic input and syntax checks do not replace this.
- [ ] Standalone executable packages to reduce Python setup.
- [ ] OS credential stores and plaintext migration; current files remain permission-protected plaintext.
- [ ] Evaluate task-wide token/currency limits, caching and bounded health records; current limits are per-command HTTP/time plus Agent task accounting.
- [ ] Add platform operations according to real demand, reusing authorized tools. Native Zhihu/Xiaohongshu/Weibo search and complete comments are not implemented.

## P2: add sources for demonstrated gaps

- [ ] Perplexity Search: another raw search-results source.
- [ ] Firecrawl Search/Scrape: search and explicitly selected page extraction.
- [ ] Parallel Search: preserve objective/query differences.
- [ ] Serper and SerpApi: third-party Google SERP access where needed.
- [ ] Jina Search: separate integration and billing from the implemented keyless Reader.

## Outside current scope

- ~~Self-hosted SearXNG integration.~~ Deferred out of scope.
- ~~Self-built web indexes and enterprise document search.~~ Deferred out of scope.
- ~~Require mode selection on every request.~~ Default Smart; preferences optional.
- ~~Require setup before any search without a key.~~ Use keyless access directly.
- ~~Open key signup pages automatically.~~ Print links only.
- ~~Ask users to find installation/config files.~~ Agent locates them.

Full-site crawling, bulk logins and challenge solving are not goals for this stage.

## Previous versions

- v0.1.0: DeepSeek Search/Fetch, Yuanbao SearchPro, hidden input and explicit dual-source calls.
- v0.2.0: local GUI input and tag publishing; real desktop acceptance remains pending.
- v0.3.0: Tavily, Exa, Brave, Bocha, v1/v2 migration, HTTP budgets and native metadata.
- Historical scope: [changelog](CHANGELOG.en.md), [validation](VALIDATION.en.md).

## Publishing

- [x] Chinese default with English switches and same-language navigation; reproducible packages and SHA-256.
- [ ] Issue templates for setup, search failures and source proposals.
- [ ] Marketplace-specific fields, screenshots, review and installation validation once selected.
