# Free and public source map (2026-11)

[简体中文](free-sources-2026-11.md) | **English**

Checked 2026-11-05, Asia/Shanghai; project baseline v0.9.0. **165 entries** cover source families, services, data interfaces, public-page candidates and exclusions. This does not mean 165 independent search engines, working free APIs or integrated providers. Native retrieval, quality, permitted use and cross-network acceptance remain per-source work. This survey installs no MCP connections, creates no accounts and changes no routing.

[CSV](free-sources-2026-11.csv) · [Structured catalog](free-sources-2026-11.data.json) · [Live probes](free-sources-2026-11.probes.json)

## Access classes

| Code | Meaning | Entries |
|---|---|---:|
| A | Keyless public API/RSS/MCP/read-subset candidates; quota/access/content-rights limits still apply | 79 |
| W | Public web, experimental frontend or legacy feed; automation/freshness not fully accepted | 35 |
| Q | Signup/key/identity, free credits or use-specific conditions; not uniformly keyless | 40 |
| T | One-off trial credits, not assumed recurring | 2 |
| R | Paid, approved or restricted use; not unconditional free access | 6 |
| S | Software/self-hosting tool, not a free hosted source; self-hosting remains out of scope | 3 |

Existing/partial means an adapter exists in v0.9.0, not every platform action. candidate_reference is only a primary/project reference, potentially without detailed documentation or API acceptance in this pass. Live observations are explicit. Free API access does not grant unrestricted republication of source content.

One anonymous reference-page check per entry: 136 returned 2xx, 8 redirected, 17 returned HTTP errors and 4 had network failures. These checks do not verify keyword search, authentication, quotas, licenses or integration. See the [per-entry audit](source-reference-audit-2026-11-05.json) and CSV.

## Priority gaps

1. **Parallel anonymous MCP:** general search/fetch. Its older documentation is marked legacy, although this anonymous query succeeded. Verify migration/limits before integration; keyed REST is separate.
2. **Microsoft Learn and MDN:** native official documentation. Cloudflare Docs also returned relevant evidence but took about 7.9 seconds including handshake; use by task, not as universal low-latency fallback.
3. **searchcode:** named-repository code retrieval with a keyless free beta. Not a global code index. grep.app protocol worked but this query had no results, so retain acceptance work.
4. **NDRC, NEA and NBS:** Chinese policy/statistical originals. Public pages still need adapters, date/explainer distinctions and schema checks.
5. **DEV.to, DataCite, Open Library and Zenodo:** valid anonymous data returned. HAL and Figshare also succeeded. Route by task rather than broadcasting every query.
6. **GDELT, Semantic Scholar, Bluesky and dblp:** valuable candidates, but this pass observed 429, 429, 403 and non-JSON respectively. Do not promise current out-of-box availability.

## Free-tier changes

- [Tavily](https://www.tavily.com/pricing): 1000 credits/month, key required, no card. Credits are not a fixed number of searches.
- [Exa API](https://exa.ai/pricing): monthly $10 credits plus $10 onboarding bonus; key required, separate from anonymous MCP.
- [Firecrawl](https://www.firecrawl.dev/pricing): 1000 credits/month, listed as about 500 searches or 1000 scraped pages; older one-off 500-credit descriptions are stale.
- [Brave](https://api-dashboard.search.brave.com/documentation/resources/help-feedback): no standalone free plan; monthly $5 credits with key/card requirements, even for zero prepayment.
- [SerpApi](https://serpapi.com/pricing): 250 free searches/month. [Serper](https://serper.dev/) advertises 2500 trial queries, not monthly; [Search1API](https://s1.dev/docs/essentials/credits-and-limits) gives 100 signup credits.
- [OpenAlex](https://help.openalex.org/access/pricing/): API key now required; $1/day free without a payment method. Old keyless descriptions are stale.
- [NewsAPI](https://newsapi.org/pricing) free development articles have a 24h delay; [GNews](https://gnews.io/pricing)/[NewsData.io](https://newsdata.io/pricing) free tiers include 12h delays and use/content restrictions, unsuitable as real-time defaults.

Existing free mode still excludes keyed adapters, including promotional-credit accounts. No free-credit strategy, automatic top-ups or signup were added. A future allowance-only strategy would need explicit configuration, balance/hard limits and stop-at-exhaustion behavior.

An additional 15 anonymous API samples produced 14 nonempty expected structures; US BLS returned 403. Each is a single sample, not an integration or full acceptance. [Per-source results](source-functional-samples-2026-11-05.json).

## Live checks

Six MCPs completed anonymous initialization/tool listing, then one real query each. Times below include three client HTTP operations for a fresh protocol connection and are not a speed ranking against existing one-request APIs.

| Source | Query outcome | Total including handshake | Boundary |
|---|---|---:|---|
| Parallel | Official Python TaskGroup docs | 1.614 s | Mixed versions still need checking |
| Microsoft Learn | Official Azure Functions docs | 1.580 s | Microsoft docs, not general web |
| MDN | AbortController doc paths/text | 3.467 s | Not complete compatibility verification |
| searchcode | Router code inside Express | 2.762 s | Named repo, not global code search |
| Cloudflare Docs | Workers KV expiration docs | 7.924 s | Tail latency, no low-latency guarantee |
| grep.app | Valid no-results response | 1.832 s | Protocol passed, retrieval task did not |

Of ten public API checks, DataCite, Open Library, DEV.to, HAL, Zenodo and Figshare returned JSON data. GDELT/Semantic Scholar returned 429, Bluesky 403 and dblp unparseable JSON. No identity rotation or repeated blocked-source requests. Initialization/list/query plus API checks total 46 client top-level HTTP operations; internal redirects/documentation browsing are unmeasured. No user keys, response bodies, cookies or session IDs are published.

## Complete catalog

### General web search and reading

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S001 | [Parallel Search MCP](https://parallel.ai/mcp) | A | Anonymous limited search/fetch, separate from keyed APIs | live_response | P0 |
| S002 | [Exa hosted MCP](https://exa.ai/docs/get-started/exa-mcp) | A | Integrated; anonymous limits differ from the keyed API plan | candidate_reference; existing/partial adapter | existing |
| S003 | [Bing RSS](https://www.bing.com/search?format=rss&q=python) | W | Integrated experimental feed, not a stable free API contract | candidate_reference; existing/partial adapter | existing |
| S004 | [DuckDuckGo HTML](https://html.duckduckgo.com/html/) | W | Integrated experimental HTML; verification may block | candidate_reference; existing/partial adapter | existing |
| S005 | [DuckDuckGo Instant Answer](https://duckduckgo.com/api) | A | Instant answers/knowledge data, not full web SERP | candidate_reference | backlog |
| S006 | [360 / Baidu / Sogou public search pages](https://www.so.com/) | W | 360 browser fallback integrated; others unverified, public UI is not API | candidate_reference; existing/partial adapter | existing |
| S007 | [Google / Bing / Brave / Mojeek public UI](https://www.google.com/) | W | Optional browser candidates; access/region/index differ | candidate_reference | backlog |
| S008 | [Tavily API](https://www.tavily.com/pricing) | Q | 1000 credits/month, key required, no card; keyed adapter integrated | candidate_reference; existing/partial adapter | existing |
| S009 | [Exa API](https://exa.ai/pricing) | Q | Monthly $10 credits plus $10 onboarding bonus; key required, not anonymous MCP | candidate_reference; existing/partial adapter | existing |
| S010 | [Brave Search API](https://api-dashboard.search.brave.com/documentation/resources/help-feedback) | Q | Monthly $5 credits; key/card required, no standalone free plan | candidate_reference; existing/partial adapter | existing |
| S011 | [Firecrawl](https://www.firecrawl.dev/pricing) | Q | 1000 credits/month, about 500 searches or 1000 scraped pages; key required | candidate_reference | backlog |
| S012 | [Serper](https://serper.dev/) | T | 2500 free trial queries, not a monthly allowance; third-party Google SERP | candidate_reference | backlog |
| S013 | [SerpApi](https://serpapi.com/pricing) | Q | 250 free searches/month, key required; third-party SERP service | candidate_reference | backlog |
| S014 | [Search1API](https://s1.dev/docs/essentials/credits-and-limits) | T | 100 signup credits, not monthly; key required | candidate_reference | backlog |
| S015 | [Jina Reader / Search](https://jina.ai/reader/) | Q | Anonymous Reader fallback integrated, local 401 observed; verify Search/keyed access separately | candidate_reference; existing/partial adapter | existing |

### Official technical documentation

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S016 | [Microsoft Learn MCP](https://learn.microsoft.com/en-us/training/support/mcp) | A | Microsoft/Azure/.NET official docs/code samples, not general web | live_response | P0 |
| S017 | [MDN MCP](https://developer.mozilla.org/en-US/mcp) | A | HTML/CSS/JS/Web API docs and browser compatibility | live_response | P0 |
| S018 | [Cloudflare Docs MCP](https://developers.cloudflare.com/workers/get-started/prompting/) | A | Official Workers/KV/R2 docs; relatively long tail in this sample | live_response | P1 |
| S019 | [OpenAI Docs MCP](https://developers.openai.com/resources/docs-mcp) | A | Official OpenAI docs; documentation discovery only, no live call here | candidate_reference | backlog |
| S020 | [Context7](https://github.com/upstash/context7) | Q | Docs recommend keys for higher limits; verify anonymous scope/current plan | candidate_reference | backlog |
| S021 | [Python official docs / Sphinx inventories](https://docs.python.org/3/) | W | Readable docs/inventories, not a universal search API | candidate_reference | backlog |
| S022 | [Rust std / docs.rs](https://docs.rs/) | W | Standard/crate docs; distinguish versions | candidate_reference | backlog |
| S023 | [Read the Docs / llms.txt publisher docs](https://docs.readthedocs.com/platform/stable/reference/sitemaps.html) | W | Sitemaps/doc indexes aid discovery, not complete/live retrieval | candidate_reference | backlog |

### News and publisher feeds

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S024 | [China News Service RSS](https://www.chinanews.com.cn/rss/) | A | Latest/finance integrated; more publisher channels can be added | candidate_reference; existing/partial adapter | existing |
| S025 | [BBC RSS](https://www.bbc.co.uk/news/10628494) | A | World integrated; other publisher feeds are candidates | candidate_reference; existing/partial adapter | existing |
| S026 | [CCTV / CGTN RSS](https://english.cctv.cn/rss/) | W | Official RSS listing exists; verify freshness of older endpoints | historical_official_listing_freshness_unverified | backlog |
| S027 | [Xinhua RSS](https://www.xinhuanet.com/english/rss/index.htm) | W | Legacy official feeds; freshness/use scope needs checking | historical_official_listing_freshness_unverified | backlog |
| S028 | [DW RSS](https://rss.dw.com/rdf/rss-en-all) | A | International news feed; distinguish excerpts from originals | candidate_reference | backlog |
| S029 | [UN News RSS](https://news.un.org/en/rss-feeds) | A | UN multilingual news, finite feed windows | candidate_reference | backlog |
| S030 | [NASA news feeds](https://www.nasa.gov/rss-feeds/) | A | Official space/research news, not general full-text search | candidate_reference | backlog |
| S031 | [GDELT DOC / Context](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) | A | Multilingual news retrieval; local 429, not currently accepted | live_limited_or_unparsed | P1-validation |
| S032 | [Google News RSS](https://news.google.com/) | W | Experimental news-index candidate, not an official free News API | candidate_reference | backlog |
| S033 | [Guardian Open Platform](https://open-platform.theguardian.com/access/) | Q | Free developer key is non-commercial; commercial/mining use differs | candidate_reference | backlog |
| S034 | [NewsAPI.org](https://newsapi.org/pricing) | Q | 100/day, development/testing, 24h article delay; unsuitable as live default | candidate_reference | backlog |
| S035 | [GNews](https://gnews.io/pricing) | Q | 100/day, non-commercial, 12h delay and truncated content | candidate_reference | backlog |
| S036 | [NewsData.io](https://newsdata.io/pricing) | Q | 200 credits/day, testing/personal use, 12h delay | candidate_reference | backlog |
| S037 | [TheNewsAPI](https://www.thenewsapi.com/pricing) | Q | 100/day, three articles/request; verify production terms | candidate_reference | backlog |

### Chinese-language public policy, disclosures and data

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S038 | [China gov.cn latest-policy index](https://www.gov.cn/zhengce/zuixin/) | A | Integrated finite JSON list incl. explainers, not national completeness | candidate_reference; existing/partial adapter | existing |
| S039 | [NDRC notices / announcements](https://www.ndrc.gov.cn/xxgk/zcfb/tz/) | W | Public originals/dates; site-specific parsing, not stable API | candidate_reference | P0 |
| S040 | [National Energy Administration](https://www.nea.gov.cn/) | W | Energy policy, notices, statistics and press releases | candidate_reference | P0 |
| S041 | [National Bureau of Statistics releases](https://www.stats.gov.cn/sj/zxfb/) | W | Original statistical releases including PMI/CPI/GDP | candidate_reference | P0 |
| S042 | [National Data / NBS database](https://data.stats.gov.cn/) | W | Statistics portal with changed frontend; old endpoints not stable contracts | candidate_reference | backlog |
| S043 | [MIIT](https://www.miit.gov.cn/) | W | Industrial/software/equipment/telecom policy originals | candidate_reference | P1 |
| S044 | [Ministry of Commerce](https://www.mofcom.gov.cn/) | W | Trade/export policy; on-demand public-page reading | candidate_reference | backlog |
| S045 | [Ministry of Ecology and Environment](https://www.mee.gov.cn/) | W | Environment/carbon-market/standards notices | candidate_reference | backlog |
| S046 | [People's Bank of China](https://www.pbc.gov.cn/) | W | Monetary policy and financial statistics releases | candidate_reference | backlog |
| S047 | [CSRC](https://www.csrc.gov.cn/) | W | Securities rules, notices and policy | candidate_reference | backlog |
| S048 | [SAMR standards disclosure](https://openstd.samr.gov.cn/) | W | Public standards/catalogs, not all standards free or bulk-accessible | candidate_reference | backlog |
| S049 | [National law database](https://flk.npc.gov.cn/) | W | Law originals; browser tool 403 here, no open API promise | candidate_reference | backlog |
| S050 | [China Government Procurement](https://www.ccgp.gov.cn/) | W | Procurement/tender notices; search controls need adaptation | candidate_reference | backlog |
| S051 | [National public resource trading platform](https://www.ggzy.gov.cn/) | W | Public works/land/property trading notices | candidate_reference | backlog |
| S052 | [CNInfo public disclosures](https://www.cninfo.com.cn/new/index) | W | Public disclosure pages/PDFs; data API has separate access/plans | candidate_reference | P1-validation |
| S053 | [SSE / SZSE / BSE disclosures](https://www.sse.com.cn/disclosure/listedinfo/announcement/) | W | Exchange original disclosures, not licensed data feeds for free | candidate_reference | backlog |
| S054 | [DATA.GOV.HK](https://data.gov.hk/en/help/api-spec) | A | Public dataset catalog/APIs; check dataset-specific terms | candidate_reference | backlog |
| S055 | [Beijing / Shanghai / Shenzhen open-data portals](https://data.sh.gov.cn/) | W | Catalogs public; some APIs require signup, not universally keyless | candidate_reference | backlog |
| S056 | [data.gov.tw](https://data.gov.tw/) | W | Open-data catalog, dataset-specific access/licensing | candidate_reference | backlog |

### International government and statistics

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S057 | [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1) | A | US federal rules/notices discovery; authoritative originals via govinfo | candidate_reference; anonymous sample succeeded | backlog |
| S058 | [SEC EDGAR public data](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | A | Keyless submissions/XBRL; not universal full-text search | candidate_reference | P1 |
| S059 | [GOV.UK content/search](https://docs.publishing.service.gov.uk/apis.html) | A | UK public content/APIs, distinguish search and page content | candidate_reference | backlog |
| S060 | [UK legislation](https://www.legislation.gov.uk/developer) | A | Legislation data/formats, not legal conclusion verification | candidate_reference | backlog |
| S061 | [Eurostat](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access) | A | European statistical APIs, release lags apply | candidate_reference | backlog |
| S062 | [World Bank Indicators](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation) | A | Macroeconomic indicators, not live market quotes | candidate_reference; anonymous sample succeeded | backlog |
| S063 | [OECD SDMX](https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html) | A | Economic statistics; verify limits/dataset scope | candidate_reference | backlog |
| S064 | [api.data.gov / govinfo / Congress APIs](https://api.data.gov/) | Q | Many federal services use free keys; not uniform authentication | candidate_reference | backlog |

### Papers, books and research

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S065 | [arXiv](https://info.arxiv.org/help/api/index.html) | A | Integrated metadata/abstracts; PDFs separate | candidate_reference; existing/partial adapter | existing |
| S066 | [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | A | Integrated DOI/publication metadata, not guaranteed full text | candidate_reference; existing/partial adapter | existing |
| S067 | [DataCite](https://support.datacite.org/docs/api) | A | Dataset/work DOI metadata; anonymous call succeeded | live_response | P1 |
| S068 | [dblp](https://dblp.org/faq/How+to+use+the+dblp+search+API.html) | A | CS bibliography; response was not parseable JSON in this check | live_limited_or_unparsed | backlog |
| S069 | [Europe PMC](https://europepmc.org/RestfulWebService) | A | Integrated biomedical abstracts/metadata, not clinical validation | candidate_reference; existing/partial adapter | existing |
| S070 | [NCBI PubMed / PMC E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | A | Metadata/open-text subset; optional key raises limits | candidate_reference | backlog |
| S071 | [HAL](https://api.archives-ouvertes.fr/docs) | A | Open research records; anonymous request succeeded | live_response | P2 |
| S072 | [OpenAIRE](https://graph.openaire.eu/develop/api.html) | Q | Open research graph; current endpoint signup/auth policy unconfirmed, not accepted as keyless | candidate_reference | backlog |
| S073 | [Zenodo public records](https://developers.zenodo.org/) | A | Anonymous public records succeeded; upload/private APIs require auth | live_response | P1 |
| S074 | [Figshare public articles](https://docs.figshare.com/) | A | Anonymous public articles succeeded; restricted files separate | live_response | P2 |
| S075 | [bioRxiv / medRxiv](https://api.biorxiv.org/) | A | Date/DOI/category preprint retrieval, not generic keyword search | candidate_reference; anonymous sample succeeded | backlog |
| S076 | [ClinicalTrials.gov](https://clinicaltrials.gov/data-api/api) | A | Trial registrations, not proof of efficacy | candidate_reference; anonymous sample succeeded | backlog |
| S077 | [OpenReview public notes](https://docs.openreview.net/) | A | Public notes/reviews; venue/record permissions vary | candidate_reference | backlog |
| S078 | [Open Library](https://openlibrary.org/developers/api) | A | Book metadata succeeded; not unrestricted book downloads/loans | live_response | P1 |
| S079 | [Internet Archive search](https://archive.org/developers/) | A | Catalog/metadata/some text; restricted resources separate | candidate_reference | backlog |
| S080 | [Library of Congress](https://www.loc.gov/apis/) | A | Public collection JSON/search; rights per item | candidate_reference | backlog |
| S081 | [Wikisource](https://www.mediawiki.org/wiki/API:Main_page) | A | Open textual library via MediaWiki interfaces | candidate_reference | backlog |
| S082 | [OpenAlex](https://help.openalex.org/access/pricing/) | Q | API key now required; $1/day free, no payment method, not keyless | candidate_reference | P2-opt-in-key |
| S083 | [Semantic Scholar](https://www.semanticscholar.org/product/api) | Q | Free key available; anonymous pool returned 429 | live_limited_or_unparsed | P2-opt-in-key |
| S084 | [CORE](https://core.ac.uk/services/api) | Q | Open research aggregation; verify free/key/limit terms | candidate_reference | backlog |
| S085 | [Unpaywall](https://unpaywall.org/products/api) | Q | DOI-to-OA links with email identification, not general paper search | candidate_reference | backlog |
| S086 | [Google Books API](https://developers.google.com/books/docs/v1/using) | Q | Book metadata/previews; key/quota separate from text rights | candidate_reference | backlog |
| S087 | [Europeana](https://pro.europeana.eu/page/apis) | Q | Cultural collections; developer keys and item rights separate | candidate_reference | backlog |
| S148 | [DOAJ](https://doaj.org/api/docs) | A | Open journal/article metadata, not all article-body downloads | candidate_reference | backlog |
| S149 | [NASA ADS](https://ui.adsabs.harvard.edu/help/api/) | Q | Astronomy/physics literature with free token; limits need acceptance | candidate_reference | backlog |
| S150 | [BASE](https://www.base-search.net/about/en/about_develop.php) | Q | Research aggregation; API access/use conditions need approval review | candidate_reference | backlog |

### Code, packages and models

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S088 | [GitHub REST public repositories](https://docs.github.com/en/rest/search/search) | A | Integrated repos/README; anonymous limits, code search needs auth | candidate_reference; existing/partial adapter | existing |
| S089 | [GitLab public projects](https://docs.gitlab.com/api/projects/) | A | Integrated public projects, not anonymous global code search | candidate_reference; existing/partial adapter | existing |
| S090 | [Codeberg / Forgejo](https://codeberg.org/api/swagger) | A | Public-project API; verify instance limits/coverage | candidate_reference | backlog |
| S091 | [Gitee API](https://gitee.com/api/v5/swagger) | Q | Chinese repos; verify per-endpoint token/access/limits | candidate_reference | backlog |
| S092 | [npm registry](https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md) | A | Integrated package search/metadata, not quality/security verdicts | candidate_reference; existing/partial adapter | existing |
| S093 | [PyPI JSON / Simple](https://docs.pypi.org/api/) | A | Named package/version/dependency metadata, not global text-search API | candidate_reference; anonymous sample succeeded | P1 |
| S094 | [crates.io](https://crates.io/data-access) | A | Integrated Rust package search; stable/prerelease distinction | candidate_reference; existing/partial adapter | existing |
| S095 | [Maven Central](https://central.sonatype.org/search/rest-api-guide/) | A | Java artifact metadata search | candidate_reference; anonymous sample succeeded | P1 |
| S096 | [NuGet](https://learn.microsoft.com/en-us/nuget/api/search-query-service-resource) | A | .NET package search/metadata | candidate_reference; anonymous sample succeeded | P2 |
| S097 | [Packagist](https://packagist.org/apidoc) | A | PHP package search/metadata; many reads anonymous | candidate_reference; anonymous sample succeeded | backlog |
| S098 | [RubyGems](https://guides.rubygems.org/rubygems-org-api/) | A | Ruby package reads/search; writes need keys | candidate_reference; anonymous sample succeeded | backlog |
| S099 | [Go module proxy](https://go.dev/ref/mod#module-proxy) | A | Module-path/version lookup, not universal keyword search | candidate_reference | backlog |
| S100 | [Hugging Face Hub](https://huggingface.co/docs/hub/api) | A | Models integrated; datasets/Spaces candidates, gated content separate | candidate_reference; existing/partial adapter | existing |
| S101 | [Docker Hub](https://docs.docker.com/reference/api/hub/latest/) | Q | Public image metadata; pull/search quotas/auth vary | candidate_reference | backlog |
| S102 | [searchcode MCP](https://searchcode.com/) | A | Keyless free beta; code within a named repo, not global code index | live_response | P0 |
| S103 | [grep.app MCP](https://vercel.com/blog/grep-a-million-github-repositories-via-mcp) | A | Public cross-repo code retrieval; this query had no hits | protocol_ok_no_hits | P1-validation |
| S104 | [Libraries.io](https://libraries.io/api) | Q | Dependency/package index; verify keys/free scope/data terms | candidate_reference | backlog |

### Community and social interfaces

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S105 | [Hacker News / Algolia](https://hn.algolia.com/api) | A | Integrated story search; item/comment-tree reading separate | candidate_reference; existing/partial adapter | existing |
| S106 | [Stack Exchange family](https://api.stackexchange.com/docs) | A | Questions integrated; answers/comments candidates, attribution required | candidate_reference; existing/partial adapter | existing |
| S107 | [Discourse public communities](https://docs.discourse.org/) | A | Python/Rust originals integrated; sites may disable public access | candidate_reference; existing/partial adapter | existing |
| S108 | [V2EX public API](https://www.v2ex.com/p/7v9TEc53) | A | Hot/original adapters implemented; local 403, not currently accepted | candidate_reference; existing/partial adapter | existing |
| S109 | [DEV.to / Forem](https://developers.forem.com/api) | A | Public technical articles; anonymous listing succeeded | live_response | P1 |
| S110 | [Lobsters](https://lobste.rs/) | A | Technical link-community RSS/JSON candidate, not live-tested | candidate_reference | backlog |
| S111 | [Lemmy public instances](https://join-lemmy.org/api/) | A | Public posts/comments vary by instance; no arbitrary public default | candidate_reference | backlog |
| S112 | [Mastodon](https://docs.joinmastodon.org/methods/search/) | Q | Full-text search often needs token/index support, not global federation | candidate_reference | backlog |
| S113 | [Bluesky public AppView](https://docs.bsky.app/docs/advanced-guides/api-directory) | A | Public social views; local search 403, further validation required | live_limited_or_unparsed | P2-validation |
| S114 | [Cnblogs RSS](https://www.cnblogs.com/) | W | Personal/community tech feeds, per-feed validation needed | candidate_reference | backlog |

### Knowledge, entities and media

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S115 | [Wikipedia](https://www.mediawiki.org/wiki/API:Search) | A | English/Chinese articles integrated; edit date is not publication | candidate_reference; existing/partial adapter | existing |
| S116 | [Wikidata](https://www.wikidata.org/wiki/Wikidata:Data_access) | A | Entities/relations/IDs, SPARQL limits, not news search | candidate_reference; anonymous sample succeeded | P1 |
| S117 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/Commons:API) | A | Media metadata; attribution/license per item | candidate_reference | backlog |
| S118 | [Openverse](https://docs.openverse.org/api/) | A | Open-license images/audio; anonymous/authenticated limits differ | candidate_reference; anonymous sample succeeded | P2 |
| S119 | [GBIF](https://www.gbif.org/developer/summary) | A | Species/biodiversity; download jobs differ from public reads | candidate_reference | backlog |
| S120 | [iNaturalist](https://api.inaturalist.org/v1/docs/) | A | Species observations, per-data/image rights | candidate_reference | backlog |
| S121 | [ROR](https://ror.readme.io/docs/rest-api) | A | Institution IDs/name disambiguation, not article search | candidate_reference; anonymous sample succeeded | backlog |
| S122 | [ORCID public API](https://info.orcid.org/documentation/integration-guide/orcid-api-2/) | Q | Researcher identities; verify public API credentials/scope | candidate_reference | backlog |

### Historical web and archives

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S123 | [Common Crawl URL Index](https://index.commoncrawl.org/) | A | Crawl-snapshot URL index, not live full-text search; no self-built index scope | candidate_reference | backlog |
| S124 | [Wayback / CDX](https://archive.org/developers/wayback-cdx-server.html) | A | Historical URL/snapshots, not current-page evidence | candidate_reference | backlog |
| S125 | [Arquivo.pt](https://arquivo.pt/api) | A | Archived full-text/URL retrieval, not live web | candidate_reference | backlog |

### Weather, geography, energy and events

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S126 | [USGS earthquake feeds/API](https://earthquake.usgs.gov/fdsnws/event/1/) | A | Standard public earthquake/event data | candidate_reference; anonymous sample succeeded | backlog |
| S127 | [NOAA NCEI data service](https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation) | A | Dataset-specific historical weather, not general search | candidate_reference | backlog |
| S128 | [weather.gov API](https://www.weather.gov/documentation/services-web-api) | A | US forecasts/alerts with UA/rate requirements | candidate_reference | backlog |
| S129 | [EIA Open Data](https://www.eia.gov/opendata/) | Q | Energy/electricity/oil/gas data with free key | candidate_reference | backlog |
| S130 | [ENTSO-E Transparency](https://transparency.entsoe.eu/) | Q | European power data; register token and check data terms | candidate_reference | backlog |
| S131 | [NASA public APIs](https://api.nasa.gov/) | Q | Many APIs use free keys; demo-key limits are low | candidate_reference | backlog |
| S132 | [Open-Meteo](https://open-meteo.com/en/pricing) | Q | Free endpoint for evaluation/prototyping; commercial subscription differs | candidate_reference | backlog |
| S133 | [OpenStreetMap Nominatim](https://operations.osmfoundation.org/policies/nominatim/) | A | Place/geocoding with strict public-service usage limits | candidate_reference; anonymous sample succeeded | backlog |
| S134 | [Overpass public API](https://wiki.openstreetmap.org/wiki/Overpass_API) | A | OSM feature queries; instance capacity limited, no fan-out default | candidate_reference | backlog |
| S135 | [GeoNames](https://www.geonames.org/export/web-services.html) | Q | Geographic names require registered username, tiered limits | candidate_reference | backlog |

### Platforms without unconditional free automation

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S136 | [X API](https://docs.x.com/x-api/getting-started/pricing) | R | Prepaid usage; promotional incentives are not permanent free search | candidate_reference | backlog |
| S137 | [Reddit Data API](https://redditinc.com/policies/data-api-terms) | R | Approval/use/commercial restrictions, not unconditionally free | candidate_reference | backlog |
| S138 | [Xiaohongshu](https://openaccount.xiaohongshu.com/docs/api-reference) | R | Account auth is not general note search; current indexed route retained | candidate_reference | backlog |
| S139 | [Weibo](https://open.weibo.com/wiki/API) | R | Public web differs from open-platform API; anonymous hot list 403 locally | candidate_reference | backlog |
| S140 | [Zhihu](https://www.zhihu.com/) | W | Experimental hot list integrated, not full search/answers/comments | candidate_reference; existing/partial adapter | existing |
| S141 | [Bilibili](https://www.bilibili.com/) | W | Hotwords integrated; native keyword search 412 locally; subtitles/comments separate | candidate_reference; existing/partial adapter | existing |
| S142 | [WeChat / Sogou WeChat](https://mp.weixin.qq.com/) | R | Authorized official-account APIs are not global article-search APIs | candidate_reference | backlog |
| S143 | [Douyin / Kuaishou](https://developer.open-douyin.com/) | R | Business-authorized APIs, not arbitrary public video/comment search | candidate_reference | backlog |
| S144 | [Douban / Tieba / Juejin / CSDN / OSChina](https://www.douban.com/) | W | Some public pages readable, no stable free native API promise | candidate_reference | backlog |

### Tools/self-hosting: not hosted sources

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S145 | [SearXNG](https://docs.searxng.org/) | S | Open-source metasearch software, not free hosting; self-hosting remains out of scope | candidate_reference | backlog |
| S146 | [RSSHub / RSS-Bridge](https://docs.rsshub.app/) | S | Feed-conversion tools, not guaranteed public hosting or new independent indexes | candidate_reference | backlog |
| S165 | [Miniflux / FreshRSS](https://miniflux.app/) | S | Feed readers, not new news sources or search engines | candidate_reference | backlog |

### Patents and intellectual property

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S151 | [USPTO Open Data Portal](https://data.uspto.gov/apis/api-catalog) | Q | US patent/trademark data; per-API registration/key rules | candidate_reference | backlog |
| S152 | [EPO Open Patent Services](https://www.epo.org/en/searching-for-patents/data/web-services/ops) | Q | Patent/bibliographic data; signup/free quota/fair-use conditions | candidate_reference | backlog |
| S153 | [Google Patents](https://patents.google.com/) | W | Public patent search UI, not an unconditional free automation API | candidate_reference | backlog |
| S154 | [CNIPA public services](https://www.cnipa.gov.cn/) | W | Patent information portal; login/challenge/API access need verification | candidate_reference | backlog |

### Finance, economics and market data

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S155 | [FRED](https://fred.stlouisfed.org/docs/api/fred/) | Q | Macro/rate data with free key, not live equity quotes | candidate_reference | backlog |
| S156 | [US BLS public data](https://www.bls.gov/developers/) | A | Statistical time series; unregistered/registered limits differ | candidate_reference; anonymous sample 403 | backlog |
| S157 | [US Census data APIs](https://www.census.gov/data/developers/data-sets.html) | Q | Statistical datasets/APIs; verify keys/dataset limits | candidate_reference | backlog |
| S158 | [Tushare](https://tushare.pro/document/1) | Q | Token/points/access tiers; not all market data free | candidate_reference | backlog |
| S159 | [BaoStock](https://www.baostock.com/) | A | Historical-market candidate with default anonymous login; verify SDK/freshness/terms | candidate_reference | backlog |
| S160 | [CoinGecko Demo API](https://docs.coingecko.com/reference/setting-up-your-api-key) | Q | Free demo key; quota/commercial/live scope needs verification | candidate_reference | backlog |
| S161 | [Yahoo Finance public pages](https://finance.yahoo.com/) | W | Public quote pages differ from unofficial APIs; no stability/live-rights promise | candidate_reference | backlog |
| S162 | [Stooq historical data](https://stooq.com/db/h/) | W | Historical data candidate, not free live quotes/redistribution rights | candidate_reference | backlog |

### Podcasts and audio metadata

| ID | Source | Access | Scope and limits | Verification/integration | Priority |
|---|---|---|---|---|---|
| S163 | [Apple iTunes Search API](https://performance-partners.apple.com/search-api) | A | Podcast/media metadata; audio/transcript rights separate | candidate_reference | backlog |
| S164 | [Podcast Index](https://podcastindex-org.github.io/docs-api/) | Q | Podcast catalog with developer key, not arbitrary transcript API | candidate_reference | backlog |
| S165 | [Listen Notes](https://www.listennotes.com/api/pricing/) | Q | Podcast-search free-tier candidate; verify quotas/use | candidate_reference | backlog |
