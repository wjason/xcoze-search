# xcoze search

[![Tests](https://github.com/wjason/xcoze-search/actions/workflows/test.yml/badge.svg)](https://github.com/wjason/xcoze-search/actions/workflows/test.yml)

我把 DeepSeek 和元宝的搜索接口接进了同一个 Skill，叫 **xcoze search**。你可以只配置其中一家，也可以配好两家的 Key，在需要时一起搜索。

搜索请求直接发给 DeepSeek 或腾讯云，不经过我的服务器。另外，我接入了 DeepSeek 的网页抓取接口，搜索之后还可以继续读原文。

这是我自己维护的开源项目，使用两家的官方 API，并非 DeepSeek 或腾讯官方发布的 Skill。

## 安装

准备好 **Python 3.10 或更新版本**，不需要另外安装 Python 依赖。你的助手需要支持 Agent Skills，并且能够运行本地 Python 脚本。

如果电脑上有 Node.js，可以用下面这条命令安装，在安装器里选择你使用的助手：

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

也可以直接下载 [v0.1.0 的 Skill 安装包](https://github.com/wjason/xcoze-search/releases/download/v0.1.0/xcoze-search-skill-v0.1.0.zip)。解压后，把 `xcoze-search` 文件夹放到助手的技能目录。Codex 默认使用 `~/.codex/skills/`，最终路径应当是：

```text
~/.codex/skills/xcoze-search/SKILL.md
```

注意别多套一层同名文件夹。装好后新开一轮对话，如果还没出现，就重新启动助手。其他助手的目录设置可以看 [安装说明](INSTALL.zh-CN.md)。

<details>
<summary>手动从 GitHub 安装到 Codex</summary>

确认目标目录还没有安装这个 Skill，然后执行：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/wjason/xcoze-search.git ~/.codex/skills/xcoze-search
cd ~/.codex/skills/xcoze-search
```

如果设置过 `CODEX_HOME`，请把安装位置换成它下面的 `skills` 目录。已有安装的升级方法见 [安装说明](INSTALL.zh-CN.md#升级与卸载)。

</details>

## 填入你的 Key

下面两种选一种就能开始用。想用双源搜索，再把另一家的 Key 配上即可。

先在自己的终端里进入 Skill 的实际安装目录。手动按上面的路径安装到 Codex 时，可以执行：

```bash
cd ~/.codex/skills/xcoze-search
```

### DeepSeek

在 [DeepSeek 平台](https://platform.deepseek.com/api_keys) 创建 API Key，然后运行：

```bash
python3 scripts/xcoze_search.py setup --provider deepseek --default --verify
```

按提示粘贴 Key，回车就行。输入时不会显示字符，这是正常的。`--default` 会把 DeepSeek 设为默认搜索源；`--verify` 会在保存后试一次搜索，可能产生 API 费用。

### 元宝

在 [腾讯云元宝搜索控制台](https://console.cloud.tencent.com/wsapi/index) 开通服务，再到“概览 → 服务 API KEY 方式”创建 Key，然后运行：

```bash
python3 scripts/xcoze_search.py setup --provider yuanbao --verify
```

这里要填的是 **元宝搜索的服务 API Key**。腾讯云的 SecretId、SecretKey，以及其他模型产品的 Key 不能混用。

macOS 也可以双击 `scripts/setup.command`，按提示选一家再输入 Key。Windows 如果没有 `python3` 命令，可以把它换成 `py -3`。

我没有把 Key 做成命令行参数，配置时请在自己的终端里输入，不要发到聊天或提交到 Git。Key 以明文保存在本机用户配置目录，macOS/Linux 下会限制目录和文件权限；详情见 [配置说明](references/setup.md)。

### 已经用环境变量管理 Key？

也可以直接用下面这些变量，不必重复运行 setup。环境变量优先于本机保存的配置，记得让运行助手的进程能够读到它。

| 搜索源 | 环境变量 |
|---|---|
| DeepSeek | `DEEPSEEK_API_KEY` |
| 元宝 | `YUANBAO_API_KEY`，也兼容 `TENCENTCLOUD_WSA_APIKEY` |

## 怎么用

配好之后，直接在助手里说：

```text
用 xcoze search 搜索这个主题，给我原始来源链接。
用元宝搜索近七天的工业视觉行业报道。
用 DeepSeek 找一下这个接口的官方文档，再读一下原文。
用 DeepSeek 和元宝一起查这条消息，看看信息有没有出入。
```

支持显式调用的助手也可以用 `$xcoze-search`。是否会自动选中这个 Skill，取决于你使用的助手。

我保留了每条结果的来源、日期和供应商信息。两家返回同一个页面时，也会保留各自的摘要，方便继续比对。搜索能帮你找到材料；重要结论还是需要回到原文核对。

## 两家有什么区别

| | DeepSeek | 元宝 |
|---|---|---|
| 网页搜索 | 支持 | 支持 |
| 指定站点 | 支持 | 支持；垂直信息卡片可能不受站点条件限制 |
| 时间筛选 | 在搜索词中使用 `after:` / `before:` 等语法 | 用 `--freshness d7` 等参数 |
| 网页正文 | 可以请求搜索结果正文，也可以单独 Fetch | 返回标准摘要或动态摘要 |
| 其他选项 | `--need-content` | `--industry`、`--mode` 等，取决于服务版本 |

元宝返回的动态摘要不等于网页全文，所以我把它和正文分开存放。两家的评分刻度也不同，结果会保留各自的顺序，不拿分数直接混排。

`auto` 默认先用你设好的搜索源；没设默认源时，只配哪家就用哪家，两家都配了则优先用 DeepSeek。请求失败会报错，不会自动换一家再发送你的问题。

`both` 会分别调用两家。它只接受共同支持的参数；想用 DeepSeek 的正文选项或元宝的时间、垂域、模式选项时，请分开搜索。

## 想直接跑命令

以下命令都在 Skill 目录下执行。

```bash
# 用默认搜索源，最多显示 5 条结果
python3 scripts/xcoze_search.py search '海上风电数字化' --count 5

# DeepSeek：限定站点，并请求可用的正文
python3 scripts/xcoze_search.py search 'Search Fetch API' --provider deepseek --site api-docs.deepseek.com --need-content

# 元宝：查近七天的结果
python3 scripts/xcoze_search.py search '工业视觉' --provider yuanbao --freshness d7

# 两家一起查，每家最多显示 5 条
python3 scripts/xcoze_search.py search '海上风电数字化' --provider both --count 5

# 用 DeepSeek 抓取一个公开网页
python3 scripts/xcoze_search.py fetch 'https://api-docs.deepseek.com/guides/search/'
```

`--count` 是每家显示的条数，最多 50 条。元宝请求超过 10 条时会按十位向上取整，再截取你需要的数量，能否使用取决于账号版本。DeepSeek 查询最多 128 个 Unicode 字符，元宝在这个工具里限制为 1500 个 UTF-8 字节；问题太长时需要拆开查。

命令返回 JSON。双源搜索有一家失败时，成功那家的结果会保留，同时返回 `ok:false`、`partial:true` 和错误信息。需要接到自己的程序里时，可以看 [输出字段说明](references/output.md)。

## 没搜出来，怎么检查

先看看本机配置：

```bash
python3 scripts/xcoze_search.py status
```

再对已经配好 Key 的那一家做一次实际搜索：

```bash
python3 scripts/xcoze_search.py doctor --provider deepseek
# 如果配的是元宝，就用这条
python3 scripts/xcoze_search.py doctor --provider yuanbao
```

`status` 不联网，只检查配置。`doctor` 返回 `search_verified: true`，才说明这次确实拿到了搜索结果。遇到 Key 无效、服务未开通、余额不足或限流，可以对照 [配置与排错](references/setup.md) 处理。

## 目前测到哪一步

我在 2026 年 10 月 24 日用真实账号跑通了 DeepSeek 的搜索和网页抓取。元宝的接口适配和离线测试已经写好，**真实账号调用还没有验证**，所以 v0.1.0 先作为预览版发布。

25 项离线测试已通过，GitHub Actions 也跑过了 Windows/Linux、Python 3.10/3.12 四组检查。它们能检查程序和接口适配逻辑，不能替代你自己的账号、额度和实际搜索效果验证。具体记录放在 [VALIDATION.md](VALIDATION.md)。

## 费用和数据

API 费用由 DeepSeek 或腾讯云按各自规则收取；双源搜索会调用两家，重试和网页抓取也可能计费。使用前请确认自己的账号额度。

查询内容会发送给你选中的供应商，网页抓取会把 URL 发给 DeepSeek。不要把不方便外传的内容或带访问令牌的链接放进查询。

这个项目没有中转服务器，不收集遥测，也不自动保存搜索历史。密钥只用于固定的官方接口，带鉴权的请求不会跟随重定向。程序不会额外调用聊天模型。

## 源码与文档

我把接口依据和两家参数的差异放在 [接口说明](references/providers.md) 里。想修改代码，可以在完整源码目录运行测试：

```bash
python3 -m unittest discover -s tests -v
```

打包命令是：

```bash
python3 scripts/build_release.py --output-dir ../release
```

完整源码包含测试、CI 和打包脚本；Skill 安装包只保留使用所需的内容。后续发布和商城上架可以参考 [发布说明](PUBLISHING.zh-CN.md) 与 [商城介绍](MARKETPLACE.zh-CN.md)。

项目使用 [MIT License](LICENSE)。DeepSeek、腾讯元宝的名称用于说明接口兼容性，搜索到的内容归原作者所有。
