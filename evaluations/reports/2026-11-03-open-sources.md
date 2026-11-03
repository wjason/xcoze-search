# 开放搜索源扩展与 Agent Reach 实现研究

**简体中文** | [English](2026-11-03-open-sources.en.md)

日期：2026-11-03。本轮查看 Agent Reach 1.6.1 的 Skill、本机 channels 和上游源码，基线提交为 `7a38047acf26a729cbb27851e3cb81639da86b29`。只做只读研究，没有运行其安装、更新或登录流程。本机 API 适配测试使用 Python 3.14.6、内存空凭据和 free 策略，不读取用户 Key 配置。完整[脱敏观察记录](2026-11-03-open-sources.data.json)保留成功、失败和修正后的复测，不含搜索摘录/正文。

## 产品定位和竞争边界

Agent Reach 的核心是平台动作与执行后端：通过统一命令声明 search/read/comments/subtitle 等操作，封装已有工具和公开接口，处理依赖、登录、浏览器、冷却及诊断。它的中文平台、视频和评论读取比 xcoze 当前更完整。单纯增加来源数量，不能据此宣称整体超过它。

xcoze search 继续定位为 **Agent 的聚合搜索与证据获取入口**：基础安装即可联网，用户不选模式；需要专用公开索引时直接选路，有 Key 时允许商用源参与，保留用户的效果/平衡/免费设置。以同题的信息支持度、原始来源、时效、完成任务的时间和费用衡量改进。平台内容深度缺口优先复用本机已有授权工具，后续再决定是否做独立适配。

| 方面 | Agent Reach 1.6.1 源码/声明 | xcoze 本轮完成 | 判断 |
|---|---|---|---|
| 组织方式 | Channel → Action → 有序 Backend | 任务 → 原生公开索引/通用免 Key/已配置 API；新增离线平台清单 | 借鉴能力声明，保留聚合搜索核心 |
| 搜索与阅读 | Web 使用 Exa MCP，Jina/Exa 阅读 | 同样有这些入口，另接 9 个公开平台索引及 6 家带 Key 服务 | 免 Key Web 不是独有引擎 |
| 平台深度 | 视频、字幕、部分评论、职位等独立动作 | 原生检索/元数据为主；新增来源不包含评论树、字幕或模型下载 | Reach 目前更完整，不能把定向搜索算作等价覆盖 |
| 访问和诊断 | 维护后端健康、平台冷却、动作实测及浏览器状态 | 新来源跨进程串行、限频/退避；platforms 区分声明/程序存在与实测 | 已实现基础限频，未实现完整历史健康学习 |
| 安装 | Python 依赖，按渠道装工具/浏览器；管理流程较完整 | Python 标准库基础包，不自动装工具或复制登录态 | 两种安装范围不同，不作绝对优劣判断 |
| 成本 | 多数读取无 API Key；转录等动作可用带 Key 服务 | 搜索策略边界、HTTP/时间预算、已知/未知费用分开记录 | 免费搜索不代表任何动作都无成本 |

源码证据：[渠道与动作定义](https://github.com/Panniantong/Agent-Reach/blob/7a38047acf26a729cbb27851e3cb81639da86b29/agent_reach/channels/base.py)、[执行调度](https://github.com/Panniantong/Agent-Reach/blob/7a38047acf26a729cbb27851e3cb81639da86b29/agent_reach/runtime/dispatch.py)、[Web 后端](https://github.com/Panniantong/Agent-Reach/blob/7a38047acf26a729cbb27851e3cb81639da86b29/agent_reach/channels/web.py)、[安装依赖](https://github.com/Panniantong/Agent-Reach/blob/7a38047acf26a729cbb27851e3cb81639da86b29/pyproject.toml)、[平台动作表](https://github.com/Panniantong/Agent-Reach/blob/7a38047acf26a729cbb27851e3cb81639da86b29/agent_reach/channels/__init__.py)。本项目按自己的既有接口实现本轮能力，没有将 Reach 变成运行依赖。

## 九个新增免 Key 适配器

以下为真实适配器路径的单次观察；每题最多三条。时长包含脚本内等待和检索，不含启动与答案生成。不能由少量 HTTP 成功推出整体准确率。

| 来源 | 查询 | 本次结果 | 耗时 |
|---|---|---|---:|
| Wikipedia 中文 | 风力发电 | 3 条中文百科结果 | 0.83 秒 |
| Wikipedia 英文 | retrieval augmented generation | 冷却修正后 3 条英文结果 | 0.78 秒 |
| Stack Exchange | asyncio TaskGroup | 3 个相关问题，未读取答案 | 0.37 秒 |
| arXiv | 2026 年 RAG 论文 | 3 条预印本记录与摘要，提交日期落在限定范围 | 0.55 秒 |
| Crossref | Attention Vaswani | 3 条同名 DOI 记录；未完成目标论文作者/出版身份核验 | 1.22 秒 |
| npm | playwright | Playwright 及相关包；版本为当日注册表元数据 | 0.52 秒 |
| crates.io | tokio | Tokio 及相关包；保留稳定/最高版本区别 | 0.54 秒 |
| GitLab.com | inkscape | 星标排序后官方 Inkscape 仓库居首 | 0.73 秒 |
| Europe PMC | 2026 年 protein structure prediction | 3 条文献/预印本记录及摘要 | 0.90 秒 |
| Hugging Face | Qwen | 3 条公开模型元数据，不是“最新模型”排名 | 见逐次记录 |

最初直接探测九条端点请求均有结果；适配器首轮发生一次本地 Wikipedia 短冷却失败，实际 HTTP 8 次。修正为最多 3 秒、受网络剩余预算约束的短等待后，连续中英文复测都通过（2 次 HTTP）；Hugging Face 补测 1 次。适配器验证合计 11 次 HTTP，失败的本地冷却不计请求。所有调用均无用户 Key；模型/宿主费用未测量。

GitLab 原默认项目 ID 排序返回多个新建镜像，不能用非空结果作为完成标准。本轮改用 star_count 排序，当前样例返回 `inkscape/inkscape`；星标仍不能证明官方身份。Crossref 标题相同但 DOI 不同，记录成功不等于认定找到某篇原论文，仍需核对作者、年份和出版渠道。

具体参数、日期含义、官方文档、许可和范围见[开放来源说明](../../references/open-sources.md)。新增的都是垂直索引，不会对普通问题无差别广播。已有 GitHub/HN 继续保留；免 Key 适配器共 15 个，其中 14 个可搜索，Jina 为纯读取。与 Reach 的渠道数不能直接比较。

## 同题对照揭示的实际问题

固定技术查询 `Python asyncio TaskGroup ExceptionGroup official documentation`，再读取官方 asyncio-task 页面。每条路径只执行一次，搜索先 Reach、阅读先 xcoze；两者共享上游，缓存/网络足以影响耗时，不形成排名。

| 动作 | Agent Reach | xcoze 默认 | 本轮修正后的 xcoze |
|---|---|---|---|
| Web 搜索 | Exa，3 条，1.48 秒 | Exa，命中相同三条 URL，0.62 秒 | 不据此宣称检索质量胜出 |
| 读取官方页 | Jina，67841 字符，1.75 秒 | Jina，24000 字符，明确截断，1.19 秒 | --max-characters 100000，返回 67841 字符，0.64 秒 |

默认截断会影响长文后半部分，已增加按需扩大读取。默认仍为 24000，避免每次给 Agent 整篇长文；缺少所需段落才在任务预算内再读，最大 200000。`truncated:false` 只表示未被本机裁剪且未触及已知上限，`completeness_verified:false` 仍保留，不声称页面、动态内容或所有附属内容已完整取得。

Reach Web 以 text 返回内容，xcoze 继续区分摘要、正文、摘要型论文内容、问题摘录、包/模型/仓库元数据。平台目录将 B 站、YouTube、小红书等标成 public_index_only，不能把关键词搜索说成字幕或评论已经读取。本机有 Reach/yt-dlp/gh/agent-browser 时仅离线报告存在，由 Agent 按各自 Skill 和用户授权使用；没有内置执行桥接。

## 接下来如何做到更好

1. **完成任务而非增加计数**：扩展同题集到中文新闻/政策、文档、软件生态、社区、视频等场景，分别评审检索与原文/评论/字幕证据是否满足问题。先建立共同测试，再讨论是否领先。
2. **按动作验收**：查询命中、正文、评论树、字幕、时间边界分开验收，优先修复用户实际遇到的缺口。滚动 N 天按真实时间剔除日期接口多取的边界记录。
3. **减少无用调用**：完善来源健康记录与任务级成本统计；保留显式免费边界和用户指定，评估结果缓存时明确数据新鲜度及失效机制。
4. **平台深度扩展**：先使用已有授权工具；再评估只读、可选、可卸载的适配器。平台限流/验证时停止，不换身份重试；未登录平台不强制登录。
5. **保持安装简单**：基础包不引入浏览器/Node 依赖。对需要额外依赖的扩展单独说明，不让普通搜索承担所有平台成本。

以上包含后续待办，当前不宣称全平台、字幕/评论或整体质量已经超过 Reach。当前验收为 120 项离线测试、公开接口实际调用及有限同题对照；没有跨网络长期可用性或盲评证据。

## 复现

```bash
python3 scripts/benchmark.py --corpus evaluations/open-source-cases.json --modes free --limit 10 --count 3 --output ../open-plan.json
python3 scripts/benchmark.py --live --corpus evaluations/open-source-cases.json --modes free --limit 10 --count 3 --max-requests 20 --output ../open-live.json
```

默认不读凭据、不联网。--live 会搜索公开平台；不要把未脱敏的本地报告直接公开。语料日期固定，后续运行应更新日期并另存报告。
