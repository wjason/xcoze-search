# Parallel across 100 questions without Exa

[简体中文](2026-11-10-parallel-no-exa.md) | **English**

On November 10, 2026 (Beijing time), we ran the same [100 questions](../agent-search-cases-v3.en.json) in Free before and after adding Parallel. Both runs disabled both Exa routes and user keys and used no host search. Query text, an eight-second provider timeout, top-five review, and local browser fallback stayed the same. The sequential runs retained source cooldowns. [Per-case data](2026-11-10-parallel-no-exa.data.json)

| Metric | Before | After |
|---|---:|---:|
| Returned candidates | 92/100 | 99/100 |
| Expected domain in top five | 70/99 | 98/99 |
| Median retrieval time | 2,267 ms | 980 ms |
| P95 retrieval time (nearest rank) | 3,428 ms | 2,266 ms |
| Browser navigations | 46 | 1 |
| Public API HTTP requests | 103 | 103 |

The run made 55 Parallel requests without hitting its limit. The expected domain appeared in 28 additional cases and remained present in all previous hits. Domain matching measures source coverage. Both runs missed the JWST deep-field image in the NASA media library. Timing includes browser startup and cleanup and varies with network, index and cooldown state.

## Reviewed cases

| Case | Before | After |
|---|---|---|
| Python TaskGroup | Third-party explanations | Official asyncio docs at rank 2, covering cancellation |
| Kubernetes CPU requests and limits | Third-party articles | Official resource management docs at rank 1 |
| Moutai's 2024 annual report on CNINFO | No candidates | Annual report PDF at rank 1. The cover confirms issuer 600519 and reporting year 2024 |
| Bilibili Git rebase | Video candidates | Video candidates still within the requested domain |
| Shanghai Museum East on Xiaohongshu | Links on the expected domain | Links on the expected domain. The post text still needs review |

[Python documentation](https://docs.python.org/3/library/asyncio-task.html#task-groups) · [Kubernetes documentation](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) · [CNINFO annual report](https://static.cninfo.com.cn/finalpage/2025-04-03/1222993920.PDF)

Mwmbl and Purili did not return the expected pages in the spot checks. Marginalia returned 429, Bing browser results failed the relevance check, and Google browser search returned a verification challenge. Parallel's documented anonymous endpoint is marked legacy. Limits and migration remain worth monitoring. The adapter supports search and checks returned hosts against the requested site. It labels returned text as excerpts. [Parallel Search MCP](https://docs.parallel.ai/integrations/mcp/search-mcp)

## Reproduce

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v3.en.json --modes free --keyless --without-exa --live --limit 100 --max-requests 300 --timeout 8 --count 5 --output /tmp/xcoze-parallel-no-exa.json
```

The before run used commit `d263f7e`. Use `search 'short query' --provider parallel-free --strategy free --site official.example.org` to probe the new adapter alone.
