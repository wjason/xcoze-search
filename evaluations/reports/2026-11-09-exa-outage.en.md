# Search during an Exa outage

[简体中文](2026-11-09-exa-outage.md) | **English**

On November 9, 2026 (Beijing time), we sampled 12 questions from the 100-question corpus and disabled Exa. A guard blocked Exa and user-key requests before transmission. Native public sources and the local browser remained available. Results depend on the network and browser environment. [Per-case records](2026-11-09-exa-outage.data.json)

| Check | Observation |
|---|---|
| Any candidates | 11/12 |
| Expected domain in top five | 7/11, with one question having no predefined domain |
| Native interfaces | GitHub, arXiv and Hacker News samples all returned candidates |
| General and scoped search | Bing RSS returned irrelevant results and DuckDuckGo entered cooldown after a challenge. The 360 browser returned candidates for Xiaohongshu and Bilibili, among others |
| Remaining gaps | Both English documentation questions, the NBS CPI release and a CNINFO annual report fell short |

## Fallback paths

- The CPI query returned the official release after switching to the native NBS releases listing with short keywords. Route known notices, statistics, repositories and papers to appropriate native sources first.
- Scoping the Python and Kubernetes queries to the official domains still left the target sections missing from the Skill's keyless fallback. Host web search could find the [Python TaskGroup documentation](https://docs.python.org/3/library/asyncio-task.html#task-groups) and the [Kubernetes resource management documentation](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/). Host access and costs depend on the environment.
- The revised CNINFO query returned links on the expected site. The requested company's annual report remained unverified. Domain matching measures source coverage.
- For an independent general search API, configure a supported source such as Brave Search as needed. Explicit Free still uses sources that need no user key. [Brave API documentation](https://api-dashboard.search.brave.com/documentation/services/web-search)

## Reproduce

`--without-exa` disables both Exa routes for the benchmark invocation. User settings are retained. The command below runs the first six questions. Set `--limit 100 --max-requests 300` for the full corpus. An installed local browser may start.

```bash
python3 scripts/benchmark.py --corpus evaluations/agent-search-cases-v3.en.json --modes free --keyless --without-exa --live --limit 6 --max-requests 18 --timeout 10 --output /tmp/xcoze-without-exa.json
```
