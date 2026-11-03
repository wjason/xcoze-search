# Setup and troubleshooting

[简体中文](setup.md) | **English**

## Start without keys; optional preferences

Ordinary search needs no key setup. Install and ask normally; use the setup flow below only to add/replace a commercial service. Configured, enabled keys make default Smart quality-first. Saved free/balanced preferences retain precedence after adding a key.

The Agent saves preferences with `preferences --strategy free|balanced|quality`; the same search/fetch flag affects one call only. `preferences --reset` restores Smart and clears the default source while keeping keys. `preferences --disable <ID>` excludes an automatic source and `--enable` restores it. See [routing](routing.en.md). These commands neither print keys nor connect; users do not find config files.

## Conversational setup

Requests such as “Configure xcoze search,” “Configure Exa,” or “Replace my Yuanbao key” enter setup. The agent locates the script relative to SKILL.md; users should not have to find installation or configuration files.

1. Use status to inspect configuration and credential sources without displaying files. Confirm the target provider if unspecified. Use capabilities for its key_url and environment variables.
2. **Provide the official key-console link in chat for the user to open. Do not automatically open a browser, signup page, or payment page.** Users with a key do not need to create another. Never ask them to reply with the key.
3. Once ready, explain the local hidden-input dialog, permissions-protected plaintext storage, and the potentially billable verification search. If an environment variable exists, explain that it overrides the saved value; do not change it on the user's behalf.
4. Run one command for the selected provider. Replace the path with its actual absolute location. Provider IDs are deepseek/yuanbao/tavily/exa/brave/bocha.

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" capabilities --provider tavily
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider tavily --gui --verify
```

Add `--default` only when the user requests a default-provider change. Wait for input to finish. Cancellation neither saves nor migrates configuration, verifies access, nor automatically reopens the dialog. Report live success only for the target provider's search_verified:true. Failed verification leaves the saved credential in place; saving alone does not establish access.

Dialogs use AppleScript on macOS, PowerShell/WinForms on Windows, and existing Zenity on a Linux desktop. They time out after about five minutes. The tool does not read the clipboard or relay child-process input/error bodies to the agent. The dialog appears on the machine executing the script; use `--gui` remotely only when the user can access that desktop.

If no dialog is available, report gui_unavailable/gui_failed. Do not install desktop dependencies automatically or collect plaintext/chat input. Provide the actual script path for hidden input in the user's visible terminal, or use managed deployment variables. Never collect keys in an agent-captured PTY. Python 3.10+ remains required.

## Official consoles and credential types

| Provider | Official console | Environment variable |
|---|---|---|
| DeepSeek | [API keys](https://platform.deepseek.com/api_keys) | DEEPSEEK_API_KEY |
| Yuanbao | [Search console](https://console.cloud.tencent.com/wsapi/index) | YUANBAO_API_KEY; alias TENCENTCLOUD_WSA_APIKEY |
| Tavily | [Dashboard](https://app.tavily.com/home) | TAVILY_API_KEY |
| Exa | [Dashboard](https://dashboard.exa.ai/api-keys) | EXA_API_KEY |
| Brave | [Dashboard](https://api-dashboard.search.brave.com/app/keys) | BRAVE_API_KEY |
| Bocha | [Open platform](https://open.bochaai.com/) | BOCHA_API_KEY |

For Yuanbao, activate Search, then create a Search Service API Key under the overview's Service API KEY section. Tencent Cloud SecretId/SecretKey, Hunyuan, and unrelated product keys are not accepted. Chat subscriptions and API entitlements are separate; permissions, quotas, and product tiers are governed by each provider.

## Manual terminal setup

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider exa --verify
```

Without `--gui`, use hidden input only in the user's own visible terminal. Abort if input cannot be hidden. Windows may use `py -3`. `--verify` performs a potentially billable search; omitting it only saves. macOS retains `scripts/setup.command` for terminal setup with all six providers.

## Storage and migration

Precedence: the provider's environment variable, then this Skill's dedicated configuration file. Variables must be injected into the actual agent process; a new terminal's variables do not automatically reach an already-running assistant. The tool does not read .env files, other Skills, browser sessions, or application credentials.

The path is `${XDG_CONFIG_HOME:-~/.config}/xcoze-search/config.json` (shell notation only describes the path). Storage is **permissions-protected plaintext**. POSIX uses 700 for the dedicated directory and 600 for the file, rejecting symbolic links at those locations. XDG_CONFIG_HOME must be absolute. Windows inherits user-directory ACLs; manual ACL acceptance is pending. Configuration and backups are excluded from the repository and packages.

v0.4.0 retains schema_version:2 and reads v1 directly. Status, search, and doctor do not rewrite v1. To upgrade explicitly:

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" migrate-config
```

Migration exclusively creates a private `config.v1.backup.json` in the same directory before atomically replacing the configuration. Existing keys, default provider, and extension fields are retained, including non-default entries for providers not yet registered. Existing backups are never overwritten. Unknown formats, unsafe permissions, or migration failures stop the operation without overwriting the original credential file. Saving after successful input also backs up and upgrades v1; cancellation does not migrate. Migration on v2 is a no-op.

Older programs cannot read v2. Downgrading requires local inspection and restoration of the v1 backup, including checking that its keys are still valid. The backup is a pre-upgrade snapshot: keys added or replaced later are absent. There is no automatic rollback or provider-key revocation. Never paste backup contents into chat.

## Inspection and cleanup

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" status
python3 "<skill_dir>/scripts/xcoze_search.py" doctor --provider exa
python3 "<skill_dir>/scripts/xcoze_search.py" doctor --provider deepseek,tavily --max-requests 2
```

Status is offline and shows credential sources, schema, and migration availability; search_verified is always false. Doctor makes one live search per provider, with no retries or persistent success cache. Only nonempty valid results pass. Empty API results do not establish verification.

Uninstalling removes program files only. To remove credentials, locally remove this Skill's configuration/backup files, clear relevant environment variables, and revoke keys on official platforms. Deleting local files does not revoke provider keys.

| Symptom or code | Action |
|---|---|
| missing_api_key / invalid_key | Configure the correct key type for the target service; do not borrow credentials |
| interactive_required | Use the user's visible terminal or --gui on an accessible desktop |
| gui_unavailable / gui_failed | Use a visible terminal or managed variables; never chat/plaintext input |
| cancelled | Cancelled or timed out without saving; restart only when the user is ready |
| unsafe_config / invalid_config | Inspect permissions, symlinks, format, and backups locally; do not reveal files or relax permissions |
| unsupported_option / unsupported_operation | Inspect capabilities; split differing provider options without dropping constraints or switching services |
| budget_exhausted | No budget remains, or fewer attempts than providers; increase only within the user's/task's budget |
| HTTP 401/403 / UnauthorizedOperation | Check effective credentials, authorization, and service activation |
| HTTP 402/432/433 / ResourceUnavailable | Check balance, quota, and service state on the official platform; the user decides on payment |
| HTTP 429/434 / RequestLimitExceeded | Reduce frequency and honor bounded retries and budgets |
| ResourceNotFound | Activate Yuanbao Search in Tencent Cloud and allow activation to take effect |
| InvalidParameter* / HTTP 400/422 | Check parameters and tier; start Yuanbao with count<=10 and no industry/mode |
| constraint_not_applied | Exa reported an ignored field; adjust options and do not claim filtering succeeded |
| extraction_failed | The provider did not retrieve the requested page successfully; use another public source without bypassing controls |
| invalid_response / response_too_large | Record provider, code, time, and any redacted RequestId; never upload keys or raw error bodies |
| network_error / retry_later | Check networking, TLS, and system time; retry later |

Error messages are constrained and do not relay raw provider error bodies or arbitrary error messages.
