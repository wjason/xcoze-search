# 100 道搜索题基线与复测

**简体中文** | [English](2026-11-09-100-question-baseline.en.md)

2026-11-09 北京时间，同一网络先用免费模式跑完 100 道题，再复测受改动影响的 6 道题，另抽查 6 道无 Key Smart。每题最多取五条结果。[题集](../agent-search-cases-v3.json) · [逐题记录](2026-11-09-100-question-baseline.data.json)

| 基线指标 | 结果 |
|---|---:|
| 返回候选 | 100/100 |
| 前五条命中预期域名 | 97/99 |
| 检索耗时中位数 | 966 ms |
| 检索耗时 P95（最近秩） | 2,606 ms |
| 免 Key HTTP 请求 | 104 |

一题未预设域名。建筑节能规范与电力需求侧管理两题缺少预期域名。域名检查只衡量候选来源。100 道题的逐题原文和时效核验仍待完成，原有 [20 道原文核验报告](2026-11-09-agent-search.md)单独保留。耗时仅计脚本内检索。Europe PMC 与世界银行各有一题发生网络错误，随后取得备用结果。

## 同题复测

| 题目 | 基线目标排名 | 复测目标排名 |
|---|---:|---:|
| Deep learning DOI | 前五未命中 | 1 |
| AlphaFold DOI | 前五未命中 | 1 |
| AI Action Plan 公告关键词 | 前五未命中 | 1 |
| 联邦公告编号 2025-02305 | 1 | 1 |
| AlphaFold 标题 | 前五未命中 | 前五未命中 |
| PRISMA 2020 标题 | 5 | 5 |

Crossref 对常见裸 DOI 使用精确过滤，出版日期条件仍可叠加。联邦公报按公告编号直接取记录，关键词默认按相关性排序，明确指定 `--intent current` 时按发布时间排序。[Crossref 过滤说明](https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/) · [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1)

6 道 Smart 抽查均选中免费策略并返回候选。三轮共 116 次免 Key HTTP 请求。付费策略需另行比较。

## 复现基线

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v3.json --modes free --keyless --live --limit 100 --max-requests 300 --timeout 8 --count 5 --output /tmp/xcoze-100-free.json
```

基线在提交 `4a021dd` 上运行。复测沿用相同查询和参数。公开数据保留链接、日期、路由和耗时，便于后续逐题核验。
