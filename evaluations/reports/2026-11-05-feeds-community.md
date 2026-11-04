# 新闻订阅、政府政策与社区主帖实测

**简体中文** | [English](2026-11-05-feeds-community.en.md)

2026-11-05，Asia/Shanghai；运行与发布版本 v0.9.0。本轮按真实问题串起“发现链接→读原文”，不以接口非空代替事实核实。单次本机测量不代表跨网络成功率或延迟分位数。

| 真实任务/操作 | 结果 | 耗时 | 实际路径 |
|---|---|---:|---|
| 中新网财经里有哪些进博会报道？ | 当前 RSS 字面筛选命中 3 条 | 0.157 秒 | cns-finance，1 HTTP |
| 中新网即时 RSS 里有哪些北京时间 11 月 5 日的条目？ | 当时窗口命中 1 条；不代表当日全部新闻 | 0.151 秒 | cns-scroll，1 HTTP |
| 看 BBC World 当前新闻条目 | 返回前 3 条，保留源提供的发布时间 | 0.944 秒 | bbc-world，1 HTTP |
| 查中国政府网登记管理相关政策 | 找到事业单位登记管理条例，日期条件未放宽 | 0.437 秒 | govcn，1 HTTP |
| 读取 Python 论坛关于拼写建议的讨论主帖 | 得到 885 字符主帖，说明问题背景；没有输出回复答案 | 0.759 秒 | community，1 HTTP |
| 读取 Rust 论坛代码排版说明主帖 | 得到 1261 字符主帖，保留反引号示例与代码缩进 | 1.272 秒 | community，1 HTTP |
| 读取 V2EX 已知话题主帖 | 403，停止换阅读渠道并进入站点冷却 | 0.437 秒 | community，1 HTTP |
| 继续读第一条进博会新闻原文 | 得到 2942 字符，正文含标题对应主题 | 1.192 秒 | Jina 401 → Exa 免 Key，2 HTTP |
| 继续读找到的政策正文 | 得到 4982 字符，能区分页面发布日期、成文日和正文生效日 | 1.141 秒 | Jina 401 → Exa 免 Key，2 HTTP |

初轮共 9 项操作、11 次可观测 API HTTP，8 项成功、1 项受限；带 Key 请求为 0，没有启动浏览器。成功不表示每个问题都已被回答：Python 主帖本身提出问题，若要原因和结论仍需读取实际回复或官方文档。本轮没有把主帖当成答案。

## 窗口、日期与原文

中新网 RSS 来自其[官方订阅目录](https://www.chinanews.com.cn/rss/)；BBC 直接读取其 [World RSS](https://feeds.bbci.co.uk/news/world/rss.xml)。只对当前返回条目过滤，不走历史分页。日期按北京时间日历日包含首尾；Atom updated 不当作发布时间，未知日期不能用检索时间填补。重复 URL 只在当前窗口去 fragment 后保留第一条，不能推导跨媒体独立性。

中国政府网[最新政策栏目](https://www.gov.cn/zhengce/zuixin/)使用公开的 ZUIXINZHENGCE.json。实测窗口 1109 行，最新条目日期为 2026-11-01，早于检索日，因此不能称为实时完整公告库。检索找到的[政策原文](https://www.gov.cn/zhengce/content/202610/content_7084279.htm)另行读取；栏目发布日期不等于政策生效日期。没有命中时 Agent 可在原有模式与预算内继续搜索，不以该列表断言没有政策。

## 社区读取的证据边界

原生 community 支持 V2EX、discuss.python.org、users.rust-lang.org，固定端点、无用户登录态。Discourse [Topic API](https://docs.discourse.org/#tag/Topics/operation/getTopic)响应可能附带首批回复；适配器只输出 post_number:1。comments_fetched/source_attached_replies 如实说明已随响应传输的回复，comments_included:false 表示回复正文未输出，thread_complete:false。不额外翻页。初版开发检查曾把“未输出回复”写成 comments_fetched:false，已修正并用两次真实读取复查，单独记在结构化记录，不计入上述九项初轮操作。

主帖根链接与回复定位严格区分，不把 /t/123/2 误解析成主题 2，不把指定回复替换成主帖。HTML 转纯文本保留代码缩进和链接目标，但不声称逐字保留 HTML/Markdown 排版。默认返回 24000 字符，截断显式标记，不证明线程完整。

V2EX 本次 403 不代表主题不存在；没有使用 Cookie/代理/浏览器或其他阅读服务反复请求。三站独立限频/暂停，一个站点受限不阻止另两个。按 [V2EX API 公平使用规则](https://www.v2ex.com/p/7v9TEc53)按需读取，不将帖子全文发布到本报告。

## 验证与限制

170 项离线测试通过，覆盖 RSS/Atom/DOCTYPE 拒绝、字面/日期/未知时间/去重、政府索引范围、免费隔离、主帖/回复地址、代码与链接、内容截断、站点独立冷却及拒绝后停止扩散。HTTP 正文不完整返回脱敏网络失败，401/403 的匿名来源不再误报用户 Key 失效。

结构化记录只发布状态、耗时、条数、字符数、内容哈希、请求计数和有限窗口元数据，不发布文章/帖子全文、凭据或用户档案。安装后的运行验收另列。初始端点发现与文档查阅不在上述 11 次计数内；两次回复计量复查另加 2 HTTP。本轮未验证跨网络/跨系统可用性，也没有实现全国公告全集、任意 RSS URL、历史新闻库或完整评论树。

[使用说明](https://github.com/wjason/xcoze-search/blob/main/references/feeds.md) · [逐次记录](2026-11-05-feeds-community.data.json)
