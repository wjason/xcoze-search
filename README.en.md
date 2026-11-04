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

These are the search, reading and trend sources currently integrated into xcoze search. Availability and rate limits depend on each upstream service.

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

### Source directory

The directory covers all 165 entries in our research, including services not yet integrated and self-hosted tools outside the current scope. A directory entry or accessible website does not imply that its search API is available or supported. “Partially integrated” may refer to only some of the services or capabilities in an entry. Public endpoints may impose limits or usage conditions. [Research and verification details](research/free-sources-2026-11.en.md).

<details>
<summary>Web search and reading（15）</summary>

| Source | Access | Project status |
|---|---|---|
| [Parallel Search MCP](https://parallel.ai/mcp) | Public endpoint | Not integrated |
| [Exa hosted MCP](https://exa.ai/docs/get-started/exa-mcp) | Public endpoint | Partially integrated |
| [Bing RSS](https://www.bing.com/search?format=rss&q=python) | Public website | Partially integrated |
| [DuckDuckGo HTML](https://html.duckduckgo.com/html/) | Public website | Partially integrated |
| [DuckDuckGo Instant Answer](https://duckduckgo.com/api) | Public endpoint | Not integrated |
| [360 / Baidu / Sogou public search pages](https://www.so.com/) | Public website | Partially integrated |
| [Google / Bing / Brave / Mojeek public UI](https://www.google.com/) | Public website | Not integrated |
| [Tavily API](https://www.tavily.com/pricing) | Registration or conditions | Partially integrated |
| [Exa API](https://exa.ai/pricing) | Registration or conditions | Partially integrated |
| [Brave Search API](https://api-dashboard.search.brave.com/documentation/resources/help-feedback) | Registration or conditions | Partially integrated |
| [Firecrawl](https://www.firecrawl.dev/pricing) | Registration or conditions | Not integrated |
| [Serper](https://serper.dev/) | Trial credits | Not integrated |
| [SerpApi](https://serpapi.com/pricing) | Registration or conditions | Not integrated |
| [Search1API](https://s1.dev/docs/essentials/credits-and-limits) | Trial credits | Not integrated |
| [Jina Reader / Search](https://jina.ai/reader/) | Registration or conditions | Partially integrated |

</details>

<details>
<summary>Technical documentation（8）</summary>

| Source | Access | Project status |
|---|---|---|
| [Microsoft Learn MCP](https://learn.microsoft.com/en-us/training/support/mcp) | Public endpoint | Not integrated |
| [MDN MCP](https://developer.mozilla.org/en-US/mcp) | Public endpoint | Not integrated |
| [Cloudflare Docs MCP](https://developers.cloudflare.com/workers/get-started/prompting/) | Public endpoint | Not integrated |
| [OpenAI Docs MCP](https://developers.openai.com/resources/docs-mcp) | Public endpoint | Not integrated |
| [Context7](https://github.com/upstash/context7) | Registration or conditions | Not integrated |
| [Python official docs / Sphinx inventories](https://docs.python.org/3/) | Public website | Not integrated |
| [Rust std / docs.rs](https://docs.rs/) | Public website | Not integrated |
| [Read the Docs / llms.txt publisher docs](https://docs.readthedocs.com/platform/stable/reference/sitemaps.html) | Public website | Not integrated |

</details>

<details>
<summary>News and feeds（14）</summary>

| Source | Access | Project status |
|---|---|---|
| [China News Service RSS](https://www.chinanews.com.cn/rss/) | Public endpoint | Partially integrated |
| [BBC RSS](https://www.bbc.co.uk/news/10628494) | Public endpoint | Partially integrated |
| [CCTV / CGTN RSS](https://english.cctv.cn/rss/) | Public website | Not integrated |
| [Xinhua RSS](https://www.xinhuanet.com/english/rss/index.htm) | Public website | Not integrated |
| [DW RSS](https://rss.dw.com/rdf/rss-en-all) | Public endpoint | Not integrated |
| [UN News RSS](https://news.un.org/en/rss-feeds) | Public endpoint | Not integrated |
| [NASA news feeds](https://www.nasa.gov/rss-feeds/) | Public endpoint | Not integrated |
| [GDELT DOC / Context](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) | Public endpoint | Not integrated |
| [Google News RSS](https://news.google.com/) | Public website | Not integrated |
| [Guardian Open Platform](https://open-platform.theguardian.com/access/) | Registration or conditions | Not integrated |
| [NewsAPI.org](https://newsapi.org/pricing) | Registration or conditions | Not integrated |
| [GNews](https://gnews.io/pricing) | Registration or conditions | Not integrated |
| [NewsData.io](https://newsdata.io/pricing) | Registration or conditions | Not integrated |
| [TheNewsAPI](https://www.thenewsapi.com/pricing) | Registration or conditions | Not integrated |

</details>

<details>
<summary>Chinese government and public data（19）</summary>

| Source | Access | Project status |
|---|---|---|
| [China gov.cn latest-policy index](https://www.gov.cn/zhengce/zuixin/) | Public endpoint | Partially integrated |
| [NDRC notices / announcements](https://www.ndrc.gov.cn/xxgk/zcfb/tz/) | Public website | Not integrated |
| [National Energy Administration](https://www.nea.gov.cn/) | Public website | Not integrated |
| [National Bureau of Statistics releases](https://www.stats.gov.cn/sj/zxfb/) | Public website | Not integrated |
| [National Data / NBS database](https://data.stats.gov.cn/) | Public website | Not integrated |
| [MIIT](https://www.miit.gov.cn/) | Public website | Not integrated |
| [Ministry of Commerce](https://www.mofcom.gov.cn/) | Public website | Not integrated |
| [Ministry of Ecology and Environment](https://www.mee.gov.cn/) | Public website | Not integrated |
| [People's Bank of China](https://www.pbc.gov.cn/) | Public website | Not integrated |
| [CSRC](https://www.csrc.gov.cn/) | Public website | Not integrated |
| [SAMR standards disclosure](https://openstd.samr.gov.cn/) | Public website | Not integrated |
| [National law database](https://flk.npc.gov.cn/) | Public website | Not integrated |
| [China Government Procurement](https://www.ccgp.gov.cn/) | Public website | Not integrated |
| [National public resource trading platform](https://www.ggzy.gov.cn/) | Public website | Not integrated |
| [CNInfo public disclosures](https://www.cninfo.com.cn/new/index) | Public website | Not integrated |
| [SSE / SZSE / BSE disclosures](https://www.sse.com.cn/disclosure/listedinfo/announcement/) | Public website | Not integrated |
| [DATA.GOV.HK](https://data.gov.hk/en/help/api-spec) | Public endpoint | Not integrated |
| [Beijing / Shanghai / Shenzhen open-data portals](https://data.sh.gov.cn/) | Public website | Not integrated |
| [data.gov.tw](https://data.gov.tw/) | Public website | Not integrated |

</details>

<details>
<summary>International government and statistics（8）</summary>

| Source | Access | Project status |
|---|---|---|
| [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1) | Public endpoint | Not integrated |
| [SEC EDGAR public data](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | Public endpoint | Not integrated |
| [GOV.UK content/search](https://docs.publishing.service.gov.uk/apis.html) | Public endpoint | Not integrated |
| [UK legislation](https://www.legislation.gov.uk/developer) | Public endpoint | Not integrated |
| [Eurostat](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access) | Public endpoint | Not integrated |
| [World Bank Indicators](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation) | Public endpoint | Not integrated |
| [OECD SDMX](https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html) | Public endpoint | Not integrated |
| [api.data.gov / govinfo / Congress APIs](https://api.data.gov/) | Registration or conditions | Not integrated |

</details>

<details>
<summary>Research and scholarly literature（26）</summary>

| Source | Access | Project status |
|---|---|---|
| [arXiv](https://info.arxiv.org/help/api/index.html) | Public endpoint | Partially integrated |
| [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | Public endpoint | Partially integrated |
| [DataCite](https://support.datacite.org/docs/api) | Public endpoint | Not integrated |
| [dblp](https://dblp.org/faq/How+to+use+the+dblp+search+API.html) | Public endpoint | Not integrated |
| [Europe PMC](https://europepmc.org/RestfulWebService) | Public endpoint | Partially integrated |
| [NCBI PubMed / PMC E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | Public endpoint | Not integrated |
| [HAL](https://api.archives-ouvertes.fr/docs) | Public endpoint | Not integrated |
| [OpenAIRE](https://graph.openaire.eu/develop/api.html) | Registration or conditions | Not integrated |
| [Zenodo public records](https://developers.zenodo.org/) | Public endpoint | Not integrated |
| [Figshare public articles](https://docs.figshare.com/) | Public endpoint | Not integrated |
| [bioRxiv / medRxiv](https://api.biorxiv.org/) | Public endpoint | Not integrated |
| [ClinicalTrials.gov](https://clinicaltrials.gov/data-api/api) | Public endpoint | Not integrated |
| [OpenReview public notes](https://docs.openreview.net/) | Public endpoint | Not integrated |
| [Open Library](https://openlibrary.org/developers/api) | Public endpoint | Not integrated |
| [Internet Archive search](https://archive.org/developers/) | Public endpoint | Not integrated |
| [Library of Congress](https://www.loc.gov/apis/) | Public endpoint | Not integrated |
| [Wikisource](https://www.mediawiki.org/wiki/API:Main_page) | Public endpoint | Not integrated |
| [OpenAlex](https://help.openalex.org/access/pricing/) | Registration or conditions | Not integrated |
| [Semantic Scholar](https://www.semanticscholar.org/product/api) | Registration or conditions | Not integrated |
| [CORE](https://core.ac.uk/services/api) | Registration or conditions | Not integrated |
| [Unpaywall](https://unpaywall.org/products/api) | Registration or conditions | Not integrated |
| [Google Books API](https://developers.google.com/books/docs/v1/using) | Registration or conditions | Not integrated |
| [Europeana](https://pro.europeana.eu/page/apis) | Registration or conditions | Not integrated |
| [DOAJ](https://doaj.org/api/docs) | Public endpoint | Not integrated |
| [NASA ADS](https://ui.adsabs.harvard.edu/help/api/) | Registration or conditions | Not integrated |
| [BASE](https://www.base-search.net/about/en/about_develop.php) | Registration or conditions | Not integrated |

</details>

<details>
<summary>Code, packages and models（17）</summary>

| Source | Access | Project status |
|---|---|---|
| [GitHub REST public repositories](https://docs.github.com/en/rest/search/search) | Public endpoint | Partially integrated |
| [GitLab public projects](https://docs.gitlab.com/api/projects/) | Public endpoint | Partially integrated |
| [Codeberg / Forgejo](https://codeberg.org/api/swagger) | Public endpoint | Not integrated |
| [Gitee API](https://gitee.com/api/v5/swagger) | Registration or conditions | Not integrated |
| [npm registry](https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md) | Public endpoint | Partially integrated |
| [PyPI JSON / Simple](https://docs.pypi.org/api/) | Public endpoint | Not integrated |
| [crates.io](https://crates.io/data-access) | Public endpoint | Partially integrated |
| [Maven Central](https://central.sonatype.org/search/rest-api-guide/) | Public endpoint | Not integrated |
| [NuGet](https://learn.microsoft.com/en-us/nuget/api/search-query-service-resource) | Public endpoint | Not integrated |
| [Packagist](https://packagist.org/apidoc) | Public endpoint | Not integrated |
| [RubyGems](https://guides.rubygems.org/rubygems-org-api/) | Public endpoint | Not integrated |
| [Go module proxy](https://go.dev/ref/mod#module-proxy) | Public endpoint | Not integrated |
| [Hugging Face Hub](https://huggingface.co/docs/hub/api) | Public endpoint | Partially integrated |
| [Docker Hub](https://docs.docker.com/reference/api/hub/latest/) | Registration or conditions | Not integrated |
| [searchcode MCP](https://searchcode.com/) | Public endpoint | Not integrated |
| [grep.app MCP](https://vercel.com/blog/grep-a-million-github-repositories-via-mcp) | Public endpoint | Not integrated |
| [Libraries.io](https://libraries.io/api) | Registration or conditions | Not integrated |

</details>

<details>
<summary>Communities and social media（10）</summary>

| Source | Access | Project status |
|---|---|---|
| [Hacker News / Algolia](https://hn.algolia.com/api) | Public endpoint | Partially integrated |
| [Stack Exchange family](https://api.stackexchange.com/docs) | Public endpoint | Partially integrated |
| [Discourse public communities](https://docs.discourse.org/) | Public endpoint | Partially integrated |
| [V2EX public API](https://www.v2ex.com/p/7v9TEc53) | Public endpoint | Partially integrated |
| [DEV.to / Forem](https://developers.forem.com/api) | Public endpoint | Not integrated |
| [Lobsters](https://lobste.rs/) | Public endpoint | Not integrated |
| [Lemmy public instances](https://join-lemmy.org/api/) | Public endpoint | Not integrated |
| [Mastodon](https://docs.joinmastodon.org/methods/search/) | Registration or conditions | Not integrated |
| [Bluesky public AppView](https://docs.bsky.app/docs/advanced-guides/api-directory) | Public endpoint | Not integrated |
| [Cnblogs RSS](https://www.cnblogs.com/) | Public website | Not integrated |

</details>

<details>
<summary>Encyclopedias and resources（8）</summary>

| Source | Access | Project status |
|---|---|---|
| [Wikipedia](https://www.mediawiki.org/wiki/API:Search) | Public endpoint | Partially integrated |
| [Wikidata](https://www.wikidata.org/wiki/Wikidata:Data_access) | Public endpoint | Not integrated |
| [Wikimedia Commons](https://commons.wikimedia.org/wiki/Commons:API) | Public endpoint | Not integrated |
| [Openverse](https://docs.openverse.org/api/) | Public endpoint | Not integrated |
| [GBIF](https://www.gbif.org/developer/summary) | Public endpoint | Not integrated |
| [iNaturalist](https://api.inaturalist.org/v1/docs/) | Public endpoint | Not integrated |
| [ROR](https://ror.readme.io/docs/rest-api) | Public endpoint | Not integrated |
| [ORCID public API](https://info.orcid.org/documentation/integration-guide/orcid-api-2/) | Registration or conditions | Not integrated |

</details>

<details>
<summary>Web archives（3）</summary>

| Source | Access | Project status |
|---|---|---|
| [Common Crawl URL Index](https://index.commoncrawl.org/) | Public endpoint | Not integrated |
| [Wayback / CDX](https://archive.org/developers/wayback-cdx-server.html) | Public endpoint | Not integrated |
| [Arquivo.pt](https://arquivo.pt/api) | Public endpoint | Not integrated |

</details>

<details>
<summary>Weather, geography and energy（10）</summary>

| Source | Access | Project status |
|---|---|---|
| [USGS earthquake feeds/API](https://earthquake.usgs.gov/fdsnws/event/1/) | Public endpoint | Not integrated |
| [NOAA NCEI data service](https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation) | Public endpoint | Not integrated |
| [weather.gov API](https://www.weather.gov/documentation/services-web-api) | Public endpoint | Not integrated |
| [EIA Open Data](https://www.eia.gov/opendata/) | Registration or conditions | Not integrated |
| [ENTSO-E Transparency](https://transparency.entsoe.eu/) | Registration or conditions | Not integrated |
| [NASA public APIs](https://api.nasa.gov/) | Registration or conditions | Not integrated |
| [Open-Meteo](https://open-meteo.com/en/pricing) | Registration or conditions | Not integrated |
| [OpenStreetMap Nominatim](https://operations.osmfoundation.org/policies/nominatim/) | Public endpoint | Not integrated |
| [Overpass public API](https://wiki.openstreetmap.org/wiki/Overpass_API) | Public endpoint | Not integrated |
| [GeoNames](https://www.geonames.org/export/web-services.html) | Registration or conditions | Not integrated |

</details>

<details>
<summary>Restricted platforms（9）</summary>

| Source | Access | Project status |
|---|---|---|
| [X API](https://docs.x.com/x-api/getting-started/pricing) | Restricted | Not integrated |
| [Reddit Data API](https://redditinc.com/policies/data-api-terms) | Restricted | Not integrated |
| [Xiaohongshu](https://openaccount.xiaohongshu.com/docs/api-reference) | Restricted | Not integrated |
| [Weibo](https://open.weibo.com/wiki/API) | Restricted | Not integrated |
| [Zhihu](https://www.zhihu.com/) | Public website | Partially integrated |
| [Bilibili](https://www.bilibili.com/) | Public website | Partially integrated |
| [WeChat / Sogou WeChat](https://mp.weixin.qq.com/) | Restricted | Not integrated |
| [Douyin / Kuaishou](https://developer.open-douyin.com/) | Restricted | Not integrated |
| [Douban / Tieba / Juejin / CSDN / OSChina](https://www.douban.com/) | Public website | Not integrated |

</details>

<details>
<summary>Self-hosted tools（3）</summary>

| Source | Access | Project status |
|---|---|---|
| [SearXNG](https://docs.searxng.org/) | Self-hosted | Out of scope |
| [RSSHub / RSS-Bridge](https://docs.rsshub.app/) | Self-hosted | Out of scope |
| [Miniflux / FreshRSS](https://miniflux.app/) | Self-hosted | Out of scope |

</details>

<details>
<summary>Patents（4）</summary>

| Source | Access | Project status |
|---|---|---|
| [USPTO Open Data Portal](https://data.uspto.gov/apis/api-catalog) | Registration or conditions | Not integrated |
| [EPO Open Patent Services](https://www.epo.org/en/searching-for-patents/data/web-services/ops) | Registration or conditions | Not integrated |
| [Google Patents](https://patents.google.com/) | Public website | Not integrated |
| [CNIPA public services](https://www.cnipa.gov.cn/) | Public website | Not integrated |

</details>

<details>
<summary>Finance and economics（8）</summary>

| Source | Access | Project status |
|---|---|---|
| [FRED](https://fred.stlouisfed.org/docs/api/fred/) | Registration or conditions | Not integrated |
| [US BLS public data](https://www.bls.gov/developers/) | Public endpoint | Not integrated |
| [US Census data APIs](https://www.census.gov/data/developers/data-sets.html) | Registration or conditions | Not integrated |
| [Tushare](https://tushare.pro/document/1) | Registration or conditions | Not integrated |
| [BaoStock](https://www.baostock.com/) | Public endpoint | Not integrated |
| [CoinGecko Demo API](https://docs.coingecko.com/reference/setting-up-your-api-key) | Registration or conditions | Not integrated |
| [Yahoo Finance public pages](https://finance.yahoo.com/) | Public website | Not integrated |
| [Stooq historical data](https://stooq.com/db/h/) | Public website | Not integrated |

</details>

<details>
<summary>Podcasts and audio（3）</summary>

| Source | Access | Project status |
|---|---|---|
| [Apple iTunes Search API](https://performance-partners.apple.com/search-api) | Public endpoint | Not integrated |
| [Podcast Index](https://podcastindex-org.github.io/docs-api/) | Registration or conditions | Not integrated |
| [Listen Notes](https://www.listennotes.com/api/pricing/) | Registration or conditions | Not integrated |

</details>

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
