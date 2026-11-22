# 按需附件与完整上下文实测

**简体中文** | [English](2026-11-22-followups.en.md)

2026-11-22 · v0.10.2。[原题集与作答要求](../research-cases-v2.json) · [逐题复核](../research-followup-reviews.json) · [实测数据与片段位置](2026-11-22-followups.data.json)。

## 三道遗留题

沿用原查询、原问题和原作答要求。v0.10.1 的本次真实基线仍为两道部分支持、一道证据不足；改进后，三道题所需事实均有原文支持。

| 题号 | 新取得的原文证据 | HTTP 次数 | 耗时 |
|---|---|---:|---:|
| R05 | AbortController：沿页面公布的同站示例，取得控制器创建、向 fetch 传入 signal、调用 abort 的完整代码。 | 3 | 1.37 秒 |
| R24 | AbortSignal：完整发布代码块包含 TimeoutError 和 AbortError 的处理，能区分该示例中的超时与用户操作取消。 | 2 | 1.02 秒 |
| R25 | 储能方案：PDF 第1页明确2027年全国新型储能装机规模达到1.8亿千瓦以上。 | 3 | 1.84 秒 |

来源：[AbortSignal 示例](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal#examples)、[AbortSignal.timeout](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static)、[能源局通知及其实际附件链接](https://www.nea.gov.cn/20250912/73455a1a61b248d4aef65cc124631398/c.html)。政策附件在请求第1–10页的范围内返回了第1–7页文本，这是提取范围记录，不据此保证整份文件完整；附件发布日期保持未知，不沿用通知日期。

## 完整回归

阻断 Exa、Parallel、用户 Key、宿主搜索和浏览器后，30 道真实问题均取得原文；按既有作答要求复核实际返回片段，**30/30** 道获得支持。3 道故意制造的日期、主题和预算负例均保留预期缺口。整轮 **79 次 HTTP**，正例耗时中位数 **1.42 秒**，付费接口、Exa/Parallel 和浏览器调用均为零。另以英文问题复测三道遗留题，用8次额外 HTTP 得到相同事实，关键代码和 PDF 片段与中文运行一致。

这是一组有针对性的回归题，由同一 Agent 复核，未独立盲审，不代表通用答案准确率。字面检查通过28题，与作答支持度是不同的检查：缺少字面词时也可能有足够的上下文证据。引用校验只确认片段存在及复核声明完整，不自动判断语义正确。

本轮30道真实题中，只有 R05 和 R25 触发示例或附件补读；R24 在已经取得的页面中保留完整代码，不增加网络请求。R13 原有年报 PDF 直接读取与附件补读分别计数。

## 有界补读

正文缺少细节、或短通知把所需内容放在附件中时，才考虑相关 PDF；操作类问题可以补读页面明确指向的示例。链接须由发布页面提供，且属于已支持的同站范围。每项任务最多读取一份 PDF 和一个示例，不递归展开。已有正文足够时不读附件。

搜索、正文、示例和 PDF 共用阅读次数、HTTP 和时间预算。父页面记录每次补读及状态，子文档记录父页面和补读原因；日期不补造。缺提取工具、扫描件、拒绝访问或预算耗尽均保留明确缺口。PDF 只使用已有 pdftotext。

完整发布代码块最多1800字符，保留缩进和分支两侧；超出返回文本上限时不标记完整。发布者原有的省略保持原样；保留完整代码块不代表整套程序或答案已被核实。

## 真实控制试验

| 设置 | HTTP 次数 | 实际结果 |
|---|---:|---|
| R05：关闭示例补读 | 2 | 不读取示例；保留示例缺口，按 follow_up_disabled 停止 |
| R25：关闭附件补读 | 2 | 保留通知，明确附件未读 |
| R25：最多两次 HTTP | 2 | 不发起 PDF 请求，保留附件和请求预算缺口 |

首次关闭示例时，程序仍继续读取搜索候选，用了5次请求。现对“仅缺已关闭的补读”提前停止；同题复测降为2次请求，缺口继续保留。这次复测与默认整轮耗时、次数分开。控制试验、英文复测、三题基线和诊断补读均不混入默认整轮的79次请求。

## 逐题复核

| 题号 | 核验结论与原文 |
|---|---|
| R01 | 普通非取消异常会取消剩余任务；等待结束后合并异常。 [原文](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup) |
| R02 | 非空 cause 由 cancel 记录，通过 Cause(ctx) 获取。 [原文](https://pkg.go.dev/context#WithCancelCause) |
| R03 | 未初始化时运行初始化闭包，后续复用已有值；方法说明和两次调用示例互相支持。 [原文](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.get_or_init) |
| R04 | 入站、出站分别隔离；源 Pod 出站和目标 Pod 入站必须都允许连接。 [原文](https://kubernetes.io/docs/concepts/services-networking/network-policies/) |
| R05 | 沿发布页面的同站示例链接补读，代码明确创建控制器、把 signal 传入 fetch，并调用 controller.abort()；两个作答要求均有原文支持。 [原文](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal#examples) |
| R06 | timeout 上下文把 CancelledError 转换成 TimeoutError。 [原文](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout) |
| R07 | 定位到对应方案通知，原文制发日期 2025-08-27，档案展示为 2025-09-12。 [原文](https://www.nea.gov.cn/20250912/73455a1a61b248d4aef65cc124631398/c.html) |
| R08 | 定位到发改能源规〔2025〕411号通知；附件仍标为未读，不据此解读全部规则。 [原文](https://www.nea.gov.cn/20250429/df8e465e859245039b24fbbe21f04c5f/c.html) |
| R09 | 原文统计期是 2025 全年；页面日期和正文提及的发布事件日期分别保留。 [原文](https://www.nea.gov.cn/20260121/715f79826488476a9162da7c8bd77c80/c.html) |
| R10 | 片段同时给出招标文件获取期 11月5日至12日和投标递交截止 11月26日09:00；原问题用词有歧义，需要明确标签。 [原文](https://www.ggzy.gov.cn/information/deal/html/b/440000/0201/20261105/004469eed41af70445c494e2d97af73d5ee8.html) |
| R11 | 找到郑东新区龙湖电化学储能 EPC 中标结果公告，排除了候选人标题。 [原文](https://www.ggzy.gov.cn/information/deal/html/b/410000/0104/20261119/004169ff84cf10094b6d881259078bd61ac7.html) |
| R12 | 原题读到三维数字化建模技术服务公开招标；投标文件截止 2026-12-11 09:00。 [原文](https://www.bidding.csg.cn/zbgg/1200450933.jhtml) |
| R13 | 首页确认贵州茅台、600519、2024 年年度报告；只提取前十页，不是全部143页。 [原文](https://static.cninfo.com.cn/finalpage/2025-04-03/1222993920.PDF) |
| R14 | 默认 return_exceptions=False 时首个异常立即传播，其他 awaitables 不自动取消。 [原文](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather) |
| R15 | 明确说明 TimeoutError 只能在 timeout 上下文外捕获。 [原文](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout) |
| R16 | 明确说明当前 contextvars.Context 从事件循环线程传播到工作线程。 [原文](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread) |
| R17 | 取消会释放 context 关联资源，操作完成应调用 cancel；示例也说明避免 goroutine 泄漏。 [原文](https://pkg.go.dev/context#WithCancel) |
| R18 | key 必须可比较；避免字符串等内置类型造成跨包冲突，使用自定义类型。 [原文](https://pkg.go.dev/context#WithValue) |
| R19 | get 对未初始化或初始化中的单元返回 None，并明确永不阻塞；没有拿 set 的行为代替。 [原文](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.get) |
| R20 | 闭包 panic 会传播给调用者，单元保持未初始化。 [原文](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.get_or_init) |
| R21 | 多条策略按允许集合取并集，不覆盖，也不依赖求值顺序。 [原文](https://kubernetes.io/docs/concepts/services-networking/network-policies/) |
| R22 | 返回 YAML 的 podSelector: {}、policyTypes: Ingress 以及不允许任何入站的说明。 [原文](https://kubernetes.io/docs/concepts/services-networking/network-policies/#default-deny-all-ingress-traffic) |
| R23 | HTTP 404 不会自行 reject，需要检查响应状态或 ok。 [原文](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch) |
| R24 | 完整发布代码块保留 TimeoutError 和 AbortError 两侧分支；该示例将前者用于超时、后者用于浏览器停止等用户操作。 [原文](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static) |
| R25 | 按需读取通知实际链接的 PDF，第1页明确2027年全国新型储能装机规模达到1.8亿千瓦以上；提取到第1至7页文本，未把通知日期当作PDF发布日期。 [原文](https://www.nea.gov.cn/20250912/73455a1a61b248d4aef65cc124631398/2025091273455a1a61b248d4aef65cc124631398_358225d8906a1840e98ffbbfcbac506bab.pdf) |
| R26 | 原文给出 103682 亿千瓦时、同比增长 5.0%，均属于 2025 全年。 [原文](https://www.nea.gov.cn/20260121/715f79826488476a9162da7c8bd77c80/c.html) |
| R27 | 项目编号 CG2600022002404187，投标截止 2026-12-11 08:40，来自同一项目。 [原文](https://www.bidding.csg.cn/zbgg/1200450806.jhtml) |
| R28 | 获取结束 2026-11-26 18:00，投标截止 2026-12-11 08:40；不是同一时间。 [原文](https://www.bidding.csg.cn/zbgg/1200450806.jhtml) |
| R29 | 采购人为南方电网澜湄国际能源有限责任公司，响应截止 2026-11-24 09:00。 [原文](https://www.bidding.csg.cn/fzbgg/1200449758.jhtml) |
| R30 | 同一项目中标联合体为中国电建华东院和中铁电气化局第三工程公司，中标报价 194687771.00 元；不使用其他公告的候选价或历史合同价。 [原文](https://www.ggzy.gov.cn/information/deal/html/b/410000/0104/20261119/004169ff84cf10094b6d881259078bd61ac7.html) |
## 复现

```bash
python3 evaluations/evaluate_research.py --live --corpus evaluations/research-cases-v2.json --output /tmp/research.json --review-output /tmp/research-private.json
python3 evaluations/review_research.py --corpus evaluations/research-cases-v2.json --results evaluations/reports/2026-11-22-followups.data.json --reviews evaluations/research-followup-reviews.json --run final --output /tmp/followup-review.json
```

省略 --live 仅生成离线计划；本机复核输出含片段，不公开保存。第二条命令校验已保存的结论，新运行需要重新复核。**279项离线测试通过**，覆盖共享预算、关闭补读、缺依赖、拒绝停止、同站与凭据检查、不递归、页码映射和代码截断。本机实测确有 pdftotext；Windows/Linux 的离线用例模拟提取工具，不当作各平台真实 PDF 安装验证。
