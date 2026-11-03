# 官方接口与适配能力

**简体中文** | [English](providers.en.md)

## v0.4.0 免 Key 路径

| ID | 固定入口 | 能力和限制 |
|---|---|---|
| bing | https://www.bing.com/search?format=rss | 实验性 RSS 搜索，最多 10 条；site 操作符后再检查返回 URL 主机；不将 RSS 日期当作文章发布日期 |
| duckduckgo | https://html.duckduckgo.com/html/ | 实验性 HTML 搜索，最多 20 条；拒绝验证页与无法识别的页面 |
| exa-free | https://mcp.exa.ai/mcp | [官方免 Key 限额入口](https://exa.ai/docs/get-started/exa-mcp)，tools/call Search/Fetch，JSON/SSE；正文读取上限 24000 字符 |
| github | https://api.github.com/search/repositories | [公开仓库接口](https://docs.github.com/en/rest/search/search)，最多 20 条；不含代码搜索，默认 README 读取走固定 repos 接口 |
| hackernews | https://hn.algolia.com/api/v1/search | 帖子检索，支持起止日期；[官方单条接口](https://github.com/HackerNews/API)读帖子/评论，保留子评论 ID 而不自动遍历 |
| jina | https://r.jina.ai/ | [Reader](https://jina.ai/reader/)固定服务转取公开 URL；仅阅读、不搜索；最多返回 24000 字符并标明截断 |

所有免 Key 适配器不读取或发送其他凭据。它们仍向外部服务发送查询或 URL；公开页面、匿名额度与可用性没有 SLA。DNS 与页面访问由固定上游服务处理，脚本不直连任意用户目标地址。过滤不支持时拒绝或在自动计划中排除该来源，不能静默忽略条件。自动规则见 [调度](routing.md)。

以下是既有六家带 Key API 的具体契约。

核对日期：2026-11-02。下列为本工具开放的适配范围；账号权限、计费和服务端限制以官方文档为准。所有端点固定，鉴权请求不跟随重定向，不接受自定义代理 URL。

## 能力矩阵

| 服务 ID | Search | Fetch / Extract | 条数上限 | 本工具查询长度上限 | 站点条件 | 日期/相对时间 |
|---|---|---|---|---|---|---|
| `deepseek` | POST Search | POST Fetch | 50 | 128 Unicode 字符，含追加 site 条件 | 追加 site 操作符 | 时间操作符由调用者写进查询 |
| `yuanbao` | POST SearchPro | 不支持 | 50 | 1500 UTF-8 字节 | Site | d1..30 / m1..12 / y1..5 |
| `tavily` | POST Search | POST Extract | 20 | 本工具 4096 字符 | include_domains | day/week/month/year，或起止日期 |
| `exa` | POST Search | POST Contents | 本工具 50 | 本工具 4096 字符 | includeDomains | 起止发布日期 |
| `brave` | GET Web Search | 不支持 | 20 | 600 字符且 75 单词，含追加 site 条件 | 追加 site 操作符 | pd/pw/pm/py，或日期范围 |
| `bocha` | POST Web Search | 不支持 | 50 | 本工具 4096 字符 | 未开放 --site | oneDay/oneWeek/oneMonth/oneYear，或日期范围 |

Tavily、Exa、博查的 4096 字符是本工具校验策略，不表示平台承诺支持所有同长度查询。Exa 的公开 numResults 上限可高于本工具 50 条。本包不自动分页、追加搜索或为了补足条数提高请求次数。机器可读能力用 `capabilities` 获取。

## DeepSeek

- Search：`POST https://api.deepseek.com/v1/tools/search`。
- Fetch：`POST https://api.deepseek.com/v1/tools/fetch`。
- Bearer Key；[官方指南](https://api-docs.deepseek.com/guides/search/) / [Search 参考](https://api-docs.deepseek.com/api/search/)。

请求保留 query/count/need_content；Fetch 请求 url，返回 title/content。搜索正文为可选，summary 与 content 分开；保留 rerank_score 和 authority 原生刻度，不跨源比较。

## 腾讯元宝

- `POST https://api.wsa.cloud.tencent.com/SearchPro`，Bearer 元宝搜索服务 API Key。
- [服务 API KEY 方式](https://cloud.tencent.com/document/product/1806/130615)、[SearchPro 参数](https://cloud.tencent.com/document/product/1806/121811)、[官方 MCP 工具说明](https://developer.cloud.tencent.com/mcp/server/11764)、[版本差异](https://cloud.tencent.com/document/product/1806/121794)。

使用 Query、可选 Site/Freshness/Industry/Mode。count<=10 时不发送付费层可选 Cnt，超过 10 时按 20/30/40/50 向上取整发送整数，再本地截取。Response.Pages 支持 JSON 字符串和对象；HTTP 200 的 Error 仍是失败。passage 是标准摘要、content 是动态摘要，均不标为正文。资格、版本和额度相关参数可能被账号拒绝。

相对时间仅开放无歧义的 d/m/y 范围，不映射旧文档中有顺序矛盾的绝对日期例子。保留 RequestId、Version、Msg 和供应商字段；Msg 是不可信资料。元宝未配置真实 Key，线上验证因暂无测试凭据保留待办。

## Tavily

- `POST https://api.tavily.com/search` / `POST https://api.tavily.com/extract`，Bearer Key。
- [Search 官方契约](https://docs.tavily.com/documentation/api-reference/endpoint/search)、[Extract 官方契约](https://docs.tavily.com/documentation/api-reference/endpoint/extract)。

默认 general/basic、关闭 auto_parameters、include_answer 和 raw content，启用官方 usage 元数据。`--site` 映射 include_domains；`--freshness` 使用 day/week/month/year（兼容 d/w/m/y），与起止日期互斥。`--start-date` / `--end-date` 使用 YYYY-MM-DD；有时间条件时启用 filter_by_published_date，排除无可检测日期的结果。日期是服务商对发布或更新日期的估计，不补造日期。

Search 的 content 是片段，不是全文；`--need-content` 才请求 Markdown raw_content。`--depth` 可显式选择 advanced/fast/ultra-fast，`--include-answer` 显式请求生成答案；答案放在请求元数据 generated_answer 中，不冒充来源或事实核实。

Extract 每次只发送一个 URL，使用 basic、Markdown，检查 results 和 failed_results，即使 HTTP 200 也可能失败。保留平台返回的规范化 URL；它可能与输入 URL 有规范化差异。usage/request_id 原样保留。

## Exa

- `POST https://api.exa.ai/search` / `POST https://api.exa.ai/contents`，`x-api-key`。
- [Search 官方契约](https://exa.ai/docs/reference/search)、[Contents 官方契约](https://exa.ai/docs/reference/get-contents)。

默认 type:auto，只检索，不自动请求 contents。`--need-content`、`--highlights`、`--summary` 分别开启 text、highlights、summary；summary 使用对象形式，Search 以原查询作为摘要目标。`--site` 映射 includeDomains；日期映射 UTC 当天起止时间 startPublishedDate / endPublishedDate，保持 ISO 8601。

Contents 每次只发送一个 URL，显式提取 text，可选 highlights/summary。URL 最多 2048 字符。检查逐 URL statuses；有失败或无法取得唯一有效页面时返回 extraction_failed，不能只凭 HTTP 200 判成功。text、highlights、summary 分别输出，保留 costDollars、warnings、requestId 和未知元数据。若平台明确报告 IGNORED_FIELD，返回约束未生效错误，避免把未应用的筛选当作成功。

## Brave Search

- `GET https://api.search.brave.com/res/v1/web/search`，`X-Subscription-Token`，Key 不进入 URL。
- [官方介绍](https://api-dashboard.search.brave.com/app/documentation/web-search/query)、[完整参数和返回结构](https://api-dashboard.search.brave.com/api-reference/web/search/get)。

q/count/result_filter:web；`--country` 映射两字母国家码，`--language` 映射 search_lang，具体允许值以官方枚举为准。freshness 支持 pd/pw/pm/py 或 YYYY-MM-DDtoYYYY-MM-DD；`--extra-snippets` 显式开启额外片段。

只转换 web.results，不把广告、新闻卡片、位置卡等合成网页正文；其他顶层元数据保留。description 和 extra_snippets 是摘要/片段。page_age 可能是发布或修改时间，age 仅保留在原始字段，不自动换算发布日期。官方 Web Search 与 LLM Context 是不同接口，本次只实现前者。

## 博查

- `POST https://api.bochaai.com/v1/web-search`，Bearer Key。
- [官方开放平台及返回示例](https://open.bochaai.com/)、[官方 MCP 接口实现](https://github.com/BochaAI/bocha-search-mcp/blob/master/src/bocha_search_mcp/server.py)。

请求 query/count/freshness，默认 summary:false；`--summary` 才开启摘要。freshness 支持 noLimit、oneDay、oneWeek、oneMonth、oneYear、YYYY-MM-DD 或 YYYY-MM-DD..YYYY-MM-DD。不添加官方 MCP 示例中的渠道追踪参数。

转换 data.webPages.value，name/url/snippet/summary/siteName/datePublished 分别保留；摘要不是全文。HTTP 200 内的非成功 code 仍为业务失败；不回显原始错误消息。不调用 AI Search 或结构化模态卡，也不承诺实时股价能力。

## 用量、成本和数据流

搜索、正文请求直接发往用户指定服务。各服务独立开通/计费；多源、重试、高级深度、正文和生成内容可能增加费用。预算只约束实际 HTTP 次数，不代表金额上限。只保留官方返回的用量和费用，未返回为 null；不根据当前价格估造费用。

本轮四家新增服务未做真实账号调用；协议和离线验证记录不能替代账号权限、余额、可达性、检索质量或现场验收。

新增公开平台索引与本机工具协作，见[开放来源](open-sources.md)。基础运行不增加依赖；原生接入、公开索引和需要专用工具的内容分别说明。
