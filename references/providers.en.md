# Official API contracts and adapter capabilities

[简体中文](providers.md) | **English**

Checked on 2026-11-02. These are the features exposed by this tool; account access, billing, and service limits remain subject to official documentation. All endpoints are fixed, authenticated redirects are blocked, and custom proxy URLs are not accepted.

## Capability matrix

| Provider ID | Search | Fetch / Extract | Result limit | Adapter query limit | Site restriction | Dates / relative time |
|---|---|---|---|---|---|---|
| `deepseek` | POST Search | POST Fetch | 50 | 128 Unicode characters, including appended site operator | Appended site operator | Write time operators explicitly in the query |
| `yuanbao` | POST SearchPro | Unsupported | 50 | 1500 UTF-8 bytes | Site | d1..30 / m1..12 / y1..5 |
| `tavily` | POST Search | POST Extract | 20 | Adapter limit: 4096 characters | include_domains | day/week/month/year or date bounds |
| `exa` | POST Search | POST Contents | Adapter limit: 50 | Adapter limit: 4096 characters | includeDomains | Publication date bounds |
| `brave` | GET Web Search | Unsupported | 20 | 600 characters and 75 words, including appended site operator | Appended site operator | pd/pw/pm/py or a date range |
| `bocha` | POST Web Search | Unsupported | 50 | Adapter limit: 4096 characters | --site not exposed | oneDay/oneWeek/oneMonth/oneYear or dates |

The 4096-character caps for Tavily, Exa, and Bocha are local validation policies, not guarantees from the providers. Exa's public numResults maximum can exceed this tool's 50-result cap. No automatic pagination, additional searches, or request expansion is performed to fill result counts. Use capabilities for machine-readable declarations.

## DeepSeek

- Search: `POST https://api.deepseek.com/v1/tools/search`.
- Fetch: `POST https://api.deepseek.com/v1/tools/fetch`.
- Bearer key; [official guide](https://api-docs.deepseek.com/guides/search/) / [Search reference](https://api-docs.deepseek.com/api/search/).

Requests use query/count/need_content. Fetch takes url and returns title/content. Search page content is optional; summary and content remain separate. Native rerank_score and authority scales are retained without cross-provider comparisons.

## Tencent Yuanbao

- `POST https://api.wsa.cloud.tencent.com/SearchPro`, using a Bearer Yuanbao Search Service API Key.
- [Service API KEY authentication](https://cloud.tencent.com/document/product/1806/130615), [SearchPro parameters](https://cloud.tencent.com/document/product/1806/121811), [official MCP tool reference](https://developer.cloud.tencent.com/mcp/server/11764), [product tiers](https://cloud.tencent.com/document/product/1806/121794).

Uses Query and optional Site/Freshness/Industry/Mode. At count<=10, optional paid-tier Cnt is omitted. Above 10, the integer is rounded up to 20/30/40/50 and results are locally truncated. Response.Pages supports JSON strings and objects. HTTP 200 with Error is still failure. passage is a standard snippet and content a dynamic summary; neither is full page text. Account eligibility, product tier, and quotas can restrict options.

Only unambiguous relative d/m/y ranges are exposed; contradictory absolute-range examples in older docs are not mapped. RequestId, Version, Msg, and provider fields are retained; Msg is untrusted data. Live verification remains pending without a test credential.

## Tavily

- `POST https://api.tavily.com/search` / `POST https://api.tavily.com/extract`, Bearer key.
- [Search contract](https://docs.tavily.com/documentation/api-reference/endpoint/search), [Extract contract](https://docs.tavily.com/documentation/api-reference/endpoint/extract).

Defaults to general/basic, with auto_parameters, include_answer, and raw content disabled; usage metadata is enabled. `--site` maps to include_domains. `--freshness` accepts day/week/month/year or d/w/m/y and is mutually exclusive with date bounds. `--start-date` / `--end-date` use YYYY-MM-DD. Time filters enable filter_by_published_date, excluding results without detectable dates. Dates are provider estimates of publication or update time; unknown dates are not invented.

Search content is snippets, not full text. `--need-content` requests Markdown raw_content. `--depth` explicitly selects advanced/fast/ultra-fast; `--include-answer` explicitly requests a generated answer. generated_answer remains request metadata, not source evidence or fact verification.

Extract submits one URL per request using basic depth and Markdown. Both results and failed_results are checked; HTTP 200 can still mean failure. Provider-normalized URLs are retained and may differ from input. usage/request_id are preserved.

## Exa

- `POST https://api.exa.ai/search` / `POST https://api.exa.ai/contents`, `x-api-key`.
- [Search contract](https://exa.ai/docs/reference/search), [Contents contract](https://exa.ai/docs/reference/get-contents).

Defaults to type:auto with no automatically requested contents. `--need-content`, `--highlights`, and `--summary` independently enable text, highlights, and summary. Summary uses an object; Search uses the original query as its summary objective. `--site` maps to includeDomains. Dates become UTC start/end-of-day ISO 8601 startPublishedDate/endPublishedDate values.

Contents sends one URL per request, explicitly extracts text, and optionally requests highlights/summary. URLs are limited to 2048 characters. Per-URL statuses are checked; a failure or missing unique valid page returns extraction_failed rather than trusting HTTP 200. Text, highlights, and summary remain separate. costDollars, warnings, requestId, and unknown metadata are retained. IGNORED_FIELD warnings produce constraint_not_applied so an ignored filter is never reported as applied.

## Brave Search

- `GET https://api.search.brave.com/res/v1/web/search`, `X-Subscription-Token`; the key is not put in the URL.
- [Official overview](https://api-dashboard.search.brave.com/app/documentation/web-search/query), [parameters and response](https://api-dashboard.search.brave.com/api-reference/web/search/get).

Uses q/count/result_filter:web. `--country` takes a two-letter country code and `--language` maps to search_lang; consult official enums for accepted codes. Freshness supports pd/pw/pm/py or YYYY-MM-DDtoYYYY-MM-DD. `--extra-snippets` explicitly enables additional snippets.

Only web.results is converted; ads, news cards, local cards, and other enrichments are not merged into page content. Other top-level metadata remains available. description and extra_snippets are snippets. page_age can indicate publication or modification; relative age is retained only in native fields rather than converted to a publication date. Web Search and LLM Context are separate products; this adapter implements Web Search only.

## Bocha

- `POST https://api.bochaai.com/v1/web-search`, Bearer key.
- [Official platform and response example](https://open.bochaai.com/), [official MCP implementation](https://github.com/BochaAI/bocha-search-mcp/blob/master/src/bocha_search_mcp/server.py).

Uses query/count/freshness and defaults summary:false; `--summary` explicitly enables summaries. Freshness supports noLimit, oneDay, oneWeek, oneMonth, oneYear, YYYY-MM-DD, or YYYY-MM-DD..YYYY-MM-DD. Channel-tracking parameters shown in official MCP examples are not added.

Maps data.webPages.value and retains name/url/snippet/summary/siteName/datePublished separately. Summaries are not full page text. A non-success code inside HTTP 200 is still an application error; raw error messages are not echoed. This adapter does not call AI Search, structured modality cards, or promise live stock prices.

## Usage, costs, and data flow

Queries and content URLs go directly to user-selected providers. Providers activate and bill independently. Multi-provider requests, retries, advanced depth, content extraction, and generated content may add charges. Budgets limit actual HTTP attempts, not money. Only provider-reported usage and cost are returned; missing values are null, with no price-table estimates.

The four added providers have not been tested with live accounts. Protocol and offline validation do not establish account authorization, balance, reachability, retrieval quality, or operational acceptance.
