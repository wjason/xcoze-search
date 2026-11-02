# 通用商城上架资料

名称：**xcoze search**

技能 ID：`xcoze-search`

版本：`0.2.0` 预览版。上架时以实际提交的版本为准。

维护方：XCoze

简述：一个 Skill 接入 DeepSeek 与腾讯元宝官方搜索 API，配置对应 API Key 后即可使用。

分类建议：搜索 / 研究 / 信息检索

标签建议：search, research, deepseek, yuanbao, tencent, citations, web-fetch

## 详情介绍

xcoze search 为支持本地 Python 的 Agent Skills 助手增加双供应商公开资料检索能力。用户可以只配置 DeepSeek 或元宝，也可以配置两家并明确发起交叉搜索。

工具保留来源链接、可用日期、供应商与原始字段，帮助助手阅读证据、核实差异并给出带引用的回答。DeepSeek 支持公开网页正文抓取；元宝支持站点与相对时间等筛选，具体能力取决于账号版本。

## 使用前提与数据说明

- Python 3.10+，无需 pip 运行依赖；宿主可以执行本地脚本。
- 用户自行开通对应官方 API 服务并提供自己的 Key。元宝需要“元宝搜索服务 API Key”。
- Key 在用户本机隐藏输入，不应发到聊天；查询直接发送到所选供应商。
- 支持在对话中发起配置：助手提供官方申请链接，用户自行点击；取得 Key 后在本地窗口输入，无需查找配置文件。窗口依赖操作系统桌面能力，无桌面时保留终端配置方式；各桌面人工验收状态见 VALIDATION.md。
- API 调用可能计费；费用、配额和条款以官方平台为准。
- 本技能是 XCoze 独立开发的集成，不是 DeepSeek 或腾讯官方发布/认证的技能。

## 示例提示词

- “用 xcoze search 搜索最新公开技术文档，优先官方来源。”
- “用元宝搜索近七天的行业报道，附原文链接。”
- “用 DeepSeek 和元宝交叉核实这条消息。”

## 提交时填写

仓库：https://github.com/wjason/xcoze-search

版本与发布资产：https://github.com/wjason/xcoze-search/releases（以实际已发布的 Release 为准）。联系渠道、商城要求的图标/截图与审核字段由发布者在确定平台后填写。

当前验证口径：离线测试已通过；DeepSeek Search/Fetch 已于 2026-10-24 实测通过；元宝账号调用仍待配置 Key 后验证。上架前若完成实测，更新 VALIDATION.md 并仅记录脱敏结果。商城是否收录、是否认证、是否通过审核均不能由本包保证。
