# xcoze search

**简体中文** | [English](README.en.md)

[![Tests](https://github.com/wjason/xcoze-search/actions/workflows/test.yml/badge.svg)](https://github.com/wjason/xcoze-search/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

xcoze search 是一个为 Agent 准备的联网搜索 Skill。它把公开搜索源、专业资料库和可选的搜索 API 放到一起，帮助 Agent 搜索信息、查找原始来源和阅读网页。

安装后可以直接提问。没有 API Key 也能使用；配置自己的 Key 后，Agent 可以在搜索时使用对应服务。你也可以指定来源，或设置长期使用的搜索方式。

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

### 其他安装方式

如果已安装 Node.js，也可以使用 Skills CLI：

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

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

Agent 会根据问题选择合适的搜索或阅读方式。你也可以说“请用 xcoze search”来明确指定这个 Skill，或者指定本次要用的来源。

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

| 分类 | 数量 | 来源 |
|---|---:|---|
| 通用网页搜索 | 3 | Bing RSS、DuckDuckGo HTML、Exa MCP |
| 网页阅读 | 2 | Jina Reader、Exa MCP |
| 开源项目、软件包与模型 | 5 | GitHub、GitLab.com、npm、crates.io、Hugging Face |
| 论文与科研 | 3 | arXiv、Crossref、Europe PMC |
| 百科与问答 | 2 | Wikipedia、Stack Exchange |
| 社区内容 | 4 | Hacker News、Python 社区论坛、Rust 社区论坛、V2EX |
| 新闻订阅 | 2 | 中新网、BBC |
| 政府政策 | 1 | 中国政府网 |
| 社区热点 | 3 | 知乎、B 站、V2EX |
| 平台定向搜索 | 9 | 知乎、小红书、微博、YouTube、B 站、Reddit、X、V2EX、豆瓣 |
| 可配置 API | 6 | DeepSeek、腾讯元宝、Tavily、Exa、Brave Search、博查 |
| 可选浏览器搜索 | 3 | 360 搜索、Bing、Google |

数量按每类中列出的来源或平台计算，同一来源可能同时出现在多个类别，不能相加作为独立来源总数。平台定向搜索使用公开网页索引；新闻按发布机构计数，其中中新网有即时、财经两个订阅源。浏览器搜索需要额外的本地工具。

[查看完整来源与适配情况 →](references/sources.md)

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
- 感谢各搜索服务、公开数据源及其维护者提供接口和文档，也感谢所有贡献者与用户的反馈。

上述项目各自遵循其许可证；第三方内容和接口遵循各自的使用条款。具体参考资料见[搜索服务调研](references/search-services.md)及[接口说明](references/providers.md)。

## 许可证

本项目采用 [MIT License](LICENSE)。xcoze search 由社区独立维护，并非上述搜索服务提供商的官方产品。
