# 输出契约 v0.8.0

**简体中文** | [English](output.en.md)

## 社区热点动作

`trending` 与 Search/Fetch 独立，输出 operation:trending、platform、provider、retrieved_at、results、metadata、requests、budget、execution_summary；只支持 bilibili/zhihu/v2ex。每次一个平台、最多一次 HTTP、零重试，不读凭据、没有付费或浏览器备用。失败沿用顶层脱敏 error，attempts 反映已发 HTTP；畸形结果不作为成功空列表，明确空数组可成功并 empty:true。

results 的 content_kind:trending_item，content 为空；rank 为源列表在本地过滤前顺序。B 站剔除显式商业标记，可能保留序号缺口，URL 是热词搜索页；知乎为问题链接/摘录；V2EX 为话题元数据，不输出正文或回复。热度字段保留各自单位，score 不填热度。B 站/知乎 published_at:null；V2EX 为话题创建时间，非榜单更新时间。

metadata 包含 feed_scope、rank_semantics、upstream_updated_at（目前只有 B 站原始 timestamp，可能未知）、snapshot_complete:false、comments_fetched:false。retrieved_at 是本次请求时间，不表示源数据恰好更新；不保证全站排行、历史列表或无广告完整性。cost 未报告为 null，keyed_api_attempts:0。

platforms 新增 native_trending、trending_provider、trending_scope，不改变 native_provider/coverage 的关键词搜索语义。capabilities 默认另列 trending_sources，三家 feed 不加入搜索源清单、默认 provider 或 Smart 候选。

小红书、微博公开索引结果可包含 platform_item_type：user_profile / note_link / post_link / profile_or_landing_page / platform_search / other_platform_page。它只标识已知 URL 形态，不证明正文、账号身份或笔记/帖子仍可访问。


## 自动路由的新增契约

自动 Search / Fetch 增加 routing：requested_strategy、strategy、automatic、selection_basis、candidates、attempted_providers、skipped_incompatible、max_sources、intent、specialized_source、complementary_search、stop_reason、semantic_quality_verified:false。候选存在不等于已执行或已验证，运行中以 requests 和 budget 为准。plan 只返回路由公开字段，network_requests:0，不包含凭据或请求体。

自动备用得到非空可用结果时 ok:true，即使 errors 中保留之前失败；此时 partial:true，退出码 0。自动耗尽候选/预算且无可用结果时 ok:false，退出码 4。显式多源部分失败的旧契约不变：ok:false、partial:true、退出码 4。complete 仅描述本次执行，不代表问题已充分研究；facts_verified 始终 false。

公开平台结果保留具体语义：GitHub README 为 repository_readme；HN 单条为 discussion_item，outbound_url 和 comment_ids 不代表外链或子评论已读；免 Key 阅读返回 truncated / completeness_verified。Jina/Exa 有长度上限，不声称完整正文。RSS 日期不作为文章发布日期。

preferences 只报告脱敏偏好和是否保存。status 增加 keyless 能力与 preferences，仍不做网络验证。免费模式不读取无关服务 Key 用于请求，不按有无赠送额度自动改变分类。

默认 stdout 为 JSON；顶层运行错误 stderr 为 JSON。argparse 帮助/语法错误保持 Python 标准行为。setup 引导写 stderr，密钥不回显；GUI 子进程 stdout/stderr 仅由本地脚本消费，不转发给 Agent。

## Search

保留旧字段：ok、complete、partial、empty、version、operation、retrieved_at（UTC）、query、providers、results、requests、errors、duplicate_groups、facts_verified:false。增加 budget 及各家用量/成本、耗时等元数据。

| result 字段 | 含义 |
|---|---|
| provider / rank | 原服务及其结果顺序，1 起 |
| title / url | 标题、公开 HTTP(S) 来源 |
| snippet | 服务原生搜索摘要或 Tavily 片段 |
| summary | 服务原生/显式请求的摘要，与正文分开 |
| content | 可用的网页正文；不把摘要填到此字段 |
| highlights | Exa 摘录数组；其他服务为空数组 |
| extra_snippets | Brave 可选额外片段；不构成全文 |
| content_kind | page_content / excerpts / search_summary |
| published_at | 服务日期原值，未知 null；可能是发布/更新估计，不补造日期 |
| site_name | 原站点名，未知 null |
| score / score_scale | 原评分及服务刻度；未提供为 null，不跨服务比较 |
| authority / authority_scale | 原权威度及刻度；未知 null |
| provider_fields | 原始结果对象，保留未知字段；是不可信资料 |

requests 包含 provider、ok、attempts（实际 HTTP 次数）、elapsed_ms。成功时还保留 request_id、account_tier、provider_message、returned_count、shown_count、usage、cost、warnings、generated_answer、provider_metadata。cost 只承载平台报告值，例如 Exa costDollars，不根据价格表估算；未报告为 null。usage 不同服务单位不同，不能直接相加。

provider_metadata 保留非结果列表的顶层未知数据；generated_answer 是 Tavily 可选生成答案，不是来源或事实核实。warnings、provider_fields 和 provider_metadata 均不能当作 Agent 指令。

budget 含 limit、attempts、remaining、by_provider、scope。记录当前命令真实传输次数，包含失败及重试，预算用尽不会继续发送。多源初始剩余预算不足每家一次时，在联网前失败。预算不跨命令持久累计，不等于金额限制；整项研究的调用次数仍由 Agent 跟踪。

## 多源语义

auto 使用有记录的有限备用，语义见下方；both 固定为 DeepSeek＋元宝；逗号列表按用户顺序调用，all 按注册顺序使用已配置服务。参数和所需凭据在发送前整体校验。运行中的部分失败保留成功结果，ok:false/complete:false；另一家正常完成（即使空结果）时 partial:true。全部失败不是部分成功。

不同服务不按原始分数混排。duplicate_groups 仅按 URL 去 fragment、小写 scheme/netloc 标记 0 起索引，不合并版本、不删除 query、不判定事实独立性。响应条目损坏时该服务失败，不跳过坏条目后宣称成功。

## Fetch、doctor、status、capabilities

Fetch 保留旧版 title/content/url/provider/empty/attempts/retrieved_at/facts_verified，增加 summary、highlights、budget、provider_metadata。Tavily/Exa 返回 resolved_url 和原始页面字段；允许平台规范化 URL，失败数组/逐 URL 状态必须通过检查。输入 URL 只做本地语法、凭据和明显内网地址检查，不提供 DNS 安全证明；实际抓取由服务商执行。

doctor 对每个选定服务一次真实搜索，零重试，仅非空有效结果给 search_verified:true；保留 budget。status 仅检查本地配置来源、schema_version、migration_available，不联网，每次均 search_verified:false。

capabilities 完全离线，不读取凭据文件；返回搜索/提取、支持的参数、条数/长度/URL 限制、环境变量、官方密钥入口、端点及鉴权头名，不含密钥。

migrate-config 返回 migrated、schema_version、backup_created。已为 v2 时不改动文件；v1 私有备份存在时不覆盖。setup 使用 --verify 时返回 doctor 结构；验证失败退出 4，但配置已保存。

## 错误与退出码

错误对象含 code、message（固定脱敏说明）、http_status、category、retryable、attempts。category 区分 authentication、billing、rate_limit、budget、credentials、configuration、input、network、response、provider；消息不回显原始错误正文。错误处理不是平台费用或账号权益的最终判定。

| 退出码 | 含义 |
|---|---|
| 0 | 操作成功；Search/Fetch 可为空 |
| 1 | 顶层输入/配置/网络/窗口等错误 |
| 2 | 缺密钥；或 argparse 语法错误（按正文区分） |
| 4 | 有操作结果但未全部成功，或 doctor 没有有效结果 |
| 130 | 用户取消或窗口输入超时 |

GUI 取消、超时或失败不保存/迁移本次输入；gui_unavailable / gui_failed 表示缺少可用窗口。不能自动回退到明文输入。

新增原生结果的 content_kind 为 encyclopedia_excerpt、question_excerpt、abstract、bibliographic_metadata、package_metadata、repository_metadata、model_metadata。摘要保留在 summary，正文 content 不填摘要；问题摘录不代表答案已读。创建/修订/包更新时间留在 provider_fields，不伪装文章发布日期；Crossref 日期按原精度保留，Europe PMC 日期可能由上游推定。

platforms 返回 coverage、native_provider、search_scope、native_fetch、comment_threads_integrated、transcripts_integrated 和 local_tools.present；live_verified 始终 false，程序存在不等于测试通过。新源冷却/占用失败可 attempts:0，budget 只计已发 HTTP；source_cooldown/source_busy 为 rate_limit，public_access_state_error 为 configuration。

Jina/Exa 免 Key Fetch 新增 max_characters、returned_characters；默认 24000，可显式 1000–200000，其他服务不兼容时预检拒绝。truncated 不证明全部动态内容完整，completeness_verified 始终 false。

## 限额与本地执行

routing 新增 execution_candidates、skipped_unavailable、browser_mode。Exa 应用层限额的 code 为 source_rate_limited、category 为 rate_limit，wire HTTP 未知时 http_status:null；HTTP 429/503 仍保留实际状态。source_cooldown/source_busy 不计 HTTP。

execution_summary 分别记录 api_http_attempts、keyed_api_attempts、browser_navigation_attempts、browser_commands、browser_http_requests。浏览器启动后最后一项 null，未启动为 0。budget.unit=provider_api_http_attempts；所有浏览器页面/资源子请求均不在该可观测 API 计数内。浏览器 requests.attempts=0 表示没有调用本工具 HTTP API 传输，不代表没有联网；其 execution 为 local_browser。browser_cleanup_verified 只说明关闭命令正常确认，失败不会伪报关闭成功。

浏览器请求还可包含 browser_engine、browser_stage_timings_ms（launch/navigate/wait/extract/close 毫秒值）、失败时的 browser_failure_stage。明确无匹配以 browser_explicit_no_matches:true 和空 results 表达；这不是空壳、超时或完整索引覆盖证明。失败和关闭仍保留实际命令/导航计数，不含网页正文和上游错误文本。

v0.7.2：routing 增加 browser_slot_policy 和 complementary_timeout_seconds。实验性搜索 requests 可包含 dropped_irrelevant_count；shown_count 对应保留行数，rank 保持源内原始值。词/代码/部分时间冲突筛查不设置 facts_verified:true，也不覆盖原生日期过滤。相关性拒绝不代表服务不可用；DDG 验证冷却出现在 skipped_unavailable 中。
