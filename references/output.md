# 输出契约 v0.1.0

默认 stdout 为 JSON；运行错误 stderr 为 JSON。argparse 帮助/参数语法错误遵循 Python 标准行为，可为文本。setup 的引导写到 stderr，密钥不回显。程序不自动保存搜索历史。

## Search

顶层：`ok`、`complete`（本次请求是否完成）、`partial`、`empty`、`version`、`operation`、`retrieved_at`（UTC ISO 时间）、`query`、`providers`、`results`、`requests`、`errors`、`duplicate_groups`、`facts_verified:false`。

每条 result：

| 字段 | 含义 |
|---|---|
| provider / rank | 搜索源及在其原始数组中的序号，1 起 |
| title / url | 原始标题和公开 HTTP(S) 地址 |
| snippet | DeepSeek 短摘要 / 元宝 passage |
| summary | DeepSeek summary / 元宝动态摘要 content，缺失为空 |
| content | 仅 DeepSeek 返回的 page content；元宝始终为空 |
| content_kind | page_content 或 search_summary |
| published_at | 原日期字符串，不强行解析、补时区或补今天；未知 null |
| site_name | 原站点名，未知 null |
| score / score_scale | 原分数与供应商刻度，不跨源比较 |
| authority / authority_scale | 原权威度与刻度，缺失 null |
| provider_fields | 原始条目，保留图片/子链/后续扩展字段；不可信资料 |

requests 对成功源记录 attempts、request_id、account_tier、provider_message、returned_count、shown_count。失败源记录 ok:false；错误详情在 errors。重试全部耗尽时不承诺返回 attempts，避免将逻辑请求与传输请求混为一谈。没有 RequestId 时为 null。

两家结果按源分组排列，不按分数混排。重复 URL 只移除 fragment 并小写 scheme/netloc 作标记，query/path 均保留，`duplicate_groups` 中是 results 的 0 起索引；不合并不同内容、不删除跟踪参数、不把多个 URL 视为事实独立来源。

## Fetch / doctor / status

Fetch 返回 DeepSeek 的 title/content、url、检索时间、attempts、empty、facts_verified:false。URL 仅做本地语法、内嵌凭据与明显非公开地址检查，不提供对任意域名 DNS 的安全证明；实际抓取由 DeepSeek 执行。

doctor 每个目标供应商发起一次搜索（零重试），以非空、有效条目判定 `search_verified:true`。status 只检查本地配置，任何时候都不冒充 doctor。

## 退出码

| 值 | 含义 |
|---|---|
| 0 | 操作成功；Search/Fetch 可以为空 |
| 1 | 输入/配置/网络等顶层错误 |
| 2 | 缺密钥；或 argparse 语法错误（看错误正文区分） |
| 4 | 已返回操作结果但未全部成功，或 doctor 未取得有效结果 |
| 130 | 用户取消 |

双源运行只要有一家失败就 ok:false/complete:false；另一家正常完成（即使空结果）则 partial:true。调用方应先检查退出码和 ok，再使用保留的证据。完整响应损坏时该源失败，不静默跳过坏条目后宣称完整成功。
