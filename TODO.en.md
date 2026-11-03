# Roadmap

[简体中文](TODO.md) | **English**

Updated 2026-11-03. Focus: Agent web search and source reading. Default automatic routing, public access without keys, quality-first with keys. Implementation, live access and search quality are recorded separately.

## v0.4.0: implemented

- [x] Smart selects quality with keys and free without keys; persistent quality/balanced/free preferences and per-call overrides.
- [x] Dependency-free Bing RSS, DuckDuckGo HTML and Exa keyless MCP search.
- [x] GitHub public repository/README adapters and HN story search/single-item reading.
- [x] Jina Reader and Exa keyless reading, with Fetch routed independently of search.
- [x] Scoped public-index search for Zhihu, Xiaohongshu and Weibo, URL-host checks and coverage boundaries.
- [x] Source/HTTP/time limits, preflight, fallback, offline plan and preference management.
- [x] Chinese/English instructions, setup, routing contracts and competitor implementation research.
- [x] Per-source local connectivity checks; successes and restrictions in [validation](VALIDATION.en.md) do not promise availability or accuracy.

## P0: task quality and reliability

- [ ] Compare keyless, single API and Smart on the same Chinese/English tasks: evidence support, primary sources, freshness, latency, request/model cost.
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
