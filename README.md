# xcoze search

**简体中文** | [English](README.en.md)

[![Tests](https://github.com/wjason/xcoze-search/actions/workflows/test.yml/badge.svg)](https://github.com/wjason/xcoze-search/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**面向 AI Agent 的多搜索源工具。** 使用各服务商的官方 API，提供网页搜索、内容提取和带来源的结构化结果。配置哪家服务的 Key，就使用哪家服务。

[安装](#安装) · [配置](#配置-api-key) · [使用](#使用) · [开发计划](TODO.md) · [贡献指南](CONTRIBUTING.md) · [更新记录](CHANGELOG.md)

## 文档语言

默认显示中文。每份文档顶部均可切换 English；需要 Agent 用英文说明时，可以说“请用英文回答”。

| 文档 | 简体中文 | English |
|---|---|---|
| 项目介绍 | [中文](README.md) | [English](README.en.md) |
| Agent 指令 | [中文](SKILL.md) | [English](SKILL.en.md) |
| 安装教程 | [中文](INSTALL.zh-CN.md) | [English](INSTALL.en.md) |
| 配置与排错 | [中文](references/setup.md) | [English](references/setup.en.md) |
| 接口与能力 | [中文](references/providers.md) | [English](references/providers.en.md) |
| 输出契约 | [中文](references/output.md) | [English](references/output.en.md) |
| 搜索服务调研 | [中文](references/search-services.md) | [English](references/search-services.en.md) |
| 开发计划 | [中文](TODO.md) | [English](TODO.en.md) |
| 贡献指南 | [中文](CONTRIBUTING.md) | [English](CONTRIBUTING.en.md) |
| 更新记录 | [中文](CHANGELOG.md) | [English](CHANGELOG.en.md) |
| 验证记录 | [中文](VALIDATION.md) | [English](VALIDATION.en.md) |
| 发布说明 | [中文](PUBLISHING.zh-CN.md) | [English](PUBLISHING.en.md) |
| 商城资料 | [中文](MARKETPLACE.zh-CN.md) | [English](MARKETPLACE.en.md) |
| 回归教程 | [中文](https://github.com/wjason/xcoze-search/blob/main/evaluations/README.md) | [English](https://github.com/wjason/xcoze-search/blob/main/evaluations/README.en.md) |

## 支持状态

| 搜索源 | 网页搜索 | 内容能力 | 账号验证 |
|---|---|---|---|
| DeepSeek | 已实现 | Search 正文、Fetch | 2026-11-02 Search/Fetch 回归通过 |
| 腾讯元宝 | 已实现 | 标准摘要、动态摘要 | 尚未配置，在线验证待办 |
| Tavily | 已实现 | Search 片段/可选正文、Extract | 未做真实账号测试 |
| Exa | 已实现 | Search/Contents 的正文、摘录、摘要分别处理 | 未做真实账号测试 |
| Brave Search | 已实现 | 网页摘要、可选额外片段 | 未做真实账号测试 |
| 博查 | 已实现 | Web Search、可选摘要 | 未做真实账号测试 |

当前版本：[v0.3.0 预览版](https://github.com/wjason/xcoze-search/releases/tag/v0.3.0)。新增搜索源的协议实现和离线测试已完成，真实账号状态分别记录，不能据此推断账号权限或检索质量。官方依据、参数和限制见 [接口说明](references/providers.md)，测试范围见 [验证记录](VALIDATION.md)。

## 安装

要求 Python 3.10+，运行不需要额外 Python 包；助手须支持 Agent Skills 并能执行本地脚本。Skills CLI 安装方式还需要 Node.js，手动解压不需要。

### 让 Agent 帮忙安装（推荐）

在支持安装 Skill、能够执行本地命令的 Agent 对话中，直接复制发送：

```text
安装 https://github.com/wjason/xcoze-search
```

也可以说得更具体：

```text
帮我安装这个 Skill：https://github.com/wjason/xcoze-search
请检查 Python 运行环境，并安装到当前助手的技能目录。
```

安装完成后，按助手提示新建会话或重新载入，再发送：

```text
帮我配置 xcoze search 的 DeepSeek 搜索。
```

可将 DeepSeek 换成其他已支持的服务。助手会提供官方密钥申请链接，并在准备好后启动本地隐藏输入窗口。安装这一步不用提供 API Key，也不要把密钥发到聊天里。若当前 Agent 不支持安装或执行本地命令，可使用下面的安装方式。

### 命令行或手动安装

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

也可下载 [v0.3.0 Skill 安装包](https://github.com/wjason/xcoze-search/releases/download/v0.3.0/xcoze-search-skill-v0.3.0.zip)，将 `xcoze-search/` 放进助手的技能目录。Codex 默认入口为 `~/.codex/skills/xcoze-search/SKILL.md`；设置过 CODEX_HOME 时使用对应的 skills 子目录。

安装或升级后新建会话，尚未识别时重新载入助手。升级、配置格式和卸载说明见 [安装指南](INSTALL.zh-CN.md)。当前 ZIP 是 Python Skill 包，独立可执行安装包仍在计划中。

## 配置 API Key

直接对助手说：

```text
帮我配置 xcoze search 的 Tavily 搜索。
我已有 Exa Key，开始配置。
更换 xcoze search 的元宝密钥。
检查 xcoze search 的配置状态。
```

助手提供官方申请链接，由用户自行点击，不自动打开网页。取得 Key 后回复“准备好了，开始输入”，助手会启动本地隐藏输入窗口；粘贴保存后执行一次可能计费的搜索，并按实际结果报告是否可用。无需找安装目录或配置文件，也不要把 Key 发到聊天里。

窗口使用 macOS 系统对话框、Windows PowerShell/WinForms，或已有 Zenity 的 Linux 图形桌面。无可用桌面时改用自己的可见终端隐藏输入或受控环境变量。各桌面的人工验收仍待完成。

| 服务 | 官方密钥入口 | 环境变量 |
|---|---|---|
| DeepSeek | [平台](https://platform.deepseek.com/api_keys) | `DEEPSEEK_API_KEY` |
| 元宝 | [搜索控制台](https://console.cloud.tencent.com/wsapi/index) | `YUANBAO_API_KEY`，兼容 `TENCENTCLOUD_WSA_APIKEY` |
| Tavily | [控制台](https://app.tavily.com/home) | `TAVILY_API_KEY` |
| Exa | [控制台](https://dashboard.exa.ai/api-keys) | `EXA_API_KEY` |
| Brave | [控制台](https://api-dashboard.search.brave.com/app/keys) | `BRAVE_API_KEY` |
| 博查 | [开放平台](https://open.bochaai.com/) | `BOCHA_API_KEY` |

元宝须使用搜索服务 API Key，与腾讯云 SecretId/SecretKey 等密钥不通用。每家服务独立开通、授权和计费。

手动配置时，在自己的可见终端执行，路径替换为实际安装目录：

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider tavily --verify
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider exa --gui --verify
```

不带 `--gui` 使用终端隐藏输入；带上则使用本地窗口。取消输入不改动配置；`--verify` 验证失败时配置已保存，但不能声称已可用。只有显式 `--default` 才改变默认源。Windows 可把 `python3` 换为 `py -3`；macOS 也保留 `scripts/setup.command` 作为手动入口。

环境变量优先于本地保存值，并须对助手实际运行进程可见。凭据目前以权限保护的明文保存在用户目录，尚未接入系统钥匙串。旧 v1 配置可直接使用，普通搜索不会改写它；迁移或保存新配置时保留私人备份，详情见 [配置与排错](references/setup.md)。

## 使用

```text
用 xcoze search 查找这个主题的官方资料，附上来源。
用 Tavily 搜索最近一周的相关报道。
用 Exa 查找文档，再读取原文，分别保留摘要和摘录。
用 Brave 搜索英国的英文资料。
用博查搜索最近一周的行业新闻。
用 DeepSeek、Tavily 和 Exa 交叉查找，比较原始来源和时间。
```

命令行示例（在 Skill 目录执行）：

```bash
# 查看每家支持的选项、条数、长度限制和密钥入口；不联网
python3 scripts/xcoze_search.py capabilities

# 单源及日期条件
python3 scripts/xcoze_search.py search 'industrial vision' --provider tavily --freshness week --count 5
python3 scripts/xcoze_search.py search 'Python TaskGroup' --provider exa --site docs.python.org --start-date 2026-01-01 --highlights
python3 scripts/xcoze_search.py search 'energy storage' --provider brave --country GB --language en --freshness pw --extra-snippets
python3 scripts/xcoze_search.py search '工业视觉' --provider bocha --freshness oneWeek --summary

# 多源，最多 6 次 HTTP 请求（含重试）
python3 scripts/xcoze_search.py search '海上风电数字化' --provider deepseek,tavily,exa --count 5 --max-requests 6

# 显式内容提取
python3 scripts/xcoze_search.py fetch 'https://docs.python.org/3/library/asyncio-task.html' --provider exa --highlights
python3 scripts/xcoze_search.py fetch 'https://docs.python.org/3/library/asyncio-task.html' --provider tavily
```

选择规则：

- `auto` 使用默认源；未设置时按 DeepSeek、元宝、Tavily、Exa、Brave、博查的顺序选择第一家已配置服务。失败不暗中切换。
- `both` 仍只表示 DeepSeek＋元宝；新接入不会改变旧命令的含义。
- 逗号列表表示指定多家服务；`all` 表示全部已配置服务。新配 Key 不会自动增加普通查询的发送对象。
- 多源在联网前校验全部参数及密钥；各家能力不同，不支持的条件会报错。Tavily/Brave 最多 20 条，其余本工具最多 50 条，不自动分页。
- Fetch 默认仍使用 DeepSeek；Tavily/Exa 必须显式指定。其余三家只有搜索适配，不自动借用其他服务提取正文。

Tavily 的 `content` 是片段，`raw_content` 才是正文；Exa 的 `text`、`highlights`、`summary` 分别返回。元宝、Brave、博查的摘要不标记成全文。`--include-answer` 只为 Tavily 显式请求生成答案，结果与来源列表分开保存。

## 预算、用量和错误

`--max-requests` 限制当前命令的实际 HTTP 次数，包括失败和重试。Search/doctor 默认 12，Fetch 默认 3；每次请求最多重试 2 次，默认重试 1 次，doctor 零重试。多源至少要留出每家一次的预算。此限制不跨命令持久累计，也不是金额上限。

结果保留各家排序、评分和原始字段，不按不同服务的分数混排。输出包含各服务实际请求次数、耗时及平台返回的用量/费用；未返回时为 `null`，不估造费用。多源运行中某家失败会保留成功结果，返回 `ok:false`、`partial:true` 和退出码 4。

空结果、鉴权失败、计费/配额问题、限流、网络问题、预算用尽和异常响应分别报告。HTTP 200 的内容提取仍检查逐 URL 失败状态。字段和退出码见 [输出契约](references/output.md)。

## 检查与配置迁移

```bash
python3 scripts/xcoze_search.py status
python3 scripts/xcoze_search.py doctor --provider tavily
python3 scripts/xcoze_search.py doctor --provider deepseek,exa --max-requests 2
python3 scripts/xcoze_search.py migrate-config
```

status 不联网、不显示密钥。doctor 会真实搜索，`search_verified:true` 只代表该次检查取得有效结果。迁移命令把 v1 配置升级到 v2，并保留权限受控的 v1 原文件备份；新格式保留已有 Key、默认源及扩展字段。详细失败与回退说明见 [配置说明](references/setup.md)。

## 开发与回归

本节命令在仓库或源码包目录执行。当前源码有 68 项离线测试（v0.3.0 发布时为 67 项），运行和测试只依赖 Python 标准库；CI 覆盖 Windows/Linux、Python 3.10/3.12。

```bash
python3 -m unittest discover -s tests -v
# 默认只生成计划，不读取凭据、不发送查询
python3 scripts/evaluate.py --provider deepseek,tavily,exa
python3 scripts/evaluate.py --operation fetch --provider deepseek,tavily,exa
```

源码包包含 12 个中英文搜索查询、3 个正文提取 URL 及显式在线运行入口，分别覆盖技术文档、原始规范、日期、版本和冲突信息。域名命中仅作人工复核线索，不能视为事实准确率或服务质量排名。在线调用需显式 `--live`，并受整轮请求预算限制；见 [回归说明](https://github.com/wjason/xcoze-search/blob/main/evaluations/README.md)（仅源码包包含）。

P0 基础代码和 P1 四家适配已实现；元宝在线验证按当前账号条件保留待办。P2/P3 新服务、独立安装包和系统凭据库等后续工作见 [TODO](TODO.md)。参与方式见 [CONTRIBUTING](CONTRIBUTING.md)。

## 数据、费用与许可

查询和 URL 直接发送到选定的服务商，不经过项目维护方服务器。项目不收集遥测、不自动保存搜索历史；回归工具只有用户显式指定输出文件时才写报告。

多源查询、重试、内容提取、生成摘要或高级搜索选项可能增加费用，以服务商实际计费为准。本项目独立维护，使用官方 API，不代表服务商官方产品或认证。请避免发送未经授权的私密查询及带访问令牌的 URL。

[MIT License](LICENSE)。搜索结果内容的权利归原权利人所有。
