# Sources and integrations

[简体中文](sources.md) | **English**

[Back to README](../README.en.md)

This page lists the sources and features already integrated into xcoze search. Public endpoints may be rate-limited or unavailable in some networks; configuration of an API key does not by itself verify account access.

## Integrated sources

### Keyless search and reading

| Source | What you can do |
|---|---|
| Bing RSS | Search public web pages |
| DuckDuckGo HTML | Search public web pages |
| Exa hosted MCP | Search and read web pages |
| Jina Reader | Read web pages |
| GitHub | Search public repositories and read their READMEs |
| GitLab.com | Search public projects |
| Hacker News | Search stories and read individual stories or comments |
| Wikipedia | Search English and Chinese articles |
| Stack Exchange | Search questions across Stack Overflow and six other communities |
| arXiv | Search preprints, abstracts, and paper metadata |
| Crossref | Search DOIs, authors, and publication metadata |
| Europe PMC | Search biomedical literature and abstracts |
| DataCite | Search research DOIs and metadata |
| Zenodo | Search public research records and abstracts |
| Open Library | Search book and author metadata |
| Wikidata | Search English and Chinese entity labels and descriptions |
| npm | Search JavaScript packages and version metadata |
| crates.io | Search Rust packages and version metadata |
| Hugging Face | Search public model metadata |
| gov.cn | Search China's latest-policy listing |
| Python and Rust community forums, V2EX | Read public topic posts |

Access to Bing RSS, DuckDuckGo HTML, and some community endpoints can change with the website or network. GitHub support covers repositories, not code search or private repositories. Research and book results are metadata or abstracts and do not imply full text was read; community search results do not imply the full discussion was read. The gov.cn listing does not cover all announcements in China.

### News and community trends

| Source | What you can do |
|---|---|
| China News Service | Read latest-news and finance feeds |
| BBC | Read the World news feed |
| Zhihu | View trending questions and excerpts |
| Bilibili | View trending search terms |
| V2EX | View trending topics |

News feeds cover each publisher's current feed window. Trend lists contain what each platform provides; they do not include complete answers, videos, or comments.

### Platform-scoped search

Public web searches can be scoped to **Zhihu, Xiaohongshu, Weibo, YouTube, Bilibili, Reddit, X, V2EX, and Douban**. Results depend on what the web index has indexed; this differs from searching within a platform or reading signed-in content and complete comment threads.

### Bring your own API key

| Service | Supported features |
|---|---|
| DeepSeek | Search, Fetch |
| Tencent Yuanbao | SearchPro search and summaries |
| Tavily | Search, Extract |
| Exa | Search, Contents |
| Brave Search | Web Search |
| Bocha | Web Search |

Each service must be enabled separately, and its provider sets the applicable limits and charges. Exa's keyless MCP and keyed API are separate endpoints. See the [provider reference](providers.en.md) for options and limits.

### Browser fallback

When other available search paths cannot return results, the Skill can use an existing local [agent-browser](https://github.com/vercel-labs/agent-browser) and browser to search. It defaults to 360 Search; Bing and Google can also be selected. This is optional: the base installation does not install a browser or use your browser login state. You can also ask your Agent to turn browser fallback off.

[View the source availability check](../evaluations/reports/2026-11-05-source-audit.en.md).

See [public sources and platforms](open-sources.en.md), [news and community content](feeds.en.md), and [search routing](routing.en.md) for details. The [full source research directory](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md) also includes sources that are not yet integrated.

