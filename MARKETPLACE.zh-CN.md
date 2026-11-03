# 通用商城上架资料

**简体中文** | [English](MARKETPLACE.en.md)

名称：**xcoze search**
ID：`xcoze-search`
版本：`0.4.0` 预览版
维护方：XCoze
仓库：[wjason/xcoze-search](https://github.com/wjason/xcoze-search)

## 简述

为 Agent 自动选择免 Key 与商用搜索来源，检索最新公开资料、读取网页并保留出处。

## 功能说明

安装后日常提问即可。无 Key 使用公开渠道，有 Key 默认效果优先；需要调整时可保存平衡、免费或默认来源偏好。自动失败备用受来源数、HTTP 次数和等待预算限制，Agent 负责判断信息缺口并核对原文。

免 Key 支持 Bing RSS、DuckDuckGo HTML、Exa 托管 MCP、GitHub 公开仓库、Hacker News；Jina Reader 用于正文读取。支持自带 Key 的 DeepSeek、元宝、Tavily、Exa、Brave、博查。知乎、小红书、微博为公开索引定向搜索，不承诺站内搜索、完整正文或评论。

## 安装与依赖

```text
安装 https://github.com/wjason/xcoze-search
```

Python 3.10+，运行无 pip 或浏览器依赖；宿主需要 Agent Skills 和本地命令能力。可选 Skills CLI 安装需 Node.js。Key 在本机隐藏输入，不发到聊天；只输出申请链接，不自动打开页面。详见 [安装](INSTALL.zh-CN.md)、[配置](references/setup.md)。

## 数据与边界

查询与目标 URL 发往所选来源，不经过 XCoze 自建中转。免 Key 仍使用外部服务和各自限额。凭据当前为权限保护的明文文件；没有系统凭据库。搜索成功不等于事实正确，实时检索不保证索引即时更新。自建搜索、企业资料、整站爬取不在当前范围。

离线测试、逐来源在线结果和未验证项目见 [验证记录](VALIDATION.md)。商城未确定，本文件不表示已上架、认证或通过审核。标签可用：search, agent, keyless, research, citations, web-fetch。
