# Changelog

[简体中文](CHANGELOG.md) | **English**

## Unreleased

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
