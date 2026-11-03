# Changelog

[简体中文](CHANGELOG.md) | **English**

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
