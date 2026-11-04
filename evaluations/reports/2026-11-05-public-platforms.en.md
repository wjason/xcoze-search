# Public-platform checks and integration choices

[简体中文](2026-11-05-public-platforms.md) | **English**

Date: 2026-11-05, Asia/Shanghai. Release: v0.8.0. The aim is more directly accessible public evidence for Agents, retaining low latency and keyless access while distinguishing search, trend discovery and page reading.

## Added in this release

| Real question | Adapter | Rows | End-to-end time | Evidence retrieved |
|---|---|---:|---:|---|
| What are Bilibili's current hotwords? | bilibili-trending | 5 | 0.224 s | Public hotwords, native heat fields and search links, not video rankings |
| What questions are hot on Zhihu? | zhihu-trending | 5 | 0.280 s | Question links, excerpts and displayed heat, without reading answers |
| What topics are hot on V2EX? | v2ex-trending | 5 | 0.597 s | Titles, nodes, creation times and reply counts, without bodies/replies |

Installed acceptance: Bilibili/Zhihu continued to succeed, while V2EX later returned 403 (about 0.635 s, one HTTP). The adapter paused for 15 minutes. A subsequent V2EX call returned source_cooldown with zero HTTP, without cookie changes, browser switching or paid calls. V2EX cannot be described as continuously available in this check.

Each ran through the real run_trending adapter, shared transport and live endpoint with one HTTP attempt. No keyed API, cookies or browser. Questions describe the selected action, not verified natural-language invocation across all Agent hosts. Times include local adaptation, pacing checks and networking, not just server time. One local sample cannot establish long-term availability or latency percentiles.

Rows retain source order. Explicit Bilibili commercial markers are filtered, potentially leaving rank gaps. Heat units are not compared across sites. Retrieval time is not upstream update time. Unknown Bilibili/Zhihu publication times stay null; V2EX dates are topic creation, not rank updates. Requested row counts do not establish a complete site ranking.

## Xiaohongshu, Weibo and blocked paths

| Probe/search | Observation | Decision |
|---|---|---|
| Anonymous Weibo ajax/side/hotSearch | HTTP 403, about 0.35 s | No native feed; no identity switching |
| Bilibili keyword endpoint, Python | HTTP 412, about 0.20 s | No native keyword adapter; hotwords are separate |
| Xiaohongshu search page, Python | HTML HTTP 200, about 0.67 s | Anonymous results/bodies not verified; 200 is not capability acceptance |
| Xiaohongshu public index, Python learning | One anonymous Exa call, about 0.73 s; mainly profiles | Retain author leads, without claiming note bodies |
| Weibo public index, artificial intelligence | One anonymous Exa call, about 1.16 s; posts and profiles mixed | Index leads, not native search or read bodies |

Both index searches explicitly used free mode with browser disabled. Keyed API attempts were zero. No credentials were added and user configuration was unchanged. Nonempty indexes do not establish content quality; the Xiaohongshu sample did not close the note-body evidence gap.

New platform_item_type labels known URL shapes such as note_link, post_link and user_profile. Profiles can help find authors but cannot answer what a note says. URL classification does not establish current page access.

## Primary documentation and implementation references

- [Xiaohongshu account API](https://openaccount.xiaohongshu.com/docs/api-reference) covers authorization, tokens and basic user information. Its [scope documentation](https://openaccount.xiaohongshu.com/docs/scope) currently opens basic_info and marks read_notes as planned. This is not anonymous general note search; other business-specific authorized interfaces may exist.
- NewsNow's [Bilibili](https://github.com/newsnext/newsnow/blob/main/server/sources/bilibili.ts) and [Zhihu](https://github.com/newsnext/newsnow/blob/main/server/sources/zhihu.ts) implementations identify public website endpoints. The Python adapters are independently implemented; these endpoints have no open-platform SLA.
- The [NewsNow Weibo implementation](https://github.com/newsnext/newsnow/blob/main/server/sources/weibo.ts) depends on a hardcoded cookie. This project does not copy/use it or call it configuration-free access.
- [V2EX API fair-use rules](https://www.v2ex.com/p/7v9TEc53) cover limits and usage boundaries. The adapter retrieves user-requested leads on demand. This report does not republish topic bodies, profiles or complete feed contents.

## Implementation and validation

- Separate trending command: one selected platform, one HTTP attempt, 8-second default timeout, no retries, config/key reading or extra ordinary-search calls.
- Two-second per-feed pacing with local cross-process serialization. Access denials (401/403/412) pause for 15 minutes; 429/503 honor Retry-After, defaulting to 60 seconds. No cookie/proxy/browser switching to evade pauses.
- Valid empty arrays may succeed with empty:true. Invalid shapes, application errors and verification pages cannot become successful empty feeds. Parsing failures still count sent HTTP attempts.
- Offline catalogs distinguish keyword coverage from native_trending. Feeds never become Smart search candidates.
- 159 offline tests pass, covering free isolation, no config/cookies/browser, ranks/ads/dates, malformed data, actual attempt counts and denial pauses. CI sends no live requests.

Initial adapter/index calls ran in a development worktree still labelled 0.7.2; the release is 0.8.0. Subsequent installed acceptance is recorded separately in the [structured record](2026-11-05-public-platforms.data.json), without mixing timings or counting repeated questions as extra tasks. There were six direct probe operations (internal redirect counts were not measured); initial adapter/index checks used five observable API HTTP attempts. Documentation browsing is outside this ledger.

## Next steps

1. Publisher RSS/Atom and government notices: improve Chinese current-information coverage and originals; validate dates and duplicates on real tasks.
2. V2EX latest topics/single-topic reading and community originals: improve completion from leads to citable text.
3. Xiaohongshu/Weibo native actions: verify public endpoints or existing authorized tools first, documenting login/maintenance costs instead of promising anonymous access.
4. Repeat across networks and observe error rates, latency distributions and schema drift. Source counts, nonempty feeds and single successful calls are not answer-quality measurements.
