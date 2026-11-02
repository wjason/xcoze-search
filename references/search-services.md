# Agent 搜索服务调研

**简体中文** | [English](search-services.en.md)

调研日期：2026-11-02。下列信息来自服务商官方文档和项目文档，用于安排 xcoze search 的后续接入，不是使用量榜单或检索质量评测。P1 四家已完成接口适配和离线测试，但没有使用其真实 Key 发起调用；P2/P3 候选仍未实现。文档或实现存在不等于账号已授权或结果质量已验证。

## 接入路线

- **结构化搜索 API**：返回标题、链接、片段和元数据，由调用 Agent 继续阅读和作答。
- **搜索与内容提取服务**：除了发现页面，也可以提取网页文本、Markdown 或相关摘录；每种内容须保留含义。
- **自建元搜索**：由用户维护实例、引擎配置与访问权限，不能套用“填一个 API Key 即可”的假设。

这些路线有交叉。REST 是本项目优先考虑的执行入口；供应商提供 MCP 或官方 Skill 可以作为生态支持信息，但不替代适配器和结果契约。

## 当前实现

| 服务 | 接入依据 | 当前状态 |
|---|---|---|
| DeepSeek Search / Fetch | [官方指南](https://api-docs.deepseek.com/guides/search/) | 已实现；2026-11-02 本版 Search / Fetch 回归通过 |
| 腾讯元宝 SearchPro | [服务 API KEY 方式](https://cloud.tencent.com/document/product/1806/130615) | 已实现；真实账号测试待完成 |
| Tavily Search / Extract | [Search](https://docs.tavily.com/documentation/api-reference/endpoint/search) / [Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract) | v0.3.0 已实现；未做真实账号测试 |
| Exa Search / Contents | [Search](https://exa.ai/docs/reference/search) / [Contents](https://exa.ai/docs/reference/get-contents) | v0.3.0 已实现；未做真实账号测试 |
| Brave Web Search | [官方参数](https://api-dashboard.search.brave.com/api-reference/web/search/get) | v0.3.0 已实现；未做真实账号测试 |
| 博查 Web Search | [官方 MCP 实现](https://github.com/BochaAI/bocha-search-mcp/blob/master/src/bocha_search_mcp/server.py) | v0.3.0 已实现；未做真实账号测试 |

## 扩展服务（P1 已实现，P2/P3 为候选）

表中的能力来自官方资料；优先级是项目判断，采用 API Key 的服务仍可能要求开通产品、购买额度或授予相应访问权限。

| 服务 | 官方入口与主要能力 | 配置与适配关注点 | 优先级 |
|---|---|---|---|
| Tavily | [Search](https://docs.tavily.com/documentation/api-reference/endpoint/search) / [Extract 说明](https://help.tavily.com/articles/3363168593-extracting-web-content-using-tavily)：网页检索与内容提取 | Bearer API Key；映射搜索深度、日期/域名条件；单独处理 raw content、答案与额外请求成本 | P1 |
| Exa | [Search API](https://exa.ai/docs/reference/search)：搜索和结果内容获取，支持 text / highlights 等字段 | API Key；区分正文、相关摘录和摘要，保留结果日期、warnings 及官方返回的成本 | P1 |
| Brave Search | [Web Search 文档](https://api-dashboard.search.brave.com/app/documentation/web-search/get-started)：网页结果、地区/语言、时效、额外片段 | `X-Subscription-Token`；摘要和额外片段不是全文，条数/分页限制与现有服务不同 | P1 |
| 博查 | [开放平台](https://open.bochaai.com/) / [官方 MCP 项目](https://github.com/BochaAI/bocha-search-mcp)：Web Search 与可选 AI Search 能力 | Web Search 使用 Bearer API Key；先映射网页结果与摘要，结构化卡片单独评估 | P1 |
| Perplexity | [Search API](https://docs.perplexity.ai/docs/search/quickstart)：结构化搜索、过滤条件和内容提取 | API Key；接原始搜索接口，与生成答案接口区分，保留 snippet 的实际语义 | P2 |
| Firecrawl | [Search](https://docs.firecrawl.dev/features/search)：搜索并可附加抓取 Markdown 等内容 | API Key；抓取需显式选择，区分发现页面与提取内容的成本和失败 | P2 |
| Parallel | [Search Quickstart](https://docs.parallel.ai/search/search-quickstart)：目标驱动的查询和相关摘录 | `x-api-key`；objective 与 search_queries 单独映射，保留 excerpts 和 warnings | P2 |
| Serper | [官方产品与结果示例](https://serper.dev/)：Google SERP 搜索服务，包括自然结果及其他类别 | API Key；实施前需在控制台核实最新鉴权/参数文档。它是第三方搜索服务，不能标成 Google 官方接口 | P2 |
| SerpApi | [Google Search API](https://serpapi.com/search-api)：结构化 SERP、地理条件和分页；另有 [Search Index](https://serpapi.com/search-index-api) | API Key；先处理 organic_results 与异步/业务状态；各 engine 的能力不同，鉴权信息不能进入日志 | P2 |
| Jina | [Search / Reader](https://jina.ai/reader/)：搜索结果与 URL 内容读取 | 核对 API Key 和对应限额；Reader 与搜索分开声明，不把所有访问方式都描述为免费 | P3 |
| SearXNG | [Search API](https://docs.searxng.org/dev/search_api.html)：自建元搜索的 HTTP 接口 | 用户实例 URL，鉴权依部署；JSON 输出要在实例配置中启用，许多公共实例未开放机器可读格式 | P3 |

## 选择优先级的理由

P1 覆盖现有两家之外的不同检索与内容处理接口，同时延续单服务凭据的配置习惯。P2 扩展内容抓取、目标式搜索和不同 SERP 返回结构。P3 涉及可选内容服务或用户维护的实例，需要额外的配置与运维约定。

这是基于接口能力与项目范围作出的安排，不表示某个服务更准确、更便宜或在特定网络中一定可用。接入前仍需核对当日官方契约、计费、内容使用条款和账号资格。

## 实施前补齐的信息

每个候选接入前均需核对：实际服务端点与鉴权、结果/内容语义、筛选条件、空结果和业务错误、限流与重试、费用/额度、数据处理条款、真实账号可用性。对需要登录控制台才能取得完整文档的服务，应记录材料缺口，不用社区示例替代最终接口依据。

已有供应商的协议参考保留在 [providers.md](providers.md)，开发顺序和验收条件见 [TODO](../TODO.md)。
