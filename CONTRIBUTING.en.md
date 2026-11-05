# Contributing

[简体中文](CONTRIBUTING.md) | **English**

Bug fixes, documentation, regression cases, and provider adapters are welcome.

## Keyless adapters and routing

Keyless adapters live in scripts/public_providers.py and PUBLIC_REGISTRY, sharing the Provider contract with requires_key:false and no access to other credentials. Decode JSON/SSE/RSS/HTML through decode_response and never treat challenge pages as empty successes. Scripts/search_routing.py plans capabilities/preferences offline; the Agent assesses semantics. Cover free-mode key exclusion, explicit precedence, retained constraints, budgets and recovery. Add runtime/tests to build_release.py and update both document languages.

## Report a problem

Use [GitHub Issues](https://github.com/wjason/xcoze-search/issues) to describe the environment, version, command, expected behavior, and actual result. Include only error codes, redacted RequestIds, and necessary output. Never upload API keys, credential files, or private queries.

New-provider proposals should link official documentation and explain needed features/authentication; check the [roadmap](TODO.en.md) first. Discuss compatibility in an Issue before changing commands, configuration, or output formats.

## Local development

Python 3.10+ is required. Runtime and offline tests use only the standard library.

```bash
git clone https://github.com/wjason/xcoze-search.git
cd xcoze-search
python3 -m unittest discover -s tests -v
```

Work on a branch and open a Pull Request against main. Describe the problem, user-visible behavior, and validation.

## Add a provider

In scripts/search_providers.py, subclass Provider. Define name/label, fixed official endpoints, env_keys/key_url, authentication, capabilities, and limits. Implement build_search and normalize; add fetch_payload/normalize_fetch only if extraction exists. Register the instance in REGISTRY. Brave demonstrates GET/specialized authentication, and Tavily/Exa demonstrate search plus extraction.

The search loop uses the registry without provider-specific branches. Shared errors, URL/field validation, and HTTP budgets live in search_common.py; credential resolution, transport, and CLI live in xcoze_search.py. Reject unsupported options before networking. Never substitute arbitrary URLs for authenticated fixed endpoints.

Use tests/test_providers.py as a protocol-test reference. Synthetic responses cover native requests/authentication, content types, empty results, application errors, unknown fields, and per-URL failures. QueueTransport exercises real request_api/normalization code rather than only mocking top-level return values. Regression tools/corpora are under evaluations/ and do not network by default.

Also:

- Implement against current official references with URLs and check dates. Distinguish official APIs, third-party proxies, and self-hosting.
- Declare supported search, page text, snippets, filters, and pagination; never silently drop unsupported options.
- Preserve sources, dates, native fields, and score semantics. Test empty results, failures, limits, and malformed responses.
- Keep keys in user configuration/process environment. Tests use synthetic credentials and temporary directories; live accounts are excluded from default CI.
- Update Skill instructions, README, provider references, tests, and changelog together. Document configuration migration compatibility and failure behavior.

See the [completion criteria](TODO.en.md#provider-completion-criteria).

When adding or changing a source, update its support status: run a live check, record sanitized results, then use `python3 evaluations/build_source_status.py --audit <sanitized-results.json>` to regenerate the bilingual tables, and update statuses shown in the source lists. Mark unchecked capabilities as not tested and update the candidate list when a source is integrated.

## Maintain both languages

README.md and existing Chinese files remain the default entry points; English counterparts use .en.md. Update commands, limits, verification state, versions, and links together. Keep agent language behavior consistent in SKILL.md and SKILL.en.md. Every page retains reciprocal language links, and release manifests include both versions.

## Documentation and releases

README covers user workflows; TODO holds plans; references hold evidence/contracts; CHANGELOG records version differences. Mark unimplemented features clearly, and separate offline validation from live verification.

Check documentation links, examples, and facts. Runtime changes need relevant tests. Update release manifests when adding files so installed documentation links remain valid.

Releases use immutable tags/source commits. Never replace published assets in place; use a new version. CHANGELOG's Unreleased section records unpublished changes.

Contributions are distributed under the project's [MIT License](LICENSE).
