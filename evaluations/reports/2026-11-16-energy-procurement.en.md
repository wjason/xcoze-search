# Energy and procurement retrieval checks

[简体中文](2026-11-16-energy-procurement.md) | **English**

November 16, 2026, Beijing time. [27 bilingual questions and filters](../energy-procurement-cases.json) · [Per-case results, initial failures and original checks](2026-11-16-energy-procurement.data.json)

## Conditions and results

Free mode, both Exa routes and Parallel disabled, no keyed services or local browser, and no host search during runtime. Each question requests up to five results, with a ten-second source timeout and zero retries. Evaluation uses an empty credential configuration and blocks forbidden services before transmission. Saved user preferences and keys are not changed.

| Scenario | Questions | Candidates from expected source |
|---|---:|---:|
| Storage policies and power market rules | 5 | 5 |
| Electricity statistics, consumption, green certificates and historical releases | 5 | 5 |
| Provincial engineering/government procurement, including region/stage filters | 9 | 9 |
| Central-enterprise and finance sources | 2 | 2 |
| Explicit second result page | 1 | 1 |
| Southern Grid tender, award and cancellation lists | 5 | 5 |
| Total | 27 | 27 |

The run used 27 search HTTP requests: ten NEA, twelve public trading and five Southern Grid. Exa, Parallel, keyed requests and browser navigations were all zero. Median retrieval time was 2.81 seconds and P95 3.06 seconds, including local pacing during consecutive queries but excluding answer generation and original reading. Six additional metadata/capability checks included government procurement contracts and the Southern Grid non-tender list; both returned candidates.

These questions test source location and filtering, not open-domain answer accuracy, complete coverage or continuous availability. Southern Grid checks cover requested public list pages, not full-site keyword search. Earlier failures and intermediate rounds remain in the data.

## Originals and dates

Fourteen result pages were checked for topic and document/notice identity. Five public trading links first opened notice directories; five actual body URLs published on those pages were then read to confirm storage projects, procurement/award stages, and selected project numbers and deadlines. Southern Grid digitization, Yunnan award and cancellation bodies were checked separately. Cancellations were not treated as open tenders.

For example, a storage procurement body identifies project `[350425]MB[GK]2026001` and a December 7, 2026 bidding deadline; its notice date is November 15. Search itself did not read that body or substitute the publication date for the deadline. Original verification is recorded separately from fields actually returned by the adapters.

Some NEA policy list dates differ from the original page dates:

| Document | List date | Original page date |
|---|---|---|
| Action plan for scaling new energy storage | 2025-09-12 | 2025-08-27 |
| Power market metering and settlement rules | 2025-08-08 | 2025-07-18 |
| Power ancillary services market rules | 2025-04-29 | 2025-04-03 |

NEA results therefore identify list-date semantics explicitly. Date filters apply to that list; original publication dates, issuance/effective dates and statistical periods require verification. Retrieval searches finite document/press datasets published by the site, not a complete archive or full-site search.

## Changes supported by live results

- **Historical title wording:** 电力工业统计数据 initially missed the query 电力统计数据. A limited title variant match now preserves the original question and date range.
- **Chinese word boundaries:** a warehouse-capacity title initially matched the adjacent characters for energy storage. This cross-word match is excluded without discarding genuine storage projects.
- **List dates:** numbered badges next to Southern Grid dates originally prevented date extraction. The date node is now read before flattening text.
- **Notice stages:** public-notice columns mix awards, candidates, direct procurement and cancellations. Stages remain separate or unknown; finance/central sources do not inherit provincial-stage mappings.
- **Requested pages:** the adapter checks the returned page number rather than substituting page one for page two.

## Support status

| Capability | Result |
|---|---|
| NEA published document/press lists | Supported · Passed |
| Provincial, central-enterprise and finance trading searches | Supported · Passed |
| Procurement category, province/date/stage filters and explicit pages | Supported · Passed; compatibility limits in the usage guide |
| Southern Grid tender/public-notice/non-tender lists | Supported · Passed; one requested page per call |
| CCGP recent homepage notices | Supported · Separate live sample passed |
| CCGP full-site keyword search | Planned · Access-frequency warning |
| Southern Grid full-site keyword search | Planned · HTTP 403 |
| State Grid search | Planned · Not verified |

The NEA general search endpoint also returned 403; this implementation uses separately published public archive lists. The CCGP keyword endpoint returned an HTTP 200 frequency-warning page and was not counted as successful. No CAPTCHA solving, login sessions or repeated attempts at denied endpoints were used. An initially incomplete public trading request disconnected; matching the official page's request headers and date mode succeeded. Custom dates require interval mode rather than the last-three-days preset.

## Reproduce

```bash
python3 scripts/benchmark.py --corpus evaluations/energy-procurement-cases.json --modes free --keyless --without-exa --without-parallel --browser off --live --limit 27 --max-requests 60 --timeout 10 --count 5 --output /tmp/xcoze-industry.json
```

Omit `--live` for an offline plan. Fixed ranges and current list windows may no longer overlap in future runs. Retain misses rather than changing questions to hide regressions. A single list page cannot promise historical retrieval; request a specific page or another compatible source separately.

[Usage](../../references/industry-search.en.md) · [Support status](../../references/source-status.en.md). Independently implemented adapters use data and links actually published by [NEA documents](https://www.nea.gov.cn/policy/zxwj.htm), [NEA press releases](https://www.nea.gov.cn/xwfb/index.htm), [public trading queries](https://www.ggzy.gov.cn/deal/dealList.html) and [Southern Grid public notices](https://www.bidding.csg.cn/zbgg/index.jhtml).
