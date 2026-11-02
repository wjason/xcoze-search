# Validation records

[简体中文](VALIDATION.md) | **English**

## Unreleased: bilingual documentation and release checks

- Fourteen document/instruction pairs provide Chinese and English, with Chinese as default. Language links and packaged references are reviewed for this change. One added bilingual-release check brings the current source to 68 passing offline tests; historical v0.3.0 records retain their original 67-test scope.

## v0.3.0 preview — 2026-11-02

- 67 local offline tests passed: 33 original search/setup tests, three release checks, 27 provider/multi-source/migration contracts, and four search/extraction corpus/budget tests. They use synthetic responses/keys and temporary directories without changing existing credentials.
- Covers fixed official endpoints, authentication, GET/POST requests, domain/date/native freshness filters, counts, and pre-network rejection of unsupported options across six providers.
- Separates Tavily snippets/text, Exa text/highlights/summary, Brave extra snippets, and Bocha summaries. Retains usage, costDollars, and unknown metadata; unreported usage/cost stays null.
- Covers three-provider order, unchanged both/auto behavior, credential preflight, runtime partial failure, native scores, and duplicate URLs.
- Budgets count retries/failures, reject insufficient initial budgets, and count HTTP successes with malformed result bodies. Covers redacted errors and Bocha HTTP 200 application failures.
- Checks Tavily failed_results, Exa per-URL statuses, and normalized URLs rather than trusting HTTP 200.
- v1 reads do not rewrite files. Migration preserves native/unknown fields, creates backups exclusively, protects originals on future schemas/write failures, and does not run after cancellation.
- Offline plans passed for 12 bilingual queries across six providers and three extraction URLs across three providers. Synthetic responses validate shared-budget live execution, not actual retrieval quality.
- Skill structure, entry points, package contents, versions, and hashes are reviewed for publication. CI covers Windows/Linux and Python 3.10/3.12.

Live status: on 2026-11-02, existing DeepSeek credentials passed Search/Fetch regression with one HTTP request each and zero retries. Search returned usable results; Fetch returned 9,405 characters of nonempty text. Configuration remained v1 and was not rewritten. No key or raw page body was printed. The four new providers lack live test keys. Yuanbao is unconfigured without an available test credential. These checks do not guarantee future account access, balance, reachability, retrieval quality, or desktop acceptance.

## v0.2.0 preview — 2026-11-02

- 33 local macOS offline tests passed, including eight new dialog tests using synthetic keys and temporary configuration. No existing user keys were read/modified and no live API calls were made.
- Covers setup without a TTY, cancellation preserving files, redacted failure/timeout output, empty/multiline rejection, effective-variable precedence, retention of another provider, and saved-but-unverified results.
- macOS hidden-input AppleScript passed osacompile. This establishes syntax only, not real dialog acceptance.
- Skill passed quick_validate.py; CLI help/version checks passed.
- Three release tests reject version mismatch or missing/empty notes and extract only the current version's section. Total: 36 offline tests.
- Real desktop input/cancellation on macOS/Windows/Linux remains pending. Windows/Linux CI exercises offline behavior without opening dialogs.
- Preview publication requires all four Windows/Linux and Python 3.10/3.12 jobs, then packages/checksums. v0.1.0 assets remain unchanged. Actual publication state is recorded in [Releases](https://github.com/wjason/xcoze-search/releases).

## v0.1.0 historical record

Dates: 2026-10-24 for API research/initial live verification; 2026-11-02 for GitHub publication review.

The release review reached 25 local offline tests, including explicit XDG_CONFIG_HOME working without a resolvable home. See [GitHub Actions](https://github.com/wjason/xcoze-search/actions/workflows/test.yml). Initial live-test dates do not imply continuous monitoring.

## Completed checks

- Python 3.10.4/macOS: 24 original unittest cases with synthetic responses and temporary files, no real keys/results/production requests.
- Seven independent behavioral scenarios replaced urllib transport while retaining main, request construction, configuration, mapping, and exit codes.
- Skill frontmatter/directory passed skill-creator quick_validate.py.
- CLI help/version, credential-free status/missing-key search, and extracted-package entry points passed.
- Local Markdown links, manifests, SHA-256, and exclusion of caches/OS metadata/local configuration passed.

## Coverage

Fixed endpoints/Bearer authentication, redirect refusal, no retries for 401/402, bounded 429 retries, long Retry-After stopping, Yuanbao HTTP 200 errors, malformed/oversized responses, Pages JSON strings, optional lite-tier fields, summary/text separation, query/filter limits, both-option rejection before networking, no silent default switch, multi-key preflight, duplicate content retention, empty vs partial results, Fetch boundaries, empty doctor results, hidden input, variable precedence, permissions, and symlinks.

Independent scenarios covered Yuanbao-only auto selection and missing DeepSeek Fetch credentials; dual-source authorization failure retaining the other source with exit 4; setup verifying the effective environment key; offline/redacted status.

## Live account verification

2026-10-24 at 16:10 Asia/Shanghai: existing locally configured DeepSeek credentials passed the following checks without recording keys/configuration contents.

- Search: doctor succeeded once, returned one usable result, search_verified:true.
- Fetch: the official Search & Fetch documentation returned nonempty Markdown (10,282 characters) in one attempt.
- This establishes access for that account/call only, not future balance, quota, availability, or general retrieval quality.

## Not verified

- Yuanbao SearchPro success with a real Search Service key and tier-specific options.
- Manual Windows ACL/terminal input behavior; Windows/Linux offline checks are recorded in GitHub Actions.
- Marketplace parsing, review, listing, certification, and installation; no marketplace is selected.
- Retrieval quality and factual accuracy of research conclusions.

The original release supports source review, offline verification, and configured trials, hence Pre-release. Synthetic tests cannot be described as both services verified live. DeepSeek's status reflects its actual checks; complete Yuanbao doctor/tier checks before changing its status.

## Reproduction

Run from the complete source directory:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/xcoze_search.py --help
python3 scripts/xcoze_search.py --version
python3 scripts/build_release.py --output-dir ../release
```

Independent temporary assessment scripts are workspace evidence, not runtime dependencies or package contents. Public contract tests are reproducible from the repository.

## Suggested live acceptance

Run doctor for each configured provider and require search_verified:true. With both original providers, run both and verify each result set. Fetch a permitted public page with DeepSeek and require nonempty content. Record only provider, redacted RequestId, counts, time, and success/error codes, never keys. Validate options against the actual account tier without automatically upgrading or paying to pass tests.
