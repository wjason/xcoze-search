# China public sources

[简体中文](china-public-sources.md) | **English**

[Back to sources](../references/sources.en.md)

This directory covers public portals for government, statistics, finance, science, weather and news. The Skill searches recent official listings, the DATA.GOV.HK update feed, and site-scoped web indexes. Results link back to their publishers; listing windows and index coverage vary. See [sources](../references/sources.en.md).

The 30 links below returned HTTP 200 during a one-time homepage request on 2026-11-05 (Beijing time). This checks page response only, not that an API, search, data download, commercial use or future access works. The search check returned results for 13 scoped sites; its final Exa request reached a rate limit, and the separate Hong Kong Observatory browser sample had no hits. [Page checks](china-public-sources-2026-11-05.json) · [Search checks](china-public-index-probes-2026-11-05.json).

## Policy and government

| Source | Content | Integration |
|---|---|---|
| [NDRC notices](https://www.ndrc.gov.cn/xxgk/zcfb/tz/) | Notice listing | Current page integrated |
| [Ministry of Industry and Information Technology](https://www.miit.gov.cn/zwgk/index.html) | Industry and IT policy documents | Current listing integrated |
| [Ministry of Commerce](https://www.mofcom.gov.cn/) | Commerce policy and public information | Current listing integrated |

## Statistics and economics

| Source | Content | Integration |
|---|---|---|
| [National Bureau of Statistics releases](https://www.stats.gov.cn/sj/zxfb/) | Data release listing | Current page integrated |
| [National Data](https://data.stats.gov.cn/) | Statistical data portal | Site-scoped search |
| [People’s Bank of China statistics](https://www.pbc.gov.cn/diaochatongjisi/116219/116225/index.html) | Financial statistics releases | Current listing integrated |

## Energy and environment

| Source | Content | Integration |
|---|---|---|
| [National Energy Administration](https://www.nea.gov.cn/) | Energy news and notices | Homepage listing integrated |
| [Ministry of Ecology and Environment](https://www.mee.gov.cn/) | Environmental policy and public information | Current listing integrated |

## Weather and hazards

| Source | Content | Integration |
|---|---|---|
| [National Meteorological Information Center](https://data.cma.cn/) | Meteorological data services | Site-scoped search |
| [China Weather](https://www.weather.com.cn/) | Weather forecasts and news | Site-scoped search |
| [Ministry of Emergency Management statistics](https://www.mem.gov.cn/gk/tjsj/index.shtml) | Disaster and emergency statistics | Current listing integrated |
| [China Earthquake Networks Center](https://www.ceic.ac.cn/) | Earthquake information | Site-scoped search |
| [National Marine Environmental Forecasting Center](https://www.nmefc.cn/) | Marine forecasts and warnings | Site-scoped search |

## Securities and finance

| Source | Content | Integration |
|---|---|---|
| [China Securities Regulatory Commission](https://www.csrc.gov.cn/) | Securities regulatory notices | Current listing integrated |
| [CNInfo](https://www.cninfo.com.cn/new/commonUrl?url=disclosure%2Flist%2Fnotice) | Listed-company disclosures | Site-scoped search |
| [Shanghai Stock Exchange](https://www.sse.com.cn/disclosure/listedinfo/announcement/) | Listed-company announcements | Site-scoped search |
| [Shenzhen Stock Exchange](https://www.szse.cn/disclosure/listed/notice/) | Listed-company announcements | Site-scoped search |
| [Beijing Stock Exchange](https://www.bse.cn/) | Market and company information | Site-scoped search |

## Law, standards and procurement

| Source | Content | Integration |
|---|---|---|
| [National standards disclosure system](https://openstd.samr.gov.cn/) | National standards catalog and public content | Site-scoped search |
| [National database of laws and regulations](https://flk.npc.gov.cn/) | Laws and regulations | Site-scoped search |
| [China Government Procurement](https://www.ccgp.gov.cn/) | Government procurement notices | Current listing integrated |
| [National public resource trading platform](https://www.ggzy.gov.cn/) | Public resource trading information | Current listing integrated |

## Research, space and geoscience

| Source | Content | Integration |
|---|---|---|
| [China National Space Administration](https://www.cnsa.gov.cn/) | Space news and data policies | Site-scoped search |
| [Chinese Academy of Sciences](https://www.cas.cn/) | Research news and institutional resources | Current listing integrated |
| [Science Data Bank](https://www.scidb.cn/) | Research datasets | Site-scoped search |
| [China Geological Survey](https://www.cgs.gov.cn/) | Geoscience news and data resources | Current listing integrated |

## Regional public data

| Source | Content | Integration |
|---|---|---|
| [DATA.GOV.HK](https://data.gov.hk/tc/) | Government open-data catalog | Dataset update RSS |
| [Hong Kong Observatory](https://www.hko.gov.hk/sc/abouthko/opendata_intro.htm) | Hong Kong observations and forecasts | Site-scoped search; sample had no hits |

## News

| Source | Content | Integration |
|---|---|---|
| [China News Service RSS](https://www.chinanews.com.cn/rss/) | News feeds | Latest and finance feeds integrated |
| [Xinhua](https://www.news.cn/) | News | Current listing integrated |

## Weather and financial data

The [Hong Kong Observatory current report](https://data.gov.hk/en-data/dataset/hk-hko-rss-current-weather-report) and nine-day forecast returned JSON with an update time in a single check. They cover Hong Kong; its website can be searched by scope. The Observatory has separate [usage conditions](https://www.hko.gov.hk/tc/readme/readme.htm); review the terms for each dataset before automated or commercial use.

Listed-company disclosures are not live quotes. Exchange coverage, quote delay, licensing and timestamps need verification before stock prices are integrated. China meteorological datasets can require accounts or individual access conditions. [CNSA scientific data policy](https://www.cnsa.gov.cn/n6758823/n6758839/c6805196/content.html) also describes registration for public datasets; a public catalog does not imply anonymous downloads.

## Search the integrated listings

```bash
python3 scripts/xcoze_search.py search '生态' --platform ndrc --strategy free
python3 scripts/xcoze_search.py search '价格' --platform nbs --strategy free
python3 scripts/xcoze_search.py search '能源' --platform nea --strategy free
```

Matching uses literal title terms in the current page. An empty result does not establish that no document exists. Displayed dates are listing dates, not necessarily effective dates; some NEA titles have no displayed date. Read the original to confirm dates, data definitions and content.
