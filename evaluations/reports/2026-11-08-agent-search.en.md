# Agent search evaluation: 2026-11-08

[简体中文](2026-11-08-agent-search.md) | **English**

This retrieval evaluation covers Chinese policy, statistics and news; English technical documentation; repositories, research, financial disclosures and community discussions. [Question set](../agent-search-cases.en.json) · [Sanitized results](2026-11-08-agent-search.data.json)

## Results

On November 8, 2026, each of eight questions was run once per mode, sequentially on one network. Both Free and Smart without keys used keyless routing; this is not a comparison of paid services.

| Metric | Free | Smart without keys |
|---|---:|---:|
| Queries | 8 | 8 |
| Returned at least one result | 8 | 8 |
| Median retrieval time | 929 ms | 872 ms |
| Range | 456–3005 ms | 116–1082 ms |

These are single observations. Times exclude process startup, agent reasoning, page reading and answer generation; network, quotas and caches affect results. They do not establish a speed ranking. The run made 16 keyless requests and no keyed requests; model costs are excluded. DeepSeek previously returned HTTP 402 for the configured account and was not retried; other keyed services were not quality-tested.

## Review

Titles, links, dates and snippets were inspected. Each question had at least one potentially relevant result. **Pages were not independently verified for every result; this is not answer accuracy or freshness accuracy.** Current information still needs primary-source checks. The research query returned several broad results before a relevant paper.

| Question | Observation |
|---|---|
| Offshore wind policy | Relevant energy-administration policy and news; publication and effective dates require separate checks. |
| Chinese statistics | Official release index and publications; recency needs verification on the original site. |
| Chinese AI news | Reports with same-day dates in search metadata, not individually verified. |
| Python TaskGroup | Official documentation page found; read the text to verify exception handling. |
| GitHub repository | The full repository name returned `microsoft/markitdown`. |
| Retrieval-augmented generation | Relevant research found, with broad results ahead of it. |
| Financial disclosures | Annual-report PDFs found on the CNINFO domain; contents not read. |
| Hacker News | SQLite discussion links found, mostly older; the task did not require recent posts. |

## Findings and changes

The first GitHub query used `microsoft markitdown` and missed the target in the first five results. Using `microsoft/markitdown` returned the target first. The first financial query did not restrict the source and returned no CNINFO disclosure in the first five; scoping the follow-up to CNINFO returned annual reports. The query conditions changed, so these illustrate query formulation, not an algorithmic improvement under identical conditions. The Skill instructions now include both practices.

Free and keyless Smart followed the same free routing in this run. Keyed Smart, long-term availability and answer correctness require separate evaluation. Search indices, links and dates can change.

## Reproduce

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases.json --modes free,smart --keyless --live --limit 8 --max-requests 48 --timeout 8 --count 5 --output /tmp/xcoze-benchmark.json
```

`--keyless` avoids reading locally configured and environment keys and blocks keyed dispatch before transmission. Online queries are sent to public services. Output includes snippets for local review; remove them and check privacy before publication. Without `--live`, the command only produces a plan. Evaluate paid modes separately with explicit configuration and reconcile charges against provider invoices.
