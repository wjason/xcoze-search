# Research on agent search services

[简体中文](search-services.md) | **English**

Research date: 2026-11-02. Official provider/project documentation informs integration planning, not adoption rankings or retrieval-quality evaluations. P1 adapters/offline tests are implemented without real-key calls; P2/P3 remain candidates. Documentation or code does not establish account authorization or result quality.

## Integration routes

- **Structured search APIs** return titles, links, snippets, and metadata for the agent to read and answer from.
- **Search plus extraction** can retrieve page text, Markdown, or relevant excerpts; retain each content type's meaning.
- **Self-hosted metasearch** requires user-managed instances, engines, and access controls, not simply a key.

Routes overlap. REST is the preferred execution interface. MCP servers or official Skills indicate ecosystem support, but do not replace adapters or result contracts.

## Implemented services

| Service | Official reference | State |
|---|---|---|
| DeepSeek Search / Fetch | [Guide](https://api-docs.deepseek.com/guides/search/) | Implemented; version regression passed on 2026-11-02 |
| Tencent Yuanbao SearchPro | [Service API KEY](https://cloud.tencent.com/document/product/1806/130615) | Implemented; live account verification pending |
| Tavily Search / Extract | [Search](https://docs.tavily.com/documentation/api-reference/endpoint/search) / [Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract) | Implemented in v0.3.0; not live-tested |
| Exa Search / Contents | [Search](https://exa.ai/docs/reference/search) / [Contents](https://exa.ai/docs/reference/get-contents) | Implemented in v0.3.0; not live-tested |
| Brave Web Search | [Parameters](https://api-dashboard.search.brave.com/api-reference/web/search/get) | Implemented in v0.3.0; not live-tested |
| Bocha Web Search | [Official MCP implementation](https://github.com/BochaAI/bocha-search-mcp/blob/master/src/bocha_search_mcp/server.py) | Implemented in v0.3.0; not live-tested |

## Expansion: implemented P1 and candidate P2/P3

Capabilities below come from official references. Priorities are project decisions. API-key access can still require activation, credits, or authorization.

| Service | Official entry points/capabilities | Configuration and adapter concerns | Priority |
|---|---|---|---|
| Tavily | [Search](https://docs.tavily.com/documentation/api-reference/endpoint/search) / [Extract guide](https://help.tavily.com/articles/3363168593-extracting-web-content-using-tavily) | Bearer key; map depth/date/domains, distinguish raw text, generated answers, and extra request cost | P1 |
| Exa | [Search](https://exa.ai/docs/reference/search), including content/text/highlights | Key; preserve text/excerpt/summary meaning, dates, warnings, and reported costs | P1 |
| Brave Search | [Web Search](https://api-dashboard.search.brave.com/app/documentation/web-search/get-started), geography/language/freshness/snippets | X-Subscription-Token; snippets are not text, with distinct count/pagination limits | P1 |
| Bocha | [Platform](https://open.bochaai.com/) / [official MCP](https://github.com/BochaAI/bocha-search-mcp), Web/AI Search | Bearer key; web results/summaries first, structured cards separately evaluated | P1 |
| Perplexity | [Search API](https://docs.perplexity.ai/docs/search/quickstart), filters and content snippets | Key; raw search is distinct from generated answers, retain native snippet meaning | P2 |
| Firecrawl | [Search](https://docs.firecrawl.dev/features/search), optional Markdown scraping | Key; explicit scraping, separate discovery/extraction cost and failures | P2 |
| Parallel | [Search quickstart](https://docs.parallel.ai/search/search-quickstart), objective-driven search/excerpts | x-api-key; map objective and search_queries separately, preserve excerpts/warnings | P2 |
| Serper | [Official product/examples](https://serper.dev/), Google SERP service | Key; verify current console auth/fields before implementation. Third-party, not Google's official API | P2 |
| SerpApi | [Google Search API](https://serpapi.com/search-api) / [Search Index](https://serpapi.com/search-index-api) | Key; organic_results, async/application status, pagination/geography; engine differences and no credential logging | P2 |
| Jina | [Search / Reader](https://jina.ai/reader/), search and URL reading | Verify keys/limits; Reader and search declared separately, no blanket free-access claim | P3 |
| SearXNG | [Search API](https://docs.searxng.org/dev/search_api.html), self-hosted metasearch | User instance/auth; JSON must be enabled and is often unavailable on public instances | P3 |

## Priority rationale

P1 broadens the original two providers with search/content interfaces while keeping provider-specific keys. P2 adds scraping, objective-driven retrieval, and SERP formats. P3 introduces optional content services and user-maintained instances requiring deployment conventions.

These are scope/capability choices, not claims about accuracy, cost, or availability on a network. Recheck current official contracts, billing, content terms, and account eligibility before implementation.

## Evidence needed before implementation

Verify endpoints/authentication, result/content semantics, filters, empty/application errors, rate limits/retries, costs/quotas, data handling, and live account access. If complete docs require console login, record that gap instead of treating community examples as authoritative.

Implemented contracts live in [providers.en.md](providers.en.md); priorities and completion criteria are in the [roadmap](../TODO.en.md).
