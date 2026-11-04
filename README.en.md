# xcoze search

[简体中文](README.md) | **English**

[![Tests](https://github.com/wjason/xcoze-search/actions/workflows/test.yml/badge.svg)](https://github.com/wjason/xcoze-search/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**An out-of-the-box web search entry point for Agents.** Use public routes without a key; configured keys enable quality-first routing by default. The Agent selects sources, reads pages and searches for missing evidence, stopping when it has enough. Users ask normally; strategies and source preferences are optional.

[Ask your Agent to install](#install) · [Use in your Agent](#use-in-your-agent) · [Sources](#sources) · [Configure keys](#configure-keys) · [Roadmap](TODO.en.md)

## Install

### Ask your Agent

Send this message to your Agent:

```text
Please install this Skill: https://github.com/wjason/xcoze-search
```

Use an Agent that supports Skill installation and can execute local scripts. It installs according to its host's rules; reload or start a new session if prompted. Installation needs no API key, and you do not need to locate the skill directory yourself.

Then check that it can actually search:

```text
Use xcoze search to find microsoft/markitdown on GitHub. Give me the repository link and explain what it does.
```

Python 3.10+ is required. Basic search uses only the standard library, with no additional Python packages. Browser fallback is optional, not a prerequisite for searching. Chat-only environments without local script execution cannot run this Skill.

### Other installation methods

The optional Skills CLI installation method requires Node.js:

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

Alternatively unpack the [v0.7.2 Skill ZIP](https://github.com/wjason/xcoze-search/releases/download/v0.7.2/xcoze-search-skill-v0.7.2.zip) into your assistant's skill directory. Start a new session or reload as required by the host. See [installation](INSTALL.en.md).

## Use in your Agent

### Ask normally

Once installed and loaded, ask questions that need current sources. The Agent can call the Skill when the task needs it; you do not need to name it, choose sources or provide parameters every time:

```text
Find offshore wind policy updates from the past week. Prefer official pages and include publication dates and source links.
```

```text
Read the official Python asyncio documentation and explain how TaskGroup handles exceptions. Include the documentation link.
```

```text
Find open-source industrial vision projects on GitHub. Compare their purpose, licenses and deployment requirements.
```

To request it explicitly, start with “Use xcoze search.” If the Agent does not recognize the Skill, ask it to check installation and loading. Reload or start a new session as required by your host, then try again.

### Change search preferences in conversation

**Smart** is the default: no key uses keyless sources; configured, enabled keys make the default quality-first. You can also tell the Agent:

| Goal | What to say |
|---|---|
| Use keyless sources from now on | “Set xcoze search to free mode for future searches.” |
| Start with keyless sources, then use configured services when needed | “Set xcoze search to balanced mode.” |
| Restore automatic selection | “Clear xcoze search preferences and restore default Smart routing. Keep my keys.” |
| Choose a source for one request | “Use DeepSeek for this search only: …” |
| Limit this request to keyless sources | “Use free mode for this search only: …” |

“From now on” saves a preference; “this search only” affects one request. Named commercial sources such as DeepSeek require their own configured keys. Free mode never calls keyed search APIs.

To add a service, say “Configure DeepSeek for xcoze search.” The Agent provides the official signup link, then guides you through a local hidden-input dialog. **Never paste keys into chat.** See [configure keys](#configure-keys) and [setup and troubleshooting](references/setup.en.md).

## Sources

### No key required

| Source | Implemented | Limits |
|---|---|---|
| Bing RSS | General public web search | Experimental public feed; at most 10 results, potentially missing dates or relevance |
| DuckDuckGo HTML | General public web search | Experimental HTML parsing; verification pages and changes may block it |
| Exa hosted MCP | Search and page reading | Official rate-limited keyless access; relies on Exa, separate from the keyed Exa API |
| GitHub | Public repository search and default-branch README | Anonymous rate limits; excludes code search, private repositories and full Issue/PR adapters |
| Hacker News | Algolia story search and official single-item reading | Discussion URLs and outbound articles stay separate; child IDs are not fetched comments |
| Jina Reader | Page text extraction | Official rate-limited keyless reading; Jina Search is not integrated |
| Wikipedia | English/Chinese article search | Excerpts/edit timestamps, not primary-source or full-text proof |
| Stack Exchange | Questions across Stack Overflow and six other communities | Question excerpts do not mean answers/comments were read |
| arXiv | Paper search, abstracts and submission-date ranges | Preprint abstracts, without PDF text or peer-review guarantees |
| Crossref | DOI/author/publication metadata and available abstracts | Match author/year as well as title |
| npm / crates.io | JavaScript/Rust package search and version metadata | Neither a security audit nor a quality score from downloads |
| GitLab.com | Public project name/path/description search | No code/private search; stars do not establish official identity |
| Europe PMC | Biomedical metadata, abstracts and date ranges | No full text/clinical validation; upstream dates may be inferred |
| Hugging Face | Public model metadata search | No model downloads/inference; gated models still require authorization |

The Agent can reuse available native search, page reading and browser tools; this Skill does not install or take them over. Zhihu, Xiaohongshu, Weibo, YouTube, Bilibili, Reddit, X, V2EX and Douban support scoped public-index search, which does not promise native site search, complete text or comments. Use existing authorized platform tools for those operations when available.

### Bring your own key

| Service | Implemented | Environment variable |
|---|---|---|
| DeepSeek | Search, Fetch | `DEEPSEEK_API_KEY` |
| Tencent Yuanbao | SearchPro with standard/dynamic summaries | `YUANBAO_API_KEY`, alias `TENCENTCLOUD_WSA_APIKEY` |
| Tavily | Search, Extract | `TAVILY_API_KEY` |
| Exa | Search, Contents | `EXA_API_KEY` |
| Brave Search | Web Search | `BRAVE_API_KEY` |
| Bocha | Web Search | `BOCHA_API_KEY` |

Accounts and billing are independent. Configured, enabled keys participate in default quality-first routing. Free strategy excludes all keyed adapters, including accounts with promotional credits. See [provider contracts](references/providers.en.md).

Implementation, account verification and search quality are separate. Local checks on 2026-11-03 obtained usable Bing RSS, GitHub, HN and Jina responses; Exa keyless MCP initially returned 403 but later search succeeded, DuckDuckGo returned a verification response, and GitHub README returned 403. These are network-specific observations, not availability promises. Keyed-provider evidence is in [validation](VALIDATION.en.md).

## Automatic routing

- **Smart by default:** no syntactically usable keys selects keyless routes; available keys select quality-first routing. Key presence does not establish live account access.
- **Task-aware:** The Agent can select native public indexes for encyclopedias, questions, papers, packages, models, GitHub/GitLab and HN. Known URLs should use native readers when useful; script auto-reading starts with Jina/Exa keyless readers.
- **Bounded complement/fallback:** general keyless search starts with Exa MCP, with Bing/DDG fallbacks. Quality reference/current tasks may consult a complementary source within the existing two-source cap. General tasks and successful GitHub/HN routes return immediately; empty/failed calls may fall back. Defaults are three total sources and 45 seconds. With a browser available, at most two compatible API paths precede browser fallback. Lower saved caps remain effective; the API HTTP budget still applies. The Agent checks gaps and reads current primary pages for prices, rules, versions and conflicts.
- **Optional controls:** quality, balanced, free, or a named source. Per-request choices override saved preferences; explicit `--strategy free` conflicts with keyed sources.

Smart combines transparent capability/source rules and Agent judgment. It does not train a router, compare native scores across providers or claim a quality leaderboard. Initial keyed-provider order is configuration policy, not a performance ranking. See [routing](references/routing.en.md).

Six live tasks and two Chinese holdouts on 2026-11-03 found paid retrieval faster in this sample, with keyless/native routes adding useful primary and dated evidence. Routing was revised accordingly. See the [dated comparison](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03.en.md), including latency, estimated costs and limitations; this is not a general accuracy claim.

There are 15 keyless API/reader adapters (14 search-capable, one reader-only), plus an optional local-browser search path. Offline `platforms` distinguishes scope and optional executable presence from live verification. See [open sources and local-tool cooperation](references/open-sources.en.md) and [live checks/Agent Reach study](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03-open-sources.en.md).

## Exa limits and browser fallback

An exhausted anonymous Exa source is paused and skipped on later calls. Retry-After is honored; absent a recovery time, a 15-minute pause precedes another probe, without promising quota reset then. Smart with keys retains API priority; platform tasks prefer native APIs. Healthy API results never start a browser, including when API complements are useful.

Browser search launches lazily only without usable API results. It requires an existing agent-browser/working local Chrome, with no installation/login/personal-session reuse. Automatic APIs cap each source at 8 seconds; browser work at 15 seconds plus up to 6 seconds close grace. Ordinary searches do not run live health checks. Ask the Agent to disable browser fallback, or use preferences --browser off. Free strategy never calls keyed providers.

v0.7.2 compares free, DeepSeek and Smart on six Chinese news, English-doc and GitHub tasks, with separate 360 probes. Healthy anonymous Exa can retrieve primary sources directly; under limits, 360 is an emergency lead source with English-doc/GitHub coverage gaps. Fixes reject irrelevant/old-year rows, pause repeated DDG challenges, skip weak complements and preserve API slots for GitHub. The [comparison](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03-comparison.en.md) retains failures, timings, cost estimates and changing conditions, not a universal accuracy claim.

## Configure keys

Keys are optional. To add a service, tell the Agent:

```text
Configure DeepSeek for xcoze search.
```

The Agent prints official signup links without opening a browser, then launches a local hidden-input dialog when ready. Never paste keys into chat. Verification after saving can incur one search charge. Yuanbao requires its search service key, not Tencent Cloud SecretId/SecretKey. See [setup](references/setup.en.md).

Credentials are currently plaintext protected by local permissions, without OS credential-store integration. Environment variables take precedence. v1 configs remain readable and the existing private-backup migration applies when saving.

## Command-line reference

The Agent normally locates the Skill and runs these commands; users do not need to find files:

```bash
python3 scripts/xcoze_search.py search 'Python asyncio official documentation'
python3 scripts/xcoze_search.py search 'industrial vision' --platform github
python3 scripts/xcoze_search.py search 'AI coding' --platform hackernews --start-date 2026-11-01
python3 scripts/xcoze_search.py search 'playwright' --platform npm
python3 scripts/xcoze_search.py search 'wind power' --platform wikipedia
python3 scripts/xcoze_search.py platforms
python3 scripts/xcoze_search.py fetch 'https://docs.python.org/3/library/asyncio.html' --max-characters 100000
python3 scripts/xcoze_search.py preferences --strategy free
python3 scripts/xcoze_search.py preferences --strategy balanced
python3 scripts/xcoze_search.py preferences --reset
python3 scripts/xcoze_search.py search 'offshore wind digitalization' --provider deepseek,yuanbao --max-requests 4
python3 scripts/xcoze_search.py plan 'Python asyncio' --platform github
```

`plan`, `status`, and `capabilities` never connect. Ordinary searches do not need doctor first. `--mode` retains its Yuanbao meaning; routing uses `--strategy`.

v0.4.0 changes `auto` to routing and Fetch's default to `auto`. Pin a source for the previous deterministic behavior. `both` still means DeepSeek plus Yuanbao; explicit multi-source requests never expand silently. Automatic recovery can return `ok:true` while retaining earlier errors and attempts; explicit multi-source partial failure still exits 4. See [output](references/output.en.md).

## Development and scope

Run offline tests: `python3 -m unittest discover -s tests -v`. Native order and scores remain intact, summaries and page text stay separate, and script success never means facts were verified.

Focus is web search and reading. Self-hosted SearXNG, web indexes and enterprise document search are outside current scope; logins, challenge solving and full-site crawling are not part of base installation. [Contributing](CONTRIBUTING.en.md) · [Changelog](CHANGELOG.en.md) · [Research](references/search-services.en.md)
