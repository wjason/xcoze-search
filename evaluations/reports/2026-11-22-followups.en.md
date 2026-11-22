# Necessary attachments and complete context

[简体中文](2026-11-22-followups.md) | **English**

2026-11-22 · v0.10.2. [Unchanged corpus and requirements](../research-cases-v2.json) · [Manual reviews](../research-followup-reviews.json) · [Live records and passage positions](2026-11-22-followups.data.json).

## Three outstanding questions

The original queries, questions and answer requirements are unchanged. The live v0.10.1 baseline still has two partially supported cases and one unsupported case. The updated results support every requirement for all three:

| Case | New original evidence | HTTP requests | Latency |
|---|---|---:|---:|
| R05 | AbortController: the published same-host example creates the controller, passes signal to fetch and calls abort. | 3 | 1.37 s |
| R24 | AbortSignal: the complete published block distinguishes timeout from user cancellation through its TimeoutError and AbortError branches. | 2 | 1.02 s |
| R25 | Storage plan: PDF page 1 states a 2027 nationwide capacity target of at least 180 million kW. | 3 | 1.84 s |

Sources: [AbortSignal examples](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal#examples), [AbortSignal.timeout](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static), [NEA notice and its published attachment](https://www.nea.gov.cn/20250912/73455a1a61b248d4aef65cc124631398/c.html). The policy attachment returned text from pages 1–7 under a pages-1–10 request. That records extracted scope, not a guarantee of full-file completeness; its publication date stays unknown rather than inheriting the notice date.

## Full regression

With Exa, Parallel, user keys, host search and browsers blocked, all 30 real questions returned originals. Manual review of actual returned passages supported **30/30** questions against their existing requirements. All three deliberate date/topic/budget negative cases retained their expected gaps. The full run used **79 HTTP requests**, with a positive-task median of **1.42 seconds**. Paid API, Exa/Parallel and browser attempts were zero. Three English-question replays also supported the same facts using eight further HTTP requests; their decisive code/PDF passages matched the Chinese runs.

These are selected regression questions, reviewed by the same Agent without independent blinding. They are not a universal answer-accuracy estimate. Literal coverage passed 28 questions, which is a different check: missing literal terms can still have sufficient contextual evidence. Reference validation confirms passage existence and requirement coverage declarations, not semantic truth.

Only R05 and R25 triggered example or attachment follow-ups among the 30 real tasks. R24 retained complete code from the already fetched page without extra network requests. R13 remains a direct annual-report PDF read, separate from an attachment follow-up.

## Bounded follow-ups

A relevant PDF is considered only when details are missing or a sparse notice delegates needed detail; one delegated example may be read for procedural questions. Both must be publisher-supplied links on the same supported host. Research follows at most one of each type, never recursively. Existing sufficient text avoids attachment reads.

Searches, bodies, examples and PDFs share one read-count, HTTP and time budget. The parent records each follow-up and its state; child documents retain their parent and reason. Dates are not manufactured. Missing extraction tools, unreadable/scanned PDFs, access denials and exhausted limits preserve explicit gaps. PDF extraction uses existing pdftotext only.

Complete published code blocks up to 1800 characters retain indentation and both branches. Blocks outside the returned-text cap are not marked complete. Published omissions remain omissions; a complete block is not a claim that the entire application or answer has been verified.

## Real controls

| Setting | HTTP requests | Observed result |
|---|---:|---|
| R05: context links off | 2 | No example read; explicit example gap and follow_up_disabled stop |
| R25: attachments off | 2 | Notice retained; attachment gap retained |
| R25: maximum two HTTP requests | 2 | No PDF request; attachment and request-budget gaps retained |

The first context-off control spent five requests reading more search candidates even though only the disabled example was missing. The stop rule was narrowed for that case; the final same-question replay spent two requests and retained the gap. This replay is separate from the default full-run total and median. Controls, English replays, the focused baseline and diagnostic reads are not mixed into the 79-request default run.

## Per-question review

| ID | Finding and original |
|---|---|
| R01 | A non-cancellation child failure cancels remaining tasks; exceptions are grouped after completion. [Original](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup) |
| R02 | cancel records a non-nil cause, retrieved with Cause(ctx). [Original](https://pkg.go.dev/context#WithCancelCause) |
| R03 | The method initializes an unset cell and reuses its stored value; prose and repeated-call examples support this. [Original](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.get_or_init) |
| R04 | Ingress and egress isolation are separate; source egress and destination ingress must both allow the connection. [Original](https://kubernetes.io/docs/concepts/services-networking/network-policies/) |
| R05 | The linked same-host example explicitly creates a controller, passes signal to fetch and calls controller.abort(); both answer requirements are supported. [Original](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal#examples) |
| R06 | The timeout context manager transforms CancelledError into TimeoutError. [Original](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout) |
| R07 | The matching notice has an original issuance date of 2025-08-27, distinct from its 2025-09-12 archive date. [Original](https://www.nea.gov.cn/20250912/73455a1a61b248d4aef65cc124631398/c.html) |
| R08 | The original notice is identified as document 411; unread attachments remain unread, so the complete rules are not interpreted. [Original](https://www.nea.gov.cn/20250429/df8e465e859245039b24fbbe21f04c5f/c.html) |
| R09 | The original covers full-year 2025; the page date and release event mentioned in its text remain distinct. [Original](https://www.nea.gov.cn/20260121/715f79826488476a9162da7c8bd77c80/c.html) |
| R10 | Passages give document acquisition on November 5–12 and bid submission on November 26 at 09:00; the ambiguous question needs explicit labels. [Original](https://www.ggzy.gov.cn/information/deal/html/b/440000/0201/20261105/004469eed41af70445c494e2d97af73d5ee8.html) |
| R11 | The Zhengdong Longhu storage EPC award original is found after excluding candidate-only titles. [Original](https://www.ggzy.gov.cn/information/deal/html/b/410000/0104/20261119/004169ff84cf10094b6d881259078bd61ac7.html) |
| R12 | The missed task finds an open tender for digital modeling services; bids are due 2026-12-11 at 09:00. [Original](https://www.bidding.csg.cn/zbgg/1200450933.jhtml) |
| R13 | The cover confirms Kweichow Moutai, 600519 and the 2024 annual report; only the first ten of 143 pages are extracted. [Original](https://static.cninfo.com.cn/finalpage/2025-04-03/1222993920.PDF) |
| R14 | With return_exceptions=False, the first exception propagates immediately and other awaitables are not automatically cancelled. [Original](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather) |
| R15 | The passage explicitly places TimeoutError handling outside the timeout context manager. [Original](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout) |
| R16 | The current contextvars.Context propagates from the event-loop thread into the worker thread. [Original](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread) |
| R17 | Cancellation releases context resources and callers should cancel after operations finish; the example also explains goroutine leaks. [Original](https://pkg.go.dev/context#WithCancel) |
| R18 | Keys must be comparable; custom types avoid cross-package collisions from built-in types such as strings. [Original](https://pkg.go.dev/context#WithValue) |
| R19 | get returns None before or during initialization and never blocks; set semantics are excluded. [Original](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.get) |
| R20 | Initializer panic propagates to the caller and leaves the cell uninitialized. [Original](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.get_or_init) |
| R21 | Policies combine their allowed connections by union, without override or evaluation-order dependence. [Original](https://kubernetes.io/docs/concepts/services-networking/network-policies/) |
| R22 | The YAML and prose show podSelector: {}, Ingress policyTypes and no allowed ingress rules. [Original](https://kubernetes.io/docs/concepts/services-networking/network-policies/#default-deny-all-ingress-traffic) |
| R23 | HTTP 404 does not itself reject fetch; the response status or ok must be checked. [Original](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch) |
| R24 | The complete published block retains both TimeoutError and AbortError branches; this example identifies timeout versus user actions such as browser stop. [Original](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static) |
| R25 | The necessary linked PDF states on page 1 that nationwide new energy-storage capacity should reach at least 180 million kW in 2027. Text was extracted from pages 1–7 without assigning the notice date to the PDF. [Original](https://www.nea.gov.cn/20250912/73455a1a61b248d4aef65cc124631398/2025091273455a1a61b248d4aef65cc124631398_358225d8906a1840e98ffbbfcbac506bab.pdf) |
| R26 | The original gives 103682 hundred-million kWh and 5.0% growth for full-year 2025. [Original](https://www.nea.gov.cn/20260121/715f79826488476a9162da7c8bd77c80/c.html) |
| R27 | The same project has ID CG2600022002404187 and bid deadline 2026-12-11 at 08:40. [Original](https://www.bidding.csg.cn/zbgg/1200450806.jhtml) |
| R28 | Document acquisition ends 2026-11-26 at 18:00; bids close 2026-12-11 at 08:40, a different time. [Original](https://www.bidding.csg.cn/zbgg/1200450806.jhtml) |
| R29 | The buyer is Southern Grid Lancang-Mekong International Energy; responses close 2026-11-24 at 09:00. [Original](https://www.bidding.csg.cn/fzbgg/1200449758.jhtml) |
| R30 | The award consortium is POWERCHINA Huadong and China Railway Electrification Third Engineering, at CNY 194687771.00; candidate bids and historical contracts are excluded. [Original](https://www.ggzy.gov.cn/information/deal/html/b/410000/0104/20261119/004169ff84cf10094b6d881259078bd61ac7.html) |
## Reproduce

```bash
python3 evaluations/evaluate_research.py --live --corpus evaluations/research-cases-v2.json --output /tmp/research.json --review-output /tmp/research-private.json
python3 evaluations/review_research.py --corpus evaluations/research-cases-v2.json --results evaluations/reports/2026-11-22-followups.data.json --reviews evaluations/research-followup-reviews.json --run final --output /tmp/followup-review.json
```

Omit --live for an offline plan. Private review output contains excerpts and is not published. The second command validates saved judgments; new results need a new manual review. **279 offline tests pass**, including shared budgets, explicit disabling, missing tools, denial stops, same-host/credential checks, no recursion, page mapping and clipped-code handling. The pdftotext availability was real for live PDF checks; Windows/Linux fixtures mock it rather than claim a cross-platform live PDF installation.
