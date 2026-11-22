# Energy and procurement search

[简体中文](industry-search.md) | **English**

Find energy policies, electricity statistics, government procurement and grid purchasing notices. The Agent chooses sources and separates keywords from filters; users do not need to remember platform parameters. These routes require no API key, Exa, Parallel or local browser.

## Energy policies and electricity statistics

`--platform nea` downloads a published National Energy Administration document or press-release list, then searches its titles and summaries locally. The document list includes historical policies; the press list includes electricity statistics, consumption, green certificates and press conferences. Each is a finite published snapshot, not a complete historical database.

```bash
python3 scripts/xcoze_search.py search '新型储能 规模化' --platform nea --energy-section policy --start-date 2025-01-01 --end-date 2025-12-31
python3 scripts/xcoze_search.py search '全国电力统计数据' --platform nea --energy-section releases --start-date 2025-10-01 --end-date 2025-10-31
```

Without `--energy-section`, statistics, capacity and consumption queries select press releases; other queries select policies. Matching accommodates both 电力统计 and the historical title wording 电力工业统计 without relaxing dates. One list is downloaded per search; keywords are not sent to the website. Results retain original links, displayed list dates and snapshot coverage. Date filters apply to the list date, which can differ from the original publication date. Read the original for statistical periods, figures, units, issuance dates and legal status. The original homepage list remains available with `--provider nea`.

Sources: [Published documents](https://www.nea.gov.cn/policy/zxwj.htm), [Press releases](https://www.nea.gov.cn/xwfb/index.htm).

## Government procurement and construction tenders

`ggzy-search` uses the public notice-query endpoint selected by China's National Public Resource Trading Platform. It supports keywords, provinces, publication ranges, business categories and notice stages. `--platform government-procurement` fixes the category to government procurement; `--platform ggzy` also covers construction and other transaction notices.

```bash
python3 scripts/xcoze_search.py search '储能' --platform government-procurement --notice-type tender --region 广东 --start-date 2026-10-01 --end-date 2026-11-16
python3 scripts/xcoze_search.py search '储能' --platform ggzy --business engineering --notice-type award --start-date 2026-10-01 --end-date 2026-11-16
python3 scripts/xcoze_search.py search '储能' --platform ggzy --business engineering --trading-source central --start-date 2026-10-01 --end-date 2026-11-16
```

| Option | Values |
|---|---|
| `--business` | `government` procurement; `engineering` construction |
| `--notice-type` | Both categories: `tender`, `award`, `correction`; government procurement also supports `contract` |
| `--region` | Chinese province name or six-digit province code, e.g. `广东`, `广东省`, `440000` |
| `--trading-source` | `province` (default), `central` enterprises, or `finance` ministry-source publications |
| `--page` | One requested page, 1–100; never followed automatically |

Region and notice-stage filters are available for provincial sources; central-enterprise and finance sources reject them rather than apply unverified mappings. A notice stage requires a business category. Without dates, the website's last-three-months window applies; a custom range requires both boundaries. One page is read per call, with up to 20 results. Returned titles, provinces, dates and notice codes are checked against the query. The Chinese phrase 仓储能力 (warehouse capacity) is not mistaken for 储能 (energy storage).

Results retain the original notice, province, publishing platform, business category and notice type. Missing project numbers, buyers and deadlines remain null. Publication dates are not bidding deadlines, and awards are not open tenders. Read the original to verify eligibility, budgets, deadlines and corrections.

China Government Procurement Network retains its recent homepage-list adapter. Its keyword-search endpoint returned an access-frequency warning in this check and **has not been integrated as full-site search**. Government procurement search here is supplied by the public trading platform, not labeled as native CCGP search.

Sources: [Public trading query](https://www.ggzy.gov.cn/deal/dealList.html), [China Government Procurement Network](https://www.ccgp.gov.cn/).

## China Southern Power Grid notices

`--platform csg` uses the keyword-search form published on the Southern Grid website. It sends the query and notice channel to `dbsearch.jspx`, reads one result page and filters its displayed dates locally. It does not scan the historical lists. Results can match text beyond a truncated title, so a search hit still needs original-source verification.

```bash
python3 scripts/xcoze_search.py research '数字化' --platform csg --notice-type tender --question 'Find a digital-project tender and its bid deadline.'
python3 scripts/xcoze_search.py research '监理' --platform csg --notice-type non-tender --question 'Who is the buyer and what is the response deadline?'
python3 scripts/xcoze_search.py search '电网' --provider csg --notice-type tender --page 2
```

`csg-search` validates the echoed query, channel and requested page. `tender` uses the tender channel, `non-tender` the non-tender channel; other stages filter explicit titles in the mixed public-notice channel. Date filters apply to the returned page, not a server-side historical range query. The original `--provider csg` keeps the public-list route and its explicit page selection. Both share pacing and access-denial cooldowns.

Published category labels can identify a truncated tender title; an explicit candidate, cancellation or award title takes precedence. Publishing organizations remain separate from verified buyers. Read the original for project identity and eligibility. Document acquisition, bid submission, response submission and opening times are separate fields, and none alone proves that bidding is currently open.

Sources: [Official search form](https://www.bidding.csg.cn/zbgg/index.jhtml), [Live answer-support review](../evaluations/reports/2026-11-22-answer-support.en.md). State Grid search remains unverified.

## Research workflow

The Agent preserves the user's question and separates the topic from province, dates and notice stage. For recent Guangdong energy storage procurement, use the Chinese keyword `储能`, Guangdong, a date range and the government procurement category rather than the entire question as a literal title phrase.

An empty page does not establish that a project does not exist. Within the task budget, request a specific next page, use another compatible official source or continue web search. Distinguish statistical periods from publication dates and procurement plans from tenders, candidate notices, awards, contracts and corrections. Do not invent missing fields or treat notice metadata as a read tender document.

Each source is paced independently. Access denial, verification challenges and frequency warnings pause the route; no CAPTCHA solving or login sessions are used. Public website endpoints can change. See the [focused live checks](../evaluations/reports/2026-11-16-energy-procurement.en.md) and [source status](source-status.en.md).
