# 来源与适配情况

**简体中文** | [English](sources.en.md)

[返回首页](../README.md)

这里列出 xcoze search 已接入的来源和能力。公开入口可能受到限流或网络环境影响；配置 API Key 后，仍需验证对应账号的服务权限。

## 已接入来源

### 免 Key 搜索与阅读

| 来源 | 可以做什么 |
|---|---|
| Bing RSS | 搜索公开网页 |
| DuckDuckGo HTML | 搜索公开网页 |
| Exa 托管 MCP | 搜索公开网页、读取网页内容 |
| Jina Reader | 读取网页内容 |
| GitHub | 搜索公开仓库、读取仓库 README |
| GitLab.com | 搜索公开项目 |
| Hacker News | 搜索帖子、读取单条帖子或评论 |
| Wikipedia | 搜索中英文百科条目 |
| Stack Exchange | 搜索 Stack Overflow 等七个社区的问题 |
| arXiv | 搜索预印本、读取摘要和论文信息 |
| Crossref | 搜索 DOI、作者和出版信息 |
| Europe PMC | 搜索生物医学文献及摘要 |
| DataCite | 搜索研究成果 DOI 和元数据 |
| Zenodo | 搜索公开研究成果及摘要 |
| Open Library | 搜索图书及作者信息 |
| Wikidata | 搜索中英文实体名称和描述 |
| npm | 搜索 JavaScript 软件包及版本信息 |
| crates.io | 搜索 Rust 软件包及版本信息 |
| Hugging Face | 搜索公开模型信息 |
| 中国政府网 | 搜索“最新政策”栏目中的文件和解读 |
| Python、Rust 社区论坛，V2EX | 读取公开话题主帖 |

Bing RSS、DuckDuckGo HTML 和部分社区入口的访问结果可能随网站调整或网络环境变化。GitHub 适配面向仓库，不包含代码搜索或私有仓库；论文、数据和图书结果主要为元数据或摘要，不代表已读取全文；社区搜索也不代表已读取完整讨论。中国政府网的栏目不覆盖全国所有公告。

### 新闻与社区热点

| 来源 | 可以做什么 |
|---|---|
| 中新网 | 读取即时新闻、财经新闻订阅 |
| BBC | 读取 World 新闻订阅 |
| 知乎 | 查看公开热榜问题及摘要 |
| B 站 | 查看公开热搜词 |
| V2EX | 查看公开热门话题 |

新闻订阅覆盖的是各来源当前提供的内容窗口。社区榜单展示各平台各自提供的内容，不包含完整的回答、视频或评论。

### 平台定向搜索

可以在公开网页索引中限定**知乎、小红书、微博、YouTube、B 站、Reddit、X、V2EX、豆瓣**。这类搜索取决于网页是否被索引，和平台内搜索、登录后内容或完整评论读取不同。

### 使用自己的 API Key

| 服务 | 支持的能力 |
|---|---|
| DeepSeek | Search、Fetch |
| 腾讯元宝 | SearchPro 搜索与摘要 |
| Tavily | Search、Extract |
| Exa | Search、Contents |
| Brave Search | Web Search |
| 博查 | Web Search |

各服务需要单独开通，额度和费用以服务商为准。Exa 的免 Key MCP 和带 Key API 是不同入口。服务的参数与限制见[接口说明](providers.md)。

### 浏览器兜底

当其他可用搜索路径无法返回结果时，Skill 可以使用本机已有的 [agent-browser](https://github.com/vercel-labs/agent-browser) 和浏览器尝试搜索。默认使用 360 搜索，也可指定 Bing 或 Google。此功能是可选的；基础安装不会自动安装浏览器或使用你的浏览器登录状态。也可以让 Agent 关闭浏览器兜底。

[查看来源可用性检查记录](../evaluations/reports/2026-11-05-source-audit.md)。

更多能力说明见[开放来源与平台](open-sources.md)、[新闻与社区内容](feeds.md)和[搜索方式](routing.md)。我们也整理了一份[完整来源调研清单](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.md)，其中包含尚未接入的来源。

