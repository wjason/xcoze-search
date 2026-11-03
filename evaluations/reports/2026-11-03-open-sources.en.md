# Open-source expansion and Agent Reach implementation study

[简体中文](2026-11-03-open-sources.md) | **English**

Dated 2026-11-03. Reviewed Agent Reach 1.6.1's installed Skill/channels and upstream commit `7a38047acf26a729cbb27851e3cb81639da86b29`. No setup, update or login was run. Native API checks used Python 3.14.6, in-memory empty credentials and free strategy, without reading user keys. [Sanitized observations](2026-11-03-open-sources.data.json) preserve successes, failures and follow-ups without copied search/page text.

## Position and competitive scope

Agent Reach models platform actions and ordered execution backends, including dependency management, sessions, browsers, cooldown and diagnostics. Its Chinese-platform, video and comment depth is currently broader. More source names do not establish overall superiority.

xcoze remains an **Agent aggregation and evidence-retrieval entry point**: usable before key setup, task-appropriate public indexes, optional paid providers, saved quality/balanced/free preferences, bounded calls and explicit evidence types. Improvement should be judged by support for actual answers, primary sources, freshness, task completion time and cost. Reuse existing authorized platform tools for missing depth before creating new adapters.

| Aspect | Agent Reach 1.6.1 source/declarations | xcoze in this revision |
|---|---|---|
| Organization | Channel → Action → ordered Backend | Task → public native index/general keyless/configured API, plus offline platform catalog |
| Web retrieval | Exa MCP search, Jina/Exa reading | Same upstream options, nine additional public native adapters and six keyed services |
| Platform depth | Separate video/subtitle/comment/job actions | Mostly search and typed metadata; no added comment trees/subtitle/model-download integration |
| Diagnostics | Backend health, platform cooldown, action checks, browser state | New-source persistent pacing/OS serialization; declared coverage/tool presence separate from live tests |
| Installation | Python dependencies and optional platform tools/browsers | Standard-library base; no automatic tool installation or session copying |
| Cost | Many keyless operations; transcription may use keyed services | Explicit search strategies, HTTP/time limits and known/unknown costs; free search does not authorize paid transcription |

Primary code: [action contracts](https://github.com/Panniantong/Agent-Reach/blob/7a38047acf26a729cbb27851e3cb81639da86b29/agent_reach/channels/base.py), [dispatcher](https://github.com/Panniantong/Agent-Reach/blob/7a38047acf26a729cbb27851e3cb81639da86b29/agent_reach/runtime/dispatch.py), [Web](https://github.com/Panniantong/Agent-Reach/blob/7a38047acf26a729cbb27851e3cb81639da86b29/agent_reach/channels/web.py), [dependencies](https://github.com/Panniantong/Agent-Reach/blob/7a38047acf26a729cbb27851e3cb81639da86b29/pyproject.toml), [channel registry](https://github.com/Panniantong/Agent-Reach/blob/7a38047acf26a729cbb27851e3cb81639da86b29/agent_reach/channels/__init__.py). Reach is not a runtime dependency.

## Nine native keyless adapters

Single observations, up to three results per task; in-process time includes pacing/retrieval, excluding startup and answer generation. Access success is not semantic accuracy.

| Source | Task/result | Seconds |
|---|---|---:|
| Wikipedia zh | Three wind-power articles | 0.83 |
| Wikipedia en | Three RAG articles after pacing fix | 0.78 |
| Stack Exchange | Three related TaskGroup questions, no answer retrieval | 0.37 |
| arXiv | Three 2026 RAG records/abstracts inside submission-date bounds | 0.55 |
| Crossref | Three same-title DOI records; author/publication identity remains unverified | 1.22 |
| npm | Playwright/related package version metadata | 0.52 |
| crates.io | Tokio/related packages, stable/highest-version distinction retained | 0.54 |
| GitLab.com | Official Inkscape repo first after star sorting | 0.73 |
| Europe PMC | Three dated paper/preprint records and abstracts | 0.90 |
| Hugging Face | Three public Qwen model records, not latest-model ranking | Per-call data |

Nine initial direct endpoint probes returned results. The first adapter run had one locally suppressed Wikipedia short-cooldown call and eight actual HTTP attempts. Bounded waiting fixed consecutive language queries; both follow-ups passed with two HTTP attempts. Hugging Face added one, totaling eleven adapter HTTP attempts. No user-keyed service was used; model/host costs were not measured.

GitLab's default project-ID order initially returned new mirrors; star sorting improved this sample, but does not establish official identity. Crossref returned same-title/different-DOI records: finding metadata is not identifying the original paper. Check authors, year and publication venue. These are specialized indexes, not indiscriminate broadcasts. Keyless adapters now total 15: 14 search-capable plus reader-only Jina. This count cannot be compared directly with Reach channels. See [parameters, dates and official API docs](../../references/open-sources.en.md).

## Same-task comparison and an observed reading gap

Used `Python asyncio TaskGroup ExceptionGroup official documentation`, then read its canonical documentation URL. One run per path; Reach searched first, xcoze read first. Shared upstream caches/network preclude quality/latency ranking.

| Action | Agent Reach | xcoze default | xcoze follow-up |
|---|---|---|---|
| Web search | Exa, three URLs, 1.48 s | Exa, same three URLs, 0.62 s | No evidence of quality superiority |
| Read official page | Jina, 67841 chars, 1.75 s | Jina, clipped to 24000 chars, 1.19 s | --max-characters 100000: 67841 chars, 0.64 s |

Added opt-in longer reading after observing the clipping gap. Default remains 24000 for bounded context; only missing required sections justify expansion, up to 200000 characters. `truncated:false` does not verify full-page or dynamic-content completeness; `completeness_verified:false` stays explicit.

Typed summaries/page text/abstracts/question excerpts/package-model-repository metadata stay distinct. Public-index-only Bilibili/YouTube/Xiaohongshu entries do not claim retrieved comments or subtitles. Existing Reach/yt-dlp/gh/agent-browser presence is reported offline; the Agent uses their own Skills/authorization. No execution bridge was added.

## What would establish a better product

Build shared task evaluation across Chinese news/policy, docs, software ecosystems, communities and video; assess whether evidence answers the question. Accept search/body/comments/subtitles/time bounds separately. Improve task-level cost accounting, bounded health records and freshness-aware cache design. Reuse authorized tools before optional platform extensions. Keep ordinary installation independent of browsers/Node. These are roadmap work, not completed universal coverage or superiority claims.

Current evidence: 120 offline tests, public API calls and this limited comparison. No blind answer evaluation or long-term multi-network acceptance exists.

```bash
python3 scripts/benchmark.py --corpus evaluations/open-source-cases.json --modes free --limit 10 --count 3 --output ../open-plan.json
python3 scripts/benchmark.py --live --corpus evaluations/open-source-cases.json --modes free --limit 10 --count 3 --max-requests 20 --output ../open-live.json
```

Default is offline without credential reads. --live queries public services. Do not publish local reports containing excerpts without sanitization. Refresh dated tasks and retain separate historical reports.
