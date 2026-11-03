# 开放来源与平台协作

**简体中文** | [English](open-sources.en.md)

这里的本地搜索是由本机 Agent 直接发起公开接口请求，仍需联网。基础包只用 Python 标准库，不要求账号、常驻服务或浏览器。以下能力与平台当前限额有关，不承诺持续可用。

## 原生接口

| platform | 任务 | 日期/语言含义 | 主要边界与官方文档 |
|---|---|---|---|
| wikipedia | 中英文百科条目 | --language en/zh；中文查询默认中文。编辑时间不作为发布日期 | 条目摘录；[MediaWiki](https://www.mediawiki.org/wiki/API:Search) |
| stackexchange | 技术问题与报错案例 | --site 支持 Stack Overflow、Super User、Server Fault、Ask Ubuntu、Math/Stats/DataScience；start/end 为问题创建日期 UTC | 问题摘录，不读答案；保留作者/许可；[API](https://api.stackexchange.com/docs/advanced-search) |
| arxiv | 预印本 | start/end 为 submittedDate 日期区间，不是最近修订时间 | 摘要与元数据，不读取 PDF；[API](https://info.arxiv.org/help/api/user-manual.html) |
| crossref | DOI 和出版信息 | start/end 映射 from/until-pub-date；年/月/日按原精度保留 | 注册书目不等于论文鉴定，同名需核对作者、年份；[API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) |
| npm | JavaScript 包 | 版本和注册表日期保留为元数据，不充当文章发布日期 | 不审计依赖与安全；[API](https://api-docs.npmjs.com/) |
| crates | Rust 包 | 保留 max_version / max_stable_version 区别，创建/更新时间不当发布日期 | 不把预发行版叫稳定版；[数据访问](https://crates.io/data-access) |
| gitlab | GitLab.com 公开项目 | 名称/路径/描述搜索，按星标排序；不提供出版日期过滤 | 不是代码搜索/官方身份验证；[Projects API](https://docs.gitlab.com/api/projects/) |
| europepmc | 生物医学文献 | start/end 为 FIRST_PDATE，上游可能推定缺失日期 | 摘要不等于全文，不据此验证临床结论；[API](https://europepmc.org/RestfulWebService) |
| huggingface | 公开模型 | 按下载量排序，创建/修改日期留在元数据 | 不读完整模型卡、不下载/推理，gated 权限另行开通；[API](https://huggingface.co/docs/hub/api) |

每个新增适配器最多 20 条，基础命令默认 10 条，不自动分页；限制可能比上游严格。`--site` 仍需匹配对应来源，Crossref 平台使用 doi.org 稳定记录链接。原生来源可由 --provider 直接指定；禁用来源不会自动启用。通用查询不会无差别广播到这些平台，Agent 从原问题选择平台或保留通用搜索。

```bash
python3 scripts/xcoze_search.py platforms
python3 scripts/xcoze_search.py platforms --platform bilibili
python3 scripts/xcoze_search.py search '风力发电' --platform wikipedia
python3 scripts/xcoze_search.py search 'asyncio TaskGroup' --platform stackexchange
python3 scripts/xcoze_search.py search 'all:"retrieval augmented generation"' --platform arxiv --start-date 2026-01-01
python3 scripts/xcoze_search.py search 'playwright' --platform npm
python3 scripts/xcoze_search.py search 'tokio' --platform crates
python3 scripts/xcoze_search.py search 'inkscape' --platform gitlab
python3 scripts/xcoze_search.py search 'Qwen' --platform huggingface
```

## 公开索引和本机工具

知乎、小红书、微博、YouTube、B 站、Reddit、X、V2EX、豆瓣目前使用站点限定的公开索引，平台列表不会把它们标为原生搜索。网页 `fetch` 不代表评论或字幕已取得。

本机已有 Agent Reach 时，可读它的 Skill 并用 `agent-reach channels` 查看实际动作；例如 read URL、youtube subtitle、xiaohongshu comments。它不是本项目依赖，本项目没有内置执行桥接，不自动安装/更新、代登或拷贝会话。需要新的依赖/登录时按用户意图处理，已有公开内容先交付。PLATFORM_BLOCKED、RATE_LIMITED、NEED_LOGIN、BUSY 不通过换账号、后端或浏览器反复请求。字幕转录可另用付费服务，免费搜索偏好不等于授权新的付费转录。

也可按宿主已有授权使用 yt-dlp、gh、agent-browser。`platforms.local_tools.present` 只说明 PATH 上存在程序；不读浏览器配置，不检测会话，不证明可用。

## 限频、缓存与长文

新增源采用带项目联系地址的 User-Agent、每源串行 OS 锁和跨命令时间戳。arXiv 至少间隔 3 秒，GitLab 2 秒，其他新增源 1 秒；短间隔最多等待 3 秒且扣减网络超时预算。较长等待返回 source_cooldown，锁占用返回 source_busy，均不计 HTTP 尝试。Stack Exchange 同 URL 请求一分钟内抑制重复，遵守 backoff；quota_remaining=0 后冷却到下个 UTC 日。429/503 的 Retry-After 支持秒数和 HTTP 日期。独立搜索索引备用不向受限平台重复直接请求。

状态位于 XDG_CACHE_HOME/xcoze-search/public-access，Windows 可回退 LOCALAPPDATA，其他情况 ~/.cache。只保存节奏时间和重复查询哈希，不保存查询文本、结果、Cookie 或 Key；不缓存搜索答案。多机器或其他工具共享同一 IP 的调用不受此本机锁约束，仍需遵守上游合计限制。缓存不可读/损坏时该源停止，不悄悄清空以绕过退避。可由 Agent 定位并排查，不要求用户找文件。

正文默认最多 24000 字符，需要遗漏段落时再执行 `fetch URL --max-characters 100000`；仅 Jina/Exa 免 Key支持，最大 200000。`truncated` 表示本机裁剪或已触及请求上限的风险，`completeness_verified:false` 始终保留，不能据长度声称整页已完整读取。

[本轮实测与 Agent Reach 研究](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03-open-sources.md)。
