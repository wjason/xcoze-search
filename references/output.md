# 输出契约 v0.3.0

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

auto 不自动多发；both 固定为 DeepSeek＋元宝；逗号列表按用户顺序调用，all 按注册顺序使用已配置服务。参数和所需凭据在发送前整体校验。运行中的部分失败保留成功结果，ok:false/complete:false；另一家正常完成（即使空结果）时 partial:true。全部失败不是部分成功。

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
