# xcoze search

[![Tests](https://github.com/wjason/xcoze-search/actions/workflows/test.yml/badge.svg)](https://github.com/wjason/xcoze-search/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**面向 AI Agent 的多搜索源工具。** 通过统一的 Skill 和命令行接口访问网页搜索与内容提取服务，为检索、研究和信息核实提供带来源的结果。

项目采用自带密钥（BYOK）的接入方式：配置所需服务的 API Key，选择搜索源后即可使用。搜索源持续扩展，已实现的功能和后续计划分别列在下方。

[安装](#安装) · [配置](#配置-api-key) · [使用](#使用) · [开发计划](TODO.md) · [参与贡献](CONTRIBUTING.md) · [更新记录](CHANGELOG.md)

## 支持状态

| 搜索源 | 网页搜索 | 内容提取 | 状态 |
|---|---|---|---|
| DeepSeek | 支持 | Search 正文 / Fetch | 已实现；2026-10-24 完成真实账号测试 |
| 腾讯元宝 | 支持 | 标准摘要 / 动态摘要 | 已实现；真实账号测试待完成 |
| Tavily、Exa、Brave、博查等 | 计划中 | 按服务能力接入 | 尚未实现，见 [TODO](TODO.md) |

目前发布版本为 [v0.1.0 预览版](https://github.com/wjason/xcoze-search/releases/tag/v0.1.0)。`main` 分支为 v0.2.0 开发版，已加入对话引导配置和本地隐藏输入窗口；v0.1.0 下载包不含这一更新。服务能力、鉴权要求和接入依据见 [搜索服务调研](references/search-services.md)。

## 安装

运行要求：

- Python 3.10+，无需额外 Python 依赖。
- 支持 Agent Skills，并能执行本地 Python 的助手。
- 使用 Skills CLI 安装时需要 Node.js；手动安装不需要。

### Skills CLI

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

在安装器中选择所使用的助手。

### 下载发布包

下载 [Skill 安装包](https://github.com/wjason/xcoze-search/releases/download/v0.1.0/xcoze-search-skill-v0.1.0.zip)，解压后将 `xcoze-search/` 放入助手的技能目录。Codex 默认目录结构为：

```text
~/.codex/skills/xcoze-search/SKILL.md
```

安装后新建会话；如果尚未识别技能，重新启动助手。其他安装方式及升级方法见 [安装指南](INSTALL.zh-CN.md)。

需要使用下方的对话配置流程，请通过 Skills CLI 安装当前 `main` 分支，或下载仓库当前源码；上述 v0.1.0 包使用终端配置。

## 配置 API Key

安装后直接在助手中输入：

```text
帮我配置 xcoze search。
更换 xcoze search 的元宝密钥。
检查 xcoze search 的配置状态。
```

助手会确认要配置的服务，并在对话中提供官方密钥申请链接。自行点击链接取得 Key 后，回复“准备好了，开始输入”，助手会启动本地隐藏输入窗口。粘贴并保存后，工具执行一次可能计费的真实搜索，助手据结果说明是否可用。已有 Key 时可以直接说“我已有 DeepSeek Key，开始配置”，无需重复申请。

申请页面不会自动打开；输入 Key 的窗口由本地工具显示。整个流程无需查找安装目录或配置文件，也不用把 Key 发给助手。取消输入时不改动已有配置。只配置一家即可使用，两家可分别配置。

窗口支持 macOS 系统对话框、Windows PowerShell/WinForms，以及已安装 Zenity 的 Linux 图形桌面。无图形界面或窗口工具不可用时，改用自己的可见终端隐藏输入或受控环境变量。当前仍需 Python 3.10+；独立可执行安装包尚未提供。

### 官方密钥申请入口

| 搜索源 | 申请入口 | 说明 |
|---|---|---|
| DeepSeek | [DeepSeek 平台](https://platform.deepseek.com/api_keys) | 创建 API Key，确认账号可调用 Search / Fetch |
| 腾讯元宝 | [元宝搜索控制台](https://console.cloud.tencent.com/wsapi/index) | 开通搜索服务，在“概览 → 服务 API KEY 方式”创建搜索服务密钥 |

元宝需要搜索服务的 API Key，与腾讯云 SecretId/SecretKey 及其他模型服务的密钥不通用。

### 手动配置（可选）

需要自行执行命令时，在实际安装目录打开自己的终端：

DeepSeek：

```bash
python3 scripts/xcoze_search.py setup --provider deepseek --default --verify
```

腾讯元宝：

```bash
python3 scripts/xcoze_search.py setup --provider yuanbao --verify
```

不带 `--gui` 时，setup 在终端隐藏输入密钥；加上 `--gui` 则使用本地输入窗口。`--default` 设置默认搜索源；`--verify` 保存配置后执行一次可能计费的搜索。验证失败时已保存的配置仍保留，应按错误原因处理，不能视为配置已验证通过。

macOS 可双击 `scripts/setup.command` 完成配置。Windows 如果没有 `python3` 命令，可使用 `py -3`。

### 环境变量

| 搜索源 | 环境变量 |
|---|---|
| DeepSeek | `DEEPSEEK_API_KEY` |
| 元宝 | `YUANBAO_API_KEY`，兼容 `TENCENTCLOUD_WSA_APIKEY` |

环境变量优先于本地配置，并需对实际运行助手的进程可见。本地配置以权限保护的明文保存于用户目录，密钥不应提交到 Git 或发送到聊天。路径、权限和清理方法见 [配置说明](references/setup.md)。

## 使用

在助手中直接提出搜索任务：

```text
用 xcoze search 查找这个主题的官方资料，附上来源链接。
用元宝搜索近七天的行业报道。
用 DeepSeek 查找接口文档，再读取相关页面正文。
用 DeepSeek 和元宝交叉搜索这条消息，比较来源和时间。
```

支持显式调用的助手也可使用 `$xcoze-search`。自动选用技能的行为由助手决定。

### 命令行

以下命令在 Skill 目录执行：

```bash
# 默认搜索源
python3 scripts/xcoze_search.py search '海上风电数字化' --count 5

# DeepSeek：限定站点并请求可用正文
python3 scripts/xcoze_search.py search 'Search Fetch API' --provider deepseek --site api-docs.deepseek.com --need-content

# 元宝：最近七天
python3 scripts/xcoze_search.py search '工业视觉' --provider yuanbao --freshness d7

# 双源搜索，每家最多显示 5 条
python3 scripts/xcoze_search.py search '海上风电数字化' --provider both --count 5

# DeepSeek 网页内容提取
python3 scripts/xcoze_search.py fetch 'https://api-docs.deepseek.com/guides/search/'
```

`auto` 使用已设置的默认源；未设置时使用已配置的服务，两家都配置则优先 DeepSeek。失败时返回错误，不自动向另一家发送查询。`both` 需要两家均已配置，并只接受共同支持的参数。

输出保留供应商、来源链接、日期和原始字段。元宝动态摘要与网页正文分别处理；不同服务的分数不直接混排。双源部分失败会保留成功结果，同时返回 `ok:false` 和 `partial:true`。

参数差异、条数和查询长度限制见 [接口说明](references/providers.md)，JSON 字段及退出码见 [输出契约](references/output.md)。

## 检查配置

```bash
# 仅检查本地配置，不联网
python3 scripts/xcoze_search.py status

# 对已经配置的服务发起真实搜索
python3 scripts/xcoze_search.py doctor --provider deepseek
python3 scripts/xcoze_search.py doctor --provider yuanbao
```

`search_verified:true` 表示该次检查取得有效结果。Key 无效、服务未开通、余额不足和限流等问题见 [排错指南](references/setup.md)。

## 开发计划

接下来先完善供应商适配接口和元宝实测，再按优先级扩展搜索源：

- **P0**：供应商注册与能力声明、配置迁移方案、统一错误处理、元宝真实账号测试。
- **P1**：Tavily、Exa、Brave Search、博查。
- **P2**：Perplexity Search、Firecrawl、Parallel、Serper、SerpApi。
- **P3**：Jina Search/Reader、SearXNG 自建实例。

详细任务、状态和完成条件见 [TODO.md](TODO.md)。优先级属于项目规划，不是服务质量排名；新增搜索源尚未实现，也未承诺发布日期。

## 参与贡献

欢迎提交问题、文档修正和搜索源适配。新增适配需附官方接口依据、参数与能力映射、错误处理和测试。提交方式见 [CONTRIBUTING.md](CONTRIBUTING.md)。

```bash
python3 -m unittest discover -s tests -v
```

当前有 33 项离线测试，CI 配置覆盖 Windows/Linux、Python 3.10/3.12。窗口流程使用合成输入测试，各桌面上的真实窗口验收状态见 [VALIDATION.md](VALIDATION.md)。

## 数据与费用

查询和 URL 直接发送给用户选择的服务，不经过项目维护方服务器。项目不收集遥测，不自动保存搜索历史。请避免发送未经授权的私密内容或带访问令牌的链接。

各服务独立计费；双源查询、重试和正文提取可能产生费用，具体以服务商规则为准。本项目使用服务商官方 API，独立维护，不代表服务商的官方产品或认证。

## 许可

[MIT License](LICENSE)。搜索结果内容的权利归原权利人所有。
