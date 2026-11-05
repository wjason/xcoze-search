# Sources and integrations

[简体中文](sources.md) | **English**

[Back to README](../README.en.md)

This page lists the sources and features already integrated into xcoze search. Public endpoints may be rate-limited or unavailable in some networks; configuration of an API key does not by itself verify account access.

## Integrated sources

[Full status and candidates](source-status.en.md) · Checked on 2026-11-05 (Beijing time).

### Keyless search and reading

| Source | What you can do | Status |
|---|---|---|
| Bing RSS | Search public web pages | Supported · Limited |
| DuckDuckGo HTML | Search public web pages | Supported · Limited |
| Exa hosted MCP | Search and read web pages | Supported · Passed |
| Jina Reader | Read web pages | Supported · Limited |
| GitHub | Search public repositories and read their READMEs | Search passed; README limited |
| GitLab.com | Search public projects | Supported · Passed |
| Hacker News | Search stories and read individual stories or comments | Supported · Passed |
| Wikipedia | Search English and Chinese articles | Supported · Passed |
| Stack Exchange | Search questions across Stack Overflow and six other communities | Supported · Passed |
| arXiv | Search preprints, abstracts, and paper metadata | Supported · Passed |
| Crossref | Search DOIs, authors, and publication metadata | Supported · Passed |
| Europe PMC | Search biomedical literature and abstracts | Supported · Passed |
| DataCite | Search research DOIs and metadata | Supported · Passed |
| Zenodo | Search public research records and abstracts | Supported · Passed |
| Open Library | Search book and author metadata | Supported · Passed |
| Wikidata | Search English and Chinese entity labels and descriptions | Supported · Passed |
| npm | Search JavaScript packages and version metadata | Supported · Passed |
| crates.io | Search Rust packages and version metadata | Supported · Passed |
| Hugging Face | Search public model metadata | Supported · Passed |
| gov.cn | Search China's latest-policy listing | Supported · Passed |
| NDRC | Filter titles on the current notices page | Supported · Passed |
| National Bureau of Statistics | Filter titles on the current data releases page | Supported · Passed |
| National Energy Administration | Filter recent homepage titles | Supported · Passed |
| Ministry of Industry and Information Technology | Recent public policy document titles | Supported · Passed |
| Ministry of Ecology and Environment | Recent homepage news releases | Supported · Passed |
| Ministry of Emergency Management | Recent disaster statistics releases | Supported · Passed |
| People’s Bank of China | Recent financial statistics releases | Supported · Passed |
| National Public Resource Trading Platform | Recent homepage trading notices | Supported · Passed |
| Ministry of Commerce | Recent homepage news | Supported · Passed |
| China Securities Regulatory Commission | Public information on its homepage | Supported · Passed |
| China Government Procurement | Recent homepage procurement notices | Supported · Passed |
| Chinese Academy of Sciences | Recent homepage research news | Supported · Passed |
| China Geological Survey | Recent homepage news | Supported · Passed |
| Xinhua | Recent homepage news | Supported · Passed |
| DATA.GOV.HK | RSS feed of recent dataset updates | Supported · Passed |
| U.S. Federal Register | Search federal notices, rules and abstracts | Supported · Passed |
| NASA Image and Video Library | Search image, video and audio metadata | Supported · Passed |
| World Bank | Look up economic and social indicators by country and code | Supported · Passed |
| USGS | Retrieve recent earthquake magnitude, location and event time | Supported · Passed |
| Python and Rust community forums, V2EX | Read public topic posts | Python/Rust passed; V2EX limited |

Access to Bing RSS, DuckDuckGo HTML, and some community endpoints can change with the website or network. GitHub support covers repositories, not code search or private repositories. Research and book results are metadata or abstracts and do not imply full text was read; community search results do not imply the full discussion was read. The gov.cn listing does not cover all announcements in China. NDRC, NBS and NEA adapters filter titles on the current page, not full sites or historical databases; missing display dates remain unknown. A Federal Register publication date is not an effective date. NASA returns media metadata, not the media itself. World Bank observations are identified by year and are not live market prices. USGS earthquake data may be revised.

### News and community trends

| Source | What you can do | Status |
|---|---|---|
| China News Service | Read latest-news and finance feeds | Supported · Passed |
| BBC | Read the World news feed | Supported · Passed |
| Zhihu | View trending questions and excerpts | Supported · Passed |
| Bilibili | View trending search terms | Supported · Passed |
| V2EX | View trending topics | Supported · Passed |

News feeds cover each publisher's current feed window. Trend lists contain what each platform provides; they do not include complete answers, videos, or comments.

### Platform-scoped search

Public web searches can be scoped to **Zhihu, Xiaohongshu, Weibo, YouTube, Bilibili, Reddit, X, V2EX, and Douban**. Results depend on the coverage and freshness of the web index.

China public sources can also be scoped: National Data, National Meteorological Information Center, China Weather, CNInfo, SSE, SZSE, BSE, National Standards, National Laws, CNSA, Science Data Bank, CENC, NMEFC, and Hong Kong Observatory. The Hong Kong Observatory scoped search returned links in this check.

### Bring your own API key

| Service | Supported features | Status |
|---|---|---|
| DeepSeek | Search, Fetch | Search limited; Fetch not tested |
| Tencent Yuanbao | SearchPro search and summaries | Supported · Key needed |
| Tavily | Search, Extract | Supported · Key needed |
| Exa | Search, Contents | Supported · Key needed |
| Brave Search | Web Search | Supported · Key needed |
| Bocha | Web Search | Supported · Key needed |

Each service must be enabled separately, and its provider sets the applicable limits and charges. Exa's keyless MCP and keyed API are separate endpoints. See the [provider reference](providers.en.md) for options and limits.

### Browser fallback

When other available search paths cannot return results, the Skill can use an existing local [agent-browser](https://github.com/vercel-labs/agent-browser) and browser to search. It defaults to 360 Search; Bing and Google can also be selected. This is optional: the base installation does not install a browser or use your browser login state. You can also ask your Agent to turn browser fallback off.

[View the source availability check](../evaluations/reports/2026-11-05-source-audit.en.md).

The [China public sources directory](../research/china-public-sources.en.md) covers additional government, financial, research and public-service portals.

See [public data source research](../research/global-public-data.en.md) for weather, stock data and other organizations.

See [public sources and platforms](open-sources.en.md), [news and community content](feeds.en.md), and [search routing](routing.en.md) for details. The [full source research directory](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md) also includes sources that are not yet integrated.

