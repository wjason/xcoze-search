# Changelog

[简体中文](CHANGELOG.md) | **English**

## Unreleased

- Publish a bilingual 100-question benchmark with eight new groups and per-question review criteria.
- Expand the Agent benchmark to 20 questions, verify against original sources and add a weekly public-source audit.
- Add a bilingual Agent search benchmark and live report, keyless benchmark isolation, and query guidance for repositories and disclosures.
- Add per-source, per-action support status and live-check records, with pending candidates listed separately.
- Add 11 recent official China listings, DATA.GOV.HK update RSS, and 14 public-index scopes; scoped indexes are not native APIs.
- Add recent public NDRC, National Bureau of Statistics and National Energy Administration listings; document additional Chinese public sources.
- Add public NASA media, U.S. Federal Register, World Bank indicator and recent USGS earthquake sources.
- Add public metadata search for Open Library, DataCite, Zenodo and Wikidata.
- Check supported keyless sources with live requests and record access limits.

## v0.9.1 — 2026-11-05

- Distinguish configuration permission failures, configuration read errors and other local permission failures.
- Summarize the source map on the homepage and check 165 reference endpoints; page responses do not establish search API acceptance or integration.
- 174 offline tests pass.

## v0.9.0 — 2026-11-05

- Add fixed publisher RSS/Atom windows with literal/date filtering and coverage metadata: CNS latest/finance and BBC World. Read originals only when needed.
- Add native-first govcn finite latest-policy retrieval; preserve portal dates without claiming complete government coverage or effective dates.
- Add native original-post reading for Python/Rust Discourse and V2EX with per-site pacing/pauses, bounds and explicit truncation. Reject reply targets, do not claim complete threads, and stop reader fan-out after access denial.
- Count incomplete HTTP bodies as redacted network failures. Keyless 401/403 no longer blames the user's key.
- 170 offline tests pass. Eight of nine live operations succeeded; V2EX returned 403. News/policy index-to-original flows passed: 11 API HTTP attempts, no keyed calls/browser. Publish bilingual evidence with failures and source-window limits.


## v0.8.0 — 2026-11-05

- Add keyless `trending` actions for Zhihu's hot list, Bilibili hotwords and V2EX hot topics. One endpoint, no retries, credentials or browser; ordinary keyword searches do not request feeds.
- Preserve source order, native heat units and retrieval time. Feeds do not establish native keyword search, read bodies/comments or complete site rankings. Catalog feed capabilities remain separate from search coverage.
- Serialize and pace feeds across local processes, pause access denials for 15 minutes and honor Retry-After. Exclude explicit Bilibili commercial markers; no hardcoded cookies or aggregation servers.
- Label Xiaohongshu/Weibo index destinations as note/post links, profiles or other pages, without claiming bodies were read.
- 159 offline tests pass and all three new paths initially succeeded live. Installed V2EX acceptance then returned 403 and correctly paused. Retain Weibo 403, Bilibili keyword-search 412 and profile-heavy Xiaohongshu index results in the bilingual report. Native search/comments for these platforms have not been added.


## v0.7.2 — 2026-11-04

- Compare free/DeepSeek/Smart on six real tasks, with same-query 360, official-site, concise-query and real limit/recovery observations. Publish bilingual evidence without equating nonempty output with correctness.
- Filter experimental RSS/HTML/browser rows for obvious Chinese mismatch, missing code identifiers and some explicit time conflicts. Record removals and retain ranks; semantic APIs/native metadata remain outside this lexical rule.
- Pause DDG verification for 15 minutes and skip it automatically; query-specific browser relevance failures no longer pause the whole source.
- Do not reserve browser slots for GitHub. Complement existing quality evidence only with configured services or Exa, skipping extra weak RSS/HTML calls and capping automatic complement request timeouts at 3 seconds. Preserve failure fallback, free isolation, explicit sources and lower budgets.
- Keep 360 as emergency leads; retain English-doc/GitHub gaps, stale content and close tail latency. 149 offline tests pass; measured calls/timings/costs are in the report.

## v0.7.1 — 2026-11-03

- Default browser fallback to 360 Search, retaining explicit Bing/Google. Extract visible organic destinations, excluding ads/AI cards.
- Fix readiness on hidden placeholders. Launch a blank page, schedule one navigation, wait for visible rows and report launch/navigation/wait/extraction/close timings.
- Distinguish explicit no-match, hidden rows, network pages, verification and timeout. No-match pages no longer waste a wait or trigger failure cooldown. Add conservative Chinese browser mismatch rejection; preserve API priority and free isolation.
- 141 offline tests pass. Three real retrieval tasks and real DDG-challenge-to-browser recovery passed with zero keyed API attempts; source bodies were checked separately. Retain GitHub index misses and weaker doc queries; multi-network/OS acceptance is pending.
- Add an explicit --live browser evaluator and bilingual report. Simulated quota injection remains a separate safety regression.

## v0.7.0 — 2026-11-03

- Detect Exa anonymous HTTP/MCP quota errors, share Search/Fetch pauses, honor Retry-After and skip later calls; never invent wire status or upgrade to keyed services.
- Added optional existing agent-browser search: API-first, isolated headless session, fixed commands, key-free environment, one navigation, close and failure cooldown, with no automatic dependency install.
- **Default change:** total automatic source cap increases from two to three; normally two APIs plus one browser when available. Lower saved caps are retained. Successful API evidence never launches a browser. Auto API caps are eight seconds; browser work defaults to 15 plus up to six seconds close grace.
- Added --browser auto/off and saved preference, --browser-engine/--browser-timeout, execution_summary and separate API/browser request accounting.
- 135 offline tests passed. Injection proves zero keyed free-mode attempts. Live anonymous API succeeded without a browser; live browsers returned a shell/timeout and failed availability acceptance. Simulated recovery is not represented as real retrieval. Bilingual report and reproducer included.

## v0.6.0 — 2026-11-03

- Added nine keyless adapters: Wikipedia en/zh, Stack Exchange, arXiv, Crossref, npm, crates.io, GitLab, Europe PMC and Hugging Face, with task-scoped native routing and existing free/budget boundaries.
- Offline platforms distinguishes native APIs, public indexes and local executable presence; more video/community index scopes do not imply native subtitle/comment support.
- New-source OS serialization, pacing/backoff, Stack Exchange duplicate/quota handling, gzip decoding and decompressed size limits; suppressed requests count zero HTTP.
- Reviewed Agent Reach 1.6.1 and ran a limited same-task comparison. Added opt-in fetch --max-characters after observing long-page clipping (Jina/keyless Exa, default 24000, maximum 200000); more text does not prove completeness.
- 120 local offline tests passed; live observations, pacing follow-ups, bilingual reports/instructions retained. No universal coverage or overall superiority claim.

## v0.5.0 — 2026-11-03

- Compared keyless, DeepSeek and Smart on six live tasks plus two Chinese holdouts, with bilingual reports, sanitized receipts and a reproducible runner.
- General keyless search now starts with Exa MCP, with Bing/DDG fallbacks. Obvious zero-topic-overlap experimental RSS/HTML results may trigger bounded fallback.
- **Behavior change:** quality reference/current tasks may consult a complementary source within the existing two-source cap, accumulating results. General tasks, platform routes, explicit selection and free/balanced do not force two sources. Internal --intent does not require user mode selection.
- Preserve first-source results and errors if a complement fails; mark duplicate URLs without cross-provider score ranking. Read current official pages for prices, rules, versions and conflicts.
- 103 local offline tests passed. Live runs used 66 search HTTP attempts; known DeepSeek search estimate USD 0.02325, not an invoice, with model costs unknown. Keyless/complementary search does not guarantee truth, index freshness or availability.

## v0.4.1 — 2026-11-03

- Correct GitHub capabilities: repository update dates are not article publication filters; unsupported date filters are no longer advertised.
- Align offline plan and execution of all: configured keyed sources only; use auto for keyless routing.
- Classify keyless 401/403 and DDG 202 as access/verification issues; doctor cannot succeed without checks.
- Consolidate validation evidence: 94 offline tests pass with successful/restricted source checks retained. Jina Reader retrieves/extracts text and is skipped when text is already available.

## v0.4.0 — 2026-11-03

- Add keyless Bing RSS, DuckDuckGo HTML, Exa MCP, GitHub, HN and Jina Reader. Public feeds/HTML are experimental; official keyless services retain access limits.
- Default Smart: keyless without keys, quality-first with configured keys, structured GitHub/HN routes first. Bounded fallback handles failed/empty calls; the Agent evaluates semantic evidence gaps.
- Add saved preferences, free/balanced/quality strategies, per-call overrides, offline plan, source disabling and reset. Free excludes keyed adapters; ordinary searches never rewrite config.
- Bound automatic source count, HTTP attempts and waiting; retain constraints and report routing/failure history.
- **Behavior changes:** auto now has bounded fallback instead of fixed single-source selection; Fetch defaults to auto instead of DeepSeek. Pin sources for older behavior; both and explicit multi-source semantics remain.
- Add scoped public-index search for Zhihu/Xiaohongshu/Weibo with coverage boundaries. Remove SearXNG, self-built indexes and enterprise document search from current scope.
- Record local keyless/keyed auto and recovery checks separately; no universal quality ranking, and Yuanbao real-account testing still awaits credentials.

- Simplify both homepages by removing the language index table; retain the top language switch and keep document links within the selected language.

- Add English versions of all documentation and agent instructions, keeping Chinese as default, with reciprocal links, bilingual packaging, and release notes.

- Add agent installation instructions using “Install” plus the GitHub repository URL, followed by configuration examples, to the README and installation guide.

## v0.3.0 — 2026-11-02

### Multiple providers

- Add Tavily Search/Extract, Exa Search/Contents, Brave Web Search, and Bocha Web Search.
- Introduce registered adapters and offline capabilities for options, limits, endpoints, environment variables, and key-console links.
- Select multiple providers with comma-separated names or explicitly select all configured providers with all. Both remains DeepSeek plus Yuanbao; auto never silently switches.
- Reject unsupported options before networking. Preserve page text, snippets, highlights, summaries, and generated answers separately without automatically requesting extra generation.

### Infrastructure

- Add schema v2 with read compatibility for v1. Explicit migration and saving after successful input create a backup first. Cancellation/migration failure does not overwrite original credentials.
- --max-requests caps actual HTTP attempts, including retries/failures, with per-provider timing, counts, and reported usage/cost. Unknown cost remains null.
- Standardize error categories, exhausted budgets, application errors, per-URL extraction failures, and multi-provider partial success.
- Add 12 bilingual search queries and three extraction URLs, separate search/extraction evaluation, offline defaults, explicit live execution, and a shared budget.

### Validation and limits

- 67 offline tests passed using only the Python 3.10+ standard library.
- DeepSeek Search/Fetch live regression passed with one request each without rewriting existing v1 configuration.
- The four added providers lack live account verification. Yuanbao remains pending without a test credential.
- Manual desktop acceptance, standalone executables, and OS credential storage remain planned.
- Publish as Pre-release while retaining v0.1.0/v0.2.0 tags/assets.

## v0.2.0 — 2026-11-02

### Configuration entry point

- Start setup in conversation, with the agent locating the script and launching local hidden input.
- Provide official key-console links without automatically opening a browser; wait for the user before key entry.
- Add setup --gui using macOS dialogs, Windows PowerShell/WinForms, or Linux Zenity, retaining terminal input and variables.
- Cancellation, timeout, or dialog failure does not save input. Child output is not forwarded to the agent. Verification failure after saving is reported explicitly.
- Preserve terminal hidden input, variable precedence, and the existing configuration format.

### Validation and limits

- 36 offline tests passed: 33 search/setup tests and three release checks. macOS dialog syntax passed compilation.
- Real desktop input/cancellation on macOS/Windows/Linux and Yuanbao live account tests remain pending.
- Python 3.10+ remains required. Standalone binaries and OS credential storage remain planned.

### Documentation

- Define the README as a multi-provider agent search project with current/planned features distinguished.
- Add service research, a prioritized roadmap, and contribution instructions.
- Move unfinished setup work out of completed features and strike through replaced approaches.
- Retain published v0.1.0 tags/assets unchanged.

### Maintenance

- Include new project documentation in future release manifests.
- Add tag-triggered GitHub Pre-release publication, with runtime/Skill/package/changelog version checks, cross-platform tests, ZIPs, and SHA-256 checksums.

## v0.1.0 — 2026-11-02

First public preview.

- DeepSeek Search/Fetch and Tencent Yuanbao SearchPro adapters.
- Hidden local key input, environment variables, and default-provider configuration.
- Single-provider and explicit dual-provider search, source retention, and partial failure output.
- Fix Windows configuration-root handling so an explicit XDG_CONFIG_HOME does not eagerly require a resolvable home directory.
- 25 offline tests and Windows/Linux, Python 3.10/3.12 CI.
- Publish the Skill package, source downloads, documentation, and SHA-256 checksums.

DeepSeek live account verification was completed on 2026-10-24; Yuanbao verification remains pending. See [validation records](VALIDATION.en.md).
