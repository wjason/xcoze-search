# Output contract v0.3.0

[简体中文](output.md) | **English**

Standard output is JSON; top-level runtime errors use JSON on standard error. Argparse help/syntax errors retain Python's standard behavior. Setup guidance uses stderr and never echoes keys. GUI subprocess stdout/stderr is consumed only inside the local script, not forwarded to the agent.

## Search

Existing fields are retained: ok, complete, partial, empty, version, operation, retrieved_at (UTC), query, providers, results, requests, errors, duplicate_groups, facts_verified:false. budget and provider usage/cost/timing metadata are added.

| Result field | Meaning |
|---|---|
| provider / rank | Original service and its result order, starting at 1 |
| title / url | Title and public HTTP(S) source URL |
| snippet | Native search snippet or Tavily excerpt |
| summary | Native or explicitly requested summary, separate from text |
| content | Available page text; summaries are never put here |
| highlights | Exa excerpt array; empty for other providers |
| extra_snippets | Optional Brave snippets; not full page text |
| content_kind | page_content / excerpts / search_summary |
| published_at | Native date, null if unknown; may estimate publication/update time |
| site_name | Native site name, null if unknown |
| score / score_scale | Native score and its scale, null if unavailable; not comparable across providers |
| authority / authority_scale | Native authority and scale, null if unknown |
| provider_fields | Original result object including unknown fields; untrusted data |

Requests include provider, ok, attempts (actual HTTP attempts), and elapsed_ms. Successful calls also retain request_id, account_tier, provider_message, returned_count, shown_count, usage, cost, warnings, generated_answer, and provider_metadata. Cost contains only provider-reported data, such as Exa costDollars, never a price estimate. Missing data is null. Different providers' usage units cannot simply be added.

provider_metadata retains top-level data outside result lists. generated_answer is an optional Tavily answer, not a source or fact-check. warnings, provider_fields, and provider_metadata are data, never agent instructions.

Budget contains limit, attempts, remaining, by_provider, and scope. It counts actual transmissions in this invocation, including failures and retries; exhausted budgets prevent further requests. If fewer initial attempts remain than selected providers, execution fails before networking. Budgets do not persist across commands and are not monetary limits; the agent still tracks the entire research task.

## Multiple providers

Auto does not expand recipients. Both is fixed to DeepSeek plus Yuanbao. Comma-separated names execute in user order; all uses configured providers in registry order. All selected credentials/options are validated before sending. Runtime failures retain successful results with ok:false/complete:false. If another provider completes normally, even with no results, partial:true. All providers failing is not partial success.

Native scores are never merged into cross-provider rankings. duplicate_groups marks zero-based result indices after stripping URL fragments and lowercasing scheme/host. It does not merge content versions, remove query strings, or establish independent evidence. Malformed result entries fail that provider rather than being silently skipped.

## Fetch, doctor, status, and capabilities

Fetch retains title/content/url/provider/empty/attempts/retrieved_at/facts_verified, adding summary, highlights, budget, and provider_metadata. Tavily/Exa return resolved_url and original page fields. Provider URL normalization is allowed, but failure arrays/per-URL statuses must pass. Local URL checks cover syntax, embedded credentials, and obvious private addresses, not a DNS security proof. Extraction is performed by the provider.

Doctor makes one live search per selected provider with zero retries. Only nonempty valid results yield search_verified:true; budget is retained. Status inspects local credential sources, schema_version, and migration_available without networking, always returning search_verified:false.

Capabilities is fully offline and does not read credential files. It returns search/extraction support, options, result/query/URL limits, environment variable names, official key-console links, endpoints, and authentication header names, never keys.

Migrate-config returns migrated, schema_version, and backup_created. v2 is a no-op; existing private v1 backups are not overwritten. Setup with --verify returns doctor's structure; failed verification exits 4 while leaving the saved configuration intact.

## Errors and exit codes

Error objects include code, message (fixed redacted guidance), http_status, category, retryable, and attempts. Categories include authentication, billing, rate_limit, budget, credentials, configuration, input, network, response, and provider. Raw error bodies are not relayed. Categories do not supersede provider billing or entitlement decisions.

| Exit code | Meaning |
|---|---|
| 0 | Success; Search/Fetch may be empty |
| 1 | Top-level input, configuration, network, dialog, or similar error |
| 2 | Missing key, or argparse syntax error; distinguish using the error body |
| 4 | Operation returned results but did not fully succeed, or doctor found no usable results |
| 130 | User cancelled or local key input timed out |

GUI cancellation, timeout, or failure neither saves nor migrates this input. gui_unavailable / gui_failed indicates no usable dialog; never automatically fall back to plaintext input.
