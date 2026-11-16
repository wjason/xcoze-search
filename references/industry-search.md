# 能源电力与招投标搜索

**简体中文** | [English](industry-search.en.md)

用于查找能源政策、电力统计、政府采购和电网采购公告。Agent 根据问题选择来源、整理关键词和筛选条件，用户无需记住平台参数。以下入口免 Key，不依赖 Exa、Parallel 或本地浏览器。

## 能源政策与电力统计

`--platform nea` 优先读取国家能源局网站公开的文件或新闻发布数据列表，再在本机检索标题和摘要。文件列表包含历史政策，新闻发布列表包含电力统计、用电量、绿证及新闻发布会。两个列表分别提供有限记录，不代表能源局完整历史数据库。

```bash
python3 scripts/xcoze_search.py search '新型储能 规模化' --platform nea --energy-section policy --start-date 2025-01-01 --end-date 2025-12-31
python3 scripts/xcoze_search.py search '全国电力统计数据' --platform nea --energy-section releases --start-date 2025-10-01 --end-date 2025-10-31
```

省略 `--energy-section` 时，统计、装机、用电量等查询优先新闻发布，其他查询优先文件。查询中的“电力统计”和历史标题中的“电力工业统计”兼容匹配，日期条件保持不变。每次读取一个公开数据列表，不向网站发送关键词；返回原文链接、列表日期及覆盖范围。日期筛选作用于列表日期，它可能与原文发布日期不同。需要确认统计期、数值、单位、成文日期或生效状态时，继续阅读原文。原首页列表仍可通过 `--provider nea` 调用。

来源：[公开文件](https://www.nea.gov.cn/policy/zxwj.htm)、[新闻发布](https://www.nea.gov.cn/xwfb/index.htm)。

## 政府采购与工程招标

`ggzy-search` 使用全国公共资源交易平台公开页面采用的公告查询接口。支持关键词、省份、发布日期区间、业务类型和公告阶段。`--platform government-procurement` 直接限定政府采购；`--platform ggzy` 可查询工程建设等交易公告。

```bash
python3 scripts/xcoze_search.py search '储能' --platform government-procurement --notice-type tender --region 广东 --start-date 2026-10-01 --end-date 2026-11-16
python3 scripts/xcoze_search.py search '储能' --platform ggzy --business engineering --notice-type award --start-date 2026-10-01 --end-date 2026-11-16
python3 scripts/xcoze_search.py search '储能' --platform ggzy --business engineering --trading-source central --start-date 2026-10-01 --end-date 2026-11-16
```

| 参数 | 可选内容 |
|---|---|
| `--business` | `government` 政府采购；`engineering` 工程建设 |
| `--notice-type` | 两类均支持 `tender` 招标/采购、`award` 中标/结果、`correction` 更正；政府采购另支持 `contract` 合同 |
| `--region` | 省级名称或六位省级代码，如 `广东`、`广东省`、`440000` |
| `--trading-source` | `province` 省平台（默认）、`central` 央企、`finance` 财政部来源 |
| `--page` | 本次读取的页码，1–100；不自动连续翻页 |

省平台支持地区和公告阶段筛选；央企、财政部来源暂不接受这两个条件，避免套用未经验证的筛选规则。指定公告阶段时需同时指定业务类型。未指定日期时使用网站的“近三月”；自定区间需要同时提供起止日期。每次读取一页，最多返回 20 条。结果再检查标题关键词、地区、日期和公告代码；“仓储能力”不会因字符相邻被当成“储能”。

结果保留公告原文、地区、来源平台、业务和公告类型。项目编号、采购人或截止时间未提供时保持空值；公告日期不等于投标截止时间，中标公告也不代表仍可投标。核验项目资格、预算、截止时间和更正内容需读原文。

中国政府采购网本身仍支持首页近期公告。其关键词搜索入口本次出现访问频繁提示，**尚未接入全站检索**；政府采购检索由公共资源交易平台提供，不将它标为采购网原生搜索。

来源：[交易公开查询](https://www.ggzy.gov.cn/deal/dealList.html)、[中国政府采购网](https://www.ccgp.gov.cn/)。

## 南方电网采购公告

南网适配读取已公开的公告列表，对本次页面的标题和日期进行筛选。每页约 10 条，默认读取招标公告第一页；它不是关键词站内搜索，不自动扫描历史页。

```bash
python3 scripts/xcoze_search.py search '数字化' --platform csg --notice-type tender
python3 scripts/xcoze_search.py search '云南' --platform csg --notice-type award
python3 scripts/xcoze_search.py search '电网' --platform csg --notice-type tender --page 2
```

`tender` 对应招标列表，`non-tender` 对应非招标列表。`award`、`candidate`、`correction`、`cancel` 在公示列表中分别筛选中标结果、候选人、更正和中止等标题；没有识别出阶段的标题不会冒充指定类型。公示栏目包含多种公告，不能把整栏视为已中标项目。列表若截断标题，会标明 `title_truncated`；发布单位不是已确认的采购人。

来源：[招标公告](https://www.bidding.csg.cn/zbgg/index.jhtml)、[公示公告](https://www.bidding.csg.cn/zbhxrgs/index.jhtml)。南网关键词搜索本次返回 403，未接入；国家电网搜索仍待验证。

## 调研时如何使用

Agent 保留用户的问题，将主题词与地区、日期、公告阶段分别表达。例如“最近广东有哪些储能政府采购？”使用 `储能` 作为查询词，并设置广东、日期区间及政府采购类型；不把整句问题当作标题中的连续文字。

一次列表没有命中不代表不存在相关项目。Agent 可在任务预算内查看指定的下一页、切换另一个符合条件的官方来源或继续通用搜索。能源统计同时区分统计期与发布日期；采购调研同时区分采购意向、招标、候选人、中标、合同与更正。缺失字段不猜测，不把采购摘要当成已读取招标文件。

各入口独立限频；遇到访问拒绝、验证或频繁提示时暂停，不识别验证码或使用登录态。公开网页接口可能变化，支持状态和本次记录见[专项实测](../evaluations/reports/2026-11-16-energy-procurement.md)与[来源状态](source-status.md)。
