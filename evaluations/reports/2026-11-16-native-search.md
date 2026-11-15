# 官方文档与国内站内检索实测

**简体中文** | [English](2026-11-16-native-search.en.md)

2026-11-16，北京时间。本轮新增 Kubernetes、Go、Rust 官方文档检索，以及巨潮公告、国家统计局站内检索。所有新入口都不要求用户 Key，也不依赖 Exa、Parallel、宿主搜索或浏览器。[逐题结果、原文核验与失败记录](2026-11-16-native-search.data.json)

## 专项检索

| 入口 | 题目 | 预期页面在前五条中的位置 |
|---|---|---|
| Kubernetes 官方导航 | CPU requests/limits 与内存；探针；持久卷回收；NetworkPolicy | 第 2、1、1、1 条 |
| Go 标准库符号搜索 | WithCancelCause；Server.Shutdown；Decoder.DisallowUnknownFields；errors.Is | 均为第 1 条 |
| Rust 标准库条目 | OnceLock；PoisonError；HashMap | 均为第 1 条 |
| 巨潮公告 | 贵州茅台 2024 年报；上市公司年报；宁德时代 2025 年报 | 均返回相关公告；两道指定公司年报位于第 1 条 |
| 统计局站内搜索 | GDP；2026 年 9 月 CPI；2026 年 10 月 PMI | 均返回统计局发布；修正后 CPI 标题与所问月份一致 |

17 道专项题均返回了满足上述定位条件的候选。文档检索多数约 0.2–1.2 秒；国内站内检索约 0.3–2.4 秒，个别统计局请求曾耗时约 7 秒。耗时包含本机限频等待，不包含回答生成与后续原文阅读。

Kubernetes 使用文档导航的标题和链接匹配，不是官方 Pagefind 全文搜索；资源管理题的正确页面排第 2。Rust 先定位类型，再读其方法，不拼造方法锚点。Go 只保留网站标为标准库的结果，第三方包不会冒充 Go 官方 API。

## 原文与日期核验

核对了 16 份原文：11 个技术文档页面、3 个统计局页面和 2 份年报 PDF 首页。页面包含所需 API 或主题标记，贵州茅台首页确认了公司、2024 年和年度报告。宁德时代的结果为港股版繁体年报：首页代码为 3750，搜索元数据代码为 `03750`，报告年度为 2025；没有将它当作 A 股报告。

检索元数据保留证券代码、市场和发布日期。年报年度不等于发布日期；统计局页面发布日期不等于所述统计期。核验限于所需页面、标记与年报首页，不是整份报告或所有统计数值的事实审计。

## 100 题：Exa 与 Parallel 同时不可用

同一份 [100 题](../agent-search-cases-v3.json)，免费模式、前五条、8 秒单源超时，禁用 Exa 两个入口、Parallel、带 Key 服务和本地浏览器。基线路由取自 `136e015`，两版使用同一更新后的评测工具；最终回放沿用基线的来源冷却。宿主搜索没有参与运行。

| 指标 | 调整前 | 最终回放 |
|---|---:|---:|
| 返回候选 | 56/100 | 65/100 |
| 前五条命中预期域名 | 55/99 | 63/99 |
| 检索耗时中位数 | 374 ms | 370 ms |
| P95 | 2,328 ms | 1,719 ms |
| API HTTP 尝试 | 105 | 103 |
| Exa / Parallel / 带 Key 请求 / 浏览器导航 | 均为 0 | 均为 0 |

Kubernetes、Go、Rust 三道原缺口题均由新入口取得预期官方页面，贵州茅台年报题取得目标 PDF，统计局题转为站内检索。域名命中只表示来源覆盖，不是答案准确率；网络波动、冷却和索引更新仍会影响复现。中间回放及失败记录保留在数据文件中。

仍有 35 道题无候选，主要涉及部分法律和标准网站、社区索引、公共数据及其他官方技术文档。本轮解决的是已有题集中的上述目标，不代表已获得稳定、无限额的全网免费搜索。

## 根据实测修正的问题

- 裸搜 `Shutdown` 曾落到 `syscall.Shutdown`；现在保留包名和所属类型，搜索 `http.Server.Shutdown`。JSON Decoder 方法做了同样修正。
- 巨潮的仅标题检索找不到完整年报问题，改用网页公开的全文索引；“上市公司”查询使用公开股票类别，避免基金、债券报告混入。
- 统计局的 10 月 CPI 曾排在 9 月问题前面；现在排除标题中明显冲突的月份，再优先排列标题与主题匹配的结果。摘要中的对比月份不会替代标题统计期。
- 固定文档索引不保证指定版本；版本、语言、日期等不支持的约束会排除来源或报错，不默默删条件。

## 接入范围和复现

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v3.json --modes free --keyless --without-exa --without-parallel --browser off --live --limit 100 --max-requests 300 --timeout 8 --count 5 --output /tmp/xcoze-native-100.json
```

新适配使用站点已公开的导航、条目或搜索入口，代码独立实现。相关来源：[Kubernetes 文档](https://kubernetes.io/docs/concepts/)、[Go 搜索说明](https://pkg.go.dev/search-help)、[Rust 标准库条目](https://doc.rust-lang.org/std/all.html)、[巨潮网站](https://www.cninfo.com.cn/)、[统计局搜索页面](https://www.stats.gov.cn/search/s?qt=%E5%9B%BD%E5%86%85%E7%94%9F%E4%BA%A7%E6%80%BB%E5%80%BC)。统计局所用第三方后端及边界见[国内站内检索](../../references/china-site-search.md)。

中国政府网的全站搜索页面也作了检查，但尚未完成其调用协议适配，不计为新增可用入口。已有的政府网近期栏目功能保持原范围。
