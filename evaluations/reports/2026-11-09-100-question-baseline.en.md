# 100-question search baseline and retest

[简体中文](2026-11-09-100-question-baseline.md) | **English**

On November 9, 2026 (Beijing time), we ran all 100 questions in Free on one network, retested the six questions affected by adapter changes, and spot-checked six questions in Smart without keys. Each search requested up to five results. [Question set](../agent-search-cases-v3.en.json) · [Per-case records](2026-11-09-100-question-baseline.data.json)

| Baseline metric | Result |
|---|---:|
| Returned candidates | 100/100 |
| Expected domain in top five | 97/99 |
| Median retrieval time | 966 ms |
| P95 retrieval time (nearest rank) | 2,606 ms |
| Keyless HTTP requests | 104 |

One question has no expected domain. The building energy standard and electricity demand-side management questions missed their expected domains. Domain matching measures source coverage. Original-source and date review for all 100 cases is still pending. The [20-question verification report](2026-11-09-agent-search.en.md) remains available separately. Timing measures retrieval inside the script. One Europe PMC request and one World Bank request had network errors and returned fallback results.

## Same-query retest

| Case | Baseline target rank | Retest target rank |
|---|---:|---:|
| Deep learning DOI | Outside top five | 1 |
| AlphaFold DOI | Outside top five | 1 |
| AI Action Plan notice keywords | Outside top five | 1 |
| Federal Register document 2025-02305 | 1 | 1 |
| AlphaFold title | Outside top five | Outside top five |
| PRISMA 2020 title | 5 | 5 |

Crossref uses an exact filter for common bare DOIs and preserves publication date filters. Federal Register retrieves a document directly by number and ranks keyword searches by relevance by default. Explicit `--intent current` orders by publication date. [Crossref filter documentation](https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/) · [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1)

All six Smart spot checks selected Free and returned candidates. The three runs made 116 keyless HTTP requests. Keyed strategies require a separate comparison.

## Reproduce the baseline

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v3.en.json --modes free --keyless --live --limit 100 --max-requests 300 --timeout 8 --count 5 --output /tmp/xcoze-100-free.json
```

The baseline used commit `4a021dd`. The retest kept the same queries and options. Published data preserves links, dates, routing and timing for further review.
