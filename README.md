# xcoze search

**简体中文** | [English](README.en.md)

[![Tests](https://github.com/wjason/xcoze-search/actions/workflows/test.yml/badge.svg)](https://github.com/wjason/xcoze-search/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**xcoze search 是面向 AI Agent 的调研搜索组件：选择来源、查找资料、读取原文并保留可核验的证据。**

它聚合公开信息源和可选搜索服务，覆盖技术文档、政策、能源电力、招投标、论文和开源项目。需要深入调研时，Agent 可以在同一预算内搜索、读原文、整理引用，并识别还缺哪些证据。

安装后即可使用免费搜索，也可以接入自己选择的搜索服务，按需要切换搜索方式。

[安装](#安装) · [使用](#使用) · [支持的来源](#支持的来源) · [配置-api-key](#配置-api-key) · [参与贡献](#参与贡献)

## 安装

### 告诉 Agent 安装

将下面这句话发给你的 Agent：

```text
帮我安装这个 Skill：https://github.com/wjason/xcoze-search
```

按照 Agent 的提示完成安装。如果安装后没有识别到 Skill，请重新加载或新建会话，再试一次：

```text
请用 xcoze search 在 GitHub 查找 microsoft/markitdown，告诉我它的用途并给出仓库链接。
```

需要支持 Skill 并能执行本地脚本的 Agent，以及 Python 3.10 或更高版本。基础功能只使用 Python 标准库。安装和使用公开搜索源不需要 API Key。

### 使用 Skills CLI 安装

如果已安装 Node.js，也可以使用 Skills CLI：

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

运行后按照提示选择要安装到的 Agent。

也可以从 [GitHub Releases](https://github.com/wjason/xcoze-search/releases) 下载 Skill 安装包。更多方式见[安装教程](INSTALL.zh-CN.md)。

## 使用

安装完成后，直接向 Agent 提问，例如：

```text
查一下最近一周海上风电有哪些政策更新，优先找官方原文，标注发布日期和来源链接。
```

```text
查阅 Python asyncio 官方文档，说明 TaskGroup 如何处理异常，并给出文档链接。
```

```text
在 GitHub 上找几个开源工业视觉项目，对比用途、许可证和部署要求。
```

```text
查最近一个月广东的储能政府采购和工程招标，区分招标、中标和更正公告，给出原文链接。
```

Agent 会根据问题选择合适的搜索或阅读方式。你也可以说“请用 xcoze search”来明确指定这个 Skill，或者指定本次要用的来源。

### 从资料到证据

查一条链接时直接搜索；需要解释、比较或核对事实时，Agent 可使用调研流程，按需读原文并返回引用片段。已适配官方站点优先直接读取，公共资源目录会继续读取其公布的正文链接。重复网页归并，未知日期和未读内容保持明确。

```text
查阅 TaskGroup 的官方原文，解释一个任务失败后其他任务会怎样，给出支持结论的段落。
```

[调研流程与预算](references/research.md) · [查看逐项支持状态](references/source-status.md)

### 搜索偏好

默认使用 **Smart**：没有配置 Key 时使用免 Key 来源；配置并启用 Key 后，优先考虑搜索效果，也会使用合适的公开来源。

| 需求 | 可以这样告诉 Agent |
|---|---|
| 以后只用免 Key 来源 | 把 xcoze search 设为免费模式，以后都用这个模式。 |
| 先用免 Key 来源，必要时使用已配置服务 | 把 xcoze search 设为平衡模式。 |
| 恢复默认设置 | 清除 xcoze search 的搜索偏好，恢复默认 Smart，保留 Key。 |
| 指定本次来源 | 这次用 DeepSeek 搜索：…… |
| 本次只用免 Key 来源 | 这次用免费模式搜索：…… |

“以后”的设置会保存；“这次”的要求只对当前请求生效。免费模式不会调用需要用户 Key 的搜索服务。指定带 Key 的服务前，需要先完成配置。

## 支持的来源

查官方文档时，Agent 可以直接检索 Python、pandas、SQLAlchemy、Kubernetes、Rust 的文档索引，或调用 Go、MDN 站内搜索。免 Key 通用搜索优先使用 Parallel，Exa 和公开 HTML 搜索作为备用；360 HTML 无需启动浏览器。更多用法见[官方文档搜索](references/documentation.md)。

| 分类 | 数量 | 来源 |
|---|---:|---|
| 通用网页搜索 | 5 | Parallel Search MCP、Exa MCP、360 HTML、Bing RSS、DuckDuckGo HTML |
| 官方文档 | 7 | Python、pandas、SQLAlchemy、MDN Web Docs、Kubernetes、Go、Rust |
| 网页阅读 | 3 | 官方站点原生读取、Jina Reader、Exa MCP |
| 开源项目、软件包与模型 | 5 | GitHub、GitLab.com、npm、crates.io、Hugging Face |
| 论文与科研 | 5 | arXiv、Crossref、Europe PMC、DataCite、Zenodo |
| 百科、知识库与问答 | 3 | Wikipedia、Wikidata、Stack Exchange |
| 图书 | 1 | Open Library |
| 社区内容 | 4 | Hacker News、Python 社区论坛、Rust 社区论坛、V2EX |
| 新闻 | 3 | 中新网、BBC、新华网 |
| 政府政策 | 5 | 中国政府网、国家发展改革委、工信部、商务部、美国联邦公报 |
| 中国统计与能源 | 3 | 国家统计局、国家能源局、人民银行 |
| 生态与应急 | 2 | 生态环境部、应急管理部 |
| 采购与交易 | 3 | 中国政府采购网、全国公共资源交易平台、南方电网采购公告 |
| 证券公告 | 1 | 巨潮资讯 |
| 证券监管 | 1 | 中国证监会 |
| 国内科研与地质 | 2 | 中国科学院、中国地质调查局 |
| 开放数据更新 | 1 | 香港政府数据一线通 |
| 航天素材 | 1 | NASA 素材库 |
| 国际经济统计 | 1 | 世界银行 |
| 地震 | 1 | 美国地质调查局 USGS |
| 社区热点 | 3 | 知乎、B 站、V2EX |
| 平台定向搜索 | 9 | 知乎、小红书、微博、YouTube、B 站、Reddit、X、V2EX、豆瓣 |
| 国内公开索引 | 13 | 国家数据、中国气象数据中心、中国天气网、上交所、深交所、北交所、国家标准、国家法律法规数据库、国家航天局、科学数据银行、中国地震台网、国家海洋预报台、香港天文台 |
| 可配置 API | 6 | DeepSeek、腾讯元宝、Tavily、Exa、Brave Search、博查 |
| 可选浏览器搜索 | 3 | 360 搜索、Bing、Google |

数量按每类中列出的来源或平台计算，同一来源可能同时出现在多个类别，不能相加作为独立来源总数。平台定向搜索使用公开网页索引；新闻按发布机构计数，其中中新网有即时、财经两个订阅源，新华网为首页资讯。国内公开索引按网站限定搜索范围，结果覆盖和新鲜度取决于搜索引擎的收录情况。浏览器搜索需要额外的本地工具。

能源电力调研可检索能源局公开文件和统计发布；招投标调研可按地区、日期和公告类型查询公共资源交易平台，或筛选南网公开列表。采购网本身仍限近期首页公告。详见[能源电力与招投标搜索](references/industry-search.md)。

[查看完整来源与能力 →](references/sources.md) · [支持状态与待支持来源](references/source-status.md)

## 搜索评测

v0.10.0 增加从搜索到原文与证据缺口的调研题集，分别记录候选、正文、引用覆盖、日期和耗时，不以非空结果代表答对。[调研实测与未命中记录](evaluations/reports/2026-11-22-research.md)。

公开题集已扩至 100 道，每道题附有来源、相关性或日期的核验条件。

2026-11-09 免费模式基线中，100 道题均返回候选。99 道预设域名的题中，有 97 道在前五条命中，检索耗时中位数为 966 毫秒。

[100 道题集](evaluations/agent-search-cases-v3.json) · [运行说明](https://github.com/wjason/xcoze-search/blob/main/evaluations/README.md#agent-搜索题集) · [100 道题基线与复测](evaluations/reports/2026-11-09-100-question-baseline.md) · [20 道题原文核验报告](evaluations/reports/2026-11-09-agent-search.md)

[100 道题无 Exa 对照](evaluations/reports/2026-11-10-parallel-no-exa.md) · [早期 Exa 断路实测](evaluations/reports/2026-11-09-exa-outage.md)

[最新免 Key 文档搜索与 100 题无 Exa 实测](evaluations/reports/2026-11-16-keyless-search.md)，保留本次限额、验证码和未命中记录。

[Kubernetes、Go、Rust 与国内站内检索实测](evaluations/reports/2026-11-16-native-search.md)，包含同时禁用 Exa 和 Parallel 的 100 题记录。

[能源电力与招投标专项实测](evaluations/reports/2026-11-16-energy-procurement.md)包含 27 道真实问题，在关闭 Exa、Parallel 和带 Key 服务的条件下运行，并记录原文核验与访问限制。

## 更新

可以直接告诉 Agent：

```text
检查并更新 xcoze search，保留我的 Key 和搜索偏好。
```

更新会校验安装包，备份旧安装；失败时保留原安装，配置目录独立保存。正常安装包不再携带历史评测数据，需要时可在仓库或源码包中查看。[版本检查、离线更新与恢复](INSTALL.zh-CN.md#升级与卸载)。

## 配置 API Key

不配置 Key 即可开始搜索。如果需要使用某家服务，可以对 Agent 说：

```text
帮我配置 xcoze search 的 DeepSeek 搜索。
```

Agent 会提供申请 Key 的官方链接；准备好后，在本机弹出的隐藏输入窗口中填写。**不要把 Key 发到聊天里。** 没有图形界面时，也可以使用终端隐藏输入或环境变量，具体方法见[配置与排错](references/setup.md)。

Key 默认保存在有权限保护的本地配置文件中，目前为明文存储；同一服务的环境变量优先。验证 Key 会发起一次真实搜索，可能产生服务费用。元宝需要使用其搜索服务 Key，不能使用腾讯云 SecretId/SecretKey 代替。

## 隐私与使用提示

搜索词和需要读取的网页地址会发送给被调用的搜索或阅读服务；免 Key 也需要联网。请避免提交敏感信息或含访问凭据的链接。API Key 仅用于对应服务的请求。

搜索结果可能过时、缺失或不准确。重要信息请查看原始来源，并留意发布日期和适用范围。

## 开发与文档

在项目目录运行离线测试：

```bash
python3 -m unittest discover -s tests -v
```

项目提供[命令行与接口说明](references/providers.md)、[Agent 指令](SKILL.md)、[开发计划](TODO.md)和[更新记录](CHANGELOG.md)。需要手动运行命令时，可从项目目录执行 `python3 scripts/xcoze_search.py --help`。

## 参与贡献

欢迎提交 Issue 和 Pull Request，帮助改进文档、修复问题或接入新的搜索源。提交来源建议时，请附上接口文档和希望支持的能力；报告问题时请移除 Key 和其他敏感信息。

开始之前请阅读[贡献指南](CONTRIBUTING.md)。

## 参考与致谢

感谢以下项目和服务为 xcoze search 的设计与实现提供帮助：

- [Agent Reach](https://github.com/Panniantong/Agent-Reach)：参考了其平台能力组织和搜索、阅读工作流。
- [DDGS](https://github.com/deedy5/ddgs) 和 [open-webSearch](https://github.com/Aas-ee/open-webSearch)：参考了公开搜索入口与多来源搜索的设计。
- [LiteLLM](https://github.com/BerriAI/litellm)、[OpenRouter](https://openrouter.ai/) 和 [Tavily Skills](https://github.com/tavily-ai/skills)：参考了统一接口和 Agent 搜索工作流。
- [agent-browser](https://github.com/vercel-labs/agent-browser)：为可选的本地浏览器搜索提供支持。
- [Sphinx](https://www.sphinx-doc.org/) 与 [MDN](https://hacks.mozilla.org/2021/03/how-mdns-site-search-works/)：官方文档搜索使用其公开索引和站内搜索入口，适配器独立实现。
- 感谢各搜索服务、公开数据源及其维护者提供接口和文档，也感谢所有贡献者与用户的反馈。

上述项目各自遵循其许可证；第三方内容和接口遵循各自的使用条款。具体参考资料见[搜索服务调研](references/search-services.md)及[接口说明](references/providers.md)。

## 许可证

本项目采用 [MIT License](LICENSE)。xcoze search 由社区独立维护，并非上述搜索服务提供商的官方产品。
