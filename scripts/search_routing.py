"""Offline route planning. The calling Agent evaluates relevance and evidence."""
from copy import copy
import re

from search_common import SearchError, invalid
from search_providers import REGISTRY
from public_providers import PUBLIC_REGISTRY
from public_access import pause_status
from browser_search import available as browser_available

ALL = {**REGISTRY, **PUBLIC_REGISTRY}
STRATEGIES = ("smart", "quality", "balanced", "free")
PLATFORMS = {"github": "github.com", "hackernews": "news.ycombinator.com", "zhihu": "zhihu.com",
             "xiaohongshu": "xiaohongshu.com", "weibo": "weibo.com", "wikipedia": "en.wikipedia.org",
             "stackexchange": "stackoverflow.com", "arxiv": "arxiv.org", "crossref": "doi.org",
             "npm": "npmjs.com", "crates": "crates.io", "gitlab": "gitlab.com", "europepmc": "europepmc.org",
             "huggingface": "huggingface.co", "youtube": "youtube.com", "bilibili": "bilibili.com",
             "reddit": "reddit.com", "twitter": "x.com", "v2ex": "v2ex.com", "douban": "douban.com"}
NATIVE_PLATFORMS = {k: k for k in PLATFORMS if k in PUBLIC_REGISTRY and PUBLIC_REGISTRY[k].supports_search}


def platform_catalog(platform=None):
    """Declarations only: do not execute another program, read credentials or probe a site."""
    import shutil
    rows = []
    for name, domain in PLATFORMS.items():
        if platform and name != platform: continue
        source = NATIVE_PLATFORMS.get(name)
        adapter = PUBLIC_REGISTRY.get(source)
        rows.append({"platform": name, "default_domain": domain, "native_provider": source,
                     "coverage": "native_public_api" if source else "public_index_only",
                     "search_scope": adapter.capabilities()["search_scope"] if adapter else "public_web_index_not_site_search",
                     "native_fetch": bool(adapter and adapter.fetch_endpoint),
                     "generic_fetch_may_help": True, "comment_threads_integrated": False, "transcripts_integrated": False,
                     "live_verified": False})
    return {"platforms": rows, "local_tools": [
        {"name": name, "present": bool(shutil.which(name)), "role": role,
         "live_verified": False, "automatic_execution": False} for name, role in (
            ("agent-reach", "optional platform reading, comments or video/subtitle workflows; inspect channels and its Skill first"),
            ("yt-dlp", "optional video metadata/subtitles; executable presence does not establish website access"),
            ("gh", "optional GitHub operations within existing authorization"),
            ("agent-browser", "optional existing browser workflow within user authorization"))],
            "network_requests": 0, "note": "Capabilities and executable presence only; no login, setup, update or tool execution."}
DEFAULTS = {"strategy": "smart", "max_sources": 3, "disabled_providers": [], "browser": "auto"}


def query_intent(query, requested="auto"):
    if requested != "auto": return requested
    if re.search(r"最新|近期|最近|截至|当前|\b(?:latest|recent|current|as of|LTS)\b", query, re.I):
        return "current"
    if re.search(r"官方|文档|收费|计费|\b(?:documentation|docs|official|pricing|billing|API)\b", query, re.I):
        return "reference"
    return "general"


def preferences(config):
    return {**DEFAULTS, **config.get("search_preferences", {})}


def validate_preferences(value):
    if (not isinstance(value, dict) or value.get("strategy", "smart") not in STRATEGIES
            or type(value.get("max_sources", 3)) is not int or not 1 <= value.get("max_sources", 3) <= 3
            or value.get("browser", "auto") not in ("auto", "off")
            or not isinstance(value.get("disabled_providers", []), list)
            or any(p not in ALL for p in value.get("disabled_providers", []))):
        raise SearchError("invalid_config", "Invalid search preferences; original config was not changed.")


def scoped_args(args):
    scoped = copy(args)
    platform = getattr(args, "platform", None)
    if platform:
        domain = PLATFORMS[platform]
        if platform == "wikipedia":
            domain = ("zh.wikipedia.org" if getattr(args, "language", None) == "zh" or
                      (not getattr(args, "language", None) and re.search(r"[\u3400-\u9fff]", args.query)) else "en.wikipedia.org")
        if platform in ("wikipedia", "stackexchange") and getattr(args, "site", None):
            if args.site not in PUBLIC_REGISTRY[platform].sites:
                invalid("Unsupported site for this platform; inspect capabilities.")
            domain = args.site
        if getattr(args, "site", None) and args.site != domain:
            invalid("--site conflicts with --platform; use one target scope.")
        scoped.site = domain
    return scoped


def plan(args, config, credential, *, fetch=False):
    scoped = scoped_args(args)
    intent = "reading" if fetch else query_intent(args.query, getattr(args, "intent", "auto"))
    prefs = preferences(config)
    browser_mode = getattr(args, "browser", None) or prefs["browser"]
    requested_strategy = getattr(args, "strategy", None) or prefs["strategy"]
    if requested_strategy not in STRATEGIES: invalid("Unknown search strategy.")
    requested = getattr(args, "provider", "auto")
    disabled = prefs["disabled_providers"]
    available = []
    for name in REGISTRY:
        if name in disabled: continue
        try:
            credential(name, config)
            available.append(name)
        except SearchError as exc:
            if exc.code not in ("missing_api_key", "invalid_key"): raise
    preferred = config.get("default_provider")
    if preferred in available:
        available.remove(preferred); available.insert(0, preferred)
    strategy = requested_strategy
    if strategy == "smart": strategy = "quality" if available else "free"
    if strategy == "quality" and not available: strategy = "free"
    explicit = requested != "auto"
    if explicit:
        if requested == "both": candidates = ["deepseek", "yuanbao"]
        elif requested == "all":
            candidates = []
            for name in REGISTRY:
                try: credential(name, config)
                except SearchError as exc:
                    if exc.code != "missing_api_key": raise
                else: candidates.append(name)
            if not candidates:
                raise SearchError("missing_api_key", "all selects configured keyed services; use auto for keyless search.")
        else: candidates = requested.split(",")
        if "browser" in candidates and getattr(args, "browser", None) == "off":
            invalid("--browser off conflicts with an explicitly selected browser source.")
        if len(set(candidates)) != len(candidates) or any(p not in ALL for p in candidates):
            invalid("Use registered provider names without duplicates.")
        # Explicit source selection overrides a saved mode. An explicit free flag remains a hard boundary.
        if getattr(args, "strategy", None) == "free" and any(ALL[p].requires_key for p in candidates):
            invalid("--strategy free conflicts with a keyed provider. Remove the keyed provider or change this invocation's strategy.")
    else:
        public = ["jina", "exa-free"] if fetch else ["exa-free", "bing", "duckduckgo"]
        specialized = None
        if fetch:
            from urllib.parse import urlsplit
            host = urlsplit(args.url).hostname
            if host == "github.com" and len(urlsplit(args.url).path.strip("/").split("/")) == 2:
                specialized = "github"
            elif host == "news.ycombinator.com": specialized = "hackernews"
            keyed = [p for p in available if ALL[p].fetch_endpoint]
            # Known-URL reading prefers existing/native readers in the Skill, then these keyless readers.
            candidates = public if strategy == "free" else public[:1] + keyed + public[1:]
        else:
            site = getattr(scoped, "site", None)
            specialized = NATIVE_PLATFORMS.get(getattr(scoped, "platform", None))
            if not specialized:
                for target, source in NATIVE_PLATFORMS.items():
                    domains = getattr(PUBLIC_REGISTRY[source], "sites", (PLATFORMS[target],))
                    if site in domains:
                        specialized = source
                        break
            candidates = (available[:1] + public[:1] + available[1:] + public[1:] if strategy == "quality" else
                          public[:1] + available + public[1:] if strategy == "balanced" else public)
        if specialized: candidates.insert(0, specialized)
        if not fetch and browser_mode == "auto" and browser_available(): candidates.append("browser")
        if preferred in candidates and preferred not in disabled and not specialized:
            candidates.remove(preferred); candidates.insert(0, preferred)
        candidates = list(dict.fromkeys(p for p in candidates if p not in disabled))
    eligible, skipped, unavailable = [], [], []
    for name in candidates:
        provider = ALL[name]
        if not explicit and name in ("exa-free", "duckduckgo", "browser"):
            pause = pause_status(name)
            if pause:
                unavailable.append({"provider": name, **pause})
                continue
        try:
            if fetch:
                if getattr(args, "max_characters", None) is not None and name not in ("jina", "exa-free"):
                    raise SearchError("unsupported_option", "Source does not support adjustable reading length.")
                if not provider.fetch_endpoint:
                    raise SearchError("unsupported_operation", "Source does not read URLs.")
                payload = provider.fetch_payload(scoped)
            else:
                if not provider.supports_search:
                    raise SearchError("unsupported_operation", "Source only reads URLs.")
                payload = provider.search_payload(scoped)
            if provider.requires_key: credential(name, config)
        except SearchError as exc:
            if explicit: raise
            skipped.append({"provider": name, "code": exc.code})
            continue
        eligible.append({"provider": name, "payload": payload})
    if not eligible:
        raise SearchError("no_compatible_provider", "No enabled source supports these constraints; inspect capabilities or simplify the request.")
    limit = getattr(args, "max_sources", None) or prefs["max_sources"]
    if type(limit) is not int or not 1 <= limit <= 3: invalid("--max-sources must be 1..3.")
    names = [x["provider"] for x in eligible]
    execution = names if explicit else names[:limit]
    if not explicit and "browser" in names and limit > 1 and preferred != "browser" and specialized != "github":
        execution = [p for p in names if p != "browser"][:limit - 1] + ["browser"]
    return {"requested_strategy": requested_strategy, "strategy": strategy, "automatic": not explicit,
            "selection_basis": "capabilities, target scope, configured default, access policy and bounded task-intent complement; no universal quality ranking",
            "candidates": names, "execution_candidates": execution, "skipped_incompatible": skipped,
            "skipped_unavailable": unavailable, "browser_mode": browser_mode,
            "browser_slot_policy": "api_priority_for_github" if not explicit and specialized == "github" else "failure_fallback",
            "max_sources": len(eligible) if explicit else limit,
            "payloads": {x["provider"]: x["payload"] for x in eligible},
            "platform": getattr(args, "platform", None),
            "intent": intent, "specialized_source": specialized if not explicit else None,
            "complementary_timeout_seconds": 3,
            "complementary_search": (not fetch and not explicit and strategy == "quality"
                                     and intent in ("reference", "current") and not specialized
                                     and limit > 1 and len(execution) > 1
                                     and (execution[1] in REGISTRY or execution[1] == "exa-free")),
            "semantic_quality_verified": False}


def public_plan(value):
    return {k: v for k, v in value.items() if k != "payloads"}
