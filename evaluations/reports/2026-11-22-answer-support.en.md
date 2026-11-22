# Can the returned passages answer the question?

[简体中文](2026-11-22-answer-support.md) | **English**

2026-11-22 · v0.10.1. [33 cases and answer requirements](../research-cases-v2.json) · [Manual reviews](../research-answer-reviews.json) · [Runs and references](2026-11-22-answer-support.data.json).

## Result

Thirty real questions cover Python, Go, Rust, Kubernetes, browser APIs, energy policies/statistics, tenders and financial disclosures. Three additional cases deliberately create date, topic or request-budget gaps. Exa, Parallel, user keys, host search and browsers were blocked before transmission; user configuration was not read.

| Check | Initial passage selection | Improved selection |
|---|---:|---:|
| Supports every answer requirement | 12/30 | 27/30 |
| Supports some requirements | 8/30 | 2/30 |
| Does not support the requested facts | 10/30 | 1/30 |

The initial run already includes the new Southern Grid search form; only its passage selection precedes the extraction improvements. This is not a released v0.10.0-versus-v0.10.1 comparison. These tasks were selected to expose known weaknesses. The same Agent reviewed returned passages against explicit requirements; the review is neither independent nor blinded, and the counts are not a general answer-accuracy estimate. Reference validation checks that cited passages exist, not that semantic judgments are correct.

The final full run retrieved and read originals for 30/30 questions. Literal checks passed for 27, but the three literal misses are not the same as the three answer-support gaps. The run used **78 HTTP requests**, with a positive-task median of **1.30 seconds**, excluding answer generation. The three deliberate negative cases retained the expected gaps. Exa/Parallel, keyed API and browser attempts were all zero. A subsequent MDN ordering replay used two requests and read the overview directly; its 0.32-second result is separate from the full-run median. Intermediate runs and diagnostic reads are not included in these 78 requests.

## Southern Grid: the previously missed question

The original query remains 数字化, with tender scope unchanged. The previous route searched only two recent list pages. The published website form at `dbsearch.jspx` searches beyond this window, and the site echoes its query and channel. Truncated titles had also lost their tender classification; an explicit published category now supplies that classification unless the title names another stage.

The original for [digital modeling services](https://www.bidding.csg.cn/zbgg/1200450933.jhtml) identifies project CG3800022002451383 and bid submission closing at **2026-12-11 09:00**. The more specific [digital construction supervision tender](https://www.bidding.csg.cn/zbgg/1200450806.jhtml) has project CG2600022002404187, document acquisition ending **2026-11-26 18:00** and bid submission closing **2026-12-11 08:40**. The dates have separate labels and do not establish current bidding eligibility. No list scan, identity change or CAPTCHA handling is used.

## What changed

- Preserve conditions, consequences and negations in explanatory passages. TaskGroup now includes ordinary child failure and exception aggregation; NetworkPolicy includes both ends of a connection.
- Bound published method sections so OnceLock.get does not inherit set behavior. Preserve Sphinx symbol spelling so `timeout` does not select the `Timeout` class.
- Follow existing default-deny headings and retain explanatory YAML; do not invent anchors.
- Separate acquisition, bid and response deadlines. Filter explicit candidate notices out of award requests instead of trusting the website category code alone.
- Match API identifiers as tokens: an AbortController constructor is not evidence that its abort operation was explained.

## Remaining gaps

- **R05:** signal and abort roles are present, but the concrete signal-to-request step needs a further example read.
- **R24:** TimeoutError is explicit; the returned code cuts at the AbortError branch before fully explaining user cancellation.
- **R25:** only the storage-plan cover notice is read. Its capacity target is in an unread PDF; no target is inferred.

R19 and R30 show the reverse problem: the passages can answer despite a missing literal term, because the method context establishes OnceLock and the award table uses an offer-price label instead of 金额. The Agent must inspect the facts, context, scope and units rather than equating either literal success or literal failure with answer quality.

## Per-question review

| ID | Result | Finding and original |
|---|---|---|
| R01 | Supported | A non-cancellation child failure cancels remaining tasks; exceptions are grouped after completion. [Original](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup) |
| R02 | Supported | cancel records a non-nil cause, retrieved with Cause(ctx). [Original](https://pkg.go.dev/context#WithCancelCause) |
| R03 | Supported | The method initializes an unset cell and reuses its stored value; prose and repeated-call examples support this. [Original](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.get_or_init) |
| R04 | Supported | Ingress and egress isolation are separate; source egress and destination ingress must both allow the connection. [Original](https://kubernetes.io/docs/concepts/services-networking/network-policies/) |
| R05 | Partial | The passages explain signal communication and aborting fetch, but lack the concrete step of passing signal to the request. [Original](https://developer.mozilla.org/en-US/docs/Web/API/AbortController/AbortController) |
| R06 | Supported | The timeout context manager transforms CancelledError into TimeoutError. [Original](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout) |
| R07 | Supported | The matching notice has an original issuance date of 2025-08-27, distinct from its 2025-09-12 archive date. [Original](https://www.nea.gov.cn/20250912/73455a1a61b248d4aef65cc124631398/c.html) |
| R08 | Supported | The original notice is identified as document 411; unread attachments remain unread, so the complete rules are not interpreted. [Original](https://www.nea.gov.cn/20250429/df8e465e859245039b24fbbe21f04c5f/c.html) |
| R09 | Supported | The original covers full-year 2025; the page date and release event mentioned in its text remain distinct. [Original](https://www.nea.gov.cn/20260121/715f79826488476a9162da7c8bd77c80/c.html) |
| R10 | Supported | Passages give document acquisition on November 5–12 and bid submission on November 26 at 09:00; the ambiguous question needs explicit labels. [Original](https://www.ggzy.gov.cn/information/deal/html/b/440000/0201/20261105/004469eed41af70445c494e2d97af73d5ee8.html) |
| R11 | Supported | The Zhengdong Longhu storage EPC award original is found after excluding candidate-only titles. [Original](https://www.ggzy.gov.cn/information/deal/html/b/410000/0104/20261119/004169ff84cf10094b6d881259078bd61ac7.html) |
| R12 | Supported | The missed task finds an open tender for digital modeling services; bids are due 2026-12-11 at 09:00. [Original](https://www.bidding.csg.cn/zbgg/1200450933.jhtml) |
| R13 | Supported | The cover confirms Kweichow Moutai, 600519 and the 2024 annual report; only the first ten of 143 pages are extracted. [Original](https://static.cninfo.com.cn/finalpage/2025-04-03/1222993920.PDF) |
| R14 | Supported | With return_exceptions=False, the first exception propagates immediately and other awaitables are not automatically cancelled. [Original](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather) |
| R15 | Supported | The passage explicitly places TimeoutError handling outside the timeout context manager. [Original](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout) |
| R16 | Supported | The current contextvars.Context propagates from the event-loop thread into the worker thread. [Original](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread) |
| R17 | Supported | Cancellation releases context resources and callers should cancel after operations finish; the example also explains goroutine leaks. [Original](https://pkg.go.dev/context#WithCancel) |
| R18 | Supported | Keys must be comparable; custom types avoid cross-package collisions from built-in types such as strings. [Original](https://pkg.go.dev/context#WithValue) |
| R19 | Supported | get returns None before or during initialization and never blocks; set semantics are excluded. [Original](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.get) |
| R20 | Supported | Initializer panic propagates to the caller and leaves the cell uninitialized. [Original](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.get_or_init) |
| R21 | Supported | Policies combine their allowed connections by union, without override or evaluation-order dependence. [Original](https://kubernetes.io/docs/concepts/services-networking/network-policies/) |
| R22 | Supported | The YAML and prose show podSelector: {}, Ingress policyTypes and no allowed ingress rules. [Original](https://kubernetes.io/docs/concepts/services-networking/network-policies/#default-deny-all-ingress-traffic) |
| R23 | Supported | HTTP 404 does not itself reject fetch; the response status or ok must be checked. [Original](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch) |
| R24 | Partial | TimeoutError is explicit, but the excerpt cuts at the AbortError branch and lacks full context establishing user cancellation. [Original](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static) |
| R25 | Unsupported | Only the plan notice is read; the installed-capacity target is in an unread PDF, so the passages cannot answer it. [Original](https://www.nea.gov.cn/20250912/73455a1a61b248d4aef65cc124631398/c.html) |
| R26 | Supported | The original gives 103682 hundred-million kWh and 5.0% growth for full-year 2025. [Original](https://www.nea.gov.cn/20260121/715f79826488476a9162da7c8bd77c80/c.html) |
| R27 | Supported | The same project has ID CG2600022002404187 and bid deadline 2026-12-11 at 08:40. [Original](https://www.bidding.csg.cn/zbgg/1200450806.jhtml) |
| R28 | Supported | Document acquisition ends 2026-11-26 at 18:00; bids close 2026-12-11 at 08:40, a different time. [Original](https://www.bidding.csg.cn/zbgg/1200450806.jhtml) |
| R29 | Supported | The buyer is Southern Grid Lancang-Mekong International Energy; responses close 2026-11-24 at 09:00. [Original](https://www.bidding.csg.cn/fzbgg/1200449758.jhtml) |
| R30 | Supported | The award consortium is POWERCHINA Huadong and China Railway Electrification Third Engineering, at CNY 194687771.00; candidate bids and historical contracts are excluded. [Original](https://www.ggzy.gov.cn/information/deal/html/b/410000/0104/20261119/004169ff84cf10094b6d881259078bd61ac7.html) |

## Reproduce

```bash
python3 evaluations/evaluate_research.py --live --corpus evaluations/research-cases-v2.json --output /tmp/research.json --review-output /tmp/research-private.json
python3 evaluations/review_research.py --corpus evaluations/research-cases-v2.json --results evaluations/reports/2026-11-22-answer-support.data.json --reviews evaluations/research-answer-reviews.json --run final --output /tmp/answer-review.json
```

The first command retrieves live material; omitting `--live` only plans offline. `--review-output` is a private local excerpt artifact. The second command validates the saved manual reviews, not new semantic judgments. Reassess new runs rather than copying old verdicts. Rolling tender lists can change. Public artifacts omit full originals, credentials and account data. **270 offline tests pass.**
