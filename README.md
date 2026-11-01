# xcoze search

[GitHub](https://github.com/wjason/xcoze-search) · [安装指南](INSTALL.zh-CN.md) · [配置与排错](references/setup.md) · [验证记录](VALIDATION.md)

**一个 Skill，连接 DeepSeek 与腾讯元宝官方搜索 API。** 配置任意一家 API Key 即可搜索，配置两家可按需交叉检索；同时提供 DeepSeek 网页正文抓取。

由 XCoze 维护的独立开源适配，**不是 DeepSeek 或腾讯官方发布/认证的产品**。运行时只直连官方端点，无 XCoze 中转服务，无遥测，无额外聊天模型调用。

版本：`0.1.0`。已完成离线协议/行为验证；DeepSeek Search/Fetch 已完成本机真实账号实测，元宝仍待配置 Key 后验证，见 [验证记录](VALIDATION.md)。

## 适合做什么

- 搜索公开资料，为回答提供标题、摘要、链接和可用的日期。
- 指定 DeepSeek 或元宝，也可明确要求两家交叉查找。
- 按站点筛选；元宝可按相对时间、垂域和结果模式检索（取决于服务版本）。
- 使用 DeepSeek Fetch 读取公开网页 Markdown，核对原文。

语义规划、信息筛选和写答案由调用 Skill 的助手完成。脚本负责请求、协议适配和结构化输出，不会因为返回几个结果就自动宣布事实已核实。

## 安装

要求：Python 3.10+；支持 Agent Skills 且可以执行本地 Python 的助手。运行不需要 pip 依赖或 Node.js。使用 `npx skills` 安装时才需要 Node.js。

### 从 ZIP 安装

如维护者已在 [GitHub Releases](https://github.com/wjason/xcoze-search/releases) 提供 `xcoze-search-skill-v0.1.0.zip`，可下载并解压得到 `xcoze-search/`，复制到你的助手支持的技能目录。Codex 可安装到 `~/.codex/skills/xcoze-search/`，其他助手依其文档选择目录。

最终结构应为 `技能目录/xcoze-search/SKILL.md`，避免多套一层 xcoze-search。下一轮对话加载，未发现时重新开启会话或重启宿主。详见 [安装说明](INSTALL.zh-CN.md)。

### 从 GitHub 安装

使用 Skills CLI 安装，在安装器中选择你的助手：

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

也可手动安装到 Codex（先确认目标目录不存在，已有安装请按升级说明处理）：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/wjason/xcoze-search.git ~/.codex/skills/xcoze-search
cd ~/.codex/skills/xcoze-search
```

如果使用自定义 CODEX_HOME，请将目标改成其 skills 子目录。其他助手使用其支持的 Agent Skills 目录。安装后新建一轮对话，输入 `$xcoze-search` 或“用 xcoze search 搜索……”。

## 配置：只填 Key

在自己的可见终端中进入 Skill 目录，选择任意一家执行。程序隐藏输入 Key；`--verify` 保存后用一次真实搜索验证，可能产生 API 费用。

**DeepSeek**：从 [官方平台](https://platform.deepseek.com/api_keys) 创建 API Key。

```bash
python3 scripts/xcoze_search.py setup --provider deepseek --default --verify
```

**元宝**：在 [腾讯云元宝搜索控制台](https://console.cloud.tencent.com/wsapi/index) 开通服务，在“概览 → 服务 API KEY 方式”创建密钥。需要元宝搜索的服务 Key，不是腾讯云 SecretId/SecretKey 或其他模型产品 Key。

```bash
python3 scripts/xcoze_search.py setup --provider yuanbao --verify
```

macOS 也可双击 `scripts/setup.command`（或 `open -a Terminal scripts/setup.command`），选择供应商后输入密钥。Windows 没有 python3 时用 `py -3` 代替。

环境变量同样支持：`DEEPSEEK_API_KEY`、`YUANBAO_API_KEY`；元宝兼容官方示例变量 `TENCENTCLOUD_WSA_APIKEY`。由用户/密钥管理系统注入实际运行进程，不要将 Key 放进命令行参数、聊天或 Git。

配置以权限保护的明文保存在用户私有目录，不在安装包中。环境变量优先于已保存值；POSIX 目录/文件权限为 700/600，Windows 需核对用户目录 ACL。完整流程见 [配置与排错](references/setup.md)。

## 验证是否成功

```bash
python3 scripts/xcoze_search.py status
python3 scripts/xcoze_search.py doctor --provider deepseek
# 配置了元宝后再执行下面这条
python3 scripts/xcoze_search.py doctor --provider yuanbao
```

`status` 只检查本地配置，不代表服务已可用。对应供应商输出 `search_verified: true` 才表示本次取得有效搜索结果。只配置一家时就验证这一家；不用为了开始使用而配置两家。

## 在助手中使用

```text
用 xcoze search 搜索这个主题，优先原始来源，并给出链接。
用元宝搜索近七天的工业视觉相关公开报道。
用 DeepSeek 查找官方技术文档，并抓取关键页面正文。
用 DeepSeek 和元宝交叉搜索这条消息，比较时间和事实差异。
```

支持显式调用的助手中可以写 `$xcoze-search`。自动触发能力取决于宿主。首次密钥配置由你在本机终端完成，助手不应向你索取明文 Key。

## 命令行使用

以下命令在 Skill 目录执行；助手应使用脚本的绝对路径。

```bash
# 本地检查，不联网
python3 scripts/xcoze_search.py status

# 实测指定服务，可能计费
python3 scripts/xcoze_search.py doctor --provider deepseek
python3 scripts/xcoze_search.py doctor --provider yuanbao

# 默认源搜索，展示最多 5 条
python3 scripts/xcoze_search.py search '海上风电数字化' --count 5

# DeepSeek 站点过滤，并请求可用的正文
python3 scripts/xcoze_search.py search 'Search Fetch API' --provider deepseek --site api-docs.deepseek.com --need-content

# 元宝相对时间、站点筛选
python3 scripts/xcoze_search.py search '工业视觉' --provider yuanbao --freshness d7 --site qq.com

# 两家分别搜索，各展示最多 5 条，要求两家均已配置
python3 scripts/xcoze_search.py search '海上风电数字化' --provider both --count 5

# 仅 DeepSeek 支持网页正文抓取
python3 scripts/xcoze_search.py fetch 'https://api-docs.deepseek.com/guides/search/'
```

`auto` 规则：已保存默认源优先；未设置时，配置哪家就用哪家；两家都有时 DeepSeek 优先。不会遇错暗中切换到另一家。`--default` 只在 setup 中设置，不会因普通搜索改变配置。

`both` 仅适用共同参数。需要 DeepSeek `--need-content` 或元宝 `--freshness/--industry/--mode` 时分别调用，防止某一家的筛选条件被静默丢弃。

## 兼容边界

| 项目 | DeepSeek | 元宝 |
|---|---|---|
| 单 Key 搜索 | 支持 | 支持，需先开通服务 |
| 返回摘要 | 支持 | 支持 |
| 网页完整正文 | search 可按需返回；另有 Fetch | 本包不提供元宝 Fetch，动态摘要不等同正文 |
| 每次展示条数 | 1–50 | 1–50；请求超过 10 时按十位取整，受服务版本限制 |
| 特有参数 | need-content；查询中的 after:/before: 等 | freshness、industry、mode |
| 真实账号状态 | 2026-10-24 Search/Fetch 实测通过 | 待用户 doctor 验证 |

结果保留供应商和原始字段；两家相关性分数使用不同刻度，不混合排名。相同 URL 不删除内容版本。未知发布日期保持 null，检索时间单独记录。

失败有明确退出码；双源一家失败会保留另一家的结果，同时返回 `ok:false, partial:true`，不能宣称完成双源核实。空结果不证明事实不存在。见 [输出契约](references/output.md)。

## 数据与费用

查询/URL 会发送给用户选定的官方供应商；不要传入未经授权的私密信息或带令牌的链接。Key 仅用于固定官方接口，不跟随鉴权重定向。脚本不运行搜索结果中的代码，不自动保存搜索历史。

搜索、重试和 Fetch 可能产生 API 费用；both 分别按两家规则计费。程序不承诺免费，不自动充值，不调用额外聊天模型。定价、额度和服务条款以供应商平台为准。

## 开发与发布

以下命令在完整 GitHub 源码目录执行；精简 Skill ZIP 不含 tests、CI 和发布构建脚本。

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py --output-dir ../release
```

通用 Skill 包、源码包和 SHA-256 清单由打包脚本生成，排除配置、缓存与 macOS 元数据。这是通用 Agent Skills 包，商城专有字段按相应平台要求另行填写。详见 [发布指南](PUBLISHING.zh-CN.md) 和 [商城上架文案](MARKETPLACE.zh-CN.md)。

## 官方文档与许可

接口依据、差异与核对日期见 [providers.md](references/providers.md)。实现为本项目独立编写。

MIT License，Copyright (c) 2026 XCoze。供应商品牌仅用于说明兼容性；搜索结果内容的权利属于原权利人。

## English

xcoze search is an independent Agent Skill integrating the official DeepSeek Search/Fetch API and Tencent Yuanbao Search service-key API. Configure either provider with hidden local input, or inject `DEEPSEEK_API_KEY` / `YUANBAO_API_KEY`. Python 3.10+ and the standard library are sufficient.

Choose `deepseek`, `yuanbao`, `auto`, or explicitly `both`. It preserves source links and provider-native metadata; it does not compare scores across providers or describe Yuanbao dynamic summaries as page content. DeepSeek Fetch requires a DeepSeek key. DeepSeek Search/Fetch passed live account checks on 2026-10-24; Yuanbao live verification remains pending. This is not an official or endorsed DeepSeek/Tencent Skill.
