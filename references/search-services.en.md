# Search routes and competitor implementation research

[简体中文](search-services.md) | **English**

Checked 2026-11-03 against project code and official documentation. Features, stars and connectivity are not search-quality rankings. Scope is web search/reading, excluding self-hosted instances, self-built indexes and enterprise document search.

## References and decisions

| Project | Observed implementation | Decision for xcoze search |
|---|---|---|
| [Agent Reach](https://github.com/Panniantong/Agent-Reach/blob/main/agent_reach/channels/web.py) | Prefers available native tools; Exa MCP search, Jina Reader, platform channels | Reuse authorized tools without requiring browsers or every platform login |
| [DDGS](https://github.com/deedy5/ddgs/blob/main/ddgs/ddgs.py) | Multiple backends, concurrency, deduplication and simple ranking; some parse public HTML | Implement a few standard-library adapters independently; no DDGS runtime dependency or claim to support every backend |
| [open-webSearch](https://github.com/Aas-ee/open-webSearch) | Shared CLI/MCP/service core, concurrent engines and optional browser reading | Keep base runtime browser-free and bounded; undocumented frontend endpoints are not stable contracts |
| [OpenRouter](https://openrouter.ai/docs/guides/features/server-tools/web-search) | Native search on compatible endpoints or external engines | Agent calls host tools; scripts do not assume access to host internals |
| [LiteLLM](https://docs.litellm.ai/docs/search) | Unified multi-provider search and cost records | Focus on default access, simple configuration and evidence scope rather than provider count |
| [Tavily Skills](https://github.com/tavily-ai/skills) | CLI-backed Skill workflows with limited keyless operations | Retain keyed API integration; no shared CLI quota/session compatibility promise |

Code snapshots: Agent Reach 7a38047acf26a729cbb27851e3cb81639da86b29; DDGS 8e74959141106702645020dcb853c6453b5e5195; open-webSearch fb11fd94df736819a0d2765bf7645224f98b2c6b. Read-only study of routing/contracts; no installer execution or user-session copying.

## Keyless support in this version

- Bing RSS and DuckDuckGo HTML are experimental public routes; access, structure and relevance may change, without an official search API SLA claim.
- [Official Exa MCP](https://exa.ai/docs/get-started/exa-mcp) documents limited keyless search/reading; separate from its keyed API.
- [GitHub search](https://docs.github.com/en/rest/search/search) has anonymous quotas; code search requires authentication and is not integrated here.
- HN uses [Algolia search](https://hn.algolia.com/api) and the [official single-item API](https://github.com/HackerNews/API). Indexes and item data can differ in freshness.
- [Jina Reader](https://jina.ai/reader/) accesses target pages, extracts content and converts it to model-friendly text: retrieval as well as formatting. This version integrates Reader only, as a fallback when snippets are insufficient or native reading fails; skip it when text is already available. Jina Search has different auth/limits and is not integrated.

Keyless, open-source and no additional payment are distinct. Requests still reach external services, including commercial free-tier endpoints. Free excludes keyed adapters, not all compute costs. See [validation](../VALIDATION.en.md) for actual checks.

## Existing keyed services

| Service | Official contract | Scope |
|---|---|---|
| DeepSeek | [Search/Fetch](https://api-docs.deepseek.com/guides/search/) | Search and page text |
| Yuanbao | [SearchPro](https://cloud.tencent.com/document/product/1806/121811) | Search/summaries with account-tier capabilities |
| Tavily | [Search](https://docs.tavily.com/documentation/api-reference/endpoint/search), [Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract) | Search and extraction |
| Exa | [Search](https://exa.ai/docs/reference/search), [Contents](https://exa.ai/docs/reference/get-contents) | Search/text/highlights/summaries |
| Brave | [Web Search](https://api-dashboard.search.brave.com/api-reference/web/search/get) | Web search |
| Bocha | [Platform](https://open.bochaai.com/) | Web Search |

## Future candidates

Perplexity Search, Firecrawl, Parallel, Serper, SerpApi and Jina Search remain unimplemented candidates for demonstrated gaps. Recheck trials, auth, contracts and costs at implementation time. Declare platform search, reading, comments and ranking capabilities independently rather than a blanket “supported platform” label.

See [open sources](open-sources.en.md) for public native indexes and existing-tool cooperation. No new base dependencies; native APIs, public indexes and specialist content tools remain separate.
