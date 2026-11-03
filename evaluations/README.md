# 搜索回归样例

**简体中文** | [English](README.en.md)

语料日期：2026-11-02。`queries.json` 包含 12 个中英文搜索查询和 3 个正文提取 URL，覆盖技术文档、原始规范、内容类型、固定日期新闻、版本差异和冲突信息。它用于复现、比较返回内容及辅助人工阅读，不是通用准确率评测。

## 默认只看计划

```bash
python3 scripts/evaluate.py --provider deepseek,tavily,exa
python3 scripts/evaluate.py --operation fetch --provider deepseek,tavily,exa
```

不读取密钥、不发起 HTTP 请求。输出查询数、计划调用数和预算；`would_stop_early:true` 表示预算不足以跑完所选组合。样例数是 12，每家每条查询算一次逻辑请求；工具不默认扩词或追加 Fetch。提取回归需显式选择 --operation fetch，只支持 DeepSeek/Tavily/Exa，不能把纯搜索服务加入提取列表。

## 显式在线运行

```bash
python3 scripts/evaluate.py --live --provider deepseek --limit 2 --count 3 --max-requests 2 --output ../evaluation-report.json
```

此命令会把样例查询发送给选定服务，可能计费。须提前配置各家凭据。`--max-requests` 是整轮评估共享的实际 HTTP 次数上限；在线回归使用零重试，剩余预算不足下一组服务时停止并报告 `complete:false`。默认上限 24，可调 1..1000。

报告保留运行时间、查询 ID、服务、来源 URL、内容类型、耗时、请求次数、官方用量/费用和错误码；不写密钥、原始响应、全文、生成答案或搜索历史。除非指定 `--output`，只输出到 stdout，不落盘。

提取报告记录正文字符数、摘要字符数、摘录条数和预设词匹配，不保存页面正文。预设词匹配仅说明返回文本中出现该词，不能证明完整性或事实正确。

## 如何复核

- 先检查运行日期、成功率、错误和是否因预算提前停止，再比较同一查询的来源与结果。
- `expected_domains` 是人工复核提示，空列表表示没有预设域名。命中预设域名不能证明结论正确，未命中也不能证明服务错误。
- 打开原始页面核对时间、版本、原话和来源关系，分别评价检索与内容提取。正文、摘录和摘要不能合并评价成“读到全文”。
- 旧六商用源回归只执行了离线计划和合成响应测试，未对四家新增服务做真实账号质量评测。需要新的查询集时保留语料版本和评估日期。

## Smart 同题实测

[2026-11-03 报告](reports/2026-11-03.md)包含六题基线/优化和两道中文留出题；[脱敏数据](reports/2026-11-03.data.json)只保留指标、URL 与人工说明。

```bash
python3 scripts/benchmark.py --output ../smart-plan.json
python3 scripts/benchmark.py --live --limit 6 --max-requests 36 --output ../smart-live.json
python3 scripts/benchmark.py --live --corpus evaluations/smart-holdout.json --limit 2 --max-requests 12 --output ../holdout-live.json
```

默认只生成计划，不读凭据、不联网。显式 --live 会把公开查询发给服务，DeepSeek/Smart 可能计费。每轮共享 HTTP 预算，零重试，顺序轮换；Smart 使用内存中的默认偏好，不保存配置。HN 显式 DeepSeek 使用语料记录的日期运算符，原生路径使用日期字段。

本地在线报告包含每条最多 1800 字符的搜索证据，可能截断，勿直接公开；发布前只保留 URL/指标/人工判断并检查隐私与转载范围。成本按原始 DeepSeek 非空成功和语料内当日单价估算，不是账单；模型费用未知。ok 只说明执行了计划单元，semantic_quality_assessed 默认 false；人工复核不能由词命中/官方域名代替。基准题里的日期答案是历史快照，重新测量时更新语料并另存报告。

## 开放源与竞品研究复测

[本轮报告](reports/2026-11-03-open-sources.md)记录九源接入、Agent Reach 研究和长文截断修正。使用 open-source-cases.json、--modes free --limit 10 --count 3 复用 benchmark.py；默认仍离线，--live 才联网。expected_provider_returned 只表示对应原生源返回，不代表结论正确。

## Exa 限额故障注入

```bash
python3 scripts/evaluate_fallback.py --output ../fallback-offline.json
python3 scripts/evaluate_fallback.py --live-api --live-browser --output ../fallback-live.json
```

默认所有 HTTP/浏览器均模拟，使用内存中的六家合成 Key，不读取用户凭据；--live-api 只做一次真实匿名 API 查询，--live-browser 在 API 故障注入后执行一条真实浏览器路径。付费 API 在传输前由测试守卫拒绝。ok 只表示路由安全断言通过；live_browser_usable 单列真实浏览器可用性，可能为 false，不能把模拟恢复当成真实检索成功。本轮[报告](reports/2026-11-03-fallback.md)记录了这一限制。

## 真实浏览器验收（v0.7.1）

```bash
python3 scripts/evaluate_browser.py --live --output ../browser-live.json
```

仅显式 --live 才执行；全部搜索页面/HTTP 响应均真实，不模拟。使用内存合成 Key、临时缓存，不读取用户凭据或保存偏好，传输前守卫拒绝带 Key API。测试三道文档/统计发布/公告转载检索、一道 GitHub 覆盖探测，再以临时禁用 Exa/Bing 的偏好运行真实 DDG 到浏览器的自动链路。若 DDG 自身取得足够证据而未启动浏览器，也不算浏览器兜底通过。

accepted 只表示取得预期来源/主题且关闭确认；不是事实正确性评分。GitHub 探测 required:false，明确记录为未通过覆盖检查，不能用总体 ok 隐藏该缺口。总体 ok 仅要求核心三题、真实自动兜底和零带 Key 调用；每项失败仍保留。运行结果受公开索引更新和网络影响。历史[限额报告](reports/2026-11-03-fallback.md)与[真实浏览器报告](reports/2026-11-03-browser.md)分别维护，不把模拟当在线成功。
