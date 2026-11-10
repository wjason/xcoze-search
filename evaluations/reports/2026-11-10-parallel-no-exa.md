# 接入 Parallel 后的 100 题无 Exa 对照

**简体中文** | [English](2026-11-10-parallel-no-exa.en.md)

2026-11-10 北京时间，同一环境对 [100 道题](../agent-search-cases-v3.json)各跑一轮。两轮均为免费模式，禁用 Exa 的两个入口和用户 Key，未调用宿主搜索。使用相同的查询、8 秒单源超时和前五条观察范围，本地浏览器均可作为末级兜底。两轮顺序执行并保留来源冷却。[逐题数据](2026-11-10-parallel-no-exa.data.json)

| 指标 | 接入前 | 接入后 |
|---|---:|---:|
| 返回候选 | 92/100 | 99/100 |
| 前五条命中预期域名 | 70/99 | 98/99 |
| 检索耗时中位数 | 2,267 ms | 980 ms |
| P95 耗时（最近秩） | 3,428 ms | 2,266 ms |
| 浏览器导航次数 | 46 | 1 |
| 公开 API HTTP 请求 | 103 | 103 |

Parallel 共收到 55 次请求，本轮未触发其限额。预期域名改善 28 题，前一轮已命中的题仍命中。域名只衡量来源覆盖。两轮均未找出 NASA 素材库的 JWST 深场图像，仍需专门核验。耗时包含本地浏览器启动和清理，受当时网络、搜索索引和冷却状态影响。

## 关键缺口核验

| 题目 | 接入前 | 接入后 |
|---|---|---|
| Python TaskGroup | 前五条为第三方讲解 | Python 官方 asyncio 文档第 2 条，可定位任务取消说明 |
| Kubernetes CPU requests / limits | 前五条为第三方文章 | 官方资源管理文档第 1 条 |
| 巨潮资讯贵州茅台 2024 年报 | 无候选 | 年报 PDF 第 1 条，封面确认证券代码 600519 和报告年度 2024 |
| B 站 Git rebase | 有视频候选 | 有视频候选，继续保持站点约束 |
| 小红书上海博物馆东馆 | 有站内链接 | 有站内链接，东馆笔记正文仍待核对 |

[Python 官方文档](https://docs.python.org/3/library/asyncio-task.html#task-groups) · [Kubernetes 官方文档](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) · [巨潮年报 PDF](https://static.cninfo.com.cn/finalpage/2025-04-03/1222993920.PDF)

匿名试探也测了 Mwmbl、Purili、Marginalia、Bing 浏览器和 Google 浏览器。Mwmbl 与 Purili 未补到抽查的目标，Marginalia 返回 429，Bing 未通过相关性检查，Google 返回验证页。Parallel 使用官方文档标记为 legacy 的匿名 Search MCP，限额与后续迁移仍需跟踪。Skill 只接入搜索，支持站点限制，并在本地再校验结果域名。结果中附带的摘录按摘录处理。[Parallel Search MCP](https://docs.parallel.ai/integrations/mcp/search-mcp)

## 复现

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v3.json --modes free --keyless --without-exa --live --limit 100 --max-requests 300 --timeout 8 --count 5 --output /tmp/xcoze-parallel-no-exa.json
```

接入前使用提交 `d263f7e`。接入后可用 `search '短查询' --provider parallel-free --strategy free --site 官方域名` 单测指定来源。
