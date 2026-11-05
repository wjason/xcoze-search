"""Keyless public backends. No browser, SDK, account or implicit credentials."""
import base64
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from search_common import SearchError, invalid, public_url
from search_providers import Provider, array, dates, option, result


def clean_html(value):
    if value is not None and not isinstance(value, str):
        raise SearchError("invalid_response", "Expected HTML/text from public source.")
    class Text(HTMLParser):
        def __init__(self):
            super().__init__(); self.parts = []; self.hidden = 0
        def handle_starttag(self, tag, attrs):
            if tag in ("script", "style"): self.hidden += 1
            if tag in ("p", "br", "li", "div"): self.parts.append(" ")
        def handle_endtag(self, tag):
            if tag in ("script", "style"): self.hidden = max(0, self.hidden - 1)
        def handle_data(self, data):
            if not self.hidden: self.parts.append(data)
    parser = Text(); parser.feed(value or "")
    return " ".join("".join(parser.parts).split())


def domain_matches(url, domain):
    host = (urllib.parse.urlsplit(url).hostname or "").lower().rstrip(".")
    return host == domain.lower() or host.endswith("." + domain.lower())


def platform_item_type(platform, url):
    """Label index destinations; finding a profile does not mean a note/post was read."""
    parsed = urllib.parse.urlsplit(url)
    path = parsed.path
    if platform == "xiaohongshu" and domain_matches(url, "xiaohongshu.com"):
        if re.fullmatch(r"/user/profile/[^/]+/?", path): return "user_profile"
        if re.fullmatch(r"/(?:explore|discovery/item)/[^/]+/?", path): return "note_link"
        if path.rstrip("/") == "/search_result": return "platform_search"
        return "other_platform_page"
    if platform == "weibo" and domain_matches(url, "weibo.com"):
        if parsed.hostname == "s.weibo.com": return "platform_search"
        if re.fullmatch(r"/\d+/[A-Za-z0-9]+/?", path): return "post_link"
        if re.fullmatch(r"/(?:u/\d+|[A-Za-z0-9_]+)/?", path): return "profile_or_landing_page"
        return "other_platform_page"
    return None


def repo_parts(url):
    parsed = urllib.parse.urlsplit(url)
    parts = parsed.path.strip("/").split("/")
    if (parsed.hostname != "github.com" or len(parts) != 2
            or any(not re.fullmatch(r"[A-Za-z0-9_.-]+", p) or p in (".", "..") for p in parts)):
        invalid("GitHub reader accepts https://github.com/owner/repository and reads its default README only.")
    return parts[0], parts[1].removesuffix(".git")


class PublicProvider(Provider):
    requires_key = False
    auth_header = None
    method = "GET"
    max_count = 20
    availability = "network_dependent"

    def capabilities(self):
        return {**super().capabilities(), "access": "keyless", "availability": self.availability,
                "search_scope": getattr(self, "search_scope", "public_web"),
                "fetch_character_limit": ({"default": 24000, "min": 1000, "max": 200000}
                                          if self.name in ("jina", "exa-free") else None),
                "note": "No user key is sent; upstream access and limits still apply."}

    def build_request(self, payload, key, version, *, fetch=False):
        endpoint = self.fetch_endpoint if fetch else self.endpoint
        if not endpoint: invalid("Unsupported operation.")
        headers = {"User-Agent": "xcoze-search/" + version, "Accept": "application/json"}
        return urllib.request.Request(endpoint + "?" + urllib.parse.urlencode(payload), headers=headers)

    def metadata(self, raw, rows, count):
        metadata = super().metadata(raw, rows, count)
        metadata["provider_metadata"] = {k: v for k, v in metadata["provider_metadata"].items()
                                         if k not in ("mcp_text", "hits", "items")}
        return {**metadata, "access": "keyless", "user_api_key_used": False}


class BingRSS(PublicProvider):
    name, label = "bing", "Bing public RSS"
    endpoint = "https://www.bing.com/search"
    options = frozenset(("site",))
    max_count = 10
    availability = "experimental_public_feed"

    def build_search(self, args):
        query = args.query + (" site:" + args.site if option(args, "site") else "")
        self.validate_query(query)
        return {"q": query, "format": "rss"}

    def decode_response(self, raw):
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            raise SearchError("invalid_response", "Bing did not return a readable RSS feed.") from None
        if root.tag != "rss" or root.find("channel") is None:
            raise SearchError("invalid_response", "Expected a Bing RSS channel.")
        rows = [{"title": clean_html(item.findtext("title")), "url": item.findtext("link") or "",
                 "snippet": clean_html(item.findtext("description")), "rss_pub_date": item.findtext("pubDate")}
                for item in root.findall("./channel/item")]
        return {"results": rows}

    def normalize(self, raw, count):
        rows = [result(self.name, i, item) for i, item in enumerate(array(raw, "results"), 1)]
        return rows[:count], self.metadata(raw, rows, count)


class DuckDuckGo(PublicProvider):
    name, label = "duckduckgo", "DuckDuckGo public HTML"
    endpoint = "https://html.duckduckgo.com/html/"
    options = frozenset(("site",))
    availability = "experimental_public_html"

    def build_search(self, args):
        query = args.query + (" site:" + args.site if option(args, "site") else "")
        self.validate_query(query)
        return {"q": query}

    def decode_response(self, raw):
        text = raw.decode("utf-8", "replace")
        if any(marker in text.lower() for marker in ("anomaly.js", "challenge-form", "verify you are human")):
            raise SearchError("access_challenge", "DuckDuckGo returned a verification page; no results obtained.")
        class Results(HTMLParser):
            def __init__(self):
                super().__init__(); self.rows = []; self.field = None; self.tag = None; self.depth = 0
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs); classes = attrs.get("class", "").split()
                if tag == "a" and "result__a" in classes:
                    url = attrs.get("href", "")
                    if url.startswith("//"): url = "https:" + url
                    if domain_matches(url, "duckduckgo.com"):
                        url = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query).get("uddg", [""])[0]
                    self.rows.append({"url": url, "title": "", "snippet": ""})
                    self.field, self.tag, self.depth = "title", tag, 1
                elif "result__snippet" in classes and self.rows:
                    self.field, self.tag, self.depth = "snippet", tag, 1
                elif self.field and tag == self.tag: self.depth += 1
            def handle_endtag(self, tag):
                if self.field and tag == self.tag:
                    self.depth -= 1
                    if not self.depth: self.field = None
            def handle_data(self, data):
                if self.field: self.rows[-1][self.field] += data
        parser = Results(); parser.feed(text)
        rows = [{**r, "title": " ".join(r["title"].split()), "snippet": " ".join(r["snippet"].split())}
                for r in parser.rows if public_url(r["url"]) and r["title"].strip()]
        if not rows and "no-results" not in text.lower() and "no results found" not in text.lower():
            raise SearchError("invalid_response", "Unrecognized DuckDuckGo page; not a verified empty search.")
        return {"results": rows}

    normalize = BingRSS.normalize


class ExaFree(PublicProvider):
    name, label = "exa-free", "Exa hosted MCP (keyless)"
    endpoint = fetch_endpoint = "https://mcp.exa.ai/mcp"
    method = "POST"
    options = frozenset(("site",))
    availability = "official_rate_limited_trial"

    def build_search(self, args):
        query = args.query + (" site:" + args.site if option(args, "site") else "")
        self.validate_query(query)
        return {"tool": "web_search_exa", "arguments": {"query": query, "numResults": args.count}}

    def build_request(self, payload, key, version, *, fetch=False):
        data = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                "params": {"name": payload["tool"], "arguments": payload["arguments"]}}
        return urllib.request.Request(self.endpoint, data=json.dumps(data).encode(), headers={
            "Content-Type": "application/json", "Accept": "application/json, text/event-stream",
            "User-Agent": "xcoze-search/" + version})

    def decode_response(self, raw):
        try:
            text = raw.decode("utf-8")
            events = [line[5:].strip() for line in text.splitlines() if line.startswith("data:")]
            messages = [json.loads(line) for line in events if line and line != "[DONE]"] if events else [json.loads(text)]
            msg = next(m for m in reversed(messages) if isinstance(m, dict) and m.get("id") == 1)
        except (ValueError, UnicodeError, StopIteration):
            raise SearchError("invalid_response", "Invalid Exa MCP response.") from None
        body = msg.get("result")
        if "error" in msg or not isinstance(body, dict) or body.get("isError"):
            error = msg.get("error")
            message = str(error.get("message", ""))[:4000] if isinstance(error, dict) else ""
            if isinstance(body, dict) and isinstance(body.get("content"), list):
                message += " ".join(str(c.get("text", ""))[:1000] for c in body["content"] if isinstance(c, dict))[:4000]
            if ((isinstance(error, dict) and error.get("code") in (429, "429")) or
                    re.search(r"rate[ _-]*limit|too many requests|quota|(?:usage|request|daily|monthly|free)[ _-]+limit|(?:credit|balance).{0,40}(?:exhaust|deplet|insufficient)|(?:out of|insufficient|exhausted).{0,20}credits?", message, re.I)):
                raise SearchError("source_rate_limited", "Exa anonymous search/read limit reached; the source is paused before another allowed route is tried.",
                                  category="rate_limit")
            raise SearchError("provider_error", "Exa hosted MCP rejected the call; check service access or limits.")
        structured = body.get("structuredContent")
        if isinstance(structured, dict) and isinstance(structured.get("results"), list):
            return structured
        blocks = body.get("content")
        if not isinstance(blocks, list):
            raise SearchError("invalid_response", "Missing Exa MCP content.")
        text = "\n".join(c.get("text", "") for c in blocks if isinstance(c, dict) and c.get("type") == "text")
        return {"mcp_text": text}

    def normalize(self, raw, count):
        if "results" in raw:
            rows = [result(self.name, i, item, snippet=None, content="text", highlights="highlights",
                           published="publishedDate") for i, item in enumerate(array(raw, "results"), 1)]
        else:
            text = raw.get("mcp_text", "")
            rows = []
            for block in re.split(r"\n(?=Title: )", "\n" + text.strip()):
                fields, body = {}, []
                for line in block.strip().splitlines():
                    match = re.match(r"^(Title|URL|Published|Author):\s*(.*)$", line)
                    if match: fields[match[1].lower()] = match[2]
                    elif line.strip() not in ("---", "Highlights:"): body.append(line)
                if "title" in fields and "url" in fields:
                    fields["snippet"] = "\n".join(body).strip()
                    if fields.get("published") == "N/A": fields["published"] = None
                    rows.append(result(self.name, len(rows) + 1, fields, published="published"))
            if not rows and not text.startswith("No search results found."):
                raise SearchError("invalid_response", "Unrecognized Exa MCP search content.")
        return rows[:count], self.metadata(raw, rows, count)

    def fetch_payload(self, args):
        if option(args, "highlights") or option(args, "summary"):
            raise SearchError("unsupported_option", "Exa keyless reader does not accept highlights/summary options.")
        return {"tool": "web_fetch_exa", "arguments": {"urls": [args.url], "maxCharacters": getattr(args, "max_characters", None) or 24000}}

    def normalize_fetch(self, raw, url):
        if "results" in raw:
            rows = array(raw, "results")
            if len(rows) != 1 or not isinstance(rows[0], dict) or not isinstance(rows[0].get("text"), str):
                raise SearchError("extraction_failed", "Exa MCP returned no readable page.")
            content, title = rows[0]["text"], rows[0].get("title") or ""
        else:
            text = raw.get("mcp_text", "")
            if not re.match(r"^# .+\nURL: https?://", text) or "\n\n" not in text:
                raise SearchError("extraction_failed", "Exa MCP returned no recognizable page content.")
            header, content = text.split("\n\n", 1)
            title = header.splitlines()[0][2:]
        if not content.strip(): raise SearchError("extraction_failed", "Exa returned empty page text.")
        return {"title": title, "content": content, "content_kind": "page_content",
                "truncated": False, "completeness_verified": False}


class GitHub(PublicProvider):
    name, label = "github", "GitHub public repositories"
    endpoint = "https://api.github.com/search/repositories"
    fetch_endpoint = "https://api.github.com/repos/"
    search_scope = "public_repositories_not_code_search"
    options = frozenset(("site",))

    def build_search(self, args):
        if option(args, "site") not in (None, "", "github.com"):
            raise SearchError("unsupported_option", "GitHub repository search only supports site github.com.")
        return {"q": args.query, "per_page": args.count}

    def normalize(self, raw, count):
        if raw.get("incomplete_results"):
            raw = {**raw, "warnings": ["GitHub reports incomplete search results."]}
        rows = []
        for i, item in enumerate(array(raw, "items"), 1):
            mapped = {**item, "title": item.get("full_name"), "url": item.get("html_url"),
                      "snippet": item.get("description") or ""}
            rows.append(result(self.name, i, mapped))
        return rows[:count], self.metadata(raw, rows, count)

    def fetch_payload(self, args):
        if option(args, "highlights") or option(args, "summary"):
            raise SearchError("unsupported_option", "GitHub README reader does not generate summaries or excerpts.")
        owner, repo = repo_parts(args.url)
        return {"owner": owner, "repo": repo}

    def build_request(self, payload, key, version, *, fetch=False):
        if not fetch: return super().build_request(payload, key, version)
        url = self.fetch_endpoint + payload["owner"] + "/" + payload["repo"] + "/readme"
        return urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                                   "User-Agent": "xcoze-search/" + version})

    def normalize_fetch(self, raw, url):
        try:
            if raw.get("encoding") != "base64" or not isinstance(raw.get("content"), str): raise ValueError
            content = base64.b64decode("".join(raw["content"].split()), validate=True).decode("utf-8")
        except (ValueError, UnicodeError):
            raise SearchError("extraction_failed", "GitHub returned no readable README.") from None
        return {"title": raw.get("name") or "README", "content": content, "content_kind": "repository_readme",
                "source_url": raw.get("html_url") or url, "truncated": False}


class HackerNews(PublicProvider):
    name, label = "hackernews", "Hacker News / Algolia"
    endpoint = "https://hn.algolia.com/api/v1/search"
    fetch_endpoint = "https://hacker-news.firebaseio.com/v0/item/"
    options = frozenset(("site", "start_date", "end_date"))
    search_scope = "hacker_news_stories"

    def build_search(self, args):
        if option(args, "site") not in (None, "", "news.ycombinator.com", "hn.algolia.com"):
            raise SearchError("unsupported_option", "Hacker News search only covers HN stories.")
        start, end = dates(args)
        filters = []
        for value, operator, offset in ((start, ">=", 0), (end, "<", 86400)):
            if value:
                timestamp = int(datetime.fromisoformat(value).replace(tzinfo=timezone.utc).timestamp()) + offset
                filters.append("created_at_i" + operator + str(timestamp))
        return {"query": args.query, "tags": "story", "hitsPerPage": args.count,
                **({"numericFilters": ",".join(filters)} if filters else {})}

    def normalize(self, raw, count):
        rows = []
        for i, item in enumerate(array(raw, "hits"), 1):
            identifier = str(item.get("objectID", ""))
            if not identifier.isdigit(): raise SearchError("invalid_response", "Invalid HN item ID.")
            mapped = {**item, "url": "https://news.ycombinator.com/item?id=" + identifier,
                      "title": item.get("title") or item.get("story_title") or "HN story",
                      "snippet": clean_html(item.get("story_text") or ""), "outbound_url": item.get("url")}
            rows.append(result(self.name, i, mapped, published="created_at"))
        return rows[:count], self.metadata(raw, rows, count)

    def fetch_payload(self, args):
        if option(args, "highlights") or option(args, "summary"):
            raise SearchError("unsupported_option", "HN reader does not generate excerpts or summaries.")
        parsed = urllib.parse.urlsplit(args.url)
        identifier = urllib.parse.parse_qs(parsed.query).get("id", [""])[0]
        if parsed.hostname != "news.ycombinator.com" or parsed.path != "/item" or not identifier.isdigit():
            invalid("HN reader requires https://news.ycombinator.com/item?id=<number>.")
        return {"id": identifier}

    def build_request(self, payload, key, version, *, fetch=False):
        if not fetch: return super().build_request(payload, key, version)
        return urllib.request.Request(self.fetch_endpoint + payload["id"] + ".json",
                                      headers={"User-Agent": "xcoze-search/" + version})

    def normalize_fetch(self, raw, url):
        if not raw.get("id") or raw.get("deleted") or raw.get("dead"):
            raise SearchError("extraction_failed", "HN item is missing, deleted or unavailable.")
        return {"title": raw.get("title") or "HN comment", "content": clean_html(raw.get("text") or ""),
                "content_kind": "discussion_item", "outbound_url": raw.get("url"),
                "comment_ids": raw.get("kids") or [], "comments_fetched": False, "truncated": False}


class JinaReader(PublicProvider):
    name, label = "jina", "Jina Reader (keyless)"
    endpoint = ""
    fetch_endpoint = "https://r.jina.ai/"
    supports_search = False
    availability = "official_rate_limited_reader"

    def build_search(self, args):
        raise SearchError("unsupported_operation", "Jina keyless adapter reads URLs; Jina Search requires a key and is not integrated.")

    def fetch_payload(self, args):
        if option(args, "highlights") or option(args, "summary"):
            raise SearchError("unsupported_option", "Jina Reader does not accept highlights/summary options.")
        return {"url": args.url}

    def build_request(self, payload, key, version, *, fetch=False):
        if not fetch: return super().build_request(payload, key, version)
        return urllib.request.Request(self.fetch_endpoint + payload["url"], headers={
            "Accept": "application/json", "User-Agent": "xcoze-search/" + version})

    def check_error(self, raw):
        if raw.get("code") != 200:
            raise SearchError("extraction_failed", "Jina Reader could not retrieve usable content.")

    def normalize_fetch(self, raw, url):
        data = raw.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("content"), str) or not data["content"].strip():
            raise SearchError("extraction_failed", "Jina returned no page content.")
        content, title = data["content"], data.get("title") or ""
        if not isinstance(title, str):
            raise SearchError("invalid_response", "Invalid Jina page title.")
        if (re.search(r"^(?:log in|sign in|登录|安全验证|just a moment)[.!…\s]*$", title, re.I)
                or "requiring CAPTCHA" in content[:2000]):
            raise SearchError("access_challenge", "Reader returned a login or verification page.")
        return {"title": title, "content": content, "content_kind": "page_content",
                "truncated": False, "completeness_verified": False,
                "source_url": data.get("url") or url}


def record_array(body, field):
    records = array(body, field)
    if any(not isinstance(item, dict) for item in records):
        raise SearchError("invalid_response", "Public source records must be objects.")
    return records


class OpenSource(PublicProvider):
    """Scoped public indexes: never a replacement for general web search."""
    options = frozenset(("site",))
    availability = "official_public_api_rate_limited"
    sites = ()
    result_kind = "search_summary"
    documentation_url = ""

    def check_site(self, args):
        if option(args, "site") and args.site not in self.sites:
            raise SearchError("unsupported_option", self.label + " does not cover this site.")

    def capabilities(self):
        return {**super().capabilities(), "supported_sites": list(self.sites),
                "result_type": self.result_kind, "documentation_url": self.documentation_url}

    def build_request(self, payload, key, version, *, fetch=False):
        req = super().build_request(payload, key, version, fetch=fetch)
        req.add_header("User-Agent", "xcoze-search/" + version + " (+https://github.com/wjason/xcoze-search)")
        req.add_header("Accept-Encoding", "gzip")
        return req

    def metadata(self, raw, rows, count):
        value = super().metadata(raw, rows, count)
        value["provider_metadata"] = {k: v for k, v in raw.items() if k not in (
            "items", "query", "message", "objects", "crates", "resultList", "entries", "docs", "data", "hits", "search", "collection", "observations", "results", "features")}
        for container, field in (("message", "items"), ("query", "search")):
            if isinstance(raw.get(container), dict):
                value["provider_metadata"][container] = {k: v for k, v in raw[container].items() if k != field}
        return value

    def rows(self, raw, items, count, *, published=None, summary=None):
        rows = [result(self.name, i, item, published=published, summary=summary) for i, item in enumerate(items, 1)]
        for row in rows: row["content_kind"] = self.result_kind
        return rows[:count], self.metadata(raw, rows, count)


class Wikipedia(OpenSource):
    name, label = "wikipedia", "Wikipedia (English / 中文)"
    endpoint = "https://en.wikipedia.org/w/api.php"
    sites = ("en.wikipedia.org", "zh.wikipedia.org")
    options = frozenset(("site", "language"))
    result_kind, search_scope = "encyclopedia_excerpt", "encyclopedia_articles"
    documentation_url = "https://www.mediawiki.org/wiki/API:Search"

    def build_search(self, args):
        self.check_site(args)
        language = option(args, "language")
        if language not in (None, "", "en", "zh"):
            raise SearchError("unsupported_option", "Wikipedia supports --language en or zh.")
        inferred = "zh" if re.search(r"[\u3400-\u9fff]", args.query) else "en"
        chosen = args.site.split(".")[0] if option(args, "site") else language or inferred
        if language and chosen != language: invalid("Wikipedia --language and --site conflict.")
        return {"action": "query", "list": "search", "srsearch": args.query, "srlimit": args.count,
                "meta": "siteinfo", "siprop": "general", "format": "json", "utf8": 1, "maxlag": 5, "_language": chosen}

    def build_request(self, payload, key, version, *, fetch=False):
        language = payload["_language"]
        if language not in ("en", "zh"): invalid("Unsupported Wikipedia language.")
        req = super().build_request({k: v for k, v in payload.items() if k != "_language"}, key, version)
        req.full_url = "https://" + language + ".wikipedia.org/w/api.php?" + req.full_url.split("?", 1)[1]
        return req

    def normalize(self, raw, count):
        query = raw.get("query")
        if not isinstance(query, dict): raise SearchError("invalid_response", "Missing Wikipedia query results.")
        general = query.get("general")
        wiki = general.get("wikiid") if isinstance(general, dict) else None
        if wiki not in ("enwiki", "zhwiki"):
            raise SearchError("invalid_response", "Missing supported Wikipedia identity.")
        host = "en.wikipedia.org" if wiki == "enwiki" else "zh.wikipedia.org"
        items = []
        for item in record_array(query, "search"):
            title = item.get("title")
            if not isinstance(title, str): raise SearchError("invalid_response", "Missing article title.")
            items.append({**item, "url": "https://" + host + "/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe=""),
                          "snippet": clean_html(item.get("snippet") or ""), "date_semantics": "timestamp_is_last_edit_not_publication"})
        return self.rows(raw, items, count)

    def metadata(self, raw, rows, count):
        value = super().metadata(raw, rows, count)
        query = value["provider_metadata"].get("query", {})
        if isinstance(query.get("general"), dict):
            query["general"] = {k: v for k, v in query["general"].items() if k in ("wikiid", "lang", "sitename")}
        return value


class StackExchange(OpenSource):
    name, label = "stackexchange", "Stack Exchange questions"
    endpoint = "https://api.stackexchange.com/2.3/search/advanced"
    sites = ("stackoverflow.com", "superuser.com", "serverfault.com", "askubuntu.com",
             "math.stackexchange.com", "stats.stackexchange.com", "datascience.stackexchange.com")
    options = frozenset(("site", "start_date", "end_date"))
    result_kind, search_scope = "question_excerpt", "public_questions_not_answers"
    documentation_url = "https://api.stackexchange.com/docs/advanced-search"

    def build_search(self, args):
        self.check_site(args)
        site = option(args, "site") or "stackoverflow.com"
        site = site.removesuffix(".stackexchange.com").removesuffix(".com")
        start, end = dates(args)
        payload = {"site": site, "q": args.query, "pagesize": args.count, "sort": "relevance", "order": "desc", "filter": "withbody"}
        for value, key, offset in ((start, "fromdate", 0), (end, "todate", 86399)):
            if value: payload[key] = int(datetime.fromisoformat(value).replace(tzinfo=timezone.utc).timestamp()) + offset
        return payload

    def check_error(self, raw):
        if "error_id" in raw:
            raise SearchError("provider_error", "Stack Exchange rejected the request; inspect quota or retry later.",
                              category="rate_limit" if raw.get("error_name") == "throttle_violation" else "provider")
        super().check_error(raw)

    def normalize(self, raw, count):
        items = []
        for item in record_array(raw, "items"):
            timestamp = item.get("creation_date")
            if type(timestamp) is not int: raise SearchError("invalid_response", "Invalid question creation date.")
            try: published = datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
            except (ValueError, OverflowError, OSError):
                raise SearchError("invalid_response", "Question creation date is out of range.") from None
            items.append({**item, "title": clean_html(item.get("title") or ""), "url": item.get("link"),
                          "snippet": clean_html(item.get("body") or "")[:1200],
                          "published": published,
                          "answers_fetched": False})
        rows, meta = self.rows(raw, items, count, published="published")
        meta["usage"] = {k: raw[k] for k in ("quota_remaining", "quota_max", "backoff") if k in raw}
        return rows, meta


class Arxiv(OpenSource):
    name, label = "arxiv", "arXiv preprints"
    endpoint = "https://export.arxiv.org/api/query"
    sites = ("arxiv.org",)
    options = frozenset(("site", "start_date", "end_date"))
    result_kind, search_scope = "abstract", "preprint_metadata_and_abstracts"
    documentation_url = "https://info.arxiv.org/help/api/user-manual.html"

    def build_search(self, args):
        self.check_site(args); start, end = dates(args)
        query = args.query
        if start or end:
            low = start.replace("-", "") + "0000" if start else "000000000000"
            high = end.replace("-", "") + "2359" if end else "999999999999"
            query = "(" + query + ") AND submittedDate:[" + low + " TO " + high + "]"
        return {"search_query": query, "max_results": args.count, "start": 0, "sortBy": "relevance"}

    def decode_response(self, raw):
        try: root = ET.fromstring(raw)
        except ET.ParseError:
            raise SearchError("invalid_response", "arXiv returned invalid Atom XML.") from None
        ns = "{http://www.w3.org/2005/Atom}"
        if root.tag != ns + "feed": raise SearchError("invalid_response", "Expected arXiv Atom feed.")
        entries = []
        for entry in root.findall(ns + "entry"):
            url = entry.findtext(ns + "id") or ""
            if "/api/errors" in url: raise SearchError("provider_error", "arXiv rejected the search expression.")
            parsed = urllib.parse.urlsplit(url)
            if parsed.hostname not in ("arxiv.org", "export.arxiv.org") or not parsed.path.startswith("/abs/"):
                raise SearchError("invalid_response", "Invalid arXiv paper URL.")
            entries.append({"title": " ".join((entry.findtext(ns + "title") or "").split()),
                            "url": "https://arxiv.org" + parsed.path,
                            "abstract": " ".join((entry.findtext(ns + "summary") or "").split()),
                            "published": entry.findtext(ns + "published"), "updated": entry.findtext(ns + "updated"),
                            "authors": [a.findtext(ns + "name") for a in entry.findall(ns + "author")],
                            "categories": [a.get("term") for a in entry.findall(ns + "category")],
                            "peer_review_verified": False})
        return {"entries": entries, "total_results": root.findtext("{http://a9.com/-/spec/opensearch/1.1/}totalResults")}

    def normalize(self, raw, count):
        return self.rows(raw, record_array(raw, "entries"), count, published="published", summary="abstract")


def partial_date(item):
    for field in ("published", "published-online", "published-print"):
        value = item.get(field)
        parts = value.get("date-parts") if isinstance(value, dict) else None
        if isinstance(parts, list) and parts and isinstance(parts[0], list) and 1 <= len(parts[0]) <= 3:
            nums = parts[0]
            if any(type(n) is not int for n in nums): continue
            try:
                from datetime import date
                date(nums[0], nums[1] if len(nums) > 1 else 1, nums[2] if len(nums) > 2 else 1)
            except (ValueError, OverflowError): continue
            return str(nums[0]).zfill(4) + "".join("-" + str(n).zfill(2) for n in nums[1:])
    return None


class Crossref(OpenSource):
    name, label = "crossref", "Crossref DOI metadata"
    endpoint = "https://api.crossref.org/works"
    sites = ("doi.org",)
    options = frozenset(("site", "start_date", "end_date"))
    result_kind, search_scope = "bibliographic_metadata", "crossref_registered_works"
    documentation_url = "https://www.crossref.org/documentation/retrieve-metadata/rest-api/"

    def build_search(self, args):
        self.check_site(args); start, end = dates(args)
        payload = {"query.bibliographic": args.query, "rows": args.count,
                   "select": "DOI,title,abstract,published,published-online,published-print,type,URL,author,container-title,score,license"}
        filters = [k + ":" + v for k, v in (("from-pub-date", start), ("until-pub-date", end)) if v]
        if filters: payload["filter"] = ",".join(filters)
        return payload

    def normalize(self, raw, count):
        message = raw.get("message")
        if not isinstance(message, dict): raise SearchError("invalid_response", "Missing Crossref message.")
        items = []
        for item in record_array(message, "items"):
            doi, titles = item.get("DOI"), item.get("title", [])
            if not isinstance(doi, str) or not doi.startswith("10.") or not isinstance(titles, list):
                raise SearchError("invalid_response", "Invalid DOI record.")
            abstract = item.get("abstract") or ""
            if not isinstance(abstract, str): raise SearchError("invalid_response", "Invalid Crossref abstract.")
            items.append({**item, "title": titles[0] if titles else doi,
                          "url": "https://doi.org/" + urllib.parse.quote(doi, safe="/"),
                          "abstract_text": clean_html(abstract), "published": partial_date(item),
                          "date_semantics": "publication_date_with_original_precision"})
        return self.rows(raw, items, count, published="published", summary="abstract_text")


class Npm(OpenSource):
    name, label = "npm", "npm public package registry"
    endpoint = "https://registry.npmjs.org/-/v1/search"
    sites = ("npmjs.com",)
    result_kind, search_scope = "package_metadata", "public_npm_packages"
    documentation_url = "https://api-docs.npmjs.com/"

    def build_search(self, args):
        self.check_site(args)
        return {"text": args.query, "size": args.count, "from": 0}

    def normalize(self, raw, count):
        items = []
        for item in record_array(raw, "objects"):
            package = item.get("package")
            if not isinstance(package, dict) or not isinstance(package.get("name"), str):
                raise SearchError("invalid_response", "Invalid npm package record.")
            name, version = package["name"], package.get("version")
            items.append({**item, "title": name + ("@" + version if isinstance(version, str) else ""),
                          "url": "https://www.npmjs.com/package/" + urllib.parse.quote(name, safe="@/"),
                          "snippet": package.get("description") or "", "date_semantics": "registry_dates_are_metadata_not_article_publication"})
        return self.rows(raw, items, count)


class Crates(OpenSource):
    name, label = "crates", "crates.io Rust packages"
    endpoint = "https://crates.io/api/v1/crates"
    sites = ("crates.io",)
    result_kind, search_scope = "package_metadata", "public_rust_crates"
    documentation_url = "https://crates.io/data-access"

    def build_search(self, args):
        self.check_site(args)
        return {"q": args.query, "page": 1, "per_page": args.count, "sort": "relevance"}

    def normalize(self, raw, count):
        items = []
        for item in record_array(raw, "crates"):
            name = item.get("name")
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", name):
                raise SearchError("invalid_response", "Invalid crate name.")
            items.append({**item, "title": name, "url": "https://crates.io/crates/" + name,
                          "snippet": item.get("description") or "", "date_semantics": "created_updated_are_registry_metadata"})
        return self.rows(raw, items, count)


class GitLab(OpenSource):
    name, label = "gitlab", "GitLab.com public projects"
    endpoint = "https://gitlab.com/api/v4/projects"
    sites = ("gitlab.com",)
    result_kind, search_scope = "repository_metadata", "public_project_name_path_description_not_code"
    documentation_url = "https://docs.gitlab.com/api/projects/"

    def build_search(self, args):
        self.check_site(args)
        return {"search": args.query, "simple": "true", "visibility": "public", "per_page": args.count,
                "order_by": "star_count", "sort": "desc"}

    def decode_response(self, raw):
        try: items = json.loads(raw)
        except (ValueError, UnicodeError): raise SearchError("invalid_response", "Invalid GitLab JSON.") from None
        if not isinstance(items, list): raise SearchError("invalid_response", "Expected GitLab project list.")
        return {"items": items}

    def normalize(self, raw, count):
        items = [{**item, "title": item.get("path_with_namespace") or item.get("name_with_namespace"),
                  "url": item.get("web_url"), "snippet": item.get("description") or "",
                  "date_semantics": "project_creation_activity_not_article_publication"} for item in record_array(raw, "items")]
        return self.rows(raw, items, count)


class EuropePMC(OpenSource):
    name, label = "europepmc", "Europe PMC literature"
    endpoint = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    sites = ("europepmc.org",)
    options = frozenset(("site", "start_date", "end_date"))
    result_kind, search_scope = "abstract", "biomedical_literature_metadata_and_abstracts"
    documentation_url = "https://europepmc.org/RestfulWebService"

    def build_search(self, args):
        self.check_site(args); start, end = dates(args)
        query = args.query
        if start or end: query = "(" + query + ") AND FIRST_PDATE:[" + (start or "0001-01-01") + " TO " + (end or "9999-12-31") + "]"
        return {"query": query, "format": "json", "pageSize": args.count, "resultType": "core"}

    def normalize(self, raw, count):
        data = raw.get("resultList")
        if not isinstance(data, dict): raise SearchError("invalid_response", "Missing Europe PMC result list.")
        items = []
        for item in record_array(data, "result"):
            source, identifier = item.get("source"), item.get("id")
            if any(not isinstance(x, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", x) for x in (source, identifier)):
                raise SearchError("invalid_response", "Invalid Europe PMC identifier.")
            items.append({**item, "url": "https://europepmc.org/article/" + source + "/" + identifier,
                          "abstract_text": clean_html(item.get("abstractText") or ""),
                          "date_semantics": "provider_first_publication_date_may_be_inferred"})
        return self.rows(raw, items, count, published="firstPublicationDate", summary="abstract_text")


class HuggingFace(OpenSource):
    name, label = "huggingface", "Hugging Face public models"
    endpoint = "https://huggingface.co/api/models"
    sites = ("huggingface.co",)
    result_kind, search_scope = "model_metadata", "public_model_repositories_not_inference_or_downloads"
    documentation_url = "https://huggingface.co/docs/hub/api"

    def build_search(self, args):
        self.check_site(args)
        return {"search": args.query, "limit": args.count, "sort": "downloads", "direction": -1}

    def decode_response(self, raw):
        try: items = json.loads(raw)
        except (ValueError, UnicodeError): raise SearchError("invalid_response", "Invalid Hugging Face JSON.") from None
        if not isinstance(items, list): raise SearchError("invalid_response", "Expected Hugging Face model list.")
        return {"items": items}

    def normalize(self, raw, count):
        items = []
        for item in record_array(raw, "items"):
            name = item.get("id") or item.get("modelId")
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?", name):
                raise SearchError("invalid_response", "Invalid Hugging Face model ID.")
            items.append({**item, "title": name, "url": "https://huggingface.co/" + name,
                          "snippet": item.get("pipeline_tag") or "", "date_semantics": "model_created_modified_not_article_publication"})
        return self.rows(raw, items, count)


class OpenLibrary(OpenSource):
    name, label = "openlibrary", "Open Library books"
    endpoint = "https://openlibrary.org/search.json"
    sites = ("openlibrary.org",)
    result_kind, search_scope = "book_metadata", "open_library_catalog"
    documentation_url = "https://openlibrary.org/dev/docs/api/search"

    def build_search(self, args):
        self.check_site(args)
        return {"q": args.query, "limit": args.count, "fields": "key,title,author_name,first_publish_year"}

    def normalize(self, raw, count):
        items = []
        for item in record_array(raw, "docs"):
            key = item.get("key")
            if not isinstance(key, str) or not re.fullmatch(r"/works/OL[0-9]+W", key):
                raise SearchError("invalid_response", "Invalid Open Library work identifier.")
            authors = item.get("author_name") or []
            if not isinstance(authors, list) or any(not isinstance(a, str) for a in authors):
                raise SearchError("invalid_response", "Invalid Open Library authors.")
            items.append({**item, "url": "https://openlibrary.org" + key,
                          "snippet": ", ".join(authors),
                          "date_semantics": "first_publication_year_of_work"})
        return self.rows(raw, items, count)


class DataCite(OpenSource):
    name, label = "datacite", "DataCite research records"
    endpoint = "https://api.datacite.org/dois"
    sites = ("doi.org",)
    result_kind, search_scope = "research_metadata", "datacite_registered_records"
    documentation_url = "https://support.datacite.org/docs/api"

    def build_search(self, args):
        self.check_site(args)
        return {"query": args.query, "page[size]": args.count}

    def normalize(self, raw, count):
        items = []
        for item in record_array(raw, "data"):
            attrs = item.get("attributes")
            if not isinstance(attrs, dict): raise SearchError("invalid_response", "Invalid DataCite record.")
            doi, titles = attrs.get("doi"), attrs.get("titles")
            if not isinstance(doi, str) or not doi.startswith("10.") or not isinstance(titles, list) or not titles or not isinstance(titles[0], dict):
                raise SearchError("invalid_response", "Invalid DataCite DOI or title.")
            items.append({"title": titles[0].get("title") or doi,
                          "url": "https://doi.org/" + urllib.parse.quote(doi, safe="/"),
                          "creators": attrs.get("creators"), "publisher": attrs.get("publisher"),
                          "publication_year": attrs.get("publicationYear"), "types": attrs.get("types"),
                          "date_semantics": "publication_year_metadata"})
        return self.rows(raw, items, count)


class Zenodo(OpenSource):
    name, label = "zenodo", "Zenodo research records"
    endpoint = "https://zenodo.org/api/records"
    sites = ("zenodo.org",)
    result_kind, search_scope = "research_metadata", "zenodo_public_records"
    documentation_url = "https://developers.zenodo.org/"

    def build_search(self, args):
        self.check_site(args)
        return {"q": args.query, "size": args.count, "page": 1}

    def normalize(self, raw, count):
        hits = raw.get("hits")
        if not isinstance(hits, dict): raise SearchError("invalid_response", "Invalid Zenodo response.")
        items = []
        for item in record_array(hits, "hits"):
            meta, ident = item.get("metadata"), item.get("id")
            if not isinstance(meta, dict) or type(ident) is not int or ident < 1:
                raise SearchError("invalid_response", "Invalid Zenodo record.")
            items.append({"title": meta.get("title"), "url": "https://zenodo.org/records/" + str(ident),
                          "description_text": clean_html(meta.get("description") or ""),
                          "published": meta.get("publication_date"), "doi": meta.get("doi"),
                          "creators": meta.get("creators"), "access_right": meta.get("access_right"),
                          "date_semantics": "zenodo_record_publication_date"})
        return self.rows(raw, items, count, published="published", summary="description_text")


class Wikidata(OpenSource):
    name, label = "wikidata", "Wikidata entities"
    endpoint = "https://www.wikidata.org/w/api.php"
    sites = ("wikidata.org",)
    options = frozenset(("site", "language"))
    result_kind, search_scope = "entity_metadata", "wikidata_entity_labels_and_descriptions"
    documentation_url = "https://www.wikidata.org/wiki/Wikidata:Data_access"

    def build_search(self, args):
        self.check_site(args)
        lang = option(args, "language") or ("zh" if re.search(r"[\u4e00-\u9fff]", args.query) else "en")
        if lang not in ("en", "zh"): raise SearchError("unsupported_option", "Wikidata supports en or zh language in this adapter.")
        return {"action": "wbsearchentities", "search": args.query, "language": lang, "format": "json", "limit": args.count}

    def normalize(self, raw, count):
        items = []
        for item in record_array(raw, "search"):
            ident = item.get("id")
            if not isinstance(ident, str) or not re.fullmatch(r"Q[1-9][0-9]*", ident):
                raise SearchError("invalid_response", "Invalid Wikidata entity identifier.")
            items.append({"title": item.get("label") or ident, "url": "https://www.wikidata.org/wiki/" + ident,
                          "snippet": item.get("description") or "", "entity_id": ident})
        return self.rows(raw, items, count)


class NasaMedia(OpenSource):
    name, label = "nasa", "NASA Image and Video Library"
    endpoint = "https://images-api.nasa.gov/search"
    sites = ("images.nasa.gov",)
    result_kind, search_scope = "media_metadata", "nasa_image_video_audio_metadata"
    documentation_url = "https://api.nasa.gov/"

    def build_search(self, args):
        self.check_site(args)
        return {"q": args.query, "page_size": args.count}

    def normalize(self, raw, count):
        collection = raw.get("collection")
        if not isinstance(collection, dict): raise SearchError("invalid_response", "Invalid NASA collection.")
        items = []
        for record in record_array(collection, "items"):
            data = record.get("data")
            if not isinstance(data, list) or not data or not isinstance(data[0], dict):
                raise SearchError("invalid_response", "Invalid NASA media metadata.")
            info = data[0]; ident = info.get("nasa_id")
            if not isinstance(ident, str) or not ident.strip() or len(ident) > 256:
                raise SearchError("invalid_response", "Invalid NASA identifier.")
            items.append({"title": info.get("title"), "url": "https://images.nasa.gov/details-" + urllib.parse.quote(ident, safe=""),
                          "summary_text": clean_html(info.get("description") or ""), "created": info.get("date_created"),
                          "nasa_id": ident, "media_type": info.get("media_type"), "center": info.get("center"),
                          "rights_owner": info.get("secondary_creator"), "date_semantics": "media_creation_date"})
        return self.rows(raw, items, count, published="created", summary="summary_text")


class FederalRegister(OpenSource):
    name, label = "federalregister", "U.S. Federal Register"
    endpoint = "https://www.federalregister.gov/api/v1/documents.json"
    sites = ("federalregister.gov",)
    result_kind, search_scope = "official_notice_metadata", "us_federal_register_documents"
    documentation_url = "https://www.federalregister.gov/developers/documentation/api/v1"

    def build_search(self, args):
        self.check_site(args)
        return {"conditions[term]": args.query, "per_page": args.count, "order": "newest"}

    def normalize(self, raw, count):
        items = []
        for item in record_array(raw, "results"):
            url = item.get("html_url")
            if not isinstance(url, str) or not domain_matches(url, "federalregister.gov") or not public_url(url):
                raise SearchError("invalid_response", "Invalid Federal Register document link.")
            items.append({"title": item.get("title"), "url": url, "abstract_text": clean_html(item.get("abstract") or ""),
                          "published": item.get("publication_date"), "document_number": item.get("document_number"),
                          "document_type": item.get("type"), "agencies": item.get("agencies"),
                          "date_semantics": "publication_date_not_effective_date"})
        return self.rows(raw, items, count, published="published", summary="abstract_text")


class WorldBank(OpenSource):
    name, label = "worldbank", "World Bank indicators"
    endpoint = "https://api.worldbank.org/v2/country/"
    sites = ("data.worldbank.org",)
    result_kind, search_scope = "statistical_observation", "world_bank_indicator_by_country_and_code"
    documentation_url = "https://datahelpdesk.worldbank.org/knowledgebase/articles/889392"

    def build_search(self, args):
        self.check_site(args)
        match = re.fullmatch(r"\s*([A-Za-z]{2,3})\s*,\s*([A-Za-z0-9][A-Za-z0-9_.-]{1,79})\s*", args.query)
        if not match: raise SearchError("invalid_input", "World Bank query requires country code,indicator code (e.g. CN,SP.POP.TOTL).")
        return {"country": match.group(1).upper(), "indicator": match.group(2).upper(), "format": "json", "per_page": args.count, "mrv": args.count}

    def build_request(self, payload, key, version, *, fetch=False):
        values = dict(payload); country = values.pop("country"); indicator = values.pop("indicator")
        url = self.endpoint + country + "/indicator/" + urllib.parse.quote(indicator, safe=".-_") + "?" + urllib.parse.urlencode(values)
        return urllib.request.Request(url, headers={"User-Agent": "xcoze-search/" + version + " (+https://github.com/wjason/xcoze-search)", "Accept": "application/json", "Accept-Encoding": "gzip"})

    def decode_response(self, raw):
        try: value = json.loads(raw)
        except (ValueError, UnicodeError): raise SearchError("invalid_response", "Invalid World Bank JSON.") from None
        if not isinstance(value, list) or len(value) != 2 or not isinstance(value[0], dict) or not isinstance(value[1], list):
            raise SearchError("invalid_response", "Invalid World Bank data response.")
        return {"page_metadata": value[0], "observations": value[1]}

    def normalize(self, raw, count):
        items = []
        for item in record_array(raw, "observations"):
            indicator, country = item.get("indicator"), item.get("country")
            if not isinstance(indicator, dict) or not isinstance(country, dict):
                raise SearchError("invalid_response", "Invalid World Bank observation.")
            code, region = indicator.get("id"), country.get("id")
            if not isinstance(code, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", code) or not isinstance(region, str) or not re.fullmatch(r"[A-Za-z0-9]+", region):
                raise SearchError("invalid_response", "Invalid World Bank indicator or country.")
            items.append({"title": str(indicator.get("value") or code) + " — " + str(country.get("value") or region),
                          "url": "https://data.worldbank.org/indicator/" + code + "?locations=" + region,
                          "year": item.get("date"), "value": item.get("value"), "unit": item.get("unit"),
                          "country": country, "indicator": indicator, "date_semantics": "observation_year_not_publication_date"})
        return self.rows(raw, items, count)


class USGSEarthquakes(OpenSource):
    name, label = "usgs", "USGS recent earthquake feed"
    endpoint = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/"
    sites = ("earthquake.usgs.gov",)
    result_kind, search_scope = "earthquake_observation", "usgs_recent_earthquake_summary_feed"
    documentation_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php"

    def build_search(self, args):
        self.check_site(args)
        match = re.fullmatch(r"\s*(all|significant|1\.0|2\.5|4\.5)\s*,\s*(hour|day|week|month)\s*", args.query, re.I)
        if not match: raise SearchError("invalid_input", "USGS query requires magnitude,period (e.g. 2.5,day).")
        return {"feed": match.group(1).lower() + "_" + match.group(2).lower()}

    def build_request(self, payload, key, version, *, fetch=False):
        feed = payload["feed"]
        if not re.fullmatch(r"(?:all|significant|1\.0|2\.5|4\.5)_(?:hour|day|week|month)", feed):
            raise SearchError("invalid_input", "Invalid earthquake feed.")
        return urllib.request.Request(self.endpoint + feed + ".geojson", headers={"User-Agent": "xcoze-search/" + version + " (+https://github.com/wjason/xcoze-search)", "Accept": "application/json", "Accept-Encoding": "gzip"})

    def normalize(self, raw, count):
        items = []
        for item in record_array(raw, "features"):
            props, geometry = item.get("properties"), item.get("geometry")
            if not isinstance(props, dict) or not isinstance(geometry, dict):
                raise SearchError("invalid_response", "Invalid USGS earthquake event.")
            url = props.get("url")
            if not isinstance(url, str) or not domain_matches(url, "earthquake.usgs.gov") or not public_url(url):
                raise SearchError("invalid_response", "Invalid USGS event link.")
            millis = props.get("time")
            if type(millis) not in (int, float): raise SearchError("invalid_response", "Invalid USGS event time.")
            try: event_time = datetime.fromtimestamp(millis / 1000, timezone.utc).isoformat().replace("+00:00", "Z")
            except (OverflowError, OSError, ValueError): raise SearchError("invalid_response", "Invalid USGS event time.") from None
            items.append({"title": props.get("title"), "url": url, "event_time": event_time,
                          "magnitude": props.get("mag"), "location": props.get("place"),
                          "updated_epoch_ms": props.get("updated"), "status": props.get("status"),
                          "coordinates_longitude_latitude_depth_km": geometry.get("coordinates"),
                          "date_semantics": "earthquake_event_time_utc_not_publication_time"})
        return self.rows(raw, items, count)


OPEN_SOURCES = (Wikipedia(), StackExchange(), Arxiv(), Crossref(), Npm(), Crates(), GitLab(), EuropePMC(), HuggingFace(), OpenLibrary(), DataCite(), Zenodo(), Wikidata(), NasaMedia(), FederalRegister(), WorldBank(), USGSEarthquakes())

from browser_search import Browser
from content_sources import GovCN, CommunityReader

PUBLIC_REGISTRY = {p.name: p for p in (BingRSS(), DuckDuckGo(), ExaFree(), GitHub(), HackerNews(), JinaReader(), *OPEN_SOURCES, Browser(), GovCN(), CommunityReader())}
