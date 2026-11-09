# Agent 搜索评测与原文核验

**简体中文** | [English](2026-11-09-agent-search.en.md)

2026-11-09（北京时间）在同一网络顺序执行。保留第一版的 8 题并新增 12 题，每题用免费模式和无 Key Smart 各检索一次。两种模式均走免 Key 路由。

[题集](../agent-search-cases-v2.json) · [逐题数据](2026-11-09-agent-search.data.json) · [上一轮](2026-11-08-agent-search.md)

从每题前五条结果中选择可回答问题的证据，另行打开发布方页面、原始文档或 API 核验。原文支持判为通过；只找到官方入口但仍缺最新一条时判为部分通过；目标未出现在前五条判为漏检，另列核验参考。新闻按近 7 天核对；发布日期、首次提交、修订时间和统计期分别记录。分数评价这轮检索提供的证据。

| 指标 | 免费 | Smart（无 Key） |
|---|---:|---:|
| 有返回结果 | 20/20 | 20/20 |
| 通过原文核验 | 17/20 | 17/20 |
| 部分通过 | 1/20 | 1/20 |
| 漏检 | 2/20 | 2/20 |
| 检索耗时中位数 | 1051 ms | 911 ms |

共 40 次免 Key HTTP 请求。耗时只计脚本检索；原文核验为另行操作，未计入耗时。单次运行的耗时受网络和服务端影响。付费模式留待具备可用额度时单独评测。

| 题目 ID | 前五条判断 | 免费 / Smart 证据排名 | 核验记录 |
|---|---|---|---|
| `cn-energy-policy` | 通过 | 1 / 1 | 能源局网站转载《经济日报》的报道，页面标明 2026-07-10。 [核验来源](https://www.nea.gov.cn/20260710/2706be51a7f1446a90658328d1c245d4/c.html) |
| `cn-statistics` | 部分通过 | 1 / 1 | 返回官方栏目，最前面的具体数据稿是 10 月 19 日。11 月 9 日发布的 CPI 原稿由另外的核验找到。 [核验来源](https://www.stats.gov.cn/sj/zxfbhjd/202611/t20261109_1965795.html) |
| `cn-news` | 通过 | 3 / 3 | 界面新闻原页显示 11 月 9 日 08:15，落在本轮采用的近 7 日范围。 [核验来源](https://www.jiemian.com/article/15308219.html) |
| `python-taskgroup` | 通过 | 1 / 1 | 官方文档说明任务异常时如何取消其余任务，并汇总异常。 [核验来源](https://docs.python.org/3/library/asyncio-task.html#task-groups) |
| `github-markitdown` | 通过 | 1 / 1 | Microsoft 仓库的 README 确认项目用于将多种文件转换为 Markdown。 [核验来源](https://raw.githubusercontent.com/microsoft/markitdown/main/README.md) |
| `research-rag` | 通过 | 1 / 1 | 图像生成方向的检索增强论文，6 月 8 日首次提交，6 月 14 日修订。 [核验来源](https://arxiv.org/abs/2506.06962v3) |
| `financial-disclosure` | 通过 | 3 / 3 | PDF 封面确认是同方股份 2025 年年度报告。 [核验来源](https://static.cninfo.com.cn/finalpage/2026-04-29/1225244797.PDF) |
| `community-hn` | 通过 | 1 / 1 | HN 原帖是 SQLite 讨论，日期为 2021-05-02。题目无近期要求。 [核验来源](https://news.ycombinator.com/item?id=27016630) |
| `nbs-cpi-oct` | 通过 | 1 / 1 | 国家统计局原稿发布于 11 月 9 日 09:30，统计期为 2026 年 10 月。与官方发布日程一致。 [核验来源](https://www.stats.gov.cn/sj/zxfb/202611/t20261109_1965795.html) |
| `python-release` | 通过 | 1 / 1 | 正式版发布于 2025-10-07。 [核验来源](https://www.python.org/downloads/release/python-3140/) |
| `pep703` | 通过 | 1 / 1 | PEP 703 提议将 GIL 设为可选，官方状态为 Final。 [核验来源](https://peps.python.org/pep-0703/) |
| `sqlite-release` | 通过 | 1 / 1 | 官方记录显示 3.45.0 发布于 2024-01-15。 [核验来源](https://www.sqlite.org/releaselog/3_45_0.html) |
| `crossref-deep-learning` | 漏检 | — / — | 两种模式前五条都没有目标 DOI。期刊原文确认在线发表日为 2015-05-27，期刊期次日期为次日。 [核验来源](https://doi.org/10.1038/nature14539) |
| `arxiv-rag-version` | 通过 | 3 / 3 | 同一论文的 v1 提交于 2020-05-22，v4 修订于 2021-04-12。 [核验来源](https://arxiv.org/abs/2005.11401v4) |
| `npm-typescript` | 通过 | 1 / 1 | npm 注册表确认包名为 typescript，仓库为 microsoft/TypeScript。 [核验来源](https://registry.npmjs.org/typescript/latest) |
| `us-ai-rfi` | 漏检 | — / — | 两种模式前五条均没有 2025-02305。政府印刷局原文确认 2025-02-06 发布。 [核验来源](https://www.govinfo.gov/content/pkg/FR-2025-02-06/html/2025-02305.htm) |
| `worldbank-pop` | 通过 | 1 / 1 | 重放查询核对世界银行 API，首条有效数据对应 2025 观察年。 [核验来源](https://api.worldbank.org/v2/country/CN/indicator/SP.POP.TOTL?format=json&per_page=5) |
| `mdn-abort` | 通过 | 1 / 1 | MDN 文档确认超时参数以毫秒计。 [核验来源](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static) |
| `nasa-artemis` | 通过 | 3 / 3 | NASA 原始媒体索引确认该项是 2022-11-16 的发射图片。 [核验来源](https://images-api.nasa.gov/search?nasa_id=NHQ202211160030) |
| `wikipedia-utc` | 通过 | 1 / 1 | 链接指向要求的中文条目。 [核验来源](https://zh.wikipedia.org/wiki/%E5%8D%8F%E8%B0%83%E4%B8%96%E7%95%8C%E6%97%B6) |

## 复现

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v2.json --modes free,smart --keyless --live --limit 20 --max-requests 120 --timeout 8 --count 5 --output /tmp/xcoze-agent-search.json
```
