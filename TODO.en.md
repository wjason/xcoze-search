# Roadmap

[简体中文](TODO.md) | **English**

Updated: 2026-11-02.

DeepSeek, Yuanbao, Tavily, Exa, Brave, and Bocha adapters are implemented. P0 infrastructure and P1 adapters are complete except for pending Yuanbao live verification. P2/P3 additions remain planned. Priorities reflect project coverage and integration needs, not market share, performance, retrieval quality, or promised release dates.

## Completed: v0.1.0

- [x] DeepSeek Search / Fetch.
- [x] Yuanbao Search Service API Key authentication.
- [x] Hidden local key input, environment variables, and default-provider selection.
- [x] Explicit dual-provider search, partial failures, and native result retention.
- [x] 25 offline tests and Windows/Linux, Python 3.10/3.12 CI.
- [x] Preview release, packages, user documentation, and checksums.

Yuanbao adapter implementation and live account verification are tracked separately; live verification remains pending.

## Completed: v0.2.0 preview

- [x] Conversational setup: the agent locates the tool and provides key-console links without opening pages.
- [x] setup --gui hidden local dialog, redaction, and cancellation/timeout/failure protection.
- [x] Compatibility with terminal hidden input, environment variables, and existing configuration.
- [x] 33 search/setup tests, Skill validation, and macOS dialog syntax checks.
- [x] Tag-triggered testing, version/changelog checks, ZIP/checksum generation, and GitHub Pre-release publication.

## Completed: v0.3.0 preview

- [x] Six-provider registry/capabilities, explicit multiple providers, and existing-command compatibility.
- [x] Read-only v1 configuration compatibility, private-backup v2 migration, and failure protection.
- [x] HTTP attempt budgets, failure/retry accounting, native usage/cost, and error categories.
- [x] 67 offline tests covering new protocols, configuration, and regression execution.
- [x] 12 bilingual search queries, three extraction URLs, and explicit live evaluation with a shared budget.

## Setup experience: future work

- [ ] **Desktop acceptance**: test real input, save, cancellation, and timeout on macOS, Windows, and Linux. Synthetic input and script syntax checks do not replace this.
- [ ] **Standalone executables**: reduce the Python installation requirement; current ZIPs contain scripts, not standalone apps.
- [ ] **OS credential storage**: evaluate services such as macOS Keychain with migration/rollback for current plaintext configuration. Storage is currently permissions-protected plaintext.

These remain future work, not completed v0.2.0 features.

## Retired or replaced setup approaches

- ~~Automatically open the official key-signup page.~~ Provide the official link in chat for the user to open.
- ~~Require users to locate installation/configuration files before setup.~~ Default to conversational setup with the agent locating and launching the local hidden-input tool. Terminal commands remain optional.

## P0: infrastructure complete, Yuanbao live verification pending

- [x] **Provider interface**: separate registration, authentication, request construction, and normalization. Register new adapters in scripts/search_providers.py without adding provider branches to the search loop.
- [x] **Capability declarations**: inspect search/fetch, inline page content, site/time/language filters, result counts, and query limits.
- [x] **Configuration compatibility**: versioned migration preserving existing keys/variables; failed migration does not overwrite credentials.
- [x] **Multiple providers**: selection beyond two services with auto/both compatibility and explicit recipients, retry, and switching behavior.
- [x] **Usage and budgets**: provider attempts/retries/reported usage, no invented costs, no automatically enabled extra paid operations.
- [x] **Error/result contracts**: distinguish empty results, authentication, application errors, rate limits, and partial success; retain unknown fields and separate snippets, excerpts, summaries, and text.
- [ ] **Yuanbao live verification**: use an activated account for SearchPro baseline/tier-specific parameters; retain only redacted metadata. No test credential is available as of 2026-11-02.
- [x] **Regression cases**: Chinese/English docs, news, freshness, and conflicting-information cases, with separate retrieval/extraction review. Includes dated corpus and offline/explicit-live entry points, not a universal accuracy claim.

## P1: implemented providers in v0.3.0

- [x] **Tavily Search + Extract**: queries, domains/time, search/content mapping; generated answers remain separate and opt-in.
- [x] **Exa Search + Contents**: retrieval/extraction with separate text/highlights/summary, dates, and reported usage.
- [x] **Brave Web Search**: web results, country/language/freshness, extra snippets without labeling them full text.
- [x] **Bocha Web Search**: basic search, snippets/optional summaries, and time filters; AI Search cards remain a separate evaluation.

Protocol implementations and offline tests are complete. Live account calls and retrieval quality are unverified. “Implemented” does not mean “accepted with a real account.”

These cover agent-oriented search/extraction, retrieval/content APIs, general web search, and Chinese search. A shared corpus is still needed for quality, latency, and cost comparison. See [service research](references/search-services.en.md).

## P2: more providers and result types

- [ ] **Perplexity Search API**: native results, domain/language filters, and snippets; separate from generated-answer products.
- [ ] **Firecrawl Search + Scrape**: search first, explicit scraping, with extraction cost/latency recorded.
- [ ] **Parallel Search**: retain objective, search_queries, excerpts, and warnings without treating objectives as equivalent to literal queries.
- [ ] **Serper**: map its Google SERP service, verifying current authentication/fields in its console; handle organic results without mixing ads/cards.
- [ ] **SerpApi**: start with Google organic_results, status, pagination, and geography. Identify it as a third-party service, not Google's official API; evaluate Search Index separately.

## P3: self-hosting and optional content services

- [ ] **Jina Search / Reader**: evaluate search and URL reading separately, documenting keys, limits, formats, and sources; content extraction should not require an enabled search service.
- [ ] **SearXNG**: user-selected self-hosted instance/authentication, JSON availability checks; no default public instance or public-instance availability promise.

Model-native web tools, browser automation, and full-site crawling are outside these adapter commitments. Any addition needs its own environment, billing, and output contract.

## Releases and maintenance

- [x] Adapter extension documentation and contract tests in v0.3.0; see CONTRIBUTING.en.md.
- [ ] Issue templates for setup, search failures, and new-provider requests.
- [ ] Text truncation/token budgets with explicit truncation markers and original URLs.
- [ ] Evaluate caching, default-off behavior, expiry, removal, and sensitive-query handling.
- [x] Tag-driven packages tied to the same commit with checksums (v0.2.0).
- [x] Runtime/Skill/package/changelog version checks (v0.2.0).
- [ ] Marketplace-specific fields, screenshots, licensing, and installation checks once a marketplace is selected.

## Provider completion criteria

A provider moves from planned to supported only when:

1. Current official documentation supports implemented authentication, request, output, and error mappings.
2. Setup/status/doctor or equivalents distinguish configuration from live access.
3. Offline contracts and failures pass; live verification is separately disclosed without calling untested accounts verified.
4. Limits, costs, and recipients are documented; unsupported filters error rather than being silently discarded.
5. Configuration/command compatibility is explicit; examples run and packages match their source version.
