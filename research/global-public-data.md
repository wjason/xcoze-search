# 全球公开数据源

**简体中文** | [English](global-public-data.en.md)

[返回来源列表](../references/sources.md)

本页整理适合 Agent 查询的公共数据。接口响应、来源内容和实际接入是不同状态；使用前还需核对上游规则、更新频率、覆盖范围及内容许可。

## 已接入

| 来源 | 能力 | 说明 |
|---|---|---|
| [NASA 素材库](https://api.nasa.gov/) | 关键词查询图片、视频、音频的标题、描述与创建时间 | 结果是素材元数据，未下载媒体；单项素材的使用条件由其来源决定。 |
| [美国联邦公报](https://www.federalregister.gov/developers/documentation/api/v1) | 关键词查询美国联邦公告及摘要 | 发布日期与生效日期不同，需要阅读原文确认。 |
| [世界银行](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392) | 按国家和指标代码查询经济与社会统计 | 数据按观察年份记录，有空值或修订，不是实时股价；需要先确认国家和指标代码。 |
| [USGS 地震订阅](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php) | 查询近期地震的震级、位置和发生时间 | 地震数据可能修订；各时间窗口和震级门槛有不同覆盖，事件时间以 UTC 返回。 |

在 2026-11-05 的单次检查中，上述四条均通过 xcoze search 的免 Key 路径返回了结果。一次成功不能保证所有网络或后续请求都成功。

```bash
python3 scripts/xcoze_search.py search 'james webb' --platform nasa --strategy free
python3 scripts/xcoze_search.py search 'renewable energy' --platform federalregister --strategy free
python3 scripts/xcoze_search.py search 'CN,SP.POP.TOTL' --platform worldbank --strategy free
python3 scripts/xcoze_search.py search '2.5,day' --platform usgs --strategy free
```

世界银行示例是中国人口指标，不是根据自然语言自动匹配指标。USGS 支持 `all`、`significant`、`1.0`、`2.5`、`4.5` 与 `hour`、`day`、`week`、`month` 的组合；例如 `2.5,day` 表示订阅源中过去一天的 2.5 级及以上事件。历史查询和任意地理范围筛选尚未接入。

## 天气与自然环境

| 来源 | 适合的数据 | 当前状态 |
|---|---|---|
| [挪威气象局 MET Norway](https://api.met.no/weatherapi/locationforecast/2.0/documentation) | 全球坐标天气预报 | 免 Key；北京坐标样例返回数据。接入前需实现按响应头缓存、坐标精度与署名要求；预报不是气象实况。 |
| [Open-Meteo](https://open-meteo.com/en/docs) | 地名坐标查询和天气预报 | 免 Key 样例返回数据；[免费接口限非商业用途](https://open-meteo.com/en/terms)，商业场景需要对应授权，暂未接入。 |
| [NOAA 空间天气](https://www.swpc.noaa.gov/products-and-data) | 太阳活动和空间天气产品 | 公开 JSON 样例返回响应；具体指标、时间和适配方式待核对。 |
| [USGS 地震](https://earthquake.usgs.gov/earthquakes/feed/v1.0/index.php) | 地震事件 | 已接入近期固定窗口；完整目录 API 未接入。 |

天气相关接口可能需要坐标，用户给出的城市名称应先消歧；局部位置、预报更新时间和数据来源都会影响结果。它们不能替代当地主管部门发布的灾害预警。

## 股票、金融与经济

| 来源 | 适合的数据 | 当前状态 |
|---|---|---|
| [美国 SEC EDGAR](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | 美国上市公司申报文件和财务数据 | 公开数据 API 无需 Key；本次公司代码入口返回 403，尚未接入。财报不是实时股价。 |
| [欧洲央行数据](https://data.ecb.europa.eu/help/api/overview) | 官方统计和参考汇率 | 一次汇率样例返回数据，另一次超时；尚未接入，参考汇率不是实时成交价。 |
| [巨潮资讯](https://www.cninfo.com.cn/) | 中国上市公司公告 | 公开入口可作为调研线索；接口、范围和自动化使用条件有待核验，尚未接入。 |
| [世界银行](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392) | 宏观经济、人口和社会统计 | 已接入指定国家和指标的年度数据。 |

目前未接入实时股票报价。股票数据源需要按交易所、授权、报价延迟、货币和更新时间分别确认；历史行情、参考价与实时成交价不能混用。

## 国际卫生与其他组织

[WHO 全球卫生数据](https://www.who.int/data/gho/info/gho-odata-api)提供卫生指标；本次旧 GHO 接口样例返回 503，且 WHO 已提示旧接口迁移，需核对新接口后再评估。[联合国新闻 RSS](https://news.un.org/en/rss-feeds)等公开订阅可补充组织新闻，尚未接入。更多组织和数据源见[完整来源调研](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.md)。

核对日期：2026-11-05（北京时间）。单次请求不等于持续可用，也不表示所有接口或数据集都可以免 Key、免费商用。
