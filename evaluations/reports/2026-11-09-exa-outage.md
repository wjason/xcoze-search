# Exa 断路测试

**简体中文** | [English](2026-11-09-exa-outage.en.md)

2026-11-09 北京时间，从 100 道题中抽取 12 道，模拟 Exa 不可用。免费模式通过请求守卫禁止发送 Exa 或带用户 Key 的请求，保留公开原生来源和本地浏览器备用。网络和浏览器结果会随环境变化。[逐题记录](2026-11-09-exa-outage.data.json)

| 检查项 | 观察 |
|---|---|
| 任意候选 | 11/12 |
| 前五条有预期域名 | 7/11（另有一题未预设域名） |
| 原生接口 | GitHub、arXiv 和 Hacker News 的三个样例均有候选 |
| 通用与站点检索 | Bing RSS 出现不相关结果，DuckDuckGo 返回验证页后进入冷却，360 浏览器补回小红书、B 站等候选 |
| 剩余缺口 | 两道英文官方文档题、统计局 CPI、巨潮年度报告未达到预期 |

## 备用路径

- 统计局 CPI 改用原生发布栏目和短关键词后，返回了官方原稿。对公告、统计、仓库和论文，先根据明确的目标选原生路径。
- Python TaskGroup 与 Kubernetes 资源管理题，限制到官方域名后，Skill 的免费备用路径仍未找到目标章节。宿主网页搜索可以查到 [Python TaskGroup 文档](https://docs.python.org/3/library/asyncio-task.html#task-groups)和 [Kubernetes 资源管理文档](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)。宿主能力及费用按实际环境判断。
- 巨潮样例改为股票代码和报告年份后，返回了域内页面，仍未核对到目标公司的年度报告。域名命中只用于判断来源覆盖。
- 需要独立的通用 API 时，可按需配置已支持的 Brave Search 或其他供应商。显式免费模式仍只走免用户 Key 来源。[Brave API 文档](https://api-dashboard.search.brave.com/documentation/services/web-search)

## 复现

基准工具的 `--without-exa` 只在本轮禁用两个 Exa 路径，不写入用户设置。以下命令跑题集前六道。加 `--limit 100 --max-requests 300` 可跑整套，已安装的本地浏览器可能启动。

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v3.json --modes free --keyless --without-exa --live --limit 6 --max-requests 18 --timeout 10 --output /tmp/xcoze-without-exa.json
```
