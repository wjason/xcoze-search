# 六题真实对照：免费、DeepSeek、Smart 与 360 兜底

**简体中文** | [English](2026-11-03-comparison.en.md)

采样日期：2026-11-03；发布及安装验收：2026-11-04（北京时间）。基线为 v0.7.1（`c307eee`），调整发布为 v0.7.2。[脱敏数据](2026-11-03-comparison.data.json)保留 75 个阶段单元、来源 URL、实际调用和失败，不含响应正文、Key、Cookie 或鉴权头。多个开发阶段沿用了 0.7.1 版本标签，不能据同一标签认定实现或网络条件相同。先前[浏览器验收](2026-11-03-browser.md)保持原样。

## 结论

- **保留 API 主路，360 只作应急候选。** Exa 正常时，免费模式能快速取得英文官方文档；本轮确实发生 Exa 匿名额度限制，免费路径随后暴露了 RSS 跑题和浏览器覆盖不足。不能把限额期间的表现推广为免费 API 都差。
- **中文新闻可用 360 找线索，原始来源仍需限定/核实。** 原查询取得媒体转载；指定已经核实的官方域名后取得国家统计局发布、国家能源局发布会及实录入口。摘要并非每次包含所问数值，且原始页面列表曾混入旧年资料。
- **360 没补齐这两道英文官方文档题，也没找到两个 GitHub 项目。** 原查询只有第三方资料或不够相关的结果；限定官方域名、缩短查询后仍未命中。结果不足已经如实保留。GitHub 原生接口定位更直接、更快。
- **Smart 不必在已有好结果时补弱 RSS。** Exa 暂停时，RSS 补充没有增加有效证据；现跳过这种互补，主源失败仍能备用。其他已配置服务/Exa 互补保留，并限制已有结果后的互补请求超时为 3 秒。

这些结论来自有限公开问题的人工来源/时间复核，不是盲评准确率，也不是供应商的长期性能排名。没有把“HTTP 成功”“非空”“官方域名命中”当作答对。

## 题组和方法

六个真实信息需求在第一轮前固定：

| 类别 | 问题 | 原查询 |
|---|---|---|
| 中文新闻 | 2026 年 10 月制造业 PMI 及环比变化，找原始发布 | `2026年10月 制造业 PMI 国家统计局` |
| 中文新闻 | 2026 年前三季度可再生能源新增装机及占比 | `2026年前三季度 可再生能源 新增装机 国家能源局` |
| 英文文档 | PostgreSQL 18 uuidv7 的顺序与 shift 参数 | `PostgreSQL 18 uuidv7 shift interval documentation` |
| 英文文档 | Rust Mutex 中毒是否阻止访问，PoisonError::into_inner 如何恢复 guard | `Rust std Mutex poisoning PoisonError into_inner documentation` |
| GitHub | 微软 MarkItDown 官方项目及 PDF 可选依赖 | `markitdown`，platform=github |
| GitHub | 微软 Playwright 官方项目及三浏览器支持 | `playwright`，platform=github |

第一轮与核心修正后的同题轮均执行 free/DeepSeek/Smart；模式顺序轮换、串行请求、每源 count=5、零重试。另单独执行同题 360、四题官方域限定、两道英文短查询及修正验证。已知官方域名由独立原文核验确定，限定域名的组不能算自然语言盲测或原样查询的算法提升。

只配置了 DeepSeek Key。Smart 使用内存中的默认偏好，不保存用户设置；free/browser 在 API 传输前拒绝带 Key 服务或非空 Key。没有模拟响应，也没有清除真实暂停。运行中第二次 Exa 请求真实返回应用层限额错误，后续自动跳过；较晚的正常调用在冷却自然到期后重新成功。

耗时为单次检索调用，含浏览器关闭；不含进程启动、模型查询生成、最终答案生成、独立参考浏览与原文阅读。每次本地证据最多 1800 字符；截断后没见某词，不能认定原始完整响应没有它。发布数据已移除证据正文，词命中标记只作复核线索。

## 同题观察：不能用快速非空代替质量

初始轮中，免费新能源题约 0.57 秒返回了年历，PostgreSQL 题约 0.48 秒只返回首页/下载页，均不支持所问。Smart 还把部分这种结果混进了已有答案线索。首次 DeepSeek PMI 请求出现网络错误，后续请求成功；这次失败未抹去。

下表是**逐条词法修正后的同题轮**，仍处在 Exa 限额期间，早于后续 DDG 暂停和互补超时调整；不是最终版本的稳定延迟承诺。每格各一次，单位秒。

| 问题 | 免费 | DeepSeek | Smart | 来源/答案支持观察 |
|---|---:|---:|---:|---|
| PMI | 5.40 | 0.51 | 1.03 | 免费为媒体线索；付费模式有正确数值线索，但原查询未取得原始发布 |
| 可再生能源 | 6.56 | 0.45 | 1.01 | 免费候选摘要不足；DeepSeek/Smart 给出当期数值的媒体来源 |
| PostgreSQL UUID | 10.24 | 0.40 | 1.08 | 免费为第三方材料；DeepSeek/Smart 有函数/shift 线索，官网邮件与正式 18 版文档需区分 |
| Rust Mutex | 9.15，拒绝结果 | 0.50 | 0.84 | 免费结果缺关键代码标识；付费模式找到官方 Mutex 文档及其他材料 |
| MarkItDown | 0.22 | 0.98 | 0.74 | 原生接口直接定位官方项目；PDF 依赖仍需读 README，元数据不代表已读正文 |
| Playwright | 0.27 | 1.41 | 0.70 | 原生描述已有三浏览器线索；DeepSeek 也找到官方 README，但包含固定提交和其他仓库材料 |

修正后的拒绝/过滤会让某些“成功率”下降：这是拒绝无关证据，不是补齐了全部覆盖。主体词、代码名和日期筛查不验证论断真假，语义 API 与原生仓库元数据不套这些词法规则。

## 360 独立检查及官方站点变体

原始六题直接调用 360，分别耗时约 7.84、6.15、5.23、7.41、3.60、4.63 秒。中文题有相关媒体线索，新能源结果还混入了 2023 年/上半年资料；英文题没有预期的官方文档，GitHub 两题明确无匹配。六题 DOM 操作成功，不能写成六题检索有效。

在四题中加入已核实的官方域名后，最终现场观察为：

| 问题 | 免费 | DeepSeek | Smart（互补尾延迟调整前） | 观察 |
|---|---:|---:|---:|---|
| PMI，stats.gov.cn | 4.36 | 0.66 | 1.03 | 找到原始发布，数值可在返回证据中核对 |
| 新能源，nea.gov.cn | 4.17 | 0.76 | 1.14 | 找到当期发布会/实录入口；需读正文确认两项所问数值 |
| UUID，postgresql.org | 4.89，无结果 | 0.66 | 0.98 | 360 无匹配；付费结果主要为官网邮件/附件/相关页，仍需转读正式函数文档 |
| Mutex，doc.rust-lang.org | 5.15，无结果 | 0.55 | 0.91 | 360 无匹配；付费模式找到官方 Mutex 文档 |

对英文两题再做短查询仍无匹配；没有因此虚构新来源。最后一次 v0.7.2 日期修正实测约 4.03 秒，新能源结果仅保留两条当期官方入口，旧年紧凑日期路径被识别。

独立核验的原文包括[国家统计局 PMI 发布](https://www.stats.gov.cn/zwfwck/sjfb/202610/t20261031_1965718.html)、[国家能源局发布材料](https://www.nea.gov.cn/20261030/28a6f818b9f843a995952940301590bd/c.html)、[PostgreSQL 18 UUID 函数](https://www.postgresql.org/docs/18/functions-uuid.html)、[Rust Mutex](https://doc.rust-lang.org/std/sync/struct.Mutex.html)、[MarkItDown](https://github.com/microsoft/markitdown)和[Playwright](https://github.com/microsoft/playwright)。它们用于核对来源和信息，不把已知参考 URL 倒算成某模式搜到了它。

## 最终调度调整与验证

1. RSS/HTML/browser 按行丢弃明显中文跑题、缺少所问函数/代码标识及显式年份/部分月份、半年度冲突。支持常见紧凑年月路径；记录丢弃数量，保留原始 rank。可能漏判或误拒，Agent 仍需核对版本、日期及答案支持。
2. DDG 验证后暂停 15 分钟，后续计划跳过，避免在每个查询重复收到同一验证响应。纯相关性失败不再暂停整个浏览器来源，便于在预算内换短查询；验证码仍停止。
3. GitHub 不强制预留 browser 名额，先用原生及通用 API 填满已有来源预算；显式 browser 选择保留。覆盖不足的 360 不能挤掉更合适的 API 尝试。
4. 已有主源结果时，只在下一候选为另一已配置服务或 Exa 时互补。临时在内存偏好中禁用 Exa 的真实检查中，Smart 的 PMI/Rust 分别约 0.65/0.43 秒，仅 1 次 DeepSeek HTTP，没有 RSS 或浏览器；这是受控偏好检查，未冒充真实额度错误。
5. Exa 恢复后的 Smart 一组实际出现约 6.86 秒尾延迟，因此已有结果后的互补请求超时改为最多 3 秒。最终 Rust 实测约 1.57 秒，两个 API、0 浏览器，互补成功；不把一次快响应当作硬时延保证。显式多源和更低用户预算保留。
6. Exa 暂停自然到期后，免费 Rust 原查询约 **1.44 秒**取得官方 Mutex/PoisonError 等来源，**0 次浏览器启动**。说明正常免费 API 与额度耗尽后的浏览器路径应分开评价。

149 项离线测试覆盖免费隔离、过滤与原始 rank、DDG 暂停、GitHub API 位次、强/弱互补与 3 秒上限。它们验证行为边界，不替代这些真实检索，也不解决英文免费覆盖缺口。

## 费用与限制

报告内 75 个单元共 85 次可观测 API HTTP 尝试、26 次浏览器导航；浏览器资源子请求数未知，不混作 HTTP 总量。34 次 DeepSeek 非空成功，1 次初始 DeepSeek 网络失败；按[11 月 3 日核对的官方 Search 价格](https://api-docs.deepseek.com/guides/search/#billing)每千次成功请求 0.75 美元，已知搜索费用估算 **0.02550 美元**，不是账单。free/browser 的带 Key API 尝试均为 **0**。模型、宿主订阅和本机成本未知；独立参考浏览及稍后的安装包冒烟不在此表账内。

浏览器关闭曾占约 5.4–5.6 秒，免费受限路径总耗时最高观测约 12.52 秒。没有省略关闭时间美化指标，也没有据此放宽清理确认。网站、索引、缓存和网络条件会变化；本机观察不代表跨网络或 Windows/Linux 浏览器验收。

安装后的 v0.7.2 又执行了一次独立端到端冒烟：原生 GitHub 搜索定位 MarkItDown，Jina 路径失败后 Exa 免 Key 读取仓库正文，约 1.77 秒取得 20202 字符并找到 PDF 可选依赖说明。搜索 1 次、读取 2 次 API 尝试，0 次带 Key 请求、0 次浏览器；不并入前述采样账本。

当前取舍：有 Key 时保持效果优先的 API 路线；无 Key 时优先正常免 Key API，360 补应急候选。已知官方域名时提高查询范围精度，GitHub 用原生接口。英文免费官方文档在 Exa 受限时仍有缺口，已保留为待办。

## 复现

```bash
python3 scripts/benchmark.py --corpus evaluations/browser-comparison-cases.json --output ../plan.json
python3 scripts/benchmark.py --live --corpus evaluations/browser-comparison-cases.json --max-requests 36 --output ../comparison.json
python3 scripts/benchmark.py --live --corpus evaluations/browser-comparison-cases.json --modes browser --max-requests 6 --output ../browser.json
python3 scripts/benchmark.py --live --corpus evaluations/browser-comparison-scoped.json --limit 4 --max-requests 24 --output ../scoped.json
python3 -m unittest discover -s tests -q
```

默认只生成离线计划。--live 才读取本机配置并联网，DeepSeek/Smart 可能计费；不得公开未经删去证据正文的本地输出。公共服务的限额状态会影响新一轮，不清空暂停追求相同结果。脚本 ok 只表示计划单元执行完成，不表示题目全部答对。
