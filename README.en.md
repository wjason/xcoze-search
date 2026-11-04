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

Alternatively unpack the [v0.9.1 Skill ZIP](https://github.com/wjason/xcoze-search/releases/download/v0.9.1/xcoze-search-skill-v0.9.1.zip) into your assistant's skill directory. Start a new session or reload as required by the host. See [installation](INSTALL.en.md).

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

### Source map: 165 entries

The map includes integrated sources, items awaiting validation and restricted platforms. Counts are catalog entries; see details for integration and API availability.

| Category | Count | Common entries (up to 10) | Details |
|---|---:|---|---|
| Web search | 15 | Parallel Search MCP, Exa hosted MCP, Bing RSS, DuckDuckGo HTML, DuckDuckGo Instant Answer, 360 / Baidu / Sogou public search pages, Google / Bing / Brave / Mojeek public UI, Tavily API, Exa API, Brave Search API | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#general-web-search-and-reading) |
| Technical docs | 8 | Microsoft Learn MCP, MDN MCP, Cloudflare Docs MCP, OpenAI Docs MCP, Context7, Python official docs / Sphinx inventories, Rust std / docs.rs, Read the Docs / llms.txt publisher docs | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#official-technical-documentation) |
| News feeds | 14 | China News Service RSS, BBC RSS, CCTV / CGTN RSS, Xinhua RSS, DW RSS, UN News RSS, NASA news feeds, GDELT DOC / Context, Google News RSS, Guardian Open Platform | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#news-and-publisher-feeds) |
| Chinese policy | 19 | China gov.cn latest-policy index, NDRC notices / announcements, National Energy Administration, National Bureau of Statistics releases, National Data / NBS database, MIIT, Ministry of Commerce, Ministry of Ecology and Environment, People's Bank of China, CSRC | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#chinese-language-public-policy-disclosures-and-data) |
| Global government | 8 | Federal Register API, SEC EDGAR public data, GOV.UK content/search, UK legislation, Eurostat, World Bank Indicators, OECD SDMX, api.data.gov / govinfo / Congress APIs | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#international-government-and-statistics) |
| Research | 26 | arXiv, Crossref, DataCite, dblp, Europe PMC, NCBI PubMed / PMC E-utilities, HAL, OpenAIRE, Zenodo public records, Figshare public articles | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#papers-books-and-research) |
| Code and packages | 17 | GitHub REST public repositories, GitLab public projects, Codeberg / Forgejo, Gitee API, npm registry, PyPI JSON / Simple, crates.io, Maven Central, NuGet, Packagist | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#code-packages-and-models) |
| Communities | 10 | Hacker News / Algolia, Stack Exchange family, Discourse public communities, V2EX public API, DEV.to / Forem, Lobsters, Lemmy public instances, Mastodon, Bluesky public AppView, Cnblogs RSS | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#community-and-social-interfaces) |
| Knowledge and media | 8 | Wikipedia, Wikidata, Wikimedia Commons, Openverse, GBIF, iNaturalist, ROR, ORCID public API | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#knowledge-entities-and-media) |
| Archives | 3 | Common Crawl URL Index, Wayback / CDX, Arquivo.pt | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#historical-web-and-archives) |
| Energy, weather and geography | 10 | USGS earthquake feeds/API, NOAA NCEI data service, weather.gov API, EIA Open Data, ENTSO-E Transparency, NASA public APIs, Open-Meteo, OpenStreetMap Nominatim, Overpass public API, GeoNames | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#weather-geography-energy-and-events) |
| Restricted platforms | 9 | X API, Reddit Data API, Xiaohongshu, Weibo, Zhihu, Bilibili, WeChat / Sogou WeChat, Douyin / Kuaishou, Douban / Tieba / Juejin / CSDN / OSChina | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#platforms-without-unconditional-free-automation) |
| Self-hosted tools | 3 | SearXNG, RSSHub / RSS-Bridge, Miniflux / FreshRSS | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#toolsself-hosting-not-hosted-sources) |
| Patents | 4 | USPTO Open Data Portal, EPO Open Patent Services, Google Patents, CNIPA public services | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#patents-and-intellectual-property) |
| Finance and economics | 8 | FRED, US BLS public data, US Census data APIs, Tushare, BaoStock, CoinGecko Demo API, Yahoo Finance public pages, Stooq historical data | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#finance-economics-and-market-data) |
| Podcasts | 3 | Apple iTunes Search API, Podcast Index, Listen Notes | [More](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md#podcasts-and-audio-metadata) |

Reference checks covered 165 entries: 136 returned 2xx, 8 redirected, 17 returned HTTP errors and 4 had network failures. **A 2xx reference page does not prove a working search API or integration.** [Per-entry audit](https://github.com/wjason/xcoze-search/blob/main/research/source-reference-audit-2026-11-05.json).

Fifteen anonymous APIs were sampled: 14 returned expected structures and one returned 403. [View samples](https://github.com/wjason/xcoze-search/blob/main/research/source-functional-samples-2026-11-05.json).

### News feeds, government policy and community originals

- **Publisher RSS:** read China News Service latest/finance and BBC World feeds directly, with literal/date filtering of the current window. For example: “Find recent CIIE reports in the CNS feed, then read the originals.”
- **Government policy:** filter the gov.cn latest-policy index for titles, portal publication dates and official links. This is not a complete nationwide notice database; read originals to check effective dates.
- **Community originals:** read original posts on Python/Rust community forums. The V2EX original-post adapter is implemented but returned 403 on this network. Code indentation and links are retained; the original post is not a complete comment thread.

These paths need no key or browser. If a feed has no matches, the Agent can search under existing preferences; an empty window does not establish that no relevant news exists. [Usage](references/feeds.en.md) · [Live search/read checks](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-05-feeds-community.en.md)


### Community trends (no key)

Ask your Agent: “What questions are trending on Zhihu?” “What are Bilibili's hot search terms?” or “Show me V2EX's hot topics.”

| Platform | Directly retrieved | Evidence limits |
|---|---|---|
| Zhihu | Public hot-list questions, excerpts, displayed heat and question links | No answer or comment bodies |
| Bilibili | Public hotwords, native heat fields and search links | Hotwords are not video popularity rankings or video content |
| V2EX | Hot-topic titles, nodes, creation times, reply counts and links | No topic bodies or replies |

The Agent selects a feed when needed; ordinary searches do not request these feeds. Each snapshot retains its source order, retrieval time and metric meaning, without combining scores or promising complete coverage or availability. V2EX succeeded initially, then returned 403 during installed acceptance and was paused. One platform per call; no login, cookies or browser. See the [public-source checks and roadmap](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-05-public-platforms.en.md).

Xiaohongshu and Weibo currently use scoped public-index search. Links distinguish notes/posts, profiles and other pages. **Native site search, complete comments and live hot lists for these two platforms are not integrated.** The direct Weibo endpoint returned 403 in this check; the Xiaohongshu index sample mainly found profiles, not evidence that notes were read.

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

There are 17 keyless search/reader adapters (15 search-capable, two reader-only), plus three publisher RSS sources, three community hot-list paths and an optional local browser. Offline `platforms` distinguishes scope and optional executable presence from live verification. See [open sources and local-tool cooperation](references/open-sources.en.md) and [live checks/Agent Reach study](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03-open-sources.en.md).

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
python3 scripts/xcoze_search.py feeds
python3 scripts/xcoze_search.py feed --source bbc-world --query 'election'
python3 scripts/xcoze_search.py search '能源' --platform govcn --strategy free
python3 scripts/xcoze_search.py fetch 'https://discuss.python.org/t/109869' --strategy free
python3 scripts/xcoze_search.py trending --platform zhihu --count 10
python3 scripts/xcoze_search.py trending --platform bilibili --count 10
python3 scripts/xcoze_search.py trending --platform v2ex --count 10
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

[Free and public source map](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md): 165 source/candidate/exclusion entries separating keyless access, free credits, public pages and self-hosted tools, with live probes and priorities.

Run offline tests: `python3 -m unittest discover -s tests -v`. Native order and scores remain intact, summaries and page text stay separate, and script success never means facts were verified.

Focus is web search and reading. Self-hosted SearXNG, web indexes and enterprise document search are outside current scope; logins, challenge solving and full-site crawling are not part of base installation. [Contributing](CONTRIBUTING.en.md) · [Changelog](CHANGELOG.en.md) · [Research](references/search-services.en.md)
