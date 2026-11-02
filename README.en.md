# xcoze search

[简体中文](README.md) | **English**

[![Tests](https://github.com/wjason/xcoze-search/actions/workflows/test.yml/badge.svg)](https://github.com/wjason/xcoze-search/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Multi-provider search for AI agents.** Access official search and content-extraction APIs through one Skill. Bring your own API keys and choose which providers receive each request.

[Install](#installation) · [Configure](#api-key-setup) · [Usage](#usage) · [Roadmap](TODO.en.md) · [Contribute](CONTRIBUTING.en.md) · [Changelog](CHANGELOG.en.md)

## Documentation languages

Chinese is the default. Use the language links at the top of each page to switch. For English agent replies, say “Reply in English.”

| Document | 简体中文 | English |
|---|---|---|
| Project overview | [中文](README.md) | [English](README.en.md) |
| Agent instructions | [中文](SKILL.md) | [English](SKILL.en.md) |
| Installation | [中文](INSTALL.zh-CN.md) | [English](INSTALL.en.md) |
| Setup and troubleshooting | [中文](references/setup.md) | [English](references/setup.en.md) |
| Provider contracts | [中文](references/providers.md) | [English](references/providers.en.md) |
| Output contract | [中文](references/output.md) | [English](references/output.en.md) |
| Service research | [中文](references/search-services.md) | [English](references/search-services.en.md) |
| Roadmap | [中文](TODO.md) | [English](TODO.en.md) |
| Contributing | [中文](CONTRIBUTING.md) | [English](CONTRIBUTING.en.md) |
| Changelog | [中文](CHANGELOG.md) | [English](CHANGELOG.en.md) |
| Validation records | [中文](VALIDATION.md) | [English](VALIDATION.en.md) |
| Publishing | [中文](PUBLISHING.zh-CN.md) | [English](PUBLISHING.en.md) |
| Marketplace listing | [中文](MARKETPLACE.zh-CN.md) | [English](MARKETPLACE.en.md) |
| Regression guide | [中文](https://github.com/wjason/xcoze-search/blob/main/evaluations/README.md) | [English](https://github.com/wjason/xcoze-search/blob/main/evaluations/README.en.md) |

## Supported providers

| Provider | Web search | Content support | Live account verification |
|---|---|---|---|
| DeepSeek | Implemented | Search content and Fetch | Search/Fetch regression passed on 2026-11-02 |
| Tencent Yuanbao | Implemented | Standard and dynamic summaries | No test credential; live verification pending |
| Tavily | Implemented | Search snippets, optional page content, Extract | Not tested with a live account |
| Exa | Implemented | Search/Contents text, highlights, and summaries kept separate | Not tested with a live account |
| Brave Search | Implemented | Web snippets and optional extra snippets | Not tested with a live account |
| Bocha | Implemented | Web Search and optional summaries | Not tested with a live account |

Current release: [v0.3.0 preview](https://github.com/wjason/xcoze-search/releases/tag/v0.3.0). Protocol implementations and offline tests are complete for the added providers. This does not establish account access or search quality. See [provider contracts](references/providers.en.md) and [validation records](VALIDATION.en.md).

## Installation

Requires Python 3.10+ and an Agent Skills host that can execute local scripts. No additional Python packages are needed. The Skills CLI installation method also requires Node.js; manual extraction does not.

### Ask your agent to install it

Send this to an agent that supports Skill installation and local command execution:

```text
Install https://github.com/wjason/xcoze-search
```

For more explicit instructions:

```text
Install this Skill: https://github.com/wjason/xcoze-search
Check the Python runtime and install it in the current assistant's skills directory.
```

After installation, start a new chat or reload the assistant if instructed, then send:

```text
Configure xcoze search with DeepSeek. Reply in English.
```

Replace DeepSeek with another supported provider as needed. The agent provides an official key-console link and starts a local hidden-input dialog once you are ready. Installation does not require an API key. Keep keys out of chat. If your agent cannot install Skills or execute local commands, use the alternatives below.

### CLI or manual installation

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

Alternatively, download the [v0.3.0 Skill ZIP](https://github.com/wjason/xcoze-search/releases/download/v0.3.0/xcoze-search-skill-v0.3.0.zip) and place `xcoze-search/` in your assistant's skills directory. The default Codex entry is `~/.codex/skills/xcoze-search/SKILL.md`; use the corresponding skills directory if CODEX_HOME is set.

Start a new chat after installation or an update; reload the assistant if it has not discovered the Skill. See the [installation guide](INSTALL.en.md) for updates, configuration formats, and removal. The ZIP contains Python scripts; a standalone executable distribution is still planned.

## API key setup

Ask the assistant:

```text
Configure Tavily for xcoze search. Reply in English.
I already have an Exa key; start local setup.
Replace my xcoze search Yuanbao key.
Check my xcoze search configuration status.
```

The assistant provides an official key-console link. Open it yourself; the Skill does not open a browser automatically. Once you have a key, reply “Ready to enter the key.” The agent starts a local hidden-input dialog, saves the key, and performs one potentially billable search to check access. You do not need to find an installation directory or configuration file. Do not paste the key into chat.

The dialog uses macOS system dialogs, Windows PowerShell/WinForms, or an existing Zenity installation on a Linux desktop. Without an accessible desktop, use hidden input in your own visible terminal or managed environment variables. Manual desktop acceptance tests remain pending.

| Provider | Official key console | Environment variable |
|---|---|---|
| DeepSeek | [Platform](https://platform.deepseek.com/api_keys) | `DEEPSEEK_API_KEY` |
| Yuanbao | [Search console](https://console.cloud.tencent.com/wsapi/index) | `YUANBAO_API_KEY`; alias `TENCENTCLOUD_WSA_APIKEY` |
| Tavily | [Dashboard](https://app.tavily.com/home) | `TAVILY_API_KEY` |
| Exa | [Dashboard](https://dashboard.exa.ai/api-keys) | `EXA_API_KEY` |
| Brave | [Dashboard](https://api-dashboard.search.brave.com/app/keys) | `BRAVE_API_KEY` |
| Bocha | [Open platform](https://open.bochaai.com/) | `BOCHA_API_KEY` |

Yuanbao requires a Search Service API Key; Tencent Cloud SecretId/SecretKey and other product keys are not interchangeable. Each provider has its own activation, authorization, and billing.

For manual setup, run these in your own visible terminal, replacing the path with the actual installation directory:

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider tavily --verify
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider exa --gui --verify
```

Without `--gui`, setup uses hidden terminal input; with it, setup opens a local input dialog. Cancelling leaves the configuration unchanged. If `--verify` fails, the key has been saved, but access has not been verified. Only `--default` changes the default provider. On Windows, `py -3` can replace `python3`. macOS also retains `scripts/setup.command` as a manual entry point.

Environment variables take precedence over saved credentials and must be visible to the process running the assistant. Credentials currently use a permissions-protected plaintext file in the user configuration directory, not an OS keychain. Existing v1 configuration remains readable and ordinary searches do not rewrite it. Explicit migration or saving new configuration creates a private backup first. See [setup and troubleshooting](references/setup.en.md).

## Usage

```text
Use xcoze search to find official sources on this topic and cite them.
Use Tavily to search for reports from the past week.
Use Exa to find the documentation, then read it; keep summaries and highlights separate.
Use Brave to search for English sources from the United Kingdom.
Use Bocha to search for industry news from the past week.
Cross-check this topic with DeepSeek, Tavily, and Exa, comparing original sources and dates.
```

CLI examples, run from the Skill directory:

```bash
# Inspect options, result counts, limits, and key-console links without networking
python3 scripts/xcoze_search.py capabilities

# Single-provider searches and filters
python3 scripts/xcoze_search.py search 'industrial vision' --provider tavily --freshness week --count 5
python3 scripts/xcoze_search.py search 'Python TaskGroup' --provider exa --site docs.python.org --start-date 2026-01-01 --highlights
python3 scripts/xcoze_search.py search 'energy storage' --provider brave --country GB --language en --freshness pw --extra-snippets
python3 scripts/xcoze_search.py search 'industrial vision' --provider bocha --freshness oneWeek --summary

# Explicit multiple providers, at most six HTTP attempts including retries
python3 scripts/xcoze_search.py search 'offshore wind digitalization' --provider deepseek,tavily,exa --count 5 --max-requests 6

# Explicit content extraction
python3 scripts/xcoze_search.py fetch 'https://docs.python.org/3/library/asyncio-task.html' --provider exa --highlights
python3 scripts/xcoze_search.py fetch 'https://docs.python.org/3/library/asyncio-task.html' --provider tavily
```

Provider selection:

- `auto` uses the configured default. Without one, it selects the first configured provider in this order: DeepSeek, Yuanbao, Tavily, Exa, Brave, Bocha. It does not silently switch after failure.
- `both` still means DeepSeek plus Yuanbao. Adding providers does not change existing commands.
- A comma-separated list selects specific providers; `all` selects every configured provider. Adding a key does not expand ordinary searches to more providers.
- All credentials and options are checked before a multi-provider request starts. Unsupported options cause an error. Tavily/Brave support at most 20 results per call; this adapter limits the others to 50. There is no automatic pagination.
- Fetch still defaults to DeepSeek. Specify Tavily or Exa explicitly to use their extraction APIs. The other three providers have search adapters only; no fallback extraction provider is selected.

Tavily `content` is snippets; `raw_content` is page content. Exa `text`, `highlights`, and `summary` remain separate. Yuanbao, Brave, and Bocha summaries are not labeled as full page text. Tavily generated answers require `--include-answer` and remain separate from source results.

## Budgets, usage, and errors

`--max-requests` caps actual HTTP attempts for the current invocation, including failures and retries. Search/doctor default to 12; Fetch defaults to 3. A request permits at most two retries, defaults to one, and doctor uses none. A multi-provider invocation needs at least one attempt available per provider. Budgets do not persist across invocations and are not monetary limits.

Results retain provider order, native scores, and original fields without comparing scores across providers. Output includes each provider's attempts, elapsed time, and any reported usage or cost. Unreported usage/cost is `null`, not an estimate. If a provider fails during multi-provider execution, successful results are retained with `ok:false`, `partial:true`, and exit code 4.

Empty results, authentication, billing/quota, rate limits, network failures, exhausted budgets, and invalid responses are reported separately. HTTP 200 extraction responses still require per-URL success checks. See the [output contract](references/output.en.md).

## Status and configuration migration

```bash
python3 scripts/xcoze_search.py status
python3 scripts/xcoze_search.py doctor --provider tavily
python3 scripts/xcoze_search.py doctor --provider deepseek,exa --max-requests 2
python3 scripts/xcoze_search.py migrate-config
```

Status does not make network requests or display keys. Doctor performs live searches; `search_verified:true` only establishes that this check returned usable results. Migration upgrades v1 configuration to v2 with a private original-file backup, preserving keys, the default provider, and extension fields. See [setup](references/setup.en.md) for failures and rollback.

## Development and regression checks

Run these from the repository or source distribution. The current source has 68 offline tests (67 at the v0.3.0 release), using only the Python standard library; CI covers Windows/Linux and Python 3.10/3.12.

```bash
python3 -m unittest discover -s tests -v
# Planning only: no credential reads or network requests by default
python3 scripts/evaluate.py --provider deepseek,tavily,exa
python3 scripts/evaluate.py --operation fetch --provider deepseek,tavily,exa
```

The source distribution includes 12 Chinese/English search queries and three extraction URLs covering technical documentation, original standards, dates, versions, and conflicting information. Domain matches support manual review; they are not factual-accuracy scores or provider rankings. Online execution requires `--live` and shares one run-wide request budget. See the [regression guide](https://github.com/wjason/xcoze-search/blob/main/evaluations/README.en.md), included in the source distribution.

P0 infrastructure and the four P1 adapters are implemented. Yuanbao live verification remains pending without a test credential. See the [roadmap](TODO.en.md) for P2/P3 providers, standalone executables, OS credential storage, and other work, and the [contribution guide](CONTRIBUTING.en.md) to contribute.

## Data, charges, and license

Queries and URLs go directly to the selected providers, not through a maintainer-operated server. The project collects no telemetry and does not automatically save search history. The regression tool writes a report only when an output file is explicitly selected.

Multiple providers, retries, extraction, generated summaries, or advanced search options may add charges under the provider's billing rules. This independently maintained integration uses official APIs; it is not an official product or certification from those providers. Do not submit unauthorized private queries or URLs containing access tokens.

[MIT License](LICENSE). Rights to search-result content remain with the respective rights holders.
