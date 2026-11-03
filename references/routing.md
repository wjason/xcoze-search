# 自动调度与平台范围

**简体中文** | [English](routing.en.md)

## 默认和覆盖关系

正常提问触发 Skill，Agent 不要求用户指定模式。运行 `search` 的 `--provider` 默认为 auto。优先级是本次明确的来源/策略、已保存偏好、默认 Smart。显式来源优先于已保存模式；本次同时指定 free 和带 Key 来源则报冲突。

Smart 在有格式有效且未禁用的 Key 时选择 quality，否则选择 free。格式有效不证明网络、余额或账号权限。quality 在没有 Key 时也能使用免 Key 路径。preferences 只修改本机配置，不联网，不修改任何 Key；旧配置扩展字段保持保留。

| 策略 | 通用搜索候选顺序 |
|---|---|
| quality | 首个已配置源、Exa 免 Key、其余已配置源，再到 Bing/DDG |
| balanced | Exa 免 Key、已配置来源，再到 Bing/DDG |
| free | Exa 免 Key、Bing、DuckDuckGo；排除带 Key 适配器 |

GitHub 仓库、HN 帖子定向任务优先平台适配器。已保存的默认来源可优先；已禁用来源不会自动启用。初始排序是可解释的启动规则，不是查询质量实测排名。暂不持久学习历史成功率。

## 脚本与 Agent 分工

脚本先校验条件，自动候选不兼容时记录 skipped_incompatible，不静默丢弃日期、站点等限制。显式多源任何一家不兼容则整体在联网前报错。脚本不自动把 freshness 等原生筛选词转换为另一家的不同语义；跨源时间条件优先使用支持的 start/end-date 或由 Agent 分别查询。

自动搜索最多尝试 2 个来源（可配置 1–3），默认总时间 45 秒。这是调度等待预算，不是对 DNS/网络读取的硬进程截止；每次发起网络调用前检查剩余时间并裁剪请求超时，自动来源零重试；HTTP 次数仍由 max-requests 限制。普通任务在成功非空时返回；quality 的 reference/current 通用任务最多再查一个候选，累积两家结果，第二家失败仍保留第一家结果和错误。GitHub/HN 专用选路、显式来源、免费/平衡模式不强制补充。errors 保留失败历史。Agent 再判断相关性、时间、信息覆盖与来源独立性，按缺口选择剩余候选或改写查询。语义核实不由脚本评分替代。

脚本不跨命令累计金额或等待预算；Agent 需要累计整项任务实际次数。没有质量保证、跨源统一分数、实时行情保证或索引延迟承诺。查询失败时备用成功可以改善可用性，但不能证明事实正确。

## 任务意图与内容核验

`--intent auto|general|reference|current` 为调用级意图，默认 auto。查询中的最新/近期/current/LTS 等词识别为 current，官方/计费/docs/API 等词识别为 reference；其余 general。Agent 应从原问题补充意图，避免短查询丢失用户的时间/官方资料要求。用户不需要选择意图。意图不会放宽约束、启用禁用源、跨越免费模式或增加既有预算。

`routing.intent`、`specialized_source` 和 `complementary_search` 说明补充策略是否启用；实际尝试以 requests 为准。两家结果仍按来源顺序保留，不比较原生评分；重复 URL 仅标记。第二源可能不是独立索引，也不保证消除错误。

实验性 Bing/DDG 的非空结果若与至少两个有效拉丁主题词完全不重合，报告 irrelevant_results 并允许有限备用。此检查跳过纯中文、短查询，不是相关性分类器。价格、最新版本、规则及内容冲突继续读当前官方页面；官方域名不保证摘要实时。

[真实任务实测与取舍](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03.md)。

## 扩展平台

Wikipedia、Stack Exchange、arXiv、Crossref、npm、crates、GitLab、Europe PMC、Hugging Face 按 --platform 或兼容站点优先对应公开接口。成功的原生选路不强制双源，不支持的日期/语言仍预检拒绝或记录跳过。platforms 完全离线，不读 Key、不执行外部工具。新增视频/社区 scope 仅为公开索引。参数、已有工具协作与冷却规则见[开放来源](open-sources.md)。

## 平台覆盖

| 目标 | 适配范围 | 不承诺 |
|---|---|---|
| GitHub | 公开仓库搜索，读取默认 README | 代码搜索、私有仓库、完整 Issue/PR 接入 |
| HN | Algolia 帖子检索，官方接口读取单条帖子/评论 | 自动读完评论树、已阅读外链文章 |
| 知乎 | 公开索引定向查询 | 任意回答正文、完整站内搜索与评论 |
| 小红书 | 公开索引定向查询 | 登录后站内排序、图片理解、笔记和评论完整读取 |
| 微博 | 公开索引定向查询 | 官方实时热搜或完整评论流 |

站点限定返回还校验 URL 主机，域名出现在路径里不算命中。公开索引可能没有相关内容。用户需要站内动作时，Agent 可使用已有授权的平台工具（例如环境中已安装的 Agent Reach），但本项目不把它作为依赖，也不自动复制登录态或安装浏览器。

## 读取与费用

`fetch auto` 对仓库根链接尝试 GitHub README，对 HN item 尝试官方读取；通用 URL 优先 Jina Reader；允许商用时优先以已配置 Fetch 服务备用，再考虑 Exa 免 Key MCP。默认来源数上限仍生效，未尝试到的候选不代表可用或不可用。宿主已经能读取时不必再调用脚本。

免 Key 不等于本地执行所有服务：Bing、DuckDuckGo、Exa、GitHub、Algolia/HN、Jina 都会收到相应请求。Exa 免 Key 与 Jina Reader 是商业服务提供的限额入口。免费策略只保证本工具不发送带用户 Key 的服务请求，不承诺模型/宿主订阅和本机计算零成本。

## 管理示例

```bash
python3 scripts/xcoze_search.py preferences
python3 scripts/xcoze_search.py preferences --strategy free
python3 scripts/xcoze_search.py preferences --strategy balanced --max-sources 2
python3 scripts/xcoze_search.py preferences --provider deepseek
python3 scripts/xcoze_search.py preferences --disable duckduckgo
python3 scripts/xcoze_search.py preferences --enable duckduckgo
python3 scripts/xcoze_search.py preferences --reset
python3 scripts/xcoze_search.py plan '工业视觉' --platform github
python3 scripts/xcoze_search.py search '工业视觉' --provider yuanbao
```

显式 source 不自动备用；both 和逗号列表的已有语义保留。auto 和默认 fetch 在 v0.4.0 改变，需要固定旧行为的调用方应显式指定来源。
