# Source support status

[简体中文](source-status.md) | **English**

[Back to sources](sources.en.md)

Each row describes a specific action. **Supported · Passed** means the live sample returned content in this environment; it is not an uptime or accuracy guarantee. Limited, no hits and key needed retain supported status but were not verified successfully. Searches and page reading are checked separately.

Checked: 2026-11-05 19:22 (Beijing time). Account-specific details and credentials are not published. [Sanitized test results](../evaluations/reports/2026-11-05-source-status.json).

## Search sources

| Source or action | Status |
|---|---|
| Bing public RSS | Supported · Limited (irrelevant results) |
| DuckDuckGo public HTML | Supported · Limited (access challenge, HTTP 202) |
| Exa hosted MCP (keyless) | Supported · Passed |
| GitHub public repositories | Supported · Passed |
| Hacker News / Algolia | Supported · Passed |
| Wikipedia (English / Chinese) | Supported · Passed |
| Stack Exchange questions | Supported · Passed |
| arXiv preprints | Supported · Passed |
| Crossref DOI metadata | Supported · Passed |
| npm public package registry | Supported · Passed |
| crates.io Rust packages | Supported · Passed |
| GitLab.com public projects | Supported · Passed |
| Europe PMC literature | Supported · Passed |
| Hugging Face public models | Supported · Passed |
| Open Library books | Supported · Passed |
| DataCite research records | Supported · Passed |
| Zenodo research records | Supported · Passed |
| Wikidata entities | Supported · Passed |
| NASA Image and Video Library | Supported · Passed |
| U.S. Federal Register | Supported · Passed |
| World Bank indicators | Supported · Passed |
| USGS recent earthquake feed | Supported · Passed |
| China government latest policy | Supported · Passed |
| NDRC notices | Supported · Passed |
| National Bureau of Statistics releases | Supported · Passed |
| National Energy Administration news | Supported · Passed |
| Ministry of Industry and Information Technology notices | Supported · Passed |
| Ministry of Ecology and Environment news | Supported · Passed |
| Ministry of Emergency Management statistics | Supported · Passed |
| People’s Bank of China statistics | Supported · Passed |
| National Public Resource Trading Platform notices | Supported · Passed |
| Ministry of Commerce news | Supported · Passed |
| China Securities Regulatory Commission information | Supported · Passed |
| China Government Procurement notices | Supported · Passed |
| Chinese Academy of Sciences research news | Supported · Passed |
| China Geological Survey news | Supported · Passed |
| Xinhua news | Supported · Passed |

## Page and community reading

| Source or action | Status |
|---|---|
| Exa MCP page reading | Supported · Passed |
| GitHub README | Supported · Limited (access denied, HTTP 403) |
| Hacker News item | Supported · Passed |
| Jina Reader | Supported · Limited (access denied, HTTP 401) |
| Python community post | Supported · Passed |
| Rust community post | Supported · Passed |
| V2EX community post | Supported · Limited (content unavailable) |

## Feeds and snapshots

| Source or action | Status |
|---|---|
| China News Service latest RSS | Supported · Passed |
| China News Service finance RSS | Supported · Passed |
| DATA.GOV.HK updates RSS | Supported · Passed |
| BBC World RSS | Supported · Passed |
| China government latest policy | Supported · Passed |

## Community trends

| Source or action | Status |
|---|---|
| Bilibili public hotwords | Supported · Passed |
| Zhihu public hot list | Supported · Passed |
| V2EX public hot topics | Supported · Passed |

## Site-scoped web search

| Source or action | Status |
|---|---|
| zhihu (`zhihu.com`) | Supported · Passed |
| xiaohongshu (`xiaohongshu.com`) | Supported · Passed |
| weibo (`weibo.com`) | Supported · Passed |
| youtube (`youtube.com`) | Supported · Passed |
| bilibili (`bilibili.com`) | Supported · Passed |
| reddit (`reddit.com`) | Supported · Passed |
| twitter (`x.com`) | Supported · No hits |
| v2ex (`v2ex.com`) | Supported · Passed |
| douban (`douban.com`) | Supported · Passed |
| china-data (`data.stats.gov.cn`) | Supported · Passed |
| cma-data (`data.cma.cn`) | Supported · Passed |
| china-weather (`weather.com.cn`) | Supported · Passed |
| cninfo (`cninfo.com.cn`) | Supported · Passed |
| sse (`sse.com.cn`) | Supported · Passed |
| szse (`szse.cn`) | Supported · Passed |
| bse (`bse.cn`) | Supported · Passed |
| china-standards (`openstd.samr.gov.cn`) | Supported · Passed |
| china-laws (`flk.npc.gov.cn`) | Supported · Passed |
| cnsa (`cnsa.gov.cn`) | Supported · Passed |
| scidb (`scidb.cn`) | Supported · Passed |
| ceic (`ceic.ac.cn`) | Supported · Passed |
| nmefc (`nmefc.cn`) | Supported · Passed |
| hko (`hko.gov.hk`) | Supported · Passed |

## Browser search

| Source or action | Status |
|---|---|
| 360 | Supported · Passed |
| bing | Supported · Limited (no usable results) |
| google | Supported · Limited (access challenge) |

## Services using your API key

| Source or action | Status |
|---|---|
| DeepSeek | Supported · Limited |
| Tencent Yuanbao | Supported · Key needed |
| Tavily | Supported · Key needed |
| Exa | Supported · Key needed |
| Brave Search | Supported · Key needed |
| Bocha | Supported · Key needed |

## Page reading with an API key

| Source or action | Status |
|---|---|
| DeepSeek · Fetch/Extract | Supported · Not tested |
| Tavily · Fetch/Extract | Supported · Key needed |
| Exa · Fetch/Extract | Supported · Key needed |

## Candidates

The following are research candidates, not a promise of support or availability. Items partially covered by existing adapters are omitted here; their current capabilities are listed above. [Full research](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md).

<details>
<summary>Web search (6)</summary>

| Candidate | Status |
|---|---|
| [Parallel Search MCP](https://parallel.ai/mcp) | Planned |
| [DuckDuckGo Instant Answer](https://duckduckgo.com/api) | Planned |
| [Firecrawl](https://www.firecrawl.dev/pricing) | Planned |
| [Serper](https://serper.dev/) | Planned |
| [SerpApi](https://serpapi.com/pricing) | Planned |
| [Search1API](https://s1.dev/docs/essentials/credits-and-limits) | Planned |

</details>

<details>
<summary>Technical docs (8)</summary>

| Candidate | Status |
|---|---|
| [Microsoft Learn MCP](https://learn.microsoft.com/en-us/training/support/mcp) | Planned |
| [MDN MCP](https://developer.mozilla.org/en-US/mcp) | Planned |
| [Cloudflare Docs MCP](https://developers.cloudflare.com/workers/get-started/prompting/) | Planned |
| [OpenAI Docs MCP](https://developers.openai.com/resources/docs-mcp) | Planned |
| [Context7](https://github.com/upstash/context7) | Planned |
| [Python official docs / Sphinx inventories](https://docs.python.org/3/) | Planned |
| [Rust std / docs.rs](https://docs.rs/) | Planned |
| [Read the Docs / llms.txt publisher docs](https://docs.readthedocs.com/platform/stable/reference/sitemaps.html) | Planned |

</details>

<details>
<summary>News (12)</summary>

| Candidate | Status |
|---|---|
| [CCTV / CGTN RSS](https://english.cctv.cn/rss/) | Planned |
| [Xinhua RSS](https://www.xinhuanet.com/english/rss/index.htm) | Planned |
| [DW RSS](https://rss.dw.com/rdf/rss-en-all) | Planned |
| [UN News RSS](https://news.un.org/en/rss-feeds) | Planned |
| [NASA news feeds](https://www.nasa.gov/rss-feeds/) | Planned |
| [GDELT DOC / Context](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) | Planned |
| [Google News RSS](https://news.google.com/) | Planned |
| [Guardian Open Platform](https://open-platform.theguardian.com/access/) | Planned |
| [NewsAPI.org](https://newsapi.org/pricing) | Planned |
| [GNews](https://gnews.io/pricing) | Planned |
| [NewsData.io](https://newsdata.io/pricing) | Planned |
| [TheNewsAPI](https://www.thenewsapi.com/pricing) | Planned |

</details>

<details>
<summary>China government (2)</summary>

| Candidate | Status |
|---|---|
| [Beijing / Shanghai / Shenzhen open-data portals](https://data.sh.gov.cn/) | Planned |
| [data.gov.tw](https://data.gov.tw/) | Planned |

</details>

<details>
<summary>International government (6)</summary>

| Candidate | Status |
|---|---|
| [SEC EDGAR public data](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | Planned |
| [GOV.UK content/search](https://docs.publishing.service.gov.uk/apis.html) | Planned |
| [UK legislation](https://www.legislation.gov.uk/developer) | Planned |
| [Eurostat](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access) | Planned |
| [OECD SDMX](https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html) | Planned |
| [api.data.gov / govinfo / Congress APIs](https://api.data.gov/) | Planned |

</details>

<details>
<summary>Research (20)</summary>

| Candidate | Status |
|---|---|
| [dblp](https://dblp.org/faq/How+to+use+the+dblp+search+API.html) | Planned |
| [NCBI PubMed / PMC E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | Planned |
| [HAL](https://api.archives-ouvertes.fr/docs) | Planned |
| [OpenAIRE](https://graph.openaire.eu/develop/api.html) | Planned |
| [Figshare public articles](https://docs.figshare.com/) | Planned |
| [bioRxiv / medRxiv](https://api.biorxiv.org/) | Planned |
| [ClinicalTrials.gov](https://clinicaltrials.gov/data-api/api) | Planned |
| [OpenReview public notes](https://docs.openreview.net/) | Planned |
| [Internet Archive search](https://archive.org/developers/) | Planned |
| [Library of Congress](https://www.loc.gov/apis/) | Planned |
| [Wikisource](https://www.mediawiki.org/wiki/API:Main_page) | Planned |
| [OpenAlex](https://help.openalex.org/access/pricing/) | Planned |
| [Semantic Scholar](https://www.semanticscholar.org/product/api) | Planned |
| [CORE](https://core.ac.uk/services/api) | Planned |
| [Unpaywall](https://unpaywall.org/products/api) | Planned |
| [Google Books API](https://developers.google.com/books/docs/v1/using) | Planned |
| [Europeana](https://pro.europeana.eu/page/apis) | Planned |
| [DOAJ](https://doaj.org/api/docs) | Planned |
| [NASA ADS](https://ui.adsabs.harvard.edu/help/api/) | Planned |
| [BASE](https://www.base-search.net/about/en/about_develop.php) | Planned |

</details>

<details>
<summary>Software and code (12)</summary>

| Candidate | Status |
|---|---|
| [Codeberg / Forgejo](https://codeberg.org/api/swagger) | Planned |
| [Gitee API](https://gitee.com/api/v5/swagger) | Planned |
| [PyPI JSON / Simple](https://docs.pypi.org/api/) | Planned |
| [Maven Central](https://central.sonatype.org/search/rest-api-guide/) | Planned |
| [NuGet](https://learn.microsoft.com/en-us/nuget/api/search-query-service-resource) | Planned |
| [Packagist](https://packagist.org/apidoc) | Planned |
| [RubyGems](https://guides.rubygems.org/rubygems-org-api/) | Planned |
| [Go module proxy](https://go.dev/ref/mod#module-proxy) | Planned |
| [Docker Hub](https://docs.docker.com/reference/api/hub/latest/) | Planned |
| [searchcode MCP](https://searchcode.com/) | Planned |
| [grep.app MCP](https://vercel.com/blog/grep-a-million-github-repositories-via-mcp) | Planned |
| [Libraries.io](https://libraries.io/api) | Planned |

</details>

<details>
<summary>Communities (6)</summary>

| Candidate | Status |
|---|---|
| [DEV.to / Forem](https://developers.forem.com/api) | Planned |
| [Lobsters](https://lobste.rs/) | Planned |
| [Lemmy public instances](https://join-lemmy.org/api/) | Planned |
| [Mastodon](https://docs.joinmastodon.org/methods/search/) | Planned |
| [Bluesky public AppView](https://docs.bsky.app/docs/advanced-guides/api-directory) | Planned |
| [Cnblogs RSS](https://www.cnblogs.com/) | Planned |

</details>

<details>
<summary>Knowledge and media (6)</summary>

| Candidate | Status |
|---|---|
| [Wikimedia Commons](https://commons.wikimedia.org/wiki/Commons:API) | Planned |
| [Openverse](https://docs.openverse.org/api/) | Planned |
| [GBIF](https://www.gbif.org/developer/summary) | Planned |
| [iNaturalist](https://api.inaturalist.org/v1/docs/) | Planned |
| [ROR](https://ror.readme.io/docs/rest-api) | Planned |
| [ORCID public API](https://info.orcid.org/documentation/integration-guide/orcid-api-2/) | Planned |

</details>

<details>
<summary>Archives (3)</summary>

| Candidate | Status |
|---|---|
| [Common Crawl URL Index](https://index.commoncrawl.org/) | Planned |
| [Wayback / CDX](https://archive.org/developers/wayback-cdx-server.html) | Planned |
| [Arquivo.pt](https://arquivo.pt/api) | Planned |

</details>

<details>
<summary>Environment and energy (8)</summary>

| Candidate | Status |
|---|---|
| [NOAA NCEI data service](https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation) | Planned |
| [weather.gov API](https://www.weather.gov/documentation/services-web-api) | Planned |
| [EIA Open Data](https://www.eia.gov/opendata/) | Planned |
| [ENTSO-E Transparency](https://transparency.entsoe.eu/) | Planned |
| [Open-Meteo](https://open-meteo.com/en/pricing) | Planned |
| [OpenStreetMap Nominatim](https://operations.osmfoundation.org/policies/nominatim/) | Planned |
| [Overpass public API](https://wiki.openstreetmap.org/wiki/Overpass_API) | Planned |
| [GeoNames](https://www.geonames.org/export/web-services.html) | Planned |

</details>

<details>
<summary>Platform APIs (4)</summary>

| Candidate | Status |
|---|---|
| [X API](https://docs.x.com/x-api/getting-started/pricing) | Planned |
| [Reddit Data API](https://redditinc.com/policies/data-api-terms) | Planned |
| [WeChat / Sogou WeChat](https://mp.weixin.qq.com/) | Planned |
| [Douyin / Kuaishou](https://developer.open-douyin.com/) | Planned |

</details>

<details>
<summary>Patents (4)</summary>

| Candidate | Status |
|---|---|
| [USPTO Open Data Portal](https://data.uspto.gov/apis/api-catalog) | Planned |
| [EPO Open Patent Services](https://www.epo.org/en/searching-for-patents/data/web-services/ops) | Planned |
| [Google Patents](https://patents.google.com/) | Planned |
| [CNIPA public services](https://www.cnipa.gov.cn/) | Planned |

</details>

<details>
<summary>Finance (8)</summary>

| Candidate | Status |
|---|---|
| [FRED](https://fred.stlouisfed.org/docs/api/fred/) | Planned |
| [US BLS public data](https://www.bls.gov/developers/) | Planned |
| [US Census data APIs](https://www.census.gov/data/developers/data-sets.html) | Planned |
| [Tushare](https://tushare.pro/document/1) | Planned |
| [BaoStock](https://www.baostock.com/) | Planned |
| [CoinGecko Demo API](https://docs.coingecko.com/reference/setting-up-your-api-key) | Planned |
| [Yahoo Finance public pages](https://finance.yahoo.com/) | Planned |
| [Stooq historical data](https://stooq.com/db/h/) | Planned |

</details>

<details>
<summary>Audio (3)</summary>

| Candidate | Status |
|---|---|
| [Apple iTunes Search API](https://performance-partners.apple.com/search-api) | Planned |
| [Podcast Index](https://podcastindex-org.github.io/docs-api/) | Planned |
| [Listen Notes](https://www.listennotes.com/api/pricing/) | Planned |

</details>
