# Chinese site search

[简体中文](china-site-search.md) | **English**

## CNINFO disclosures

`cninfo` uses the public full-text search entry point used by CNINFO's website. Results include announcement titles, publication dates, security codes, market fields and PDF URLs, without a key.

```bash
python3 scripts/xcoze_search.py search '贵州茅台 2024 年度报告' --platform cninfo
python3 scripts/xcoze_search.py search '上市公司 年度报告' --platform cninfo
```

One first page is read, with up to ten results and no automatic pagination. Full-text search describes the announcement index; output does not include PDF bodies. Read the report before citing figures. Publication dates and reporting years differ: a 2024 annual report may be published in 2025.

Queries explicitly requesting listed companies use the website's equity categories to avoid fund and bond reports. Other queries retain their scope. Results preserve security codes and market fields; A-share and Hong Kong reports are not merged. This is not a live-quote adapter. Other attachment formats, complex combined filters and bulk downloads are outside the current scope.

## National Bureau of Statistics site search

`nbs-search` uses the `api.so-gov.cn` backend selected by NBS's own search page, with a fixed NBS site identifier. Queries go to that search service; returned links are restricted to `stats.gov.cn`. This is not a numerical National Data database API.

```bash
python3 scripts/xcoze_search.py search '2026年9月 居民消费价格' --platform nbs
python3 scripts/xcoze_search.py search '2026年10月 制造业 采购经理指数' --site stats.gov.cn
```

One page of ten entries is read and capped to the requested count. Explicit year/month questions reject clearly conflicting periods in titles, with title/topic matches ranked first. Comparison months in excerpts and webpage publication dates do not replace the requested statistical period. Publication dates retain service precision; figures and definitions still require the original page.

Automatic `--platform nbs` or `--site stats.gov.cn` searches start with site search. The earlier recent-listing filter remains available through explicit `--provider nbs`.

## Scope and failures

Neither route requires Exa, Parallel, host search or a browser. Both use the Python standard library. These are public website entry points, not a promise of stable developer APIs or availability.

Unsupported date ranges, languages and body-return options fail or exclude the route from an automatic plan instead of silently dropping constraints. Access denial pauses the route; subsequent searches use only sources allowed by the current mode. Free mode never dispatches keyed services. Empty results, access failures and cooldowns remain distinct.

[Focused checks and remaining gaps](../evaluations/reports/2026-11-16-native-search.en.md) · [All sources](sources.en.md)
