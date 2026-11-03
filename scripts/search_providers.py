"""Fixed official endpoints and provider-specific adapters; no credentials on disk."""
from datetime import date
import json
import math
import re
import urllib.parse
import urllib.request

from search_common import SearchError, invalid, public_url, text_field, text_list, validate_site

SEARCH_OPTIONS = ("site", "freshness", "industry", "mode", "need_content", "start_date", "end_date",
                  "country", "language", "extra_snippets", "highlights", "summary", "include_answer", "depth")


def option(args, name):
    return getattr(args, name, None)


def dates(args):
    start, end = option(args, "start_date"), option(args, "end_date")
    for value in (start, end):
        if value:
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                    raise ValueError
                date.fromisoformat(value)
            except ValueError:
                invalid("Dates must be valid YYYY-MM-DD values.")
    if start and end and start > end:
        invalid("--start-date must not be later than --end-date.")
    return start, end


def result(provider, rank, item, *, title="title", snippet="snippet", summary=None,
           content=None, published=None, site=None, score=None, score_scale=None,
           authority=None, authority_scale=None, highlights=None):
    if not isinstance(item, dict):
        raise SearchError("invalid_response", "Result must be an object.")
    url = text_field(item, "url")
    if not public_url(url):
        raise SearchError("invalid_response", "Result URL is not a public HTTP(S) URL.")
    body = text_field(item, content, optional=True) if content else ""
    pieces = text_list(item, highlights) if highlights else []
    return {"provider": provider, "rank": rank, "title": text_field(item, title), "url": url,
            "snippet": text_field(item, snippet, optional=True) if snippet else "",
            "summary": text_field(item, summary, optional=True) if summary else "",
            "content": body, "highlights": pieces,
            "content_kind": "page_content" if body else "excerpts" if pieces else "search_summary",
            "published_at": item.get(published) or None if published else None,
            "site_name": item.get(site) or None if site else None,
            "score": item.get(score) if score else None, "score_scale": score_scale,
            "authority": item.get(authority) if authority else None, "authority_scale": authority_scale,
            "provider_fields": item}


def array(body, field):
    if not isinstance(body, dict) or not isinstance(body.get(field), list):
        raise SearchError("invalid_response", "Expected provider result array: " + field)
    return body[field]


class Provider:
    name = label = endpoint = key_url = ""
    env_keys = ()
    auth_header, auth_prefix, method = "Authorization", "Bearer ", "POST"
    fetch_endpoint = None
    fetch_url_limit = 8192
    setup_hint = ""
    options = frozenset()
    max_count, query_limit, query_unit = 50, 4096, "characters"
    requires_key = True
    supports_search = True

    def capabilities(self):
        return {"provider": self.name, "label": self.label, "search": self.supports_search,
                "requires_key": self.requires_key,
                "fetch": bool(self.fetch_endpoint), "search_content": "need_content" in self.options,
                "site": "site" in self.options,
                "time_filters": sorted(self.options & {"freshness", "start_date", "end_date"}),
                "language": "language" in self.options, "country": "country" in self.options,
                "options": sorted(self.options), "count": {"min": 1, "max": self.max_count},
                "query_limit": {"value": self.query_limit, "unit": self.query_unit,
                                "scope": "adapter limit; may be stricter than the service"},
                "fetch_url_limit": self.fetch_url_limit,
                "environment_variables": list(self.env_keys), "key_url": self.key_url,
                "endpoint": self.endpoint, "fetch_endpoint": self.fetch_endpoint,
                "auth_header": self.auth_header, "method": self.method}

    def decode_response(self, raw):
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeError):
            raise SearchError("invalid_response", "Provider returned invalid JSON.") from None
        if not isinstance(data, dict):
            raise SearchError("invalid_response", "Expected a JSON object.")
        return data

    def validate_query(self, query):
        if not isinstance(query, str) or not query.strip():
            invalid("Query must not be empty.")
        length = len(query.encode("utf-8")) if self.query_unit == "utf8_bytes" else len(query)
        if length > self.query_limit:
            invalid("%s query exceeds %s %s; split the query." % (self.label, self.query_limit, self.query_unit))

    def search_payload(self, args):
        self.validate_query(args.query)
        if type(args.count) is not int or not 1 <= args.count <= self.max_count:
            invalid("%s --count must be 1..%s; no automatic pagination." % (self.label, self.max_count))
        validate_site(option(args, "site"))
        for name in SEARCH_OPTIONS:
            value = option(args, name)
            if value is not None and value is not False and value != "" and name not in self.options:
                raise SearchError("unsupported_option", "%s does not support --%s." % (self.label, name.replace("_", "-")))
        return self.build_search(args)

    def build_request(self, payload, key, version, *, fetch=False):
        endpoint = self.fetch_endpoint if fetch else self.endpoint
        if not endpoint:
            raise SearchError("unsupported_operation", self.label + " does not support fetch.")
        method = "POST" if fetch else self.method
        headers = {self.auth_header: self.auth_prefix + key, "User-Agent": "xcoze-search/" + version,
                   "Accept": "application/json"}
        if method == "GET":
            endpoint += "?" + urllib.parse.urlencode(payload)
            data = None
        else:
            headers["Content-Type"] = "application/json; charset=utf-8"
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return urllib.request.Request(endpoint, data=data, headers=headers, method=method)

    def check_error(self, raw):
        if "error" in raw or "Error" in raw:
            raise SearchError("provider_error", "Provider returned an application error.")

    def metadata(self, raw, rows, count):
        return {"request_id": raw.get("request_id") or raw.get("requestId"),
                "account_tier": None, "provider_message": None, "usage": raw.get("usage"),
                "cost": {"currency": "USD", "reported": raw["costDollars"]} if "costDollars" in raw else None,
                "warnings": raw.get("warnings", []), "generated_answer": raw.get("answer"),
                "provider_metadata": {k: v for k, v in raw.items() if k not in (
                    "results", "Pages", "web", "data", "Response", "title", "content", "raw_content", "text")},
                "returned_count": len(rows), "shown_count": min(len(rows), count)}

    def fetch_payload(self, args):
        raise SearchError("unsupported_operation", self.label + " does not support fetch.")


class DeepSeek(Provider):
    name, label = "deepseek", "DeepSeek"
    env_keys, key_url = ("DEEPSEEK_API_KEY",), "https://platform.deepseek.com/api_keys"
    endpoint, fetch_endpoint = "https://api.deepseek.com/v1/tools/search", "https://api.deepseek.com/v1/tools/fetch"
    options, query_limit = frozenset(("site", "need_content")), 128

    def build_search(self, args):
        query = args.query + (" site:" + args.site if option(args, "site") else "")
        self.validate_query(query)
        return {"query": query, "count": args.count, "need_content": bool(option(args, "need_content"))}

    def normalize(self, raw, count):
        rows = [result(self.name, i, item, summary="summary", content="content", published="date",
                       site="site_name", score="rerank_score", score_scale="deepseek_0_3",
                       authority="authority", authority_scale="deepseek_-1_4")
                for i, item in enumerate(array(raw, "results"), 1)]
        return rows[:count], self.metadata(raw, rows, count)

    def fetch_payload(self, args):
        if option(args, "highlights") or option(args, "summary"):
            raise SearchError("unsupported_option", "DeepSeek fetch does not support --highlights/--summary.")
        return {"url": args.url}

    def normalize_fetch(self, raw, url):
        return {"title": text_field(raw, "title"), "content": text_field(raw, "content"),
                "summary": "", "highlights": []}


class Yuanbao(Provider):
    name, label = "yuanbao", "腾讯元宝搜索"
    env_keys = ("YUANBAO_API_KEY", "TENCENTCLOUD_WSA_APIKEY")
    key_url, endpoint = "https://console.cloud.tencent.com/wsapi/index", "https://api.wsa.cloud.tencent.com/SearchPro"
    options = frozenset(("site", "freshness", "industry", "mode"))
    query_limit, query_unit = 1500, "utf8_bytes"
    setup_hint = "先开通元宝搜索，再在概览 > 服务 API KEY 方式创建密钥（不是腾讯云 SecretKey）。"

    def build_search(self, args):
        payload = {"Query": args.query}
        if args.count > 10:
            payload["Cnt"] = int(math.ceil(args.count / 10) * 10)
        for field, target in (("site", "Site"), ("industry", "Industry")):
            if option(args, field):
                payload[target] = option(args, field)
        if option(args, "freshness"):
            match = re.fullmatch(r"([dmy])(\d+)", args.freshness)
            if not match or not 1 <= int(match[2]) <= {"d": 30, "m": 12, "y": 5}[match[1]]:
                invalid("Yuanbao --freshness supports d1..d30/m1..m12/y1..y5.")
            payload["Freshness"] = args.freshness
        if option(args, "industry") and args.industry not in ("gov", "news", "acad", "finance"):
            invalid("Invalid Yuanbao industry.")
        if option(args, "mode") is not None:
            if type(args.mode) is not int or args.mode not in (0, 1, 2):
                invalid("--mode must be 0, 1, or 2.")
            payload["Mode"] = args.mode
        return payload

    def check_error(self, raw):
        body = raw.get("Response", raw)
        if isinstance(body, dict) and "Error" in body:
            error = body["Error"]
            code = error.get("Code") if isinstance(error, dict) else None
            root = code.split(".")[0] if isinstance(code, str) else ""
            known = {"InternalError", "RequestLimitExceeded", "UnauthorizedOperation", "ResourceNotFound",
                     "ResourceUnavailable", "InvalidParameter", "InvalidParameterValue"}
            safe = code if root in known and re.fullmatch(r"[A-Za-z0-9_.]{1,100}", code) else "provider_error"
            raise SearchError(safe, "Yuanbao rejected the request; check service, quota and parameters.",
                              retryable=root in ("InternalError", "RequestLimitExceeded"))
        super().check_error(raw)

    def normalize(self, raw, count):
        body = raw.get("Response")
        rows = []
        for i, item in enumerate(array(body, "Pages"), 1):
            if isinstance(item, str):
                try:
                    item = json.loads(item)
                except ValueError:
                    raise SearchError("invalid_response", "Yuanbao Pages contains invalid JSON.") from None
            rows.append(result(self.name, i, item, snippet="passage", summary="content", published="date", site="site",
                               score="score", score_scale="yuanbao_0_1", authority="authority_level", authority_scale="yuanbao_0_5"))
        meta = self.metadata(body, rows, count)
        meta.update(request_id=body.get("RequestId"), account_tier=body.get("Version"), provider_message=body.get("Msg"))
        return rows[:count], meta


class Tavily(Provider):
    name, label = "tavily", "Tavily"
    env_keys, key_url = ("TAVILY_API_KEY",), "https://app.tavily.com/home"
    endpoint, fetch_endpoint = "https://api.tavily.com/search", "https://api.tavily.com/extract"
    max_count = 20
    options = frozenset(("site", "start_date", "end_date", "freshness", "need_content", "include_answer", "depth"))

    def build_search(self, args):
        depth = option(args, "depth") or "basic"
        if depth not in ("basic", "advanced", "fast", "ultra-fast"):
            invalid("Unsupported Tavily depth.")
        payload = {"query": args.query, "max_results": args.count, "search_depth": depth,
                   "include_answer": bool(option(args, "include_answer")),
                   "include_raw_content": "markdown" if option(args, "need_content") else False,
                   "auto_parameters": False, "include_usage": True, "include_published_date": True}
        if option(args, "site"):
            payload["include_domains"] = [args.site]
        start, end = dates(args)
        for value, name in ((start, "start_date"), (end, "end_date")):
            if value:
                payload[name] = value
        if option(args, "freshness"):
            if args.freshness not in ("day", "week", "month", "year", "d", "w", "m", "y"):
                invalid("Tavily --freshness uses day/week/month/year (or d/w/m/y).")
            if start or end:
                invalid("Use Tavily relative freshness or date bounds, not both.")
            payload["time_range"] = args.freshness
        if start or end or option(args, "freshness"):
            payload["filter_by_published_date"] = True
        return payload

    def normalize(self, raw, count):
        rows = [result(self.name, i, item, snippet="content", content="raw_content", published="published_date",
                       score="score", score_scale="tavily_native") for i, item in enumerate(array(raw, "results"), 1)]
        return rows[:count], self.metadata(raw, rows, count)

    def fetch_payload(self, args):
        if option(args, "highlights") or option(args, "summary"):
            raise SearchError("unsupported_option", "Tavily extract does not support --highlights/--summary.")
        return {"urls": [args.url], "extract_depth": "basic", "format": "markdown", "include_usage": True}

    def normalize_fetch(self, raw, url):
        rows = array(raw, "results")
        failures = raw.get("failed_results", [])
        if (not isinstance(failures, list) or failures or len(rows) != 1
                or not isinstance(rows[0], dict) or not public_url(rows[0].get("url"))):
            raise SearchError("extraction_failed", "Tavily did not successfully extract the requested URL.")
        return {"title": text_field(rows[0], "title", optional=True),
                "content": text_field(rows[0], "raw_content"), "summary": "", "highlights": [],
                "resolved_url": rows[0]["url"], "provider_fields": rows[0]}


class Exa(Provider):
    name, label = "exa", "Exa"
    env_keys, key_url = ("EXA_API_KEY",), "https://dashboard.exa.ai/api-keys"
    auth_header, auth_prefix = "x-api-key", ""
    endpoint, fetch_endpoint = "https://api.exa.ai/search", "https://api.exa.ai/contents"
    options = frozenset(("site", "start_date", "end_date", "need_content", "highlights", "summary"))
    fetch_url_limit = 2048

    def build_search(self, args):
        payload = {"query": args.query, "numResults": args.count, "type": "auto"}
        if option(args, "site"):
            payload["includeDomains"] = [args.site]
        start, end = dates(args)
        if start:
            payload["startPublishedDate"] = start + "T00:00:00.000Z"
        if end:
            payload["endPublishedDate"] = end + "T23:59:59.999Z"
        content = {}
        for flag, target in (("need_content", "text"), ("highlights", "highlights")):
            if option(args, flag):
                content[target] = True
        if option(args, "summary"):
            content["summary"] = {"query": args.query}
        if content:
            payload["contents"] = content
        return payload

    def normalize(self, raw, count):
        warnings = raw.get("warnings") or []
        if not isinstance(warnings, list):
            raise SearchError("invalid_response", "Invalid Exa warnings.")
        if any(isinstance(w, dict) and w.get("code") == "IGNORED_FIELD" for w in warnings):
            raise SearchError("constraint_not_applied", "Exa reported an ignored request field; adjust the options.")
        rows = [result(self.name, i, item, snippet=None, summary="summary", content="text",
                       published="publishedDate", score="score", score_scale="exa_native", highlights="highlights")
                for i, item in enumerate(array(raw, "results"), 1)]
        return rows[:count], self.metadata(raw, rows, count)

    def fetch_payload(self, args):
        if len(args.url) > self.fetch_url_limit:
            invalid("Exa contents URL is limited to 2048 characters.")
        payload = {"urls": [args.url], "text": True}
        if option(args, "highlights"):
            payload["highlights"] = True
        if option(args, "summary"):
            payload["summary"] = {}
        return payload

    def normalize_fetch(self, raw, url):
        rows = array(raw, "results")
        statuses = raw.get("statuses", [])
        if (not isinstance(statuses, list) or any(not isinstance(s, dict) or s.get("status") != "success" for s in statuses)
                or len(rows) != 1 or not isinstance(rows[0], dict) or not public_url(rows[0].get("url"))
                or "error" in rows[0]):
            raise SearchError("extraction_failed", "Exa did not successfully extract the requested URL.")
        return {"title": text_field(rows[0], "title", optional=True), "content": text_field(rows[0], "text", optional=True),
                "summary": text_field(rows[0], "summary", optional=True), "highlights": text_list(rows[0], "highlights"),
                "resolved_url": rows[0]["url"], "provider_fields": rows[0]}


class Brave(Provider):
    name, label = "brave", "Brave Search"
    env_keys, key_url = ("BRAVE_API_KEY",), "https://api-dashboard.search.brave.com/app/keys"
    endpoint, method = "https://api.search.brave.com/res/v1/web/search", "GET"
    auth_header, auth_prefix = "X-Subscription-Token", ""
    max_count, query_limit = 20, 600
    options = frozenset(("site", "freshness", "country", "language", "extra_snippets"))

    def validate_query(self, query):
        super().validate_query(query)
        if len(query.split()) > 75:
            invalid("Brave queries are limited to 75 words.")

    def build_search(self, args):
        query = args.query + (" site:" + args.site if option(args, "site") else "")
        self.validate_query(query)
        payload = {"q": query, "count": args.count, "result_filter": "web"}
        if option(args, "freshness"):
            value = args.freshness
            if value not in ("pd", "pw", "pm", "py"):
                parts = value.split("to")
                if len(parts) != 2:
                    invalid("Brave freshness uses pd/pw/pm/py or YYYY-MM-DDtoYYYY-MM-DD.")
                for part in parts:
                    try:
                        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", part):
                            raise ValueError
                        date.fromisoformat(part)
                    except ValueError:
                        invalid("Invalid Brave freshness date range.")
                if parts[0] > parts[1]:
                    invalid("Invalid Brave freshness date order.")
            payload["freshness"] = value
        country, language = option(args, "country"), option(args, "language")
        if country:
            if not re.fullmatch(r"[A-Za-z]{2}", country):
                invalid("Brave country must be a two-letter country code.")
            payload["country"] = country.upper()
        if language:
            if not re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z]{2,4})?", language):
                invalid("Invalid Brave search language code.")
            payload["search_lang"] = language
        if option(args, "extra_snippets"):
            payload["extra_snippets"] = "true"
        return payload

    def normalize(self, raw, count):
        body = raw.get("web")
        if body is None and isinstance(raw.get("query"), dict):
            body = {"results": []}
        rows = [result(self.name, i, item, snippet="description", published="page_age")
                for i, item in enumerate(array(body, "results"), 1)]
        for row in rows:
            row["extra_snippets"] = text_list(row["provider_fields"], "extra_snippets")
        return rows[:count], self.metadata(raw, rows, count)


class Bocha(Provider):
    name, label = "bocha", "博查"
    env_keys, key_url = ("BOCHA_API_KEY",), "https://open.bochaai.com/"
    endpoint = "https://api.bochaai.com/v1/web-search"
    options = frozenset(("freshness", "summary"))

    def build_search(self, args):
        freshness = option(args, "freshness") or "noLimit"
        if freshness not in ("noLimit", "oneDay", "oneWeek", "oneMonth", "oneYear"):
            parts = freshness.split("..")
            if len(parts) not in (1, 2):
                invalid("Invalid Bocha freshness.")
            for part in parts:
                try:
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", part):
                        raise ValueError
                    date.fromisoformat(part)
                except ValueError:
                    invalid("Bocha freshness uses noLimit/oneDay/oneWeek/oneMonth/oneYear or ISO dates.")
            if len(parts) == 2 and parts[0] > parts[1]:
                invalid("Invalid Bocha freshness date order.")
        return {"query": args.query, "count": args.count, "freshness": freshness,
                "summary": bool(option(args, "summary"))}

    def check_error(self, raw):
        code = raw.get("code")
        if code is not None and (type(code) is not int or code != 200):
            status = code if type(code) is int and code in (400, 401, 402, 403, 429, 500, 503) else None
            raise SearchError("provider_error", "Bocha returned an application error; check account and parameters.",
                              status=status, retryable=status in (429, 500, 503))
        super().check_error(raw)

    def normalize(self, raw, count):
        body = raw.get("data")
        if not isinstance(body, dict):
            raise SearchError("invalid_response", "Expected Bocha data object.")
        pages = body.get("webPages")
        if pages is None and isinstance(body.get("queryContext"), dict):
            pages = {"value": []}
        rows = [result(self.name, i, item, title="name", summary="summary", published="datePublished", site="siteName")
                for i, item in enumerate(array(pages, "value"), 1)]
        meta = self.metadata(raw, rows, count)
        meta["request_id"] = raw.get("log_id") or raw.get("requestId") or body.get("requestId")
        meta["provider_metadata"]["data_metadata"] = {k: v for k, v in body.items() if k != "webPages"}
        return rows[:count], meta


REGISTRY = {provider.name: provider for provider in (DeepSeek(), Yuanbao(), Tavily(), Exa(), Brave(), Bocha())}


def get_provider(name):
    try:
        return REGISTRY[name]
    except KeyError:
        invalid("Unknown provider; use capabilities to list supported services.")
