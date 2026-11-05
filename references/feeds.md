# 新闻订阅、政府政策与社区主帖

**简体中文** | [English](feeds.en.md)

## 新闻 RSS 与政策窗口

```bash
python3 scripts/xcoze_search.py feeds
python3 scripts/xcoze_search.py feed --source cns-scroll --start-date 2026-11-05 --end-date 2026-11-05
python3 scripts/xcoze_search.py feed --source cns-finance --query '进博会' --count 5
python3 scripts/xcoze_search.py feed --source bbc-world --count 5
python3 scripts/xcoze_search.py feed --source hk-data --count 5
python3 scripts/xcoze_search.py feed --source govcn --query '登记管理'
python3 scripts/xcoze_search.py search '登记管理' --platform govcn --strategy free
```

`feeds` 完全离线。`feed` 每次只读一个固定公开源，默认 8 秒、一次 HTTP、零重试，不读凭据、不启动浏览器。--query 为全部空白分隔词的字面匹配，范围仅标题/摘要；使用短关键词，不能把整句问题当语义搜索。日期为 UTC+08:00 的日历日，首尾包含；未知日期在有日期条件时排除。RSS pubDate/Atom published 用作源提供的发布时间，Atom updated 不充当发布时间。重复 URL 去 fragment 后只保留第一条，保留源顺序与 rank 缺口，不跨站判断独立性。

当前源：中新网即时与财经 RSS、BBC World RSS、香港政府数据更新 RSS、中国政府网最新政策 JSON。香港 RSS 是近期数据集更新目录，内容主要为英文。只读本次返回窗口，不追历史分页、不持续订阅。metadata 报 source_row_count、matched_count、shown_count、newest_publication、oldest_publication、unknown_dates_excluded 和 duplicate_urls_removed；window_complete:false。最新发布时间不等于源更新时间，也不保证窗口覆盖了每一条新闻。BBC 的原始时区保留在 published_at，筛选时换算北京时间。

GovCN 可通过 search --platform govcn 参与原生优先选路，仍遵守免费模式、已保存来源禁用和原有请求预算。其列表包含政策文件、解读等，不是全国全部公告；只能按当前列表过滤。发布日、成文日、生效日分别核对，正文仍需 fetch/宿主读取。没有匹配或窗口太旧时，Agent 按原有偏好继续搜索，不能据此断言没有相关信息。

RSS 描述与政府索引分别标记 feed_excerpt、official_policy_index，content 保持为空；不能当作已读整篇文章。文章 URL 只作为来源，不自动抓取；需要正文时再读。每源至少间隔 2 秒、跨进程串行，429/503 遵守 Retry-After；源失效/格式变化保留错误，不当作成功空列表。

## 社区主帖原文

```bash
python3 scripts/xcoze_search.py fetch 'https://discuss.python.org/t/109869' --strategy free
python3 scripts/xcoze_search.py fetch 'https://users.rust-lang.org/t/forum-code-formatting-and-syntax-highlighting/42214' --strategy free
python3 scripts/xcoze_search.py fetch 'https://www.v2ex.com/t/1254349' --provider community --strategy free
```

自动 fetch 对这三站优先 community 原生读取。只接受标准 HTTPS 主帖根 URL；拒绝 fragment、查询参数与回复定位，避免误读成另一篇主题或悄悄把回复替换为主帖。已知回复链接由宿主工具读取该确切目标。

Python/Rust 使用 Discourse 公开 Topic JSON，选择 post_number:1；V2EX 使用公开单主题接口。返回 community_original_post，默认最多 24000 字符，可用 --max-characters 1000–200000；truncated 和 returned_characters 如实报告。Discourse cooked HTML 转为保留代码缩进/链接目标的纯文本，content_format 说明转换形式，不承诺原 HTML/Markdown 的逐字排版。

只输出主帖。Discourse 响应可能附带首批回复，comments_fetched/source_attached_replies 记录实际附带数量，comments_included:false 表示回复正文未输出；不额外翻页拉评论。thread_complete:false、completeness_verified:false，不声称读过完整讨论，也不把用户观点当事实结论。

三站各自限频和冷却；HTTP 401/403/412 暂停 15 分钟，自动 fetch 在访问拒绝或冷却时停止切换阅读服务，不换身份/代理/浏览器。V2EX 的访问可能受到网络环境或平台限制。其他任意社区暂不走此原生适配，可按既有授权使用宿主阅读工具。

[真实测试记录](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-05-feeds-community.md) · [输出契约](output.md)
