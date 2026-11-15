# Multi Search Engine Skill reference

[简体中文](multi-search-engine.md) | **English**

Reference: [Zhaopintong AI · Multi Search Engine](https://skillhub.cn/skills/zhaopintong/multi-search-engine), identified on SkillHub as `@zhaopintong/multi-search-engine`. The package downloaded and inspected on 2026-11-15 was **1.0.2**. This is distinct from similarly named multi-engine Skills in other repositories.

The review covered the public page, packaged instructions, service rules and client implementation. We did not install or run its scripts, invoke platform search, create an account or test billing. Service rules below describe that package version and may change.

## Implementation

| Area | Observation |
|---|---|
| Search entry point | The client submits tasks through Zhaopintong's platform gateway; the package does not list multiple upstream engines that users can select independently |
| Credentials | Users do not supply upstream search keys; the platform maintains task identity and account association |
| Pricing rules | The package states that the first successful search is free, with later searches requiring an account and costing CNY 0.10 each; successful zero-result searches also count |
| Result volume | Requests 30 results by default, with a maximum of 50; actual counts are retained when fewer results are available |
| Delivery | The platform generates PDF, Markdown and CSV; the client downloads and checks their consistency with search results |
| Recovery and reuse | Existing request identifiers support status queries, downloads and exports without another search; normal retention is 30 days |
| Attribution | Original URLs and available dates are preserved; sequence numbers indicate retrieval order, and excerpts do not imply verification of original pages |

The project emphasizes delivery and recovery of search outputs. The package alone does not establish upstream coverage, relevance, speed or live reliability of the paid service.

## Application in xcoze search

xcoze search continues to provide multiple search sources and on-demand reading. This update adds local result persistence and reuse:

- Generate `results.json`, `report.md` and `links.csv` when needed, with Chinese or English reports.
- Change report language or export location from saved JSON without networking or another search.
- Preserve providers, original ranks, links, available dates and error status; repeated URLs are not independent evidence.
- Preserve completed search output after a saving failure, allowing the local export alone to be retried.
- Protect existing different files and use only the standard library, without new runtime dependencies.

Platform accounts, quotes, usage tracking and server-generated reports are outside this adaptation. PDF export remains a possible extension; current Markdown and CSV delivery runs locally.

See the [output contract](../references/output.en.md#save-and-export-search-results) for usage.

## Attribution and licensing

We referenced workflow design and independently implemented the local exporter. No project-level open-source license was found in the inspected package. Its font license applies to the font and does not establish permission for other files. No code, fonts, branding or package files from the reference project are copied or redistributed.

Inspected package SHA-256: `2e83eec8a7eb7601f89e457c8825795fa8529f4a4fa3beb7f1ad2b8b2d431b0e`.
