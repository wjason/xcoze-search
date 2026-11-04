# 搜索路线与竞品实现调研

**简体中文** | [English](search-services.en.md)

免费来源政策盘点更新：2026-11-05；下列竞品源码快照核对于 2026-11-03。资料来自项目代码和官方文档；没有将功能说明、星标或连通性测试作为检索质量排名。当前范围是联网搜索与读取，不包含自建实例、网页索引和企业资料搜索。

## 实现参考与取舍

| 项目 | 实现观察 | xcoze search 的取舍 |
|---|---|---|
| [Agent Reach](https://github.com/Panniantong/Agent-Reach/blob/main/agent_reach/channels/web.py) | 提醒优先使用宿主已有工具；通过 Exa MCP 搜索、Jina Reader 读取，并提供平台专用渠道 | 复用已有授权工具，不把浏览器和全部平台登录变成安装要求 |
| [DDGS](https://github.com/deedy5/ddgs/blob/main/ddgs/ddgs.py) | 多搜索后端、并发、去重和简单排序；部分后端解析公开 HTML | 参考公共搜索入口，本版自行实现少量标准库适配，不引入 DDGS 运行依赖或声称其所有后端已支持 |
| [open-webSearch](https://github.com/Aas-ee/open-webSearch) | CLI/MCP/本地服务共用核心；搜索可并发多个引擎，网页提取可选浏览器 | 基础包保持无浏览器依赖，限定来源数；未文档化的网站前端接口不作为稳定契约 |
| [OpenRouter](https://openrouter.ai/docs/guides/features/server-tools/web-search) | 在可用端点选择原生搜索或外部引擎 | 宿主工具由 Agent 调用，本地脚本不假定可调用所有宿主内部工具 |
| [LiteLLM](https://docs.litellm.ai/docs/search) | 多服务统一搜索接口、成本记录 | 统一入口已有同类；本项目以默认可用路径、简单配置和证据范围为重点 |
| [Tavily Skills](https://github.com/tavily-ai/skills) | Skill 配合 CLI，提供搜索和阅读工作流；部分操作有免认证限额 | 保留自带 Key API，暂不承诺与其 CLI 匿名额度或登录状态互通 |

代码核对快照：Agent Reach 7a38047acf26a729cbb27851e3cb81639da86b29；DDGS 8e74959141106702645020dcb853c6453b5e5195；open-webSearch fb11fd94df736819a0d2765bf7645224f98b2c6b。仅参考选路和公开契约，未运行其安装脚本或复制用户会话。

## 本版免 Key 支持

- Bing RSS、DuckDuckGo HTML 是实验性公开搜索路径，结构、访问和相关性可能变化；不宣称厂商提供正式搜索 API SLA。
- [Exa 官方 MCP](https://exa.ai/docs/get-started/exa-mcp) 明确提供搜索与读取的有限免 Key 入口；与带 Key Exa API 分开。
- [GitHub 公开搜索](https://docs.github.com/en/rest/search/search) 有匿名限额，代码搜索需要认证，本版不适配代码搜索。
- HN 帖子检索使用 [Algolia HN Search](https://hn.algolia.com/api)，单条帖子/评论使用 [HN 官方 API](https://github.com/HackerNews/API)。索引与官方单条数据可能存在时差。
- [Jina Reader](https://jina.ai/reader/) 访问目标网页、提取内容并输出适合模型的文本，既负责获取也负责转换。本版只接 Reader：已有正文时不重复调用；摘要不足或宿主读取失败时用作备用。Jina Search 与 Reader 认证和限额不同，Search 本版未接入。

免 Key、服务开源和不额外付费是不同概念。上述请求仍到外部服务，官方限额入口也属于商业服务；免费策略排除带 Key 适配器，不承诺所有计算免费。具体当次验证见 [验证记录](../VALIDATION.md)。

## 已有带 Key 服务

| 服务 | 官方契约 | 当前范围 |
|---|---|---|
| DeepSeek | [Search / Fetch](https://api-docs.deepseek.com/guides/search/) | 搜索、正文读取 |
| 元宝 | [SearchPro](https://cloud.tencent.com/document/product/1806/121811) | 网页搜索与摘要，权限随实际版本 |
| Tavily | [Search](https://docs.tavily.com/documentation/api-reference/endpoint/search)、[Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract) | 搜索、内容提取 |
| Exa | [Search](https://exa.ai/docs/reference/search)、[Contents](https://exa.ai/docs/reference/get-contents) | 搜索、正文/摘录/摘要 |
| Brave | [Web Search](https://api-dashboard.search.brave.com/api-reference/web/search/get) | 网页搜索 |
| 博查 | [开放平台](https://open.bochaai.com/) | Web Search |

## 后续候选

2026-11-05 扩展为 [165 条免费与公开来源图谱](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.md)，覆盖匿名 MCP、新闻、政策、科研、代码、社区、金融/地理数据及受限平台。Parallel、Microsoft Learn、MDN、searchcode、Cloudflare Docs 本轮返回相关内容；grep.app 本题无命中。GDELT/Semantic Scholar 429、Bluesky 403、dblp 非 JSON 均保留，不能将参考文档当验收。

Tavily/Exa/Firecrawl/Brave/OpenAlex 等免费额度与免 Key 区分；已有 free 仍排除带 Key 适配器。没有安装新 MCP 或改变默认选路。

Perplexity Search、Firecrawl、Parallel、Serper、SerpApi 和 Jina Search 仅按实际信息缺口安排，尚未接入。它们的免费体验、认证、数据契约和成本在实施时重新核对。平台专用动作也应逐项声明搜索、正文、评论和榜单覆盖，不用一个“支持平台”笼统代替。

新增公开平台索引与本机工具协作，见[开放来源](open-sources.md)。基础运行不增加依赖；原生接入、公开索引和需要专用工具的内容分别说明。
