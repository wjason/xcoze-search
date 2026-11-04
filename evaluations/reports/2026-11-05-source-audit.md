# 来源可用性检查

**简体中文** | [English](2026-11-05-source-audit.en.md)

检查时间：2026-11-05（北京时间）。使用独立的临时配置和缓存，未读取或发送用户 API Key。每项为一次真实请求或一次浏览器搜索；结果只反映当时网络和查询，不代表持续可用或搜索质量保证。

| 范围 | 结果 |
|---|---|
| 公开搜索 | Exa MCP、GitHub、Hacker News、Wikipedia、Stack Exchange、arXiv、Crossref、npm、crates.io、GitLab.com、Europe PMC、Hugging Face、中国政府网均返回结果；Bing RSS 的英文样例被相关性检查拒绝，DuckDuckGo 返回验证页（202）。 |
| 网页与社区阅读 | Exa MCP、GitHub README、Hacker News 单条、Python 和 Rust 社区主帖读取成功；Jina Reader 返回 401，V2EX 主帖返回 403。 |
| 新闻和热点 | 中新网即时、财经、BBC World 返回内容；知乎和 B 站热点返回内容，V2EX 热点返回 403。 |
| 平台定向搜索 | 使用 Exa MCP 对九个平台各查询一次；知乎、小红书、微博、YouTube、B 站、Reddit、V2EX、豆瓣返回链接，X 本题返回空结果。平台链接不代表正文、评论或站内搜索可用。 |
| 浏览器搜索 | 本机使用已有 agent-browser：360 返回结果，Bing 的样例被相关性检查拒绝，Google 返回验证页。 |
| 新增来源 | Open Library、DataCite、Zenodo、Wikidata 均通过本项目适配器返回 3 条结果；返回的是书目、研究成果或实体元数据，不代表取得全文。 |
| 带 Key 服务 | DeepSeek、元宝、Tavily、Exa API、Brave 和博查本次未调用，配置状态不能替代在线验证。 |

另对世界银行公开指标接口做了一次匿名请求，返回数据，但该次检查未验证关键词搜索，因此没有接入或列为已支持搜索源。此前发现的 Microsoft Learn、MDN、Parallel 等候选见[来源调研](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.md)；此前成功不代表本次已验证或已接入。

请求出现访问拒绝或验证页后停止，未切换身份绕过。上游服务可随时改变访问规则，内容使用请遵守各来源的条款。
