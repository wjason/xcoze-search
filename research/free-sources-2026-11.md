# 免费与公开来源图谱（2026-11）

**简体中文** | [English](free-sources-2026-11.en.md)

核对日期：2026-11-05，北京时间；项目基线 v0.9.0。共 **165 个条目**，包含来源族、服务、数据接口、公开网页候选和排除项。它们不是 165 个独立搜索引擎，也不是 165 个已实现或保证可用的免费 API。尚未逐项完成原生检索、质量、用途许可与跨网络验收。本次只补调研资料，不自动安装 MCP、不申请账号、不修改现有选路。

[CSV 清单](free-sources-2026-11.csv) · [结构化清单](free-sources-2026-11.data.json) · [本轮真实探测](free-sources-2026-11.probes.json)

## 怎么看“免费”

| 标记 | 含义 | 条目数 |
|---|---|---:|
| A | 免 Key 的公开 API/RSS/MCP 或读取子集候选；仍有配额、访问和内容许可边界，不代表全部验收 | 79 |
| W | 公开网页、实验前端或历史 feed；自动化接口与更新鲜度未全部确认 | 35 |
| Q | 需注册/Key/标识、免费额度，或有用途条件；不可概括为免 Key | 40 |
| T | 一次性体验额度，不按月度免费额度计算 | 2 |
| R | 付费、审批或用途受限，不能作为无条件免费渠道 | 6 |
| S | 软件/自建工具，不是免费托管来源；当前自建路线仍移出范围 | 3 |

“已接部分”只说明仓库 v0.9.0 存在对应适配，不表示表中该平台的所有动作已接入。`candidate_reference` 只是官方或项目参考入口，可能未完成本次文档细读/接口验证；实际探测另有明确结果。API 免费不等于文章全文可任意再发布；按需检索/引用与建内容镜像不同。

对 165 条参考入口各做一次匿名访问检查：136 个返回 2xx、8 个重定向、17 个 HTTP 错误、4 个网络失败。检查的是参考页面响应，不能代替关键词搜索、权限、额度、许可或实际接入验收。逐项状态见 [检查记录](source-reference-audit-2026-11-05.json)和 CSV。

## 最值得优先补的缺口

1. **Parallel 匿名 MCP**：补通用搜索/阅读；官方旧文档标为 legacy，本轮匿名查询仍成功，需关注迁移及匿名限额。不要把付费 REST API 与免 Key 入口等同。
2. **Microsoft Learn、MDN**：补官方技术资料；本轮免 Key 返回相关内容。Cloudflare Docs 同样成功，但本题整体约 7.9 秒，宜按任务调用，不能当低延迟万能备用。
3. **searchcode**：指定 GitHub 仓库内代码搜索；公测免 Key，本轮成功。不是全网代码索引。grep.app 协议成功但本题无命中，先做第二阶段验收。
4. **国家发改委、能源局、统计局**：中文政策/统计原文比再加一个聚合热榜更有价值；公开栏目可读，仍需专用解析、日期/解读区分和变更检测。
5. **DEV.to、DataCite、Open Library、Zenodo**：本轮匿名接口返回有效结构；HAL、Figshare 也成功。适合做主题定向补充，不向所有查询广播。
6. **GDELT、Semantic Scholar、Bluesky、dblp**：都有接入价值，但本次分别为 429、429、403、非 JSON；保留验证待办，当前不应宣传开箱可用。

## 免费套餐的最新变化

- [Tavily](https://www.tavily.com/pricing)：1000 credits/月，需 Key、无需信用卡；credits 不是固定搜索次数。
- [Exa API](https://exa.ai/pricing)：$10 credits/月和 $10 开户奖励，需 Key；与已接匿名 MCP 分开。
- [Firecrawl](https://www.firecrawl.dev/pricing)：1000 credits/月，页面标约 500 次搜索或 1000 页提取。不是旧资料中常见的“500 次一次性试用”。
- [Brave](https://api-dashboard.search.brave.com/documentation/resources/help-feedback)：不是独立免费套餐；各计划每月 $5 credits，需 Key 和信用卡，即使预充值设 $0 也需卡验证。
- [SerpApi](https://serpapi.com/pricing)：免费 250 次/月；[Serper](https://serper.dev/)的 2500 次属于体验，不应写成每月额度；[Search1API](https://s1.dev/docs/essentials/credits-and-limits)开户 100 credits 同理。
- [OpenAlex](https://help.openalex.org/access/pricing/)：当前 API 需要 Key，免费预算 $1/日，无需付款方式；旧“完全免 Key”的资料已不适用。
- [NewsAPI](https://newsapi.org/pricing)免费开发版文章延迟 24 小时；[GNews](https://gnews.io/pricing)、[NewsData.io](https://newsdata.io/pricing)免费档存在 12 小时延迟及用途/内容限制，不能列为实时新闻主路。

现有 `free` 仍排除所有带 Key 适配器，包括有赠送额度的账号。本调研没有新增“免费额度模式”，也没有自动启用充值或替用户注册。若将来做额度专用策略，需要显式配置、余额/硬限额与用完停止，不能默认余额免费。

补充 15 个匿名接口实测：14 个返回非空预期结构，US BLS 返回 403。包括 Wikidata、Packagist、RubyGems、Maven、NuGet、世界银行、USGS、Federal Register、PyPI、bioRxiv、ClinicalTrials.gov、ROR、Openverse 和 Nominatim。每项只测一个样例，不代表已接入或完整验收。[逐项结果](source-functional-samples-2026-11-05.json)。

## 本轮真实探测

六个 MCP 均完成匿名初始化与工具目录读取。随后各执行一道真实查询，表中总耗时包括重新建立协议连接的三个客户端 HTTP 操作，不与现有单请求 API 直接评出速度排名。

| 来源 | 单题结果 | 含握手总耗时 | 证据边界 |
|---|---|---:|---|
| Parallel | 找到 Python TaskGroup 官方文档 | 1.614 秒 | 多版本混合，仍需按问题核对版本 |
| Microsoft Learn | Azure Functions 官方资料 | 1.580 秒 | 限微软文档，不是通用网页索引 |
| MDN | AbortController 文档路径/说明 | 3.467 秒 | 文档检索，不表示已查完兼容表 |
| searchcode | Express 仓库内 Router 代码命中 | 2.762 秒 | 指定仓库，不等于全局代码搜索 |
| Cloudflare Docs | Workers KV 过期设置资料 | 7.924 秒 | 有较长尾延迟，不能保证低时延 |
| grep.app | 正常返回“无结果” | 1.832 秒 | 仅协议路径通过，本题检索未通过 |

10 个直接公开 API 检查中，DataCite、Open Library、DEV.to、HAL、Zenodo、Figshare 返回 JSON 数据；GDELT/Semantic Scholar 429，Bluesky 403，dblp 内容未能按 JSON 解析。未反复请求受限源，未变换身份或清除冷却。初始化/目录/查询与直接探测合计 46 次客户端顶层 HTTP 操作；内部重定向、文档查阅未计量。没有发送用户 Key，没有发布响应全文、Cookie 或会话标识。

## 完整来源清单

### 通用网页搜索与阅读

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S001 | [Parallel Search MCP](https://parallel.ai/mcp) | A | 搜索与网页读取，匿名有限额；独立于带 Key API | 本轮有真实返回 | P0 |
| S002 | [Exa hosted MCP](https://exa.ai/docs/get-started/exa-mcp) | A | 已接入；匿名限额与 API 套餐分开 | 候选参考，未全面验收；已接部分 | existing |
| S003 | [Bing RSS](https://www.bing.com/search?format=rss&q=python) | W | 已接实验路径，相关性/结构可变，不是正式免费 API 契约 | 候选参考，未全面验收；已接部分 | existing |
| S004 | [DuckDuckGo HTML](https://html.duckduckgo.com/html/) | W | 已接实验路径，验证页会阻断 | 候选参考，未全面验收；已接部分 | existing |
| S005 | [DuckDuckGo Instant Answer](https://duckduckgo.com/api) | A | 知识卡/即时答案，不是完整网页 SERP | 候选参考，未全面验收 | backlog |
| S006 | [360 / Baidu / Sogou public search pages](https://www.so.com/) | W | 360 浏览器兜底已接；其他引擎待验证，免费网页不等于 API | 候选参考，未全面验收；已接部分 | existing |
| S007 | [Google / Bing / Brave / Mojeek public UI](https://www.google.com/) | W | 可选浏览器路径；验证码、地区与索引不同，不承诺匿名自动化 | 候选参考，未全面验收 | backlog |
| S008 | [Tavily API](https://www.tavily.com/pricing) | Q | 1000 credits/月，需 Key，无需信用卡；已接带 Key 适配 | 候选参考，未全面验收；已接部分 | existing |
| S009 | [Exa API](https://exa.ai/pricing) | Q | 每月 $10 credits 加 $10 开户奖励，需 Key；不等于匿名 MCP | 候选参考，未全面验收；已接部分 | existing |
| S010 | [Brave Search API](https://api-dashboard.search.brave.com/documentation/resources/help-feedback) | Q | 每月 $5 credits；需 Key 和信用卡；不是独立免费套餐 | 候选参考，未全面验收；已接部分 | existing |
| S011 | [Firecrawl](https://www.firecrawl.dev/pricing) | Q | 1000 credits/月，约500次搜索或1000页抓取，需 Key | 候选参考，未全面验收 | backlog |
| S012 | [Serper](https://serper.dev/) | T | 2500 次免费体验，不能当作每月重置额度；第三方 Google SERP | 候选参考，未全面验收 | backlog |
| S013 | [SerpApi](https://serpapi.com/pricing) | Q | 250 次/月免费搜索，需 Key；第三方搜索结果服务 | 候选参考，未全面验收 | backlog |
| S014 | [Search1API](https://s1.dev/docs/essentials/credits-and-limits) | T | 新账号100 credits，非月度额度，需 Key | 候选参考，未全面验收 | backlog |
| S015 | [Jina Reader / Search](https://jina.ai/reader/) | Q | Reader 已接匿名备用，本机见401；Search/高额度需单独核对鉴权 | 候选参考，未全面验收；已接部分 | existing |

### 官方技术文档

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S016 | [Microsoft Learn MCP](https://learn.microsoft.com/en-us/training/support/mcp) | A | 微软/Azure/.NET 官方文档与代码样例，非全网搜索 | 本轮有真实返回 | P0 |
| S017 | [MDN MCP](https://developer.mozilla.org/en-US/mcp) | A | HTML/CSS/JS/Web API 文档与兼容数据 | 本轮有真实返回 | P0 |
| S018 | [Cloudflare Docs MCP](https://developers.cloudflare.com/workers/get-started/prompting/) | A | Workers/KV/R2 等官方文档；本题耗时尾部偏长 | 本轮有真实返回 | P1 |
| S019 | [OpenAI Docs MCP](https://developers.openai.com/resources/docs-mcp) | A | OpenAI 官方文档；本轮仅发现文档，未联调 | 候选参考，未全面验收 | backlog |
| S020 | [Context7](https://github.com/upstash/context7) | Q | 文档称 Key 推荐用于更高限额；匿名范围与当前套餐需联调 | 候选参考，未全面验收 | backlog |
| S021 | [Python official docs / Sphinx inventories](https://docs.python.org/3/) | W | 文档页/索引文件可读，不是统一搜索 API | 候选参考，未全面验收 | backlog |
| S022 | [Rust std / docs.rs](https://docs.rs/) | W | 标准库与 crate 文档，版本需区分 | 候选参考，未全面验收 | backlog |
| S023 | [Read the Docs / llms.txt publisher docs](https://docs.readthedocs.com/platform/stable/reference/sitemaps.html) | W | 站点地图/文档索引辅助定位，不保证全文或实时 | 候选参考，未全面验收 | backlog |

### 新闻与订阅

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S024 | [China News Service RSS](https://www.chinanews.com.cn/rss/) | A | 即时/财经已接；还可扩国际、时政、科技等栏目 | 候选参考，未全面验收；已接部分 | existing |
| S025 | [BBC RSS](https://www.bbc.co.uk/news/10628494) | A | World 已接；可扩其他新闻栏目 | 候选参考，未全面验收；已接部分 | existing |
| S026 | [CCTV / CGTN RSS](https://english.cctv.cn/rss/) | W | 官方 RSS 页面存在，历史地址须验证更新鲜度 | 历史官方目录，鲜度待核验 | backlog |
| S027 | [Xinhua RSS](https://www.xinhuanet.com/english/rss/index.htm) | W | 历史官方订阅入口；更新情况/使用范围待验证 | 历史官方目录，鲜度待核验 | backlog |
| S028 | [DW RSS](https://rss.dw.com/rdf/rss-en-all) | A | 国际新闻订阅；摘要与正文分开 | 候选参考，未全面验收 | backlog |
| S029 | [UN News RSS](https://news.un.org/en/rss-feeds) | A | 联合国新闻、多语言，有限订阅窗口 | 候选参考，未全面验收 | backlog |
| S030 | [NASA news feeds](https://www.nasa.gov/rss-feeds/) | A | 航天/科研官方新闻，不是全文通用搜索 | 候选参考，未全面验收 | backlog |
| S031 | [GDELT DOC / Context](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) | A | 多语言新闻检索；本次429，不能直接宣称当前可用 | 本轮受限/响应未解析 | P1-validation |
| S032 | [Google News RSS](https://news.google.com/) | W | 实验性新闻索引候选，不称正式免费 News API | 候选参考，未全面验收 | backlog |
| S033 | [Guardian Open Platform](https://open-platform.theguardian.com/access/) | Q | 免费开发 Key 限非商业；商业/数据挖掘用途另议 | 候选参考，未全面验收 | backlog |
| S034 | [NewsAPI.org](https://newsapi.org/pricing) | Q | 100次/日，开发测试，文章延迟24小时；不宜免费实时主路 | 候选参考，未全面验收 | backlog |
| S035 | [GNews](https://gnews.io/pricing) | Q | 100次/日，非商业，12小时延迟、正文截断 | 候选参考，未全面验收 | backlog |
| S036 | [NewsData.io](https://newsdata.io/pricing) | Q | 200 credits/日，测试/个人，新闻延迟12小时 | 候选参考，未全面验收 | backlog |
| S037 | [TheNewsAPI](https://www.thenewsapi.com/pricing) | Q | 100次/日，每次3篇；生产用途需继续核对许可 | 候选参考，未全面验收 | backlog |

### 中文政务、公告与公共数据

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S038 | [China gov.cn latest-policy index](https://www.gov.cn/zhengce/zuixin/) | A | 已接有限 JSON 列表，包含文件/解读，不是全国全集 | 候选参考，未全面验收；已接部分 | existing |
| S039 | [NDRC notices / announcements](https://www.ndrc.gov.cn/xxgk/zcfb/tz/) | W | 公开文件原文与日期；需专用解析，不承诺稳定 API | 候选参考，未全面验收 | P0 |
| S040 | [National Energy Administration](https://www.nea.gov.cn/) | W | 能源政策、公告、统计与发布会 | 候选参考，未全面验收 | P0 |
| S041 | [National Bureau of Statistics releases](https://www.stats.gov.cn/sj/zxfb/) | W | PMI/CPI/GDP 等发布原文 | 候选参考，未全面验收 | P0 |
| S042 | [National Data / NBS database](https://data.stats.gov.cn/) | W | 统计数据门户；新前端，不能把旧接口当稳定契约 | 候选参考，未全面验收 | backlog |
| S043 | [MIIT](https://www.miit.gov.cn/) | W | 产业、软件、装备、通信公告原文 | 候选参考，未全面验收 | P1 |
| S044 | [Ministry of Commerce](https://www.mofcom.gov.cn/) | W | 贸易、出口、产业政策；公开栏目按需读取 | 候选参考，未全面验收 | backlog |
| S045 | [Ministry of Ecology and Environment](https://www.mee.gov.cn/) | W | 环保、碳市场、环境标准与公告 | 候选参考，未全面验收 | backlog |
| S046 | [People's Bank of China](https://www.pbc.gov.cn/) | W | 货币政策、金融统计等官方发布 | 候选参考，未全面验收 | backlog |
| S047 | [CSRC](https://www.csrc.gov.cn/) | W | 证券监管规则、公告和政策 | 候选参考，未全面验收 | backlog |
| S048 | [SAMR standards disclosure](https://openstd.samr.gov.cn/) | W | 公开标准目录/可公开全文；不承诺所有标准免费或可批量下载 | 候选参考，未全面验收 | backlog |
| S049 | [National law database](https://flk.npc.gov.cn/) | W | 法律原文入口；本轮浏览工具403，无开放 API 承诺 | 候选参考，未全面验收 | backlog |
| S050 | [China Government Procurement](https://www.ccgp.gov.cn/) | W | 招标、中标、采购公告；搜索访问控制待适配 | 候选参考，未全面验收 | backlog |
| S051 | [National public resource trading platform](https://www.ggzy.gov.cn/) | W | 工程、土地、产权等交易公告 | 候选参考，未全面验收 | backlog |
| S052 | [CNInfo public disclosures](https://www.cninfo.com.cn/new/index) | W | 公告网页/PDF公开；官方数据 API 另有鉴权/套餐 | 候选参考，未全面验收 | P1-validation |
| S053 | [SSE / SZSE / BSE disclosures](https://www.sse.com.cn/disclosure/listedinfo/announcement/) | W | 交易所原始公告，不把授权数据服务称免费 API | 候选参考，未全面验收 | backlog |
| S054 | [DATA.GOV.HK](https://data.gov.hk/en/help/api-spec) | A | 公开数据集目录/API；具体数据集授权单独核对 | 候选参考，未全面验收 | backlog |
| S055 | [Beijing / Shanghai / Shenzhen open-data portals](https://data.sh.gov.cn/) | W | 目录可查，部分 API 需注册；不能概括全免 Key | 候选参考，未全面验收 | backlog |
| S056 | [data.gov.tw](https://data.gov.tw/) | W | 开放数据目录，逐数据集区分访问和授权 | 候选参考，未全面验收 | backlog |

### 国际政务与统计

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S057 | [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1) | A | 美国联邦规则/公告检索；法定原件另核对 govinfo | 候选参考，未全面验收；匿名样例成功 | backlog |
| S058 | [SEC EDGAR public data](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | A | 公司申报/XBRL免 Key；提交历史不等于全站全文检索 | 候选参考，未全面验收 | P1 |
| S059 | [GOV.UK content/search](https://docs.publishing.service.gov.uk/apis.html) | A | 英国政府公开内容/API，区分搜索与单页内容 | 候选参考，未全面验收 | backlog |
| S060 | [UK legislation](https://www.legislation.gov.uk/developer) | A | 法律数据/格式访问，非法律结论验证 | 候选参考，未全面验收 | backlog |
| S061 | [Eurostat](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access) | A | 欧洲统计 API，指标有发布滞后 | 候选参考，未全面验收 | backlog |
| S062 | [World Bank Indicators](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation) | A | 宏观/经济指标，非实时行情 | 候选参考，未全面验收；匿名样例成功 | backlog |
| S063 | [OECD SDMX](https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html) | A | 经济统计，限频/数据集范围待联调 | 候选参考，未全面验收 | backlog |
| S064 | [api.data.gov / govinfo / Congress APIs](https://api.data.gov/) | Q | 很多联邦服务用免费 Key；不是所有 data.gov 数据同一鉴权 | 候选参考，未全面验收 | backlog |

### 论文、图书与科研

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S065 | [arXiv](https://info.arxiv.org/help/api/index.html) | A | 已接论文元数据/摘要；PDF按需另读 | 候选参考，未全面验收；已接部分 | existing |
| S066 | [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | A | 已接 DOI/出版信息，不保证有正文 | 候选参考，未全面验收；已接部分 | existing |
| S067 | [DataCite](https://support.datacite.org/docs/api) | A | 数据/论文 DOI 元数据；本轮匿名请求成功 | 本轮有真实返回 | P1 |
| S068 | [dblp](https://dblp.org/faq/How+to+use+the+dblp+search+API.html) | A | 计算机论文；本轮响应未能按 JSON 解析，需再核验 | 本轮受限/响应未解析 | backlog |
| S069 | [Europe PMC](https://europepmc.org/RestfulWebService) | A | 已接生物医学摘要/元数据；不等于临床结论 | 候选参考，未全面验收；已接部分 | existing |
| S070 | [NCBI PubMed / PMC E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | A | 元数据与开放全文子集；可选 Key 提升限额 | 候选参考，未全面验收 | backlog |
| S071 | [HAL](https://api.archives-ouvertes.fr/docs) | A | 开放科研记录；本轮匿名请求成功 | 本轮有真实返回 | P2 |
| S072 | [OpenAIRE](https://graph.openaire.eu/develop/api.html) | Q | 开放科研图谱；当前端点注册/鉴权政策未核定，不列为已确认免 Key | 候选参考，未全面验收 | backlog |
| S073 | [Zenodo public records](https://developers.zenodo.org/) | A | 公开 records 搜索本轮免 Key 成功；上传/私有接口需授权 | 本轮有真实返回 | P1 |
| S074 | [Figshare public articles](https://docs.figshare.com/) | A | 公开科研记录本轮免 Key 成功；受限文件另行授权 | 本轮有真实返回 | P2 |
| S075 | [bioRxiv / medRxiv](https://api.biorxiv.org/) | A | 按日期/DOI/类别获取预印本；不等于通用关键词搜索 | 候选参考，未全面验收；匿名样例成功 | backlog |
| S076 | [ClinicalTrials.gov](https://clinicaltrials.gov/data-api/api) | A | 试验注册资料，不证明疗效 | 候选参考，未全面验收；匿名样例成功 | backlog |
| S077 | [OpenReview public notes](https://docs.openreview.net/) | A | 公开论文/评审，权限按 venue/记录区分 | 候选参考，未全面验收 | backlog |
| S078 | [Open Library](https://openlibrary.org/developers/api) | A | 图书元数据查询本轮成功；不等于免费借阅/下载整书 | 本轮有真实返回 | P1 |
| S079 | [Internet Archive search](https://archive.org/developers/) | A | 馆藏/元数据与部分全文，受限资源不可等同开放 | 候选参考，未全面验收 | backlog |
| S080 | [Library of Congress](https://www.loc.gov/apis/) | A | 公开馆藏 JSON/检索接口，权限逐资源判断 | 候选参考，未全面验收 | backlog |
| S081 | [Wikisource](https://www.mediawiki.org/wiki/API:Main_page) | A | 开放文献库，复用 MediaWiki 访问规范 | 候选参考，未全面验收 | backlog |
| S082 | [OpenAlex](https://help.openalex.org/access/pricing/) | Q | 当前 API 要 Key；免费 $1/日，无需付款方式，非免 Key | 候选参考，未全面验收 | P2-opt-in-key |
| S083 | [Semantic Scholar](https://www.semanticscholar.org/product/api) | Q | 可申请免费 Key；匿名池本轮429，不作为可靠默认源 | 本轮受限/响应未解析 | P2-opt-in-key |
| S084 | [CORE](https://core.ac.uk/services/api) | Q | 开放研究聚合，免费范围/Key/限额需实施时核对 | 候选参考，未全面验收 | backlog |
| S085 | [Unpaywall](https://unpaywall.org/products/api) | Q | 找 DOI 的开放获取链接，需邮箱标识；不是通用论文搜索 | 候选参考，未全面验收 | backlog |
| S086 | [Google Books API](https://developers.google.com/books/docs/v1/using) | Q | 图书元数据/有限预览，Key/配额与正文权限分开 | 候选参考，未全面验收 | backlog |
| S087 | [Europeana](https://pro.europeana.eu/page/apis) | Q | 文化馆藏，开发 Key 与资源授权各自核对 | 候选参考，未全面验收 | backlog |
| S148 | [DOAJ](https://doaj.org/api/docs) | A | 开放期刊/文章元数据；不是所有文章正文下载接口 | 候选参考，未全面验收 | backlog |
| S149 | [NASA ADS](https://ui.adsabs.harvard.edu/help/api/) | Q | 天文物理论文检索需免费 token；具体限额待验收 | 候选参考，未全面验收 | backlog |
| S150 | [BASE](https://www.base-search.net/about/en/about_develop.php) | Q | 科研聚合检索，API 接入/使用条件须申请核定 | 候选参考，未全面验收 | backlog |

### 代码、软件包与模型

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S088 | [GitHub REST public repositories](https://docs.github.com/en/rest/search/search) | A | 已接仓库/README；匿名受限，代码搜索需要认证 | 候选参考，未全面验收；已接部分 | existing |
| S089 | [GitLab public projects](https://docs.gitlab.com/api/projects/) | A | 已接公开项目；不是匿名全局代码搜索 | 候选参考，未全面验收；已接部分 | existing |
| S090 | [Codeberg / Forgejo](https://codeberg.org/api/swagger) | A | 公开项目 API；实例限额和索引范围要验证 | 候选参考，未全面验收 | backlog |
| S091 | [Gitee API](https://gitee.com/api/v5/swagger) | Q | 国内开源项目，可读范围/令牌与限频逐端点核对 | 候选参考，未全面验收 | backlog |
| S092 | [npm registry](https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md) | A | 已接包搜索和元数据，不是质量/安全结论 | 候选参考，未全面验收；已接部分 | existing |
| S093 | [PyPI JSON / Simple](https://docs.pypi.org/api/) | A | 包名/版本/依赖元数据；不是全站关键词搜索 API | 候选参考，未全面验收；匿名样例成功 | P1 |
| S094 | [crates.io](https://crates.io/data-access) | A | 已接 Rust 包检索，版本/稳定版要区分 | 候选参考，未全面验收；已接部分 | existing |
| S095 | [Maven Central](https://central.sonatype.org/search/rest-api-guide/) | A | Java 构件元数据搜索 | 候选参考，未全面验收；匿名样例成功 | P1 |
| S096 | [NuGet](https://learn.microsoft.com/en-us/nuget/api/search-query-service-resource) | A | .NET 包搜索/元数据 | 候选参考，未全面验收；匿名样例成功 | P2 |
| S097 | [Packagist](https://packagist.org/apidoc) | A | PHP 包搜索/元数据，多数读取免认证 | 候选参考，未全面验收；匿名样例成功 | backlog |
| S098 | [RubyGems](https://guides.rubygems.org/rubygems-org-api/) | A | Ruby 包搜索/元数据，写操作需 Key | 候选参考，未全面验收；匿名样例成功 | backlog |
| S099 | [Go module proxy](https://go.dev/ref/mod#module-proxy) | A | 按模块路径查版本；不是全站关键词搜索 | 候选参考，未全面验收 | backlog |
| S100 | [Hugging Face Hub](https://huggingface.co/docs/hub/api) | A | 模型已接，可扩数据集/Space；受限内容需授权 | 候选参考，未全面验收；已接部分 | existing |
| S101 | [Docker Hub](https://docs.docker.com/reference/api/hub/latest/) | Q | 公开镜像元数据，拉取/搜索配额及认证另核对 | 候选参考，未全面验收 | backlog |
| S102 | [searchcode MCP](https://searchcode.com/) | A | 公测免费免 Key；指定仓库内代码检索，不是全网代码索引 | 本轮有真实返回 | P0 |
| S103 | [grep.app MCP](https://vercel.com/blog/grep-a-million-github-repositories-via-mcp) | A | 公开跨仓库代码检索；本题无命中，不能称质量通过 | 协议通过，本题无命中 | P1-validation |
| S104 | [Libraries.io](https://libraries.io/api) | Q | 依赖/包索引；Key、免费范围与数据许可待核验 | 候选参考，未全面验收 | backlog |

### 社区与社交公开接口

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S105 | [Hacker News / Algolia](https://hn.algolia.com/api) | A | 已接帖子检索；官方单条与评论树分开 | 候选参考，未全面验收；已接部分 | existing |
| S106 | [Stack Exchange family](https://api.stackexchange.com/docs) | A | 已接问题，可扩回答/评论；保留署名许可 | 候选参考，未全面验收；已接部分 | existing |
| S107 | [Discourse public communities](https://docs.discourse.org/) | A | Python/Rust 主帖已接；各站可关闭公开 API | 候选参考，未全面验收；已接部分 | existing |
| S108 | [V2EX public API](https://www.v2ex.com/p/7v9TEc53) | A | 热点/主帖已实现；本机403，不能宣称当前可用 | 候选参考，未全面验收；已接部分 | existing |
| S109 | [DEV.to / Forem](https://developers.forem.com/api) | A | 公开技术文章，列表本轮免 Key 成功 | 本轮有真实返回 | P1 |
| S110 | [Lobsters](https://lobste.rs/) | A | 技术链接社区 RSS/JSON 候选，未联调 | 候选参考，未全面验收 | backlog |
| S111 | [Lemmy public instances](https://join-lemmy.org/api/) | A | 公开帖子/评论，依赖实例开放策略，不默认任意公共实例 | 候选参考，未全面验收 | backlog |
| S112 | [Mastodon](https://docs.joinmastodon.org/methods/search/) | Q | 全文搜索常需 token/索引支持，不能称全联邦搜索 | 候选参考，未全面验收 | backlog |
| S113 | [Bluesky public AppView](https://docs.bsky.app/docs/advanced-guides/api-directory) | A | 公开社交流；本轮搜索403，需继续验证 | 本轮受限/响应未解析 | P2-validation |
| S114 | [Cnblogs RSS](https://www.cnblogs.com/) | W | 个人/社区技术订阅候选，逐 feed 验证 | 候选参考，未全面验收 | backlog |

### 百科、实体与素材

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S115 | [Wikipedia](https://www.mediawiki.org/wiki/API:Search) | A | 已接中英文条目；编辑日期非发布日期 | 候选参考，未全面验收；已接部分 | existing |
| S116 | [Wikidata](https://www.wikidata.org/wiki/Wikidata:Data_access) | A | 实体/关系/标识符，SPARQL有限流，不是新闻搜索 | 候选参考，未全面验收；匿名样例成功 | P1 |
| S117 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/Commons:API) | A | 图片/音视频元数据；逐项署名许可 | 候选参考，未全面验收 | backlog |
| S118 | [Openverse](https://docs.openverse.org/api/) | A | 开放许可图片/音频；匿名与认证限额不同 | 候选参考，未全面验收；匿名样例成功 | P2 |
| S119 | [GBIF](https://www.gbif.org/developer/summary) | A | 物种/生物多样性，下载任务与读取权限不同 | 候选参考，未全面验收 | backlog |
| S120 | [iNaturalist](https://api.inaturalist.org/v1/docs/) | A | 物种观察记录，逐数据/图片许可 | 候选参考，未全面验收 | backlog |
| S121 | [ROR](https://ror.readme.io/docs/rest-api) | A | 机构标识/名称消歧；不是文章搜索 | 候选参考，未全面验收；匿名样例成功 | backlog |
| S122 | [ORCID public API](https://info.orcid.org/documentation/integration-guide/orcid-api-2/) | Q | 研究者身份信息；公开 API 凭据/使用范围要核对 | 候选参考，未全面验收 | backlog |

### 历史网页与档案

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S123 | [Common Crawl URL Index](https://index.commoncrawl.org/) | A | 抓取快照 URL 索引，不是实时全文搜索；自建全文索引仍不做 | 候选参考，未全面验收 | backlog |
| S124 | [Wayback / CDX](https://archive.org/developers/wayback-cdx-server.html) | A | 历史 URL/快照，不能替代当前网页原文 | 候选参考，未全面验收 | backlog |
| S125 | [Arquivo.pt](https://arquivo.pt/api) | A | 历史网页全文/URL检索，非实时网络 | 候选参考，未全面验收 | backlog |

### 天气、地理、能源与事件

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S126 | [USGS earthquake feeds/API](https://earthquake.usgs.gov/fdsnws/event/1/) | A | 事件与地震资料，已提供标准公开接口 | 候选参考，未全面验收；匿名样例成功 | backlog |
| S127 | [NOAA NCEI data service](https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation) | A | 特定气象历史数据无需统一通用搜索 | 候选参考，未全面验收 | backlog |
| S128 | [weather.gov API](https://www.weather.gov/documentation/services-web-api) | A | 美国天气预报/告警，User-Agent与限频要求 | 候选参考，未全面验收 | backlog |
| S129 | [EIA Open Data](https://www.eia.gov/opendata/) | Q | 能源、电力、油气数据，免费 Key | 候选参考，未全面验收 | backlog |
| S130 | [ENTSO-E Transparency](https://transparency.entsoe.eu/) | Q | 欧洲电力，注册 token 与数据条款核对 | 候选参考，未全面验收 | backlog |
| S131 | [NASA public APIs](https://api.nasa.gov/) | Q | 多数接口使用免费 Key，演示 Key 限额低 | 候选参考，未全面验收 | backlog |
| S132 | [Open-Meteo](https://open-meteo.com/en/pricing) | Q | 免费端点用于评估/原型；商用需订阅许可 | 候选参考，未全面验收 | backlog |
| S133 | [OpenStreetMap Nominatim](https://operations.osmfoundation.org/policies/nominatim/) | A | 地名/地理编码，严格公共服务用量规范，不是全网搜索 | 候选参考，未全面验收；匿名样例成功 | backlog |
| S134 | [Overpass public API](https://wiki.openstreetmap.org/wiki/Overpass_API) | A | OSM地理要素查询，实例容量有限，不默认广播 | 候选参考，未全面验收 | backlog |
| S135 | [GeoNames](https://www.geonames.org/export/web-services.html) | Q | 地名服务需要注册用户名，免费/付费限额分开 | 候选参考，未全面验收 | backlog |

### 不能承诺免费自动化的平台

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S136 | [X API](https://docs.x.com/x-api/getting-started/pricing) | R | 按量预付费；赠送激励不是永久免费公开搜索 | 候选参考，未全面验收 | backlog |
| S137 | [Reddit Data API](https://redditinc.com/policies/data-api-terms) | R | 审批、用途和商用范围限制，不称无条件免费 | 候选参考，未全面验收 | backlog |
| S138 | [Xiaohongshu](https://openaccount.xiaohongshu.com/docs/api-reference) | R | 账号授权不等于通用笔记搜索；只保留已有公开索引路径 | 候选参考，未全面验收 | backlog |
| S139 | [Weibo](https://open.weibo.com/wiki/API) | R | 公开网页/开放平台不同；本机匿名热榜403 | 候选参考，未全面验收 | backlog |
| S140 | [Zhihu](https://www.zhihu.com/) | W | 实验热榜已接，不含完整站内检索/答案/评论 | 候选参考，未全面验收；已接部分 | existing |
| S141 | [Bilibili](https://www.bilibili.com/) | W | 热词已接，关键词接口本机412，字幕/评论另论 | 候选参考，未全面验收；已接部分 | existing |
| S142 | [WeChat / Sogou WeChat](https://mp.weixin.qq.com/) | R | 公众号授权接口不是公开全网公众号文章搜索 API | 候选参考，未全面验收 | backlog |
| S143 | [Douyin / Kuaishou](https://developer.open-douyin.com/) | R | 业务授权 API，不等于任意视频/评论公共搜索 | 候选参考，未全面验收 | backlog |
| S144 | [Douban / Tieba / Juejin / CSDN / OSChina](https://www.douban.com/) | W | 部分公开网页可读，不承诺稳定免费站内 API | 候选参考，未全面验收 | backlog |

### 工具与自建：不计作托管来源

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S145 | [SearXNG](https://docs.searxng.org/) | S | 开源元搜索软件，不是免费托管源；自建路线仍移出范围 | 候选参考，未全面验收 | backlog |
| S146 | [RSSHub / RSS-Bridge](https://docs.rsshub.app/) | S | 订阅转换工具，公共实例/目标登录/维护成本不能忽略 | 候选参考，未全面验收 | backlog |
| S165 | [Miniflux / FreshRSS](https://miniflux.app/) | S | 订阅阅读器，不是新增新闻来源或搜索引擎 | 候选参考，未全面验收 | backlog |

### 专利与知识产权

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S151 | [USPTO Open Data Portal](https://data.uspto.gov/apis/api-catalog) | Q | 美国专利/商标数据，注册/Key 要求按 API 核对 | 候选参考，未全面验收 | backlog |
| S152 | [EPO Open Patent Services](https://www.epo.org/en/searching-for-patents/data/web-services/ops) | Q | 专利检索/书目信息，注册、免费额度与公平使用另核对 | 候选参考，未全面验收 | backlog |
| S153 | [Google Patents](https://patents.google.com/) | W | 公开专利网页检索；不是无条件免费自动化 API | 候选参考，未全面验收 | backlog |
| S154 | [CNIPA public services](https://www.cnipa.gov.cn/) | W | 专利公开信息入口，登录/验证码与接口权限须核对 | 候选参考，未全面验收 | backlog |

### 金融、经济与行情

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S155 | [FRED](https://fred.stlouisfed.org/docs/api/fred/) | Q | 宏观/利率数据需免费 Key，非实时股票行情 | 候选参考，未全面验收 | backlog |
| S156 | [US BLS public data](https://www.bls.gov/developers/) | A | 统计时间序列；免注册与注册版本限额不同 | 候选参考，未全面验收；匿名样例 403 | backlog |
| S157 | [US Census data APIs](https://www.census.gov/data/developers/data-sets.html) | Q | 统计数据/API，Key 与数据集配额需核验 | 候选参考，未全面验收 | backlog |
| S158 | [Tushare](https://tushare.pro/document/1) | Q | 需 token，积分/权限不同；不能称全部行情免费 | 候选参考，未全面验收 | backlog |
| S159 | [BaoStock](https://www.baostock.com/) | A | 匿名默认登录的历史行情候选；SDK协议/时效/许可待联调 | 候选参考，未全面验收 | backlog |
| S160 | [CoinGecko Demo API](https://docs.coingecko.com/reference/setting-up-your-api-key) | Q | 免费 Demo Key，配额与商业/实时能力另核对 | 候选参考，未全面验收 | backlog |
| S161 | [Yahoo Finance public pages](https://finance.yahoo.com/) | W | 公开行情页与非官方端点不同；不承诺稳定 API/实时许可 | 候选参考，未全面验收 | backlog |
| S162 | [Stooq historical data](https://stooq.com/db/h/) | W | 历史资料候选，不代表免费实时行情或可再分发 | 候选参考，未全面验收 | backlog |

### 播客与音频资料

| ID | 来源 | 类型 | 范围与限制 | 验证/接入状态 | 优先级 |
|---|---|---|---|---|---|
| S163 | [Apple iTunes Search API](https://performance-partners.apple.com/search-api) | A | 播客/媒体元数据，音频全文和转录权限分开 | 候选参考，未全面验收 | backlog |
| S164 | [Podcast Index](https://podcastindex-org.github.io/docs-api/) | Q | 播客目录需开发 Key，不能当作任意节目转录 API | 候选参考，未全面验收 | backlog |
| S165 | [Listen Notes](https://www.listennotes.com/api/pricing/) | Q | 播客检索有免费档候选，配额/用途须验收 | 候选参考，未全面验收 | backlog |
