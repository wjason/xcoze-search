# Research search and evidence

[简体中文](research.md) | **English**

Use `search` to locate material. `research` searches, reads originals and identifies explicit evidence gaps within one task budget. The calling Agent verifies the final claim; no additional model service is used.

```bash
python3 scripts/xcoze_search.py research 'asyncio TaskGroup' --platform python-docs --question 'What happens to other tasks when a task fails?' --require-topic TaskGroup --require-topic ExceptionGroup
python3 scripts/xcoze_search.py research '储能' --platform government-procurement --region 广东 --notice-type tender --start-date 2026-10-22 --end-date 2026-11-22 --require-topic 储能 --require-topic 截止时间
```

## Workflow

1. Preserve the question and choose compatible sources under existing preferences. Keep site, date, province and notice-stage constraints.
2. Read originals when needed. Adapted official sites use native reading first. Follow only the body link actually published by a notice directory, one level at most.
3. Check essential terms in read text, distinct-document requirements and requested original-publication ranges. Continue within the original source plan when evidence is missing.
4. Return cited passages, document identities, dates, request use and gaps for Agent review. Stop when reviewable coverage or a budget limit is reached.

These are literal evidence checks, not semantic scoring or fact verification. A term appearing in text does not establish a claim. An unknown date does not establish noncompliance. `ok:true` means candidates were retrieved; `complete:false` leaves final verification to the Agent. `coverage.enough_for_agent_review` means the checks found no listed gaps, not that an answer is correct.

## Budgets and scope

| Option | Default or range |
|---|---|
| `--read-count` | Up to three original/follow-up read attempts; 1–5 |
| `--min-documents` | At least one distinct document; 1–3, not a claim of source independence |
| `--require-topic` | Repeat essential terms; otherwise derive them from short query terms |
| `--max-read-characters` | 12000 characters per read; 1000–24000 |
| `--max-requests` | Shared task limit, default 12; search, directory, body and follow-up requests all count |
| `--max-seconds` | Default 45; requests use remaining time, not a hard underlying DNS deadline |
| `--page-count` | Up to two Southern Grid pages on an empty window; 1–3, published next links only |

Explicit `--page` remains one page. Ordinary `search` does not follow pages automatically. Southern Grid titles can be truncated; an empty bounded window is not a whole-site absence result. Restarting a command must not evade the total task budget.

## Originals, PDFs and dates

Native reading covers adapted official technical documentation, NEA, NBS, public trading, Southern Grid and CNINFO PDF hosts. Inspect exact hosts with `capabilities --provider native-reader`. Prefer article containers or the requested anchor; a fallback to visible page text is labeled. Navigation and directories are not automatically claim evidence.

PDF extraction uses an existing `pdftotext` and requests up to ten pages. Missing tools, scanned PDFs and extraction failures remain gaps; no installation or full-report claim is made. Page bounds and truncation are returned. Other URLs use permitted reading services or existing host tools.

Search dates and original publication dates remain separate. Native reading uses explicit metadata or labeled publication text, never the URL or retrieval date. Statistical periods, effective dates and tender deadlines require passage-level verification.

Bid deadlines are extracted only from explicit labels with adjacent dates, retaining their source location. Generic mentions of a deadline are not date values and do not establish an active tender. Method focus selects an ID actually present on the page rather than inventing a method link.

## Documents and citations

Merge matching document URLs across fragments and common tracking parameters, retaining provider/rank provenance in `retrieved_by`. Keep version paths and meaningful query parameters. Same-title pages on different sites are possible republications, not proven independent sources. Read documents with essential-term matches appear first without comparing vendor scores.

Bodies remain separate from search summaries. `documents.passages` contains literal excerpts and line positions, not generated answers. `read_characters`, `truncated` and `extraction_scope` describe the reading boundary. `coverage.gaps` helps the Agent decide what to verify next or which limitation to disclose.

## Availability and upgrades

Offline `sources` separates adapter scope from action-level check dates and stale samples. Checks older than seven days are not current availability. Weekly checks refresh the public snapshot and bilingual status pages; anonymous quotas, networks and site changes can still affect the next request. Local pacing and access-denial cooldowns do not use identity changes.

See [installation](../INSTALL.en.md) for version checks and upgrades. The normal package contains runtime code and usage documents; historical corpora, studies and evaluation data remain in the repository and source archive.

Run `sources --refresh` explicitly to update the local cache with one public request. It reads no keys, changes no installed files and does not probe individual sources. Ordinary queries continue using an offline snapshot.

## Check whether passages answer the question

List the facts required by the question and verify that passages retain conditions, negations, units, project identity and date types. `coverage.answer_support` stays `not_assessed` with `answer_review_required`; literal checks do not generate answer-accuracy scores. Native method extraction stops before the next method or peer heading where possible, and keeps conditions with consequences.

Southern Grid defaults to the website keyword form, `csg-search`. The bounded list pagination above applies only to explicit `--provider csg`. Observations distinguish acquisition, bid and non-tender response deadlines without inferring current bidding status.

## Attachments and complete examples

When a question needs details missing from a notice, research can read one relevant PDF linked by the publisher. For procedural questions, it can also follow one published example link when the current page delegates examples elsewhere. Only the same host on the native reader's supported list is eligible. External hosts, credential-bearing URLs, recursive links and unrelated attachments are not followed.

Both follow-ups use the current `--read-count` (default three), HTTP budget and remaining time. `--attachments off` and `--context-links off` turn them off separately. Plain source-location questions and notices already containing sufficient topic/value evidence do not download attachments. The Agent still checks whether the excerpts answer the facts required.

A child document carries `relationship`, `parent_document_id`, `parent_url`, `follow_up_reason` and `date_context`. The parent retains `follow_up_reads` and the URLs of read attachments. Disabled, failed or budget-limited reads remain explicit gaps. Publication filters keep their notice-date meaning; they never manufacture a publication date for an attached PDF.

PDF text uses an existing `pdftotext`, requesting pages 1–10. `pdf_pages_extracted` lists pages with returned text and `passages.pdf_pages` locates the evidence. This does not prove full-file extraction. Missing tools, scanned documents or access denials keep the notice and the gap, without installing software or switching to a paid reader.

For code, research prefers a complete published HTML code block of at most 1800 characters, retaining indentation and both sides of error branches. Blocks outside the returned text limit are not labeled complete. `context_complete` describes the retained published block, not the completeness of the whole program or the truth of an answer.
