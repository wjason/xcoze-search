# 返回的原文片段能否回答问题

**简体中文** | [English](2026-11-22-answer-support.en.md)

2026-11-22 · v0.10.1。[33 道题与作答要求](../research-cases-v2.json) · [逐题复核](../research-answer-reviews.json) · [运行数据与引用位置](2026-11-22-answer-support.data.json)。

## 结果

30 道真实问题覆盖 Python、Go、Rust、Kubernetes、网页 API、能源政策与统计、招投标和上市公司披露；另有 3 道日期、主题及请求预算负例。运行前阻断 Exa、Parallel、带 Key 服务、宿主搜索和浏览器，不读取用户配置。

| 检查项 | 初始片段选择 | 改进后 |
|---|---:|---:|
| 足以回答全部要求 | 12/30 | 27/30 |
| 只支持部分要求 | 8/30 | 2/30 |
| 不能支持所问事实 | 10/30 | 1/30 |

初始轮已经包含新接入的南网官网搜索表单，片段选择尚未应用本轮改进；不是已发布 v0.10.0 与 v0.10.1 的整版对照。题目侧重已知薄弱点。由本轮 Agent 按明确要求复核实际返回片段，未进行独立盲审，这些数量不能当作通用答案准确率。引用校验只确认片段存在，不代替语义判断。

最终整轮 30/30 题取得候选并读到原文，27 题通过字面检查；字面未覆盖的 3 题与作答证据不足的 3 题并不相同。整轮 **78 次 HTTP**，正例耗时中位数 **1.30 秒**，不含最终回答生成。3 道负例均保留预期缺口，Exa/Parallel、带 Key 接口和浏览器调用均为零。之后单独复测 MDN 排序，用两次请求直接读取概览，耗时 0.32 秒，不混入整轮中位数。中间轮次与诊断补读不计入这 78 次请求。

## 南网：原来的未命中题

保留原查询“数字化”和公开招标条件。旧路径只查了最新列表的两页；官网公布的 `dbsearch.jspx` 搜索表单能查到这一窗口以外的公告，并回显关键词和栏目。被截断的标题还可能失去末尾的“招标公告”，现可采用页面明确公布的分类；标题若明确标注其他阶段，仍以实际阶段为准。

[三维数字化建模技术服务公告](https://www.bidding.csg.cn/zbgg/1200450933.jhtml)确认项目编号 CG3800022002451383，投标文件递交截止 **2026-12-11 09:00**。更具体的[数字化建设监理公告](https://www.bidding.csg.cn/zbgg/1200450806.jhtml)确认编号 CG2600022002404187，文件获取结束 **2026-11-26 18:00**，投标截止 **2026-12-11 08:40**。时间类型分别标注，不据此保证项目当前仍可投标。没有扫描历史列表、更换身份或处理验证码。

## 本轮改进

- 片段保留条件、后果与否定。TaskGroup 返回普通子任务失败与异常合并的说明；NetworkPolicy 返回连接两端都需允许的条件。
- 方法读取限制在对应范围，OnceLock.get 不混入 set 的行为；Sphinx 检索保留符号大小写，避免把 timeout 函数定位到 Timeout 类。
- 定位页面已有的默认拒绝标题并保留 YAML，不拼造锚点。
- 文件获取、投标和响应截止分别提取；中标筛选排除明确的候选人标题，不只信网站的分类代码。
- 英文 API 标识符按边界匹配，构造器里的 AbortController 不再自动满足对 abort 操作的检查。

## 仍需补读的问题

- **R05**：能说明 signal 和 abort 的作用，但缺少把 signal 连接到具体请求的操作片段。
- **R24**：超时对应 TimeoutError 已明确；代码片段截在 AbortError 分支，用户取消的完整上下文仍不足。
- **R25**：只读取储能方案通知，装机目标在未读 PDF 中，不能推断目标值。

R19、R30 则说明相反的问题：正文虽然缺少指定字面词，方法所在文档仍能确认 OnceLock，表格中的“中标报价”也能回答金额。Agent 应核对实际事实、范围和单位，不能把字面检查的通过或失败直接等同于回答质量。

## 逐题复核

| 题号 | 结果 | 核验结论与原文 |
|---|---|---|
| R01 | 足以作答 | 普通非取消异常会取消剩余任务；等待结束后合并异常。 [原文](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup) |
| R02 | 足以作答 | 非空 cause 由 cancel 记录，通过 Cause(ctx) 获取。 [原文](https://pkg.go.dev/context#WithCancelCause) |
| R03 | 足以作答 | 未初始化时运行初始化闭包，后续复用已有值；方法说明和两次调用示例互相支持。 [原文](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.get_or_init) |
| R04 | 足以作答 | 入站、出站分别隔离；源 Pod 出站和目标 Pod 入站必须都允许连接。 [原文](https://kubernetes.io/docs/concepts/services-networking/network-policies/) |
| R05 | 部分支持 | 能确认 signal 用于通信、abort 中止 fetch；仍缺把 signal 传入具体请求的操作片段，不补造完整示例。 [原文](https://developer.mozilla.org/en-US/docs/Web/API/AbortController/AbortController) |
| R06 | 足以作答 | timeout 上下文把 CancelledError 转换成 TimeoutError。 [原文](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout) |
| R07 | 足以作答 | 定位到对应方案通知，原文制发日期 2025-08-27，档案展示为 2025-09-12。 [原文](https://www.nea.gov.cn/20250912/73455a1a61b248d4aef65cc124631398/c.html) |
| R08 | 足以作答 | 定位到发改能源规〔2025〕411号通知；附件仍标为未读，不据此解读全部规则。 [原文](https://www.nea.gov.cn/20250429/df8e465e859245039b24fbbe21f04c5f/c.html) |
| R09 | 足以作答 | 原文统计期是 2025 全年；页面日期和正文提及的发布事件日期分别保留。 [原文](https://www.nea.gov.cn/20260121/715f79826488476a9162da7c8bd77c80/c.html) |
| R10 | 足以作答 | 片段同时给出招标文件获取期 11月5日至12日和投标递交截止 11月26日09:00；原问题用词有歧义，需要明确标签。 [原文](https://www.ggzy.gov.cn/information/deal/html/b/440000/0201/20261105/004469eed41af70445c494e2d97af73d5ee8.html) |
| R11 | 足以作答 | 找到郑东新区龙湖电化学储能 EPC 中标结果公告，排除了候选人标题。 [原文](https://www.ggzy.gov.cn/information/deal/html/b/410000/0104/20261119/004169ff84cf10094b6d881259078bd61ac7.html) |
| R12 | 足以作答 | 原题读到三维数字化建模技术服务公开招标；投标文件截止 2026-12-11 09:00。 [原文](https://www.bidding.csg.cn/zbgg/1200450933.jhtml) |
| R13 | 足以作答 | 首页确认贵州茅台、600519、2024 年年度报告；只提取前十页，不是全部143页。 [原文](https://static.cninfo.com.cn/finalpage/2025-04-03/1222993920.PDF) |
| R14 | 足以作答 | 默认 return_exceptions=False 时首个异常立即传播，其他 awaitables 不自动取消。 [原文](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather) |
| R15 | 足以作答 | 明确说明 TimeoutError 只能在 timeout 上下文外捕获。 [原文](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout) |
| R16 | 足以作答 | 明确说明当前 contextvars.Context 从事件循环线程传播到工作线程。 [原文](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread) |
| R17 | 足以作答 | 取消会释放 context 关联资源，操作完成应调用 cancel；示例也说明避免 goroutine 泄漏。 [原文](https://pkg.go.dev/context#WithCancel) |
| R18 | 足以作答 | key 必须可比较；避免字符串等内置类型造成跨包冲突，使用自定义类型。 [原文](https://pkg.go.dev/context#WithValue) |
| R19 | 足以作答 | get 对未初始化或初始化中的单元返回 None，并明确永不阻塞；没有拿 set 的行为代替。 [原文](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.get) |
| R20 | 足以作答 | 闭包 panic 会传播给调用者，单元保持未初始化。 [原文](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.get_or_init) |
| R21 | 足以作答 | 多条策略按允许集合取并集，不覆盖，也不依赖求值顺序。 [原文](https://kubernetes.io/docs/concepts/services-networking/network-policies/) |
| R22 | 足以作答 | 返回 YAML 的 podSelector: {}、policyTypes: Ingress 以及不允许任何入站的说明。 [原文](https://kubernetes.io/docs/concepts/services-networking/network-policies/#default-deny-all-ingress-traffic) |
| R23 | 足以作答 | HTTP 404 不会自行 reject，需要检查响应状态或 ok。 [原文](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch) |
| R24 | 部分支持 | 片段明确超时产生 TimeoutError，但代码截在 AbortError 分支处，缺少说明其代表用户取消的完整上下文。 [原文](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static) |
| R25 | 证据不足 | 只读到方案通知，装机目标位于未读 PDF；片段不能回答目标值。 [原文](https://www.nea.gov.cn/20250912/73455a1a61b248d4aef65cc124631398/c.html) |
| R26 | 足以作答 | 原文给出 103682 亿千瓦时、同比增长 5.0%，均属于 2025 全年。 [原文](https://www.nea.gov.cn/20260121/715f79826488476a9162da7c8bd77c80/c.html) |
| R27 | 足以作答 | 项目编号 CG2600022002404187，投标截止 2026-12-11 08:40，来自同一项目。 [原文](https://www.bidding.csg.cn/zbgg/1200450806.jhtml) |
| R28 | 足以作答 | 获取结束 2026-11-26 18:00，投标截止 2026-12-11 08:40；不是同一时间。 [原文](https://www.bidding.csg.cn/zbgg/1200450806.jhtml) |
| R29 | 足以作答 | 采购人为南方电网澜湄国际能源有限责任公司，响应截止 2026-11-24 09:00。 [原文](https://www.bidding.csg.cn/fzbgg/1200449758.jhtml) |
| R30 | 足以作答 | 同一项目中标联合体为中国电建华东院和中铁电气化局第三工程公司，中标报价 194687771.00 元；不使用其他公告的候选价或历史合同价。 [原文](https://www.ggzy.gov.cn/information/deal/html/b/410000/0104/20261119/004169ff84cf10094b6d881259078bd61ac7.html) |

## 复现

```bash
python3 evaluations/evaluate_research.py --live --corpus evaluations/research-cases-v2.json --output /tmp/research.json --review-output /tmp/research-private.json
python3 evaluations/review_research.py --corpus evaluations/research-cases-v2.json --results evaluations/reports/2026-11-22-answer-support.data.json --reviews evaluations/research-answer-reviews.json --run final --output /tmp/answer-review.json
```

第一条命令实测，省略 `--live` 仅生成离线计划；`--review-output` 用于本机私下复核片段。第二条命令只校验已有人工结论及引用位置，不会自动完成新的语义判断。新运行要重新复核，不能沿用旧结论；滚动招标列表可能变化。公开产物不保存整页原文、凭据或账号数据。**270 项离线测试通过。**
