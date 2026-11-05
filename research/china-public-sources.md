# 国内公开消息与数据源

**简体中文** | [English](china-public-sources.en.md)

[返回来源列表](../references/sources.md)

这里整理政府、统计、金融、科研、天气和新闻等公开入口。三个已接入的国内部门适配器只在当前栏目页面按标题字面筛选，不是全站或历史数据库。中国政府网最新政策栏目也已接入，见[来源与适配情况](../references/sources.md)。

下列 30 个入口在 2026-11-05（北京时间）的一次页面请求中均返回 HTTP 200；这只说明页面响应，不代表接口、搜索、下载、商业使用或后续访问均可用。接入状态以项目实现为准。[查看检查记录](china-public-sources-2026-11-05.json)。

## 政策与政务

| 来源 | 主要内容 | 接入情况 |
|---|---|---|
| [国家发展改革委通知](https://www.ndrc.gov.cn/xxgk/zcfb/tz/) | 通知栏目 | 已接入当前页面 |
| [工信部政务公开](https://www.miit.gov.cn/zwgk/index.html) | 工业与信息化政策文件 | 未接入 |
| [商务部](https://www.mofcom.gov.cn/) | 商务政策及公开信息 | 未接入 |

## 统计与经济

| 来源 | 主要内容 | 接入情况 |
|---|---|---|
| [国家统计局数据发布](https://www.stats.gov.cn/sj/zxfb/) | 数据发布栏目 | 已接入当前页面 |
| [国家数据](https://data.stats.gov.cn/) | 统计数据查询 | 未接入 |
| [人民银行统计](https://www.pbc.gov.cn/diaochatongjisi/116219/116225/index.html) | 金融统计发布 | 未接入 |

## 能源与环境

| 来源 | 主要内容 | 接入情况 |
|---|---|---|
| [国家能源局](https://www.nea.gov.cn/) | 能源资讯与公告 | 已接入首页资讯 |
| [生态环境部](https://www.mee.gov.cn/) | 生态环境政策与公开信息 | 未接入 |

## 气象与灾害

| 来源 | 主要内容 | 接入情况 |
|---|---|---|
| [国家气象科学数据中心](https://data.cma.cn/) | 气象数据服务 | 未接入 |
| [中国天气网](https://www.weather.com.cn/) | 天气预报与资讯 | 未接入 |
| [应急管理部统计](https://www.mem.gov.cn/gk/tjsj/index.shtml) | 灾害和应急统计发布 | 未接入 |
| [中国地震台网](https://www.ceic.ac.cn/) | 地震信息 | 未接入 |
| [中国海洋预报台](https://www.nmefc.cn/) | 海洋预报与警报 | 未接入 |

## 证券与金融

| 来源 | 主要内容 | 接入情况 |
|---|---|---|
| [证监会](https://www.csrc.gov.cn/) | 证券监管公告 | 未接入 |
| [巨潮资讯](https://www.cninfo.com.cn/new/commonUrl?url=disclosure%2Flist%2Fnotice) | 上市公司信息披露 | 未接入 |
| [上海证券交易所](https://www.sse.com.cn/disclosure/listedinfo/announcement/) | 上市公司公告 | 未接入 |
| [深圳证券交易所](https://www.szse.cn/disclosure/listed/notice/) | 上市公司公告 | 未接入 |
| [北京证券交易所](https://www.bse.cn/) | 证券市场与公司信息 | 未接入 |

## 法规标准与采购

| 来源 | 主要内容 | 接入情况 |
|---|---|---|
| [国家标准公开系统](https://openstd.samr.gov.cn/) | 国家标准目录及公开内容 | 未接入 |
| [国家法律法规数据库](https://flk.npc.gov.cn/) | 法律法规原文 | 未接入 |
| [中国政府采购网](https://www.ccgp.gov.cn/) | 政府采购公告 | 未接入 |
| [全国公共资源交易平台](https://www.ggzy.gov.cn/) | 公共资源交易信息 | 未接入 |

## 科研、航天与地学

| 来源 | 主要内容 | 接入情况 |
|---|---|---|
| [国家航天局](https://www.cnsa.gov.cn/) | 航天资讯与数据政策 | 未接入 |
| [中国科学院](https://www.cas.cn/) | 科研资讯与机构资源 | 未接入 |
| [科学数据银行](https://www.scidb.cn/) | 科学数据集 | 未接入 |
| [中国地质调查局](https://www.cgs.gov.cn/) | 地质资讯与数据资源 | 未接入 |

## 地方公开数据

| 来源 | 主要内容 | 接入情况 |
|---|---|---|
| [香港政府数据一线通](https://data.gov.hk/tc/) | 政府公开数据目录 | 未接入 |
| [香港天文台](https://www.hko.gov.hk/sc/abouthko/opendata_intro.htm) | 香港天气与预报 | 未接入 |

## 新闻

| 来源 | 主要内容 | 接入情况 |
|---|---|---|
| [中国新闻社 RSS](https://www.chinanews.com.cn/rss/) | 新闻订阅 | 已接入即时、财经 |
| [新华网](https://www.news.cn/) | 新闻资讯 | 未接入 |

## 天气和金融数据

[香港天文台实况天气](https://data.gov.hk/en-data/dataset/hk-hko-rss-current-weather-report)及九天天气预报在单次检查中返回带更新时间的 JSON，覆盖香港，目前尚未接入。天文台另有[使用条件](https://www.hko.gov.hk/tc/readme/readme.htm)，自动化或商业使用前应核对对应数据集的具体授权。

上市公司公告不等于实时股价；接入股票行情前仍需核实交易所覆盖、延迟、授权和时间标记。中国气象数据可能需要账号或满足单项数据的获取条件。[国家航天局科学数据管理办法](https://www.cnsa.gov.cn/n6758823/n6758839/c6805196/content.html)也列明公开数据需注册下载；公开目录不代表可匿名下载所有数据。

## 使用已接入的近期栏目

```bash
python3 scripts/xcoze_search.py search '生态' --platform ndrc --strategy free
python3 scripts/xcoze_search.py search '价格' --platform nbs --strategy free
python3 scripts/xcoze_search.py search '能源' --platform nea --strategy free
```

匹配方式是对当前页面标题进行字面筛选，未命中不能证明没有相关文件。显示日期是栏目日期，不一定是生效日期；能源局首页有的标题未显示日期。需要核对日期、统计口径和正文时，请继续读取原文。
