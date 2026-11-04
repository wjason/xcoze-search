# xcoze search

**简体中文** | [English](README.en.md)

[![Tests](https://github.com/wjason/xcoze-search/actions/workflows/test.yml/badge.svg)](https://github.com/wjason/xcoze-search/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**给 Agent 一个开箱即用的联网搜索入口。** 无 Key 时使用公开渠道；配置 Key 后默认效果优先。Agent 根据问题选择来源、读取原文、补充搜索，取得足够证据后停止。日常提问即可，模式和搜索源都是可选设置。

[让 Agent 安装](#安装) · [在 Agent 中使用](#在-agent-中使用) · [支持的来源](#支持的来源) · [配置 Key](#配置-key) · [开发计划](TODO.md)

## 安装

### 直接告诉 Agent

把下面这句话发给你正在使用的 Agent：

```text
帮我安装这个 Skill：https://github.com/wjason/xcoze-search
```

需要使用支持 Skill 安装、能够执行本地脚本的 Agent。Agent 会按当前工具的规则安装；完成后，如提示需要重新加载或新建会话，照提示操作即可。安装时不需要 API Key，也不用自己找技能目录。

然后发一句话，确认它能实际搜索：

```text
请用 xcoze search 在 GitHub 搜索 microsoft/markitdown，给我仓库链接，并说明它是做什么的。
```

运行环境需要 Python 3.10+，基础搜索只使用标准库，无需额外 Python 包。浏览器兜底是可选功能，不是开始搜索的前提。只有聊天、无法执行本地脚本的环境不能运行本 Skill。

### 其他安装方式

使用 Skills CLI 安装时另需 Node.js：

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

也可下载 [v0.9.1 Skill 包](https://github.com/wjason/xcoze-search/releases/download/v0.9.1/xcoze-search-skill-v0.9.1.zip) 解压到助手技能目录。安装后按宿主要求新建会话或重新加载。详见 [安装教程](INSTALL.zh-CN.md)。

## 在 Agent 中使用

### 日常提问即可

安装并加载后，直接提出需要联网查证的问题。Agent 会按任务需要调用 Skill，不用每次说技能名、选择来源或填写参数：

```text
查一下最近一周海上风电有哪些政策更新，优先找官方原文，标注发布日期和来源链接。
```

```text
查阅 Python asyncio 的官方文档，说明 TaskGroup 的异常处理方式，并给出文档链接。
```

```text
在 GitHub 找几个开源工业视觉项目，对比用途、许可证和部署要求。
```

需要明确指定时，在问题前加上“请用 xcoze search”。如果 Agent 没有识别到技能，让它检查是否安装并加载成功；按当前工具要求重新加载或新建会话后再试。

### 用对话调整搜索方式

默认是 **Smart**：不填 Key 就用免 Key 来源；配置并启用 Key 后默认效果优先。也可以直接告诉 Agent：

| 想做什么 | 直接这样说 |
|---|---|
| 以后只用免 Key 来源 | “把 xcoze search 设为免费模式，以后都用这个模式。” |
| 以后先用免 Key，必要时使用已配置服务 | “把 xcoze search 设为平衡模式。” |
| 恢复自动选择 | “清除 xcoze search 的搜索偏好，恢复默认 Smart，保留 Key。” |
| 仅本次指定来源 | “这次用 DeepSeek 搜索这个问题：……” |
| 仅本次使用免 Key 来源 | “这次用免费模式搜索这个问题：……” |

“以后”会保存为偏好，“这次”只影响当前请求。指定 DeepSeek 等商用来源前需要配置对应 Key；免费模式不调用带 Key 的搜索接口。

需要添加服务时，说“帮我配置 xcoze search 的 DeepSeek 搜索”即可。Agent 提供官方申请链接，再引导你在本机隐藏输入窗口填写，**不要把 Key 发到聊天里**。完整流程见 [配置 Key](#配置-key)和[配置与排错](references/setup.md)。

## 支持的来源

以下是 xcoze search 目前已接入的搜索、阅读和热点来源。各来源的可用性和限额取决于上游服务。

### 无需 Key

| 来源 | 已实现能力 | 边界 |
|---|---|---|
| Bing RSS | 通用公开网页搜索 | 实验性公开 RSS 路径；最多 10 条，结果可能缺日期或不够相关 |
| DuckDuckGo HTML | 通用公开网页搜索 | 实验性 HTML 解析；验证页和改版会导致不可用 |
| Exa 托管 MCP | 搜索、网页读取 | 官方有限免 Key 入口，仍依赖 Exa 服务和限额；与 Exa API 独立 |
| GitHub | 公开仓库搜索、默认分支 README 读取 | 匿名接口有限流；不包含代码搜索、私有仓库或完整 Issue/PR 适配 |
| Hacker News | Algolia 帖子搜索、官方接口读取单条帖子或评论 | 保留讨论地址和外链；子评论 ID 不等于已读取评论树 |
| Jina Reader | 网页正文读取 | 官方限额内免 Key；本项目未接入 Jina Search |
| Wikipedia | 中英文条目搜索 | 摘录与最后编辑时间，不等于一手来源或全文 |
| Stack Exchange | Stack Overflow 等七个社区的问题搜索 | 返回问题摘录，不代表读过答案/评论 |
| arXiv | 论文检索、摘要、提交日期范围 | 预印本摘要，不包含 PDF 全文或同行评审保证 |
| Crossref | DOI、作者、出版日期及可用摘要 | 书目元数据；同名论文需核对作者/年份 |
| npm / crates.io | JavaScript / Rust 软件包搜索、版本元数据 | 不是安全审计，不把下载量当质量分 |
| GitLab.com | 公开项目名称/路径/描述搜索 | 不含代码搜索和私有仓库；星标不是官方身份认证 |
| Europe PMC | 生物医学文献检索、摘要、出版日期范围 | 不是全文或临床结论验证；日期可能由上游推定 |
| Hugging Face | 公开模型元数据检索 | 不下载模型、不调用推理，受限模型仍需各自授权 |

宿主已有搜索、网页读取及浏览器工具由 Agent 按需复用，Skill 不安装或接管宿主工具。知乎、小红书、微博、YouTube、B 站、Reddit、X、V2EX、豆瓣支持公开索引定向搜索；这不等同站内搜索、完整正文或评论读取。需要站内能力时，可使用环境中已有且已授权的平台工具。

### 新闻 RSS、政府政策与社区原文

- **新闻 RSS**：直接读取中新网即时/财经、BBC World 订阅源，可按关键词和日期筛选当前窗口。比如“看看中新网最近关于进博会的报道，再读原文”。
- **政府政策**：检索中国政府网“最新政策”栏目，返回标题、栏目发布日期与官方链接。支持关键词和日期条件；它不是全国公告全集，生效日期需要读政策正文核对。
- **社区主帖**：直接读取 Python、Rust 官方社区论坛主帖；V2EX 主帖适配已实现，但本次网络返回 403，暂不可用。保留主帖代码缩进和链接，不把主帖当完整评论区。

这些路径无需 Key，也不依赖浏览器。订阅源没有命中时，Agent 再按原有偏好搜索，不会把空列表解释成“没有相关新闻”。[使用方法](references/feeds.md) · [真实检索与阅读记录](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-05-feeds-community.md)

### 社区热点（无需 Key）

直接问 Agent：“知乎现在有哪些热议问题？”“B 站热搜有哪些？”“看看 V2EX 的热门话题。”

| 平台 | 直接取得的内容 | 继续查证时要注意 |
|---|---|---|
| 知乎 | 公开热榜的问题、摘录、热度文字与问题链接 | 不包含答案和评论正文 |
| B 站 | 公开热搜词、原生热度字段与搜索链接 | 热搜词不是热门视频排行，也不是视频内容 |
| V2EX | 热门话题标题、节点、创建时间、回复数与链接 | 不包含话题正文和回复 |

Agent 按问题选择榜单；普通搜索不会额外请求这些接口。榜单保留各自顺序、检索时间与热度含义，不混排分数，不保证覆盖全站或持续可用；V2EX 本轮首次成功，安装后复测遇到 403，已按规则暂停。每次只请求一个平台，不需要登录、Cookie 或浏览器。见 [公开源实测与接入计划](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-05-public-platforms.md)。

小红书、微博目前支持下方的公开索引搜索；返回链接会区分笔记/帖子、账号主页和其他页面。**尚未接入两者的原生站内搜索、完整评论或实时热榜**。本轮微博直接入口返回 403；小红书公开索引样例主要命中账号主页，不能据此宣称读到了笔记。

### 使用自己的 Key

| 服务 | 已实现能力 | 环境变量 |
|---|---|---|
| DeepSeek | Search、Fetch | `DEEPSEEK_API_KEY` |
| 腾讯元宝 | SearchPro，标准/动态摘要 | `YUANBAO_API_KEY`，兼容 `TENCENTCLOUD_WSA_APIKEY` |
| Tavily | Search、Extract | `TAVILY_API_KEY` |
| Exa | Search、Contents | `EXA_API_KEY` |
| Brave Search | Web Search | `BRAVE_API_KEY` |
| 博查 | Web Search | `BOCHA_API_KEY` |

各服务独立开通和计费。配置且未禁用的 Key 会参与默认效果优先选路；免费模式排除全部带 Key 的适配器，即使账号仍有赠送额度。服务能力和参数见 [接口说明](references/providers.md)。

实现、账号验证和检索质量分别记录。2026-11-03 本机验证中，Bing RSS、GitHub、HN、Jina 返回可用内容；Exa 免 Key MCP 初次 403、后续搜索通过，DuckDuckGo 返回验证响应；GitHub README 本次 403。这些是当时网络的调用结果，不是所有用户的可用性承诺。六家带 Key 服务的验证范围见 [验证记录](VALIDATION.md)。

### 完整来源清单

这里列出调研中的全部 165 项，包括尚未接入的服务和当前不规划的自建工具。清单中的网站能访问，不代表搜索接口可用或已接入；“部分接入”也可能只覆盖该条目中的部分服务或能力。公开入口可能有额度和使用条件。[查看调研与核验记录](research/free-sources-2026-11.md)。

<details>
<summary>通用搜索与阅读（15）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [Parallel Search MCP](https://parallel.ai/mcp) | 公开入口 | 未接入 |
| [Exa hosted MCP](https://exa.ai/docs/get-started/exa-mcp) | 公开入口 | 部分接入 |
| [Bing RSS](https://www.bing.com/search?format=rss&q=python) | 公开网页 | 部分接入 |
| [DuckDuckGo HTML](https://html.duckduckgo.com/html/) | 公开网页 | 部分接入 |
| [DuckDuckGo Instant Answer](https://duckduckgo.com/api) | 公开入口 | 未接入 |
| [360 / Baidu / Sogou public search pages](https://www.so.com/) | 公开网页 | 部分接入 |
| [Google / Bing / Brave / Mojeek public UI](https://www.google.com/) | 公开网页 | 未接入 |
| [Tavily API](https://www.tavily.com/pricing) | 需注册或有使用条件 | 部分接入 |
| [Exa API](https://exa.ai/pricing) | 需注册或有使用条件 | 部分接入 |
| [Brave Search API](https://api-dashboard.search.brave.com/documentation/resources/help-feedback) | 需注册或有使用条件 | 部分接入 |
| [Firecrawl](https://www.firecrawl.dev/pricing) | 需注册或有使用条件 | 未接入 |
| [Serper](https://serper.dev/) | 试用额度 | 未接入 |
| [SerpApi](https://serpapi.com/pricing) | 需注册或有使用条件 | 未接入 |
| [Search1API](https://s1.dev/docs/essentials/credits-and-limits) | 试用额度 | 未接入 |
| [Jina Reader / Search](https://jina.ai/reader/) | 需注册或有使用条件 | 部分接入 |

</details>

<details>
<summary>技术文档（8）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [Microsoft Learn MCP](https://learn.microsoft.com/en-us/training/support/mcp) | 公开入口 | 未接入 |
| [MDN MCP](https://developer.mozilla.org/en-US/mcp) | 公开入口 | 未接入 |
| [Cloudflare Docs MCP](https://developers.cloudflare.com/workers/get-started/prompting/) | 公开入口 | 未接入 |
| [OpenAI Docs MCP](https://developers.openai.com/resources/docs-mcp) | 公开入口 | 未接入 |
| [Context7](https://github.com/upstash/context7) | 需注册或有使用条件 | 未接入 |
| [Python official docs / Sphinx inventories](https://docs.python.org/3/) | 公开网页 | 未接入 |
| [Rust std / docs.rs](https://docs.rs/) | 公开网页 | 未接入 |
| [Read the Docs / llms.txt publisher docs](https://docs.readthedocs.com/platform/stable/reference/sitemaps.html) | 公开网页 | 未接入 |

</details>

<details>
<summary>新闻与订阅（14）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [China News Service RSS](https://www.chinanews.com.cn/rss/) | 公开入口 | 部分接入 |
| [BBC RSS](https://www.bbc.co.uk/news/10628494) | 公开入口 | 部分接入 |
| [CCTV / CGTN RSS](https://english.cctv.cn/rss/) | 公开网页 | 未接入 |
| [Xinhua RSS](https://www.xinhuanet.com/english/rss/index.htm) | 公开网页 | 未接入 |
| [DW RSS](https://rss.dw.com/rdf/rss-en-all) | 公开入口 | 未接入 |
| [UN News RSS](https://news.un.org/en/rss-feeds) | 公开入口 | 未接入 |
| [NASA news feeds](https://www.nasa.gov/rss-feeds/) | 公开入口 | 未接入 |
| [GDELT DOC / Context](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) | 公开入口 | 未接入 |
| [Google News RSS](https://news.google.com/) | 公开网页 | 未接入 |
| [Guardian Open Platform](https://open-platform.theguardian.com/access/) | 需注册或有使用条件 | 未接入 |
| [NewsAPI.org](https://newsapi.org/pricing) | 需注册或有使用条件 | 未接入 |
| [GNews](https://gnews.io/pricing) | 需注册或有使用条件 | 未接入 |
| [NewsData.io](https://newsdata.io/pricing) | 需注册或有使用条件 | 未接入 |
| [TheNewsAPI](https://www.thenewsapi.com/pricing) | 需注册或有使用条件 | 未接入 |

</details>

<details>
<summary>中国政务与公共数据（19）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [China gov.cn latest-policy index](https://www.gov.cn/zhengce/zuixin/) | 公开入口 | 部分接入 |
| [NDRC notices / announcements](https://www.ndrc.gov.cn/xxgk/zcfb/tz/) | 公开网页 | 未接入 |
| [National Energy Administration](https://www.nea.gov.cn/) | 公开网页 | 未接入 |
| [National Bureau of Statistics releases](https://www.stats.gov.cn/sj/zxfb/) | 公开网页 | 未接入 |
| [National Data / NBS database](https://data.stats.gov.cn/) | 公开网页 | 未接入 |
| [MIIT](https://www.miit.gov.cn/) | 公开网页 | 未接入 |
| [Ministry of Commerce](https://www.mofcom.gov.cn/) | 公开网页 | 未接入 |
| [Ministry of Ecology and Environment](https://www.mee.gov.cn/) | 公开网页 | 未接入 |
| [People's Bank of China](https://www.pbc.gov.cn/) | 公开网页 | 未接入 |
| [CSRC](https://www.csrc.gov.cn/) | 公开网页 | 未接入 |
| [SAMR standards disclosure](https://openstd.samr.gov.cn/) | 公开网页 | 未接入 |
| [National law database](https://flk.npc.gov.cn/) | 公开网页 | 未接入 |
| [China Government Procurement](https://www.ccgp.gov.cn/) | 公开网页 | 未接入 |
| [National public resource trading platform](https://www.ggzy.gov.cn/) | 公开网页 | 未接入 |
| [CNInfo public disclosures](https://www.cninfo.com.cn/new/index) | 公开网页 | 未接入 |
| [SSE / SZSE / BSE disclosures](https://www.sse.com.cn/disclosure/listedinfo/announcement/) | 公开网页 | 未接入 |
| [DATA.GOV.HK](https://data.gov.hk/en/help/api-spec) | 公开入口 | 未接入 |
| [Beijing / Shanghai / Shenzhen open-data portals](https://data.sh.gov.cn/) | 公开网页 | 未接入 |
| [data.gov.tw](https://data.gov.tw/) | 公开网页 | 未接入 |

</details>

<details>
<summary>国际政务与统计（8）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1) | 公开入口 | 未接入 |
| [SEC EDGAR public data](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | 公开入口 | 未接入 |
| [GOV.UK content/search](https://docs.publishing.service.gov.uk/apis.html) | 公开入口 | 未接入 |
| [UK legislation](https://www.legislation.gov.uk/developer) | 公开入口 | 未接入 |
| [Eurostat](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access) | 公开入口 | 未接入 |
| [World Bank Indicators](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation) | 公开入口 | 未接入 |
| [OECD SDMX](https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html) | 公开入口 | 未接入 |
| [api.data.gov / govinfo / Congress APIs](https://api.data.gov/) | 需注册或有使用条件 | 未接入 |

</details>

<details>
<summary>论文与科研（26）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [arXiv](https://info.arxiv.org/help/api/index.html) | 公开入口 | 部分接入 |
| [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | 公开入口 | 部分接入 |
| [DataCite](https://support.datacite.org/docs/api) | 公开入口 | 未接入 |
| [dblp](https://dblp.org/faq/How+to+use+the+dblp+search+API.html) | 公开入口 | 未接入 |
| [Europe PMC](https://europepmc.org/RestfulWebService) | 公开入口 | 部分接入 |
| [NCBI PubMed / PMC E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | 公开入口 | 未接入 |
| [HAL](https://api.archives-ouvertes.fr/docs) | 公开入口 | 未接入 |
| [OpenAIRE](https://graph.openaire.eu/develop/api.html) | 需注册或有使用条件 | 未接入 |
| [Zenodo public records](https://developers.zenodo.org/) | 公开入口 | 未接入 |
| [Figshare public articles](https://docs.figshare.com/) | 公开入口 | 未接入 |
| [bioRxiv / medRxiv](https://api.biorxiv.org/) | 公开入口 | 未接入 |
| [ClinicalTrials.gov](https://clinicaltrials.gov/data-api/api) | 公开入口 | 未接入 |
| [OpenReview public notes](https://docs.openreview.net/) | 公开入口 | 未接入 |
| [Open Library](https://openlibrary.org/developers/api) | 公开入口 | 未接入 |
| [Internet Archive search](https://archive.org/developers/) | 公开入口 | 未接入 |
| [Library of Congress](https://www.loc.gov/apis/) | 公开入口 | 未接入 |
| [Wikisource](https://www.mediawiki.org/wiki/API:Main_page) | 公开入口 | 未接入 |
| [OpenAlex](https://help.openalex.org/access/pricing/) | 需注册或有使用条件 | 未接入 |
| [Semantic Scholar](https://www.semanticscholar.org/product/api) | 需注册或有使用条件 | 未接入 |
| [CORE](https://core.ac.uk/services/api) | 需注册或有使用条件 | 未接入 |
| [Unpaywall](https://unpaywall.org/products/api) | 需注册或有使用条件 | 未接入 |
| [Google Books API](https://developers.google.com/books/docs/v1/using) | 需注册或有使用条件 | 未接入 |
| [Europeana](https://pro.europeana.eu/page/apis) | 需注册或有使用条件 | 未接入 |
| [DOAJ](https://doaj.org/api/docs) | 公开入口 | 未接入 |
| [NASA ADS](https://ui.adsabs.harvard.edu/help/api/) | 需注册或有使用条件 | 未接入 |
| [BASE](https://www.base-search.net/about/en/about_develop.php) | 需注册或有使用条件 | 未接入 |

</details>

<details>
<summary>代码、软件包与模型（17）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [GitHub REST public repositories](https://docs.github.com/en/rest/search/search) | 公开入口 | 部分接入 |
| [GitLab public projects](https://docs.gitlab.com/api/projects/) | 公开入口 | 部分接入 |
| [Codeberg / Forgejo](https://codeberg.org/api/swagger) | 公开入口 | 未接入 |
| [Gitee API](https://gitee.com/api/v5/swagger) | 需注册或有使用条件 | 未接入 |
| [npm registry](https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md) | 公开入口 | 部分接入 |
| [PyPI JSON / Simple](https://docs.pypi.org/api/) | 公开入口 | 未接入 |
| [crates.io](https://crates.io/data-access) | 公开入口 | 部分接入 |
| [Maven Central](https://central.sonatype.org/search/rest-api-guide/) | 公开入口 | 未接入 |
| [NuGet](https://learn.microsoft.com/en-us/nuget/api/search-query-service-resource) | 公开入口 | 未接入 |
| [Packagist](https://packagist.org/apidoc) | 公开入口 | 未接入 |
| [RubyGems](https://guides.rubygems.org/rubygems-org-api/) | 公开入口 | 未接入 |
| [Go module proxy](https://go.dev/ref/mod#module-proxy) | 公开入口 | 未接入 |
| [Hugging Face Hub](https://huggingface.co/docs/hub/api) | 公开入口 | 部分接入 |
| [Docker Hub](https://docs.docker.com/reference/api/hub/latest/) | 需注册或有使用条件 | 未接入 |
| [searchcode MCP](https://searchcode.com/) | 公开入口 | 未接入 |
| [grep.app MCP](https://vercel.com/blog/grep-a-million-github-repositories-via-mcp) | 公开入口 | 未接入 |
| [Libraries.io](https://libraries.io/api) | 需注册或有使用条件 | 未接入 |

</details>

<details>
<summary>社区与社交（10）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [Hacker News / Algolia](https://hn.algolia.com/api) | 公开入口 | 部分接入 |
| [Stack Exchange family](https://api.stackexchange.com/docs) | 公开入口 | 部分接入 |
| [Discourse public communities](https://docs.discourse.org/) | 公开入口 | 部分接入 |
| [V2EX public API](https://www.v2ex.com/p/7v9TEc53) | 公开入口 | 部分接入 |
| [DEV.to / Forem](https://developers.forem.com/api) | 公开入口 | 未接入 |
| [Lobsters](https://lobste.rs/) | 公开入口 | 未接入 |
| [Lemmy public instances](https://join-lemmy.org/api/) | 公开入口 | 未接入 |
| [Mastodon](https://docs.joinmastodon.org/methods/search/) | 需注册或有使用条件 | 未接入 |
| [Bluesky public AppView](https://docs.bsky.app/docs/advanced-guides/api-directory) | 公开入口 | 未接入 |
| [Cnblogs RSS](https://www.cnblogs.com/) | 公开网页 | 未接入 |

</details>

<details>
<summary>百科与素材（8）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [Wikipedia](https://www.mediawiki.org/wiki/API:Search) | 公开入口 | 部分接入 |
| [Wikidata](https://www.wikidata.org/wiki/Wikidata:Data_access) | 公开入口 | 未接入 |
| [Wikimedia Commons](https://commons.wikimedia.org/wiki/Commons:API) | 公开入口 | 未接入 |
| [Openverse](https://docs.openverse.org/api/) | 公开入口 | 未接入 |
| [GBIF](https://www.gbif.org/developer/summary) | 公开入口 | 未接入 |
| [iNaturalist](https://api.inaturalist.org/v1/docs/) | 公开入口 | 未接入 |
| [ROR](https://ror.readme.io/docs/rest-api) | 公开入口 | 未接入 |
| [ORCID public API](https://info.orcid.org/documentation/integration-guide/orcid-api-2/) | 需注册或有使用条件 | 未接入 |

</details>

<details>
<summary>历史网页与档案（3）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [Common Crawl URL Index](https://index.commoncrawl.org/) | 公开入口 | 未接入 |
| [Wayback / CDX](https://archive.org/developers/wayback-cdx-server.html) | 公开入口 | 未接入 |
| [Arquivo.pt](https://arquivo.pt/api) | 公开入口 | 未接入 |

</details>

<details>
<summary>天气、地理与能源（10）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [USGS earthquake feeds/API](https://earthquake.usgs.gov/fdsnws/event/1/) | 公开入口 | 未接入 |
| [NOAA NCEI data service](https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation) | 公开入口 | 未接入 |
| [weather.gov API](https://www.weather.gov/documentation/services-web-api) | 公开入口 | 未接入 |
| [EIA Open Data](https://www.eia.gov/opendata/) | 需注册或有使用条件 | 未接入 |
| [ENTSO-E Transparency](https://transparency.entsoe.eu/) | 需注册或有使用条件 | 未接入 |
| [NASA public APIs](https://api.nasa.gov/) | 需注册或有使用条件 | 未接入 |
| [Open-Meteo](https://open-meteo.com/en/pricing) | 需注册或有使用条件 | 未接入 |
| [OpenStreetMap Nominatim](https://operations.osmfoundation.org/policies/nominatim/) | 公开入口 | 未接入 |
| [Overpass public API](https://wiki.openstreetmap.org/wiki/Overpass_API) | 公开入口 | 未接入 |
| [GeoNames](https://www.geonames.org/export/web-services.html) | 需注册或有使用条件 | 未接入 |

</details>

<details>
<summary>受限平台（9）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [X API](https://docs.x.com/x-api/getting-started/pricing) | 访问受限 | 未接入 |
| [Reddit Data API](https://redditinc.com/policies/data-api-terms) | 访问受限 | 未接入 |
| [Xiaohongshu](https://openaccount.xiaohongshu.com/docs/api-reference) | 访问受限 | 未接入 |
| [Weibo](https://open.weibo.com/wiki/API) | 访问受限 | 未接入 |
| [Zhihu](https://www.zhihu.com/) | 公开网页 | 部分接入 |
| [Bilibili](https://www.bilibili.com/) | 公开网页 | 部分接入 |
| [WeChat / Sogou WeChat](https://mp.weixin.qq.com/) | 访问受限 | 未接入 |
| [Douyin / Kuaishou](https://developer.open-douyin.com/) | 访问受限 | 未接入 |
| [Douban / Tieba / Juejin / CSDN / OSChina](https://www.douban.com/) | 公开网页 | 未接入 |

</details>

<details>
<summary>自建工具（3）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [SearXNG](https://docs.searxng.org/) | 自建 | 当前不规划 |
| [RSSHub / RSS-Bridge](https://docs.rsshub.app/) | 自建 | 当前不规划 |
| [Miniflux / FreshRSS](https://miniflux.app/) | 自建 | 当前不规划 |

</details>

<details>
<summary>专利（4）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [USPTO Open Data Portal](https://data.uspto.gov/apis/api-catalog) | 需注册或有使用条件 | 未接入 |
| [EPO Open Patent Services](https://www.epo.org/en/searching-for-patents/data/web-services/ops) | 需注册或有使用条件 | 未接入 |
| [Google Patents](https://patents.google.com/) | 公开网页 | 未接入 |
| [CNIPA public services](https://www.cnipa.gov.cn/) | 公开网页 | 未接入 |

</details>

<details>
<summary>金融与经济（8）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [FRED](https://fred.stlouisfed.org/docs/api/fred/) | 需注册或有使用条件 | 未接入 |
| [US BLS public data](https://www.bls.gov/developers/) | 公开入口 | 未接入 |
| [US Census data APIs](https://www.census.gov/data/developers/data-sets.html) | 需注册或有使用条件 | 未接入 |
| [Tushare](https://tushare.pro/document/1) | 需注册或有使用条件 | 未接入 |
| [BaoStock](https://www.baostock.com/) | 公开入口 | 未接入 |
| [CoinGecko Demo API](https://docs.coingecko.com/reference/setting-up-your-api-key) | 需注册或有使用条件 | 未接入 |
| [Yahoo Finance public pages](https://finance.yahoo.com/) | 公开网页 | 未接入 |
| [Stooq historical data](https://stooq.com/db/h/) | 公开网页 | 未接入 |

</details>

<details>
<summary>播客（3）</summary>

| 来源 | 访问方式 | 项目状态 |
|---|---|---|
| [Apple iTunes Search API](https://performance-partners.apple.com/search-api) | 公开入口 | 未接入 |
| [Podcast Index](https://podcastindex-org.github.io/docs-api/) | 需注册或有使用条件 | 未接入 |
| [Listen Notes](https://www.listennotes.com/api/pricing/) | 需注册或有使用条件 | 未接入 |

</details>

## 自动调度

- **默认 Smart**：没有可用格式的 Key 时选免 Key 路径；存在 Key 时按效果优先策略选路。Key 的存在不等于账号在线可用。
- **按任务选择**：百科、技术问答、论文、软件包、模型、GitHub/GitLab、HN 任务由 Agent 选择对应原生接口。已知 URL 优先复用宿主读取；脚本自动读取优先 Jina/Exa 免 Key 阅读路径。
- **有限补充**：通用免 Key 优先 Exa MCP，Bing/DDG 备用；quality 的官方资料、最新信息任务可在原有两源预算内补一个来源。普通任务和 GitHub/HN 专用路线有可用结果即返回，空结果/失败时备用。默认最多 3 个来源、45 秒；有浏览器时默认最多两条兼容 API 后才使用浏览器，受 API 请求预算约束。已有更低来源上限保持生效。Agent 判断缺口，价格、规则、最新版本与冲突信息继续读当前原文。
- **可选设置**：支持效果优先、平衡、免费，以及指定来源。本次指定优先于已保存设置；明确 `--strategy free` 时不能同时指定带 Key 来源。

Smart 当前采用透明的能力/来源规则与 Agent 的语义判断，没有跨供应商评分比较、检索质量排行榜或自动训练路由。元宝、DeepSeek 等通用 API 的初始顺序是配置规则，不代表质量排名。详见 [调度说明](references/routing.md)。

2026-11-03 用六道真实任务和两道中文留出题做了同题比较：付费源更快，但官方资料与近期平台讨论并非每题更好，已据此调整默认选路。查看[实测报告](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03.md)（含耗时、费用估算和局限）；结果不代表通用准确率。

免 Key 搜索/读取适配器共 17 个（15 个可搜索、2 个纯读取），另有 3 个新闻 RSS 源、3 条社区热点和 1 条可选浏览器路径。平台能力与已有工具的检测见 `platforms`，不把安装状态当实测通过。详见[开放来源与平台协作](references/open-sources.md)和[本轮实测/Agent Reach 研究](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03-open-sources.md)。

## Exa 限额与浏览器兜底

Exa 匿名额度耗尽会记录冷却，后续调用跳过该源；遵守 Retry-After，未提供恢复时间时暂缓 15 分钟后才允许试探，不承诺届时额度已恢复。普通 Smart 有 Key 时仍优先配置的接口；平台题优先原生 API，健康接口返回后不启动浏览器。官方/最新信息可进行 API 互补，但不会为了互补启动浏览器。

浏览器只在没有 API 可用结果时按需启动，需要已有 agent-browser 和本机 Chrome 运行条件，不自动安装、登录或复用个人会话。默认 API 每源最多 8 秒，浏览器工作预算最多 15 秒，另有最多 6 秒关闭宽限；普通查询不做联网体检。可对 Agent 说“关闭浏览器兜底”，或用 preferences --browser off。免费模式始终不调用带 Key 服务。

v0.7.2 用六道中文新闻、英文文档和 GitHub 项目问题比较免费、DeepSeek、Smart，并单独检查 360。Exa 正常时免费 API 可以直接取得官方资料；限额时 360 只能应急补线索，英文官方文档和 GitHub 索引有缺口。已修正跑题/旧年份结果误判成功、反复请求 DDG 验证页、弱来源互补和 GitHub 浏览器位置预留。[对照报告](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03-comparison.md)保留失败、耗时、费用估算和不同轮次的条件；不据此宣传通用准确率。

## 配置 Key

不配置也能开始搜索。需要增加商用服务时，对 Agent 说：

```text
帮我配置 xcoze search 的 DeepSeek 搜索。
```

Agent 只提供官方申请链接，不自动打开网页；准备好后启动本地隐藏输入窗口。不要把 Key 发到聊天里。保存后可执行一次可能计费的验证。元宝须使用搜索服务 Key，与腾讯云 SecretId/SecretKey 不通用。详见 [配置与排错](references/setup.md)。

凭据目前以权限保护的明文保存在用户配置目录，尚未接入系统凭据库。环境变量优先。v1 读取保持兼容，保存时按原迁移流程保留私人备份。

## 命令行参考

以下命令通常由 Agent 定位 Skill 后执行，用户无需查找文件：

```bash
python3 scripts/xcoze_search.py feeds
python3 scripts/xcoze_search.py feed --source cns-finance --query '进博会'
python3 scripts/xcoze_search.py search '登记管理' --platform govcn --strategy free
python3 scripts/xcoze_search.py fetch 'https://discuss.python.org/t/109869' --strategy free
python3 scripts/xcoze_search.py trending --platform zhihu --count 10
python3 scripts/xcoze_search.py trending --platform bilibili --count 10
python3 scripts/xcoze_search.py trending --platform v2ex --count 10
python3 scripts/xcoze_search.py search 'Python asyncio 官方文档'
python3 scripts/xcoze_search.py search 'industrial vision' --platform github
python3 scripts/xcoze_search.py search 'AI coding' --platform hackernews --start-date 2026-11-01
python3 scripts/xcoze_search.py search 'playwright' --platform npm
python3 scripts/xcoze_search.py search '风力发电' --platform wikipedia
python3 scripts/xcoze_search.py platforms
python3 scripts/xcoze_search.py fetch 'https://docs.python.org/3/library/asyncio.html' --max-characters 100000
python3 scripts/xcoze_search.py preferences --strategy free
python3 scripts/xcoze_search.py preferences --strategy balanced
python3 scripts/xcoze_search.py preferences --reset
python3 scripts/xcoze_search.py search '海上风电数字化' --provider deepseek,yuanbao --max-requests 4
python3 scripts/xcoze_search.py plan 'Python asyncio' --platform github
```

`plan`、`status`、`capabilities` 不联网；普通搜索无需先运行 doctor。`--mode` 保留元宝原生参数含义，调度模式使用 `--strategy`。

`auto` 在 v0.4.0 改为自动选路，Fetch 默认也改为 `auto`；需要旧行为时显式指定服务。`both` 仍只表示 DeepSeek＋元宝；显式多源不自动扩大发送范围。自动备用成功可返回 `ok:true`，之前失败保留在 errors/requests；显式多源部分失败仍为退出码 4。见 [输出契约](references/output.md)。

## 开发与范围

[国内外免费与公开来源图谱](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.md)：165 个来源/候选与排除项，区分免 Key、免费额度、公开网页和自建工具，并附真实探测与接入优先级。

运行离线测试：`python3 -m unittest discover -s tests -v`。结果保留原生顺序与分数、摘要与正文分别处理，不把脚本返回成功当作事实核实完成。

当前聚焦联网搜索和阅读。自建 SearXNG、网页索引、企业资料搜索不在当前范围；站点登录、验证码处理和整站爬取也不是基础安装的一部分。[贡献指南](CONTRIBUTING.md) · [更新记录](CHANGELOG.md) · [竞品与服务调研](references/search-services.md)
