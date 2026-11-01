# 官方接口依据与能力矩阵

核对日期：2026-10-24。本文件概述适配决策，具体计费、配额、可选字段与版本以官方实时文档为准。

| 能力 | DeepSeek | 腾讯元宝 |
|---|---|---|
| 官方端点 | `POST https://api.deepseek.com/v1/tools/search` | `POST https://api.wsa.cloud.tencent.com/SearchPro` |
| 鉴权 | Bearer API Key | Bearer 元宝搜索服务 API Key |
| 查询字段 | `query` | `Query` |
| 查询限制 | 128 Unicode 字符，含追加 site 条件 | 本工具保守限制 1500 UTF-8 字节；依据官方 MCP 工具参数说明 |
| 条数 | `count` 1–50 | 基线不发送 `Cnt`；count>10 时按 20/30/40/50 取整发送，再本地截取 |
| 站点 | 追加 `site:域名` | `Site` 单域名；混合/垂直结果中的 VR 不保证受站点限制 |
| 时效 | 查询词支持 `after:`/`before:`，由调用方显式编写 | `Freshness`；CLI 仅支持 d1..30/m1..12/y1..5 |
| 垂域/模式 | 本工具不映射 | `Industry`/`Mode`，按服务版本可用 |
| 正文 | search 可 `need_content`；另有 Fetch API | `passage` 标准摘要、`content` 动态摘要；不当作全文 |
| 响应 | `results` 对象数组 | `Response.Pages` JSON 字符串数组；兼容对象条目 |
| 评分 | 原样保留 0–3 相关性、-1..4 权威度 | 原样保留 0–1 相关性、0–5 权威度；部分版本缺字段 |

## DeepSeek

- [Search & Fetch 指南](https://api-docs.deepseek.com/guides/search/)
- [Search 参考](https://api-docs.deepseek.com/api/search/)

Fetch 端点固定为 `POST https://api.deepseek.com/v1/tools/fetch`，请求 `url`，返回 `title` 和 Markdown `content`。网页可能受站点策略限制。空内容/空结果与网络失败分别表达。

## 元宝

- [服务 API KEY 方式](https://cloud.tencent.com/document/product/1806/130615)：单 Key 的 HTTPS REST 入口、响应包裹和业务错误。
- [SearchPro 参数](https://cloud.tencent.com/document/product/1806/121811)：使用其中业务字段结构，不能把腾讯云标准签名入口当作 Bearer Key 入口。
- [官方 MCP 工具说明](https://developer.cloud.tencent.com/mcp/server/11764)：补充查询字节限制；本包直接调用 REST，不要求安装 MCP。
- [产品概述/版本差异](https://cloud.tencent.com/document/product/1806/121794)。

官方 MCP 页面曾把 Cnt 标成字符串，而 REST API 参数表明确是 Integer；本工具按 REST Integer 实现。时效日期范围在文档文字与例子存在顺序矛盾，v0.1.0 只开放无歧义的相对范围。极速版不支持部分参数，故基线请求只发送 Query 和用户显式要求的通用条件。响应版本、Msg 和 RequestId 会被保留，结果不足条数不补造。

## 费用与数据流

查询发送到选定供应商；both 发送两次，各自按平台计费。Fetch 把 URL 发给 DeepSeek。可能发生短期免费/配额优惠，本工具不承诺免费、不把某个客户端的免费政策推广到所有直接 REST 调用。

不调用聊天补全接口，不要求额外大模型 Key，无 XCoze 中转服务器、遥测或后台上传；只请求固定官方端点。调用方仍需遵守平台服务条款和网页内容使用规则。
