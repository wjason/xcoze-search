# 搜索回归样例

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
- 本轮只执行了离线计划和合成响应测试，未对四家新增服务做真实账号质量评测。需要新的查询集时保留语料版本和评估日期。
