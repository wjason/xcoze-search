"""Keyless public backends. No browser, SDK, account or implicit credentials."""
import base64
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from search_common import SearchError, invalid, public_url
from search_providers import Provider, array, dates, option, result


def clean_html(value):
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
        return {"tool": "web_fetch_exa", "arguments": {"urls": [args.url], "maxCharacters": 24000}}

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
                "truncated": len(content) >= 24000, "completeness_verified": False}


class GitHub(PublicProvider):
    name, label = "github", "GitHub public repositories"
    endpoint = "https://api.github.com/search/repositories"
    fetch_endpoint = "https://api.github.com/repos/"
    search_scope = "public_repositories_not_code_search"
    options = frozenset(("site", "start_date", "end_date"))

    def build_search(self, args):
        if option(args, "site") not in (None, "", "github.com"):
            raise SearchError("unsupported_option", "GitHub repository search only supports site github.com.")
        start, end = dates(args)
        if start or end:
            raise SearchError("unsupported_option", "GitHub repository update dates are not publication-date filters.")
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
        return {"title": title, "content": content[:24000], "content_kind": "page_content",
                "truncated": len(content) > 24000, "completeness_verified": False,
                "source_url": data.get("url") or url}


PUBLIC_REGISTRY = {p.name: p for p in (BingRSS(), DuckDuckGo(), ExaFree(), GitHub(), HackerNews(), JinaReader())}
