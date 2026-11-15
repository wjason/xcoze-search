# 免 Key 文档搜索与备用路径实测

**简体中文** | [English](2026-11-16-keyless-search.en.md)

2026-11-16（北京时间）。本轮接入 Python、pandas、SQLAlchemy 的官方静态搜索索引和 MDN 站内搜索，并将 360 公开 HTML 作为轻量备用。它们均不要求用户 Key，也不使用宿主搜索或浏览器。完整记录见[逐题数据与探测记录](2026-11-16-keyless-search.data.json)。

## 专项样例

| 检索方式 | 样例 | 结果 |
|---|---|---|
| 官方 Sphinx 索引 | Python TaskGroup、Path.read_text、tomllib.loads；pandas read_csv dtype；SQLAlchemy select/join | 5/5 在前五条定位到预期文档页面 |
| MDN 站内搜索 | AbortController signal、Promise.allSettled | 2/2 定位到预期 API 文档 |
| 360 HTML 中文站点 | 购置税政策、巨潮年报、知乎 asyncio、小红书东馆、微博人工智能、B 站 rebase、统计局 GDP、能源局海上风电 | 6/8 返回通过本地主题检查的站内候选；年报和东馆未通过 |

官方文档查询约 0.3–1.1 秒，MDN 约 0.4–1.0 秒；360 中文样例约 0.9–2.3 秒，包含本机限频等待。部分社区候选是主页或平台搜索页，不代表已经读到正文、评论或视频内容。

另读取 Python、pandas、SQLAlchemy、MDN 和国家统计局共 5 个原始页面，均返回内容并包含所需主题或 API 标记。这只确认页面与主题对应，不是全部论断、版本和日期的事实验收。静态文档结果标为 `documentation_index`，不冒充正文摘要。

## 100 题无 Exa 对照

同一份 [100 题](../agent-search-cases-v3.json)，免费模式、前五条、8 秒单源超时，禁用 Exa 的两个入口、用户 Key、宿主搜索及本地浏览器。两轮之间保留原有来源冷却。前轮使用路由修改前的路径，后轮使用最终代码。

| 指标 | 调整前 | 调整后 |
|---|---:|---:|
| 返回候选 | 60/100 | 67/100 |
| 前五条命中预期域名 | 57/99 | 65/99 |
| 检索耗时中位数 | 477 ms | 433 ms |
| P95 耗时 | 2,239 ms | 2,111 ms |
| Exa 请求、带 Key API 请求、浏览器导航 | 均为 0 | 均为 0 |

两轮上游状态不同，表中变化不能当作准确率提升或稳定性能承诺。前轮 Parallel 在第 11 次请求遇到真实额度限制；后轮沿用冷却，后段自然恢复后收到 10 次请求。后轮 360 首次请求跳转至验证码域名，适配器识别后暂停，只请求了 1 次，没有继续跟随或重试。

后轮 Python TaskGroup、tomllib、ExceptionGroup、pandas merge，以及两道 MDN 题均通过直接文档入口取得候选。其他来源仍有空结果和访问限制。Kubernetes CPU requests/limits、Go context、Rust OnceLock 等题在这些通用备用不可用时仍有缺口，不能宣称已完全摆脱通用搜索服务。

中间轮暴露的两类问题已修正：文档索引的英文词形导致 `one_to_one` 未命中，以及发布/版本查询被误导向当前文档。最终代码补充有限后缀匹配，并保持发布查询走网页搜索；固定索引不能保证指定版本时跳过该入口。100 题后轮是在这些修改完成后运行。

## 公开入口筛选

每个入口以英文官方文档与中文站点查询各探测一次。页面响应不是可用结果：

| 入口 | 本次观察 | 处理 |
|---|---|---|
| 360 公开 HTML | 小批样例有相关结果；批量后出现验证码重定向 | 接为受限备用，验证后冷却 15 分钟 |
| Google HTML | 返回 JavaScript 页面，没有可提取的自然结果 | 未接入 HTTP 搜索 |
| Yahoo | HTTP 500 / 403 | 未接入 |
| Brave HTML | HTTP 429 | 未接入 |
| 百度 HTML / JSON | 重定向至验证页 | 未接入，不绕过验证 |
| 搜狗 | 验证页 | 未接入 |
| Mojeek | 验证页 | 未接入 |
| Ecosia | HTTP 403 | 未接入 |
| Qwant | HTML 无自然结果，公开 JSON 路径返回 403 | 未接入 |
| Mwmbl v2 | 两道定向题均为零结果 | 暂未接入，保留为后续复测对象 |
| Bing HTML | 有结果但与题目、站点不符 | 未新增 HTML 适配；既有 RSS 保留 |
| Stract | 所测搜索路径 HTTP 404 | 未接入 |

MDN 的入口设计有[Mozilla 官方说明](https://hacks.mozilla.org/2021/03/how-mdns-site-search-works/)；Sphinx 适配直接读取文档站公开的 JSON 索引，未执行其 JavaScript。Mwmbl 的[开发者页面](https://developer.mwmbl.org/)公开了匿名入口与额度，本次零结果不代表其所有查询都不可用。适配器独立实现，未复制第三方搜索项目代码。

## 复现

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v3.json --modes free --keyless --without-exa --browser off --live --limit 100 --max-requests 300 --timeout 8 --count 5 --output /tmp/xcoze-no-exa.json
python3 scripts/xcoze_search.py search 'asyncio TaskGroup exception cancellation' --platform python-docs --strategy free --browser off
python3 scripts/xcoze_search.py search 'merge validate one_to_one' --platform pandas-docs --strategy free --browser off
python3 scripts/xcoze_search.py search 'AbortSignal.timeout' --platform mdn --strategy free --browser off
```

对照运行不清除真实冷却，不更换身份绕过限额，不调用付费接口补齐分数。域名命中只是来源覆盖；不同日期复现的结果和耗时可能不同。
