# Agent search benchmark and source verification

[简体中文](2026-11-09-agent-search.md) | **English**

On November 9, 2026 (Beijing time), we ran the eight original questions and 12 new ones sequentially on one network, once in Free and once in Smart without keys. Both modes used keyless routing.

[Questions](../agent-search-cases-v2.en.json) · [Per-case data](2026-11-09-agent-search.data.json) · [Previous run](2026-11-08-agent-search.en.md)

We reviewed each top-five list and checked the publisher page, original document, or API separately. Verified means the original supports the task. Partial means the official index was found but the current release was missing. Miss means the expected item was absent; the reference was found separately. The news window was seven days. Publication, first submission, revision, and observation dates were reviewed separately.

| Metric | Free | Smart without keys |
|---|---:|---:|
| Nonempty results | 20/20 | 20/20 |
| Verified against original | 17/20 | 17/20 |
| Partial | 1/20 | 1/20 |
| Missed | 2/20 | 2/20 |
| Median retrieval time | 1051 ms | 911 ms |

The run made 40 keyless HTTP requests. Timing covers retrieval within the script. Original-source checks were performed separately. Network and provider conditions affect these single observations. Keyed modes require a separate run with available quota.

| Case ID | Top-five assessment | Free / Smart evidence rank | Source check |
|---|---|---|---|
| `cn-energy-policy` | Verified | 1 / 1 | The NEA page republishes an Economic Daily report dated 2026-07-10. [Reference](https://www.nea.gov.cn/20260710/2706be51a7f1446a90658328d1c245d4/c.html) |
| `cn-statistics` | Partial | 1 / 1 | The official index was returned. The highest-ranked individual release was dated October 19. Separate verification found the November 9 CPI release. [Reference](https://www.stats.gov.cn/sj/zxfbhjd/202611/t20261109_1965795.html) |
| `cn-news` | Verified | 3 / 3 | The publisher page shows November 9 at 08:15, within the seven-day review window. [Reference](https://www.jiemian.com/article/15308219.html) |
| `python-taskgroup` | Verified | 1 / 1 | The official docs explain cancellation of remaining tasks and aggregation of exceptions. [Reference](https://docs.python.org/3/library/asyncio-task.html#task-groups) |
| `github-markitdown` | Verified | 1 / 1 | The Microsoft repository README confirms the project converts files to Markdown. [Reference](https://raw.githubusercontent.com/microsoft/markitdown/main/README.md) |
| `research-rag` | Verified | 1 / 1 | The paper applies retrieval augmentation to image generation. First submitted June 8 and revised June 14. [Reference](https://arxiv.org/abs/2506.06962v3) |
| `financial-disclosure` | Verified | 3 / 3 | The PDF cover confirms Tongfang’s 2025 annual report. [Reference](https://static.cninfo.com.cn/finalpage/2026-04-29/1225244797.PDF) |
| `community-hn` | Verified | 1 / 1 | The HN thread discusses SQLite and is dated 2021-05-02. The question has no recency requirement. [Reference](https://news.ycombinator.com/item?id=27016630) |
| `nbs-cpi-oct` | Verified | 1 / 1 | The official release was published at 09:30 on November 9 and covers October 2026. The release calendar agrees. [Reference](https://www.stats.gov.cn/sj/zxfb/202611/t20261109_1965795.html) |
| `python-release` | Verified | 1 / 1 | The final release is dated 2025-10-07. [Reference](https://www.python.org/downloads/release/python-3140/) |
| `pep703` | Verified | 1 / 1 | PEP 703 makes the GIL optional and has Final status. [Reference](https://peps.python.org/pep-0703/) |
| `sqlite-release` | Verified | 1 / 1 | The official release log dates 3.45.0 to 2024-01-15. [Reference](https://www.sqlite.org/releaselog/3_45_0.html) |
| `crossref-deep-learning` | Miss | — / — | The DOI was absent from both top-five lists. The journal shows online publication on 2015-05-27 and the issue date one day later. [Reference](https://doi.org/10.1038/nature14539) |
| `arxiv-rag-version` | Verified | 3 / 3 | The paper was first submitted on 2020-05-22 and revised as v4 on 2021-04-12. [Reference](https://arxiv.org/abs/2005.11401v4) |
| `npm-typescript` | Verified | 1 / 1 | The npm registry confirms the typescript package and microsoft/TypeScript upstream. [Reference](https://registry.npmjs.org/typescript/latest) |
| `us-ai-rfi` | Miss | — / — | Neither top-five list contained 2025-02305. The Government Publishing Office copy confirms publication on 2025-02-06. [Reference](https://www.govinfo.gov/content/pkg/FR-2025-02-06/html/2025-02305.htm) |
| `worldbank-pop` | Verified | 1 / 1 | A replay against the World Bank API confirmed 2025 as the first observation year. [Reference](https://api.worldbank.org/v2/country/CN/indicator/SP.POP.TOTL?format=json&per_page=5) |
| `mdn-abort` | Verified | 1 / 1 | MDN confirms that the timeout parameter is measured in milliseconds. [Reference](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static) |
| `nasa-artemis` | Verified | 3 / 3 | The NASA media index confirms that the item is a launch image dated 2022-11-16. [Reference](https://images-api.nasa.gov/search?nasa_id=NHQ202211160030) |
| `wikipedia-utc` | Verified | 1 / 1 | The link points to the requested Chinese-language article. [Reference](https://zh.wikipedia.org/wiki/%E5%8D%8F%E8%B0%83%E4%B8%96%E7%95%8C%E6%97%B6) |

## Reproduce

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v2.en.json --modes free,smart --keyless --live --limit 20 --max-requests 120 --timeout 8 --count 5 --output /tmp/xcoze-agent-search.json
```
