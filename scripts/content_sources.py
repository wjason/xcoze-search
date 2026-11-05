"""Fixed publisher feeds, government policy index and public community originals."""
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
import json
import posixpath
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from search_common import SearchError, RequestBudget, invalid, public_url
from search_providers import Provider, dates, option, result

CHINA = timezone(timedelta(hours=8))
COMMUNITY_HOSTS = ("www.v2ex.com", "discuss.python.org", "users.rust-lang.org")


def bad_response():
    return SearchError("invalid_response", "Unrecognized public content response.")


def html_text(value):
    """Plain text with block/code whitespace and link destinations preserved."""
    if not isinstance(value, str): raise bad_response()
    class Text(HTMLParser):
        def __init__(self):
            super().__init__(); self.parts = []; self.hidden = 0; self.links = []
        def handle_starttag(self, tag, attrs):
            if tag in ("script", "style"): self.hidden += 1
            if self.hidden: return
            if tag in ("p", "div", "br", "pre", "blockquote", "li"): self.parts.append("\n")
            if tag == "a": self.links.append(dict(attrs).get("href", ""))
            if tag == "img": self.parts.append(dict(attrs).get("alt", ""))
        def handle_endtag(self, tag):
            if tag in ("script", "style"): self.hidden = max(0, self.hidden - 1); return
            if self.hidden: return
            if tag == "a" and self.links:
                url = self.links.pop()
                if public_url(url): self.parts.append(" (" + url + ")")
            if tag in ("p", "div", "pre", "blockquote", "li"): self.parts.append("\n")
        def handle_data(self, data):
            if not self.hidden: self.parts.append(data)
    parser = Text(); parser.feed(value)
    return re.sub(r"\n{3,}", "\n\n", "".join(parser.parts)).strip()


def parse_timestamp(value):
    if not isinstance(value, str) or not value.strip(): return None
    try:
        stamp = parsedate_to_datetime(value)
    except (ValueError, TypeError):
        try: stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError: return None
    if stamp.tzinfo is None: return None
    return stamp.isoformat()


def filter_snapshot(rows, args):
    """Literal filtering of one returned window, never historical/semantic search."""
    start, end = dates(args)
    query = option(args, "query") or ""
    if len(query) > 4096: invalid("Feed query is too long.")
    terms = query.casefold().split()
    kept, seen, duplicates, unknown = [], set(), 0, 0
    for row in rows:
        url = urllib.parse.urldefrag(row["url"])[0]
        if url in seen: duplicates += 1; continue
        seen.add(url)
        text = (row["title"] + " " + row["snippet"]).casefold()
        if any(term not in text for term in terms): continue
        stamp = row["published_at"]
        if stamp and re.fullmatch(r"\d{4}-\d{2}-\d{2}", stamp): day = stamp
        elif stamp: day = datetime.fromisoformat(stamp).astimezone(CHINA).date().isoformat()
        else: day = None
        if (start or end) and not day: unknown += 1; continue
        if day and ((start and day < start) or (end and day > end)): continue
        kept.append(row)
    known = sorted([r["published_at"] for r in rows if r["published_at"]],
                   key=lambda s: datetime.fromisoformat(s).replace(tzinfo=CHINA).timestamp()
                   if len(s) == 10 else datetime.fromisoformat(s).timestamp())
    return kept[:args.count], {"window_only": True, "historical_search": False,
        "filter_semantics": "all_whitespace_separated_literal_terms_in_title_or_excerpt",
        "date_filter_timezone": "UTC+08:00", "source_row_count": len(rows), "matched_count": len(kept),
        "shown_count": min(len(kept), args.count), "duplicate_urls_removed": duplicates,
        "unknown_dates_excluded": unknown, "newest_publication": known[-1] if known else None,
        "oldest_publication": known[0] if known else None, "window_complete": False,
        "facts_verified": False}


class FixedPublic(Provider):
    requires_key, supports_search = False, False
    method, auth_header = "GET", None
    availability = "public_endpoint_rate_limited"

    def capabilities(self):
        return {**super().capabilities(), "access": "keyless", "availability": self.availability}

    def build_request(self, payload, key, version, *, fetch=False):
        url = self.fetch_endpoint if fetch else self.endpoint
        if payload: url += "?" + urllib.parse.urlencode(payload)
        return urllib.request.Request(url, headers={"User-Agent": "xcoze-search/" + version + " (+https://github.com/wjason/xcoze-search)",
                                                    "Accept": "application/json, application/rss+xml, application/atom+xml"})

    def metadata(self, raw, rows, count):
        return {"access": "keyless", "user_api_key_used": False, "cost": None,
                "returned_count": len(rows), "shown_count": min(len(rows), count)}


class PublisherFeed(FixedPublic):
    def __init__(self, name, label, endpoint, documentation_url):
        self.name, self.label, self.endpoint, self.documentation_url = name, label, endpoint, documentation_url

    def decode_response(self, raw):
        if re.search(br"<!\s*(?:DOCTYPE|ENTITY)\b", raw.replace(b"\0", b""), re.I): raise bad_response()
        try: root = ET.fromstring(raw)
        except (ET.ParseError, LookupError, ValueError): raise bad_response() from None
        atom = "{http://www.w3.org/2005/Atom}"
        entries = []
        if root.tag == "rss" and root.find("channel") is not None:
            for item in root.findall("./channel/item"):
                entries.append({"title": item.findtext("title"), "url": item.findtext("link"),
                                "snippet": item.findtext("description") or "", "published_raw": item.findtext("pubDate"),
                                "updated_raw": None})
        elif root.tag == atom + "feed":
            for item in root.findall(atom + "entry"):
                link = next((link.get("href") for link in item.findall(atom + "link")
                             if link.get("rel", "alternate") == "alternate"), None)
                entries.append({"title": item.findtext(atom + "title"), "url": link,
                                "snippet": item.findtext(atom + "summary") or "",
                                "published_raw": item.findtext(atom + "published"), "updated_raw": item.findtext(atom + "updated")})
        else: raise bad_response()
        return {"entries": entries}

    def records(self, raw):
        rows = []
        for rank, item in enumerate(raw["entries"], 1):
            mapped = {**item, "title": html_text(item["title"]), "snippet": html_text(item["snippet"]),
                      "published_at": parse_timestamp(item["published_raw"]),
                      "updated_at": parse_timestamp(item["updated_raw"]), "feed_url": self.endpoint}
            if not mapped["title"].strip(): raise bad_response()
            row = result(self.name, rank, mapped, published="published_at")
            row["content_kind"] = "feed_excerpt"
            rows.append(row)
        return rows


class GovCN(FixedPublic):
    name, label = "govcn", "中国政府网最新政策栏目"
    endpoint = "https://www.gov.cn/zhengce/zuixin/ZUIXINZHENGCE.json"
    supports_search = True
    sites = ("gov.cn", "www.gov.cn")
    options = frozenset(("site", "start_date", "end_date"))
    max_count = 50

    def build_search(self, args):
        if option(args, "site") not in (None, "", *self.sites): invalid("Government policy index only covers the gov.cn portal.")
        dates(args)
        return {}

    def capabilities(self):
        return {**super().capabilities(), "search_scope": "finite_govcn_latest_policy_index_including_explainers",
                "result_type": "official_policy_index", "supported_sites": list(self.sites),
                "documentation_url": "https://www.gov.cn/zhengce/zuixin/", "historical_search": False}

    def decode_response(self, raw):
        try: items = json.loads(raw)
        except (ValueError, UnicodeError): raise bad_response() from None
        if not isinstance(items, list): raise bad_response()
        return {"items": items}

    def records(self, raw):
        rows = []
        for rank, item in enumerate(raw["items"], 1):
            if not isinstance(item, dict): raise bad_response()
            url, title, day = item.get("URL"), item.get("TITLE"), item.get("DOCRELPUBTIME")
            if not isinstance(url, str) or not public_url(url): raise bad_response()
            host = urllib.parse.urlsplit(url).hostname
            if host != "gov.cn" and not host.endswith(".gov.cn"): raise bad_response()
            if not isinstance(title, str) or not title.strip(): raise bad_response()
            try:
                if not isinstance(day, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day): raise ValueError
                datetime.fromisoformat(day)
            except ValueError: raise bad_response() from None
            mapped = {"title": html_text(title), "url": url, "snippet": "", "published_at": day,
                      "index_scope": "portal_latest_policy_including_explainers_not_all_government_notices",
                      "publication_semantics": "portal_display_date_not_effective_date"}
            row = result(self.name, rank, mapped, published="published_at"); row["content_kind"] = "official_policy_index"
            rows.append(row)
        return rows

    def normalize_search(self, raw, args):
        all_rows = self.records(raw)
        rows, meta = filter_snapshot(all_rows, args)
        return rows, {**self.metadata(raw, all_rows, args.count), **meta}

    def normalize(self, raw, count):
        rows = self.records(raw)
        return rows[:count], self.metadata(raw, rows, count)


class OfficialListParser(HTMLParser):
    """Extract official list entries only; nested related links are separate items."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.records = []
        self.hidden = 0
        self.anchor = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style'): self.hidden += 1
        if tag in ('li', 'tr'): self.stack.append({'tag': tag, 'links': [], 'dates': []})
        if tag == 'a' and self.stack and not self.hidden:
            self.anchor = {'href': attrs.get('href', ''), 'title': attrs.get('title', ''), 'text': []}

    def handle_data(self, data):
        if self.hidden or not self.stack: return
        if self.anchor is not None and not re.fullmatch(r'\s*20\d\d[/-]\d{2}[/-]\d{2}(?:\s+\d{1,2}:\d{2})?\s*', data): self.anchor['text'].append(data)
        self.stack[-1]['dates'].extend(re.findall(r'(?<!\d)(20\d\d)[/-](\d{2})[/-](\d{2})(?!\d)', data))

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor is not None:
            if self.stack: self.stack[-1]['links'].append(self.anchor)
            self.anchor = None
        if tag in ('li', 'tr') and self.stack and self.stack[-1]['tag'] == tag: self.records.append(self.stack.pop())
        if tag in ('script', 'style'): self.hidden = max(0, self.hidden - 1)


class ChinaOfficialIndex(GovCN):
    """A locally filtered current HTML list, not full-archive search."""
    content_host = ''
    path_pattern = ''
    index_scope = ''
    max_count = 20

    def build_search(self, args):
        if option(args, 'site') not in (None, '', *self.sites): invalid('This source only covers its official site.')
        dates(args)
        return {}

    def capabilities(self):
        return {**super().capabilities(), 'search_scope': self.index_scope,
                'result_type': 'official_index', 'supported_sites': list(self.sites),
                'documentation_url': self.endpoint, 'historical_search': False}

    def decode_response(self, raw):
        try: page = raw.decode('utf-8') if isinstance(raw, bytes) else raw
        except UnicodeError: raise bad_response() from None
        if not isinstance(page, str) or '<html' not in page.lower(): raise bad_response()
        parser = OfficialListParser()
        try: parser.feed(page)
        except Exception: raise bad_response() from None
        return {'list_items': parser.records}

    def records(self, raw):
        rows = []
        for frame in raw['list_items']:
            for link in frame['links']:
                href = link.get('href') or ''
                absolute = urllib.parse.urljoin(self.endpoint, href)
                parsed = urllib.parse.urlsplit(absolute)
                path = posixpath.normpath(parsed.path)
                if parsed.hostname != self.content_host or not re.fullmatch(self.path_pattern, path): continue
                url = urllib.parse.urlunsplit(('https', parsed.netloc, path, '', ''))
                title = (link.get('title') or ''.join(link.get('text', []))).strip()
                if not title or not public_url(url): continue
                day = None
                if frame['dates']:
                    try: day = datetime(*map(int, frame['dates'][-1])).strftime('%Y-%m-%d')
                    except ValueError: day = None
                mapped = {'title': html_text(title), 'url': url, 'snippet': '', 'published_at': day,
                          'index_scope': self.index_scope, 'publication_semantics': 'index_display_date_not_effective_date'}
                row = result(self.name, len(rows)+1, mapped, published='published_at')
                row['content_kind'] = 'official_index'
                rows.append(row)
                break
        if not rows: raise bad_response()
        return rows


class NDRCIndex(ChinaOfficialIndex):
    name, label = 'ndrc', '国家发展改革委通知栏目'
    endpoint = 'https://www.ndrc.gov.cn/xxgk/zcfb/tz/'
    content_host, sites = 'www.ndrc.gov.cn', ('ndrc.gov.cn', 'www.ndrc.gov.cn')
    path_pattern = r'/xxgk/zcfb/tz/20\d{4}/t20\d{6}_\d+\.html'
    index_scope = 'ndrc_recent_notice_page_only'


class NationalStatisticsIndex(ChinaOfficialIndex):
    name, label = 'nbs', '国家统计局数据发布栏目'
    endpoint = 'https://www.stats.gov.cn/sj/zxfb/'
    content_host, sites = 'www.stats.gov.cn', ('stats.gov.cn', 'www.stats.gov.cn')
    path_pattern = r'/sj/zxfb/20\d{4}/t20\d{6}_\d+\.html'
    index_scope = 'nbs_recent_data_release_page_only'


class NationalEnergyIndex(ChinaOfficialIndex):
    name, label = 'nea', '国家能源局首页资讯'
    endpoint = 'https://www.nea.gov.cn/'
    content_host, sites = 'www.nea.gov.cn', ('nea.gov.cn', 'www.nea.gov.cn')
    path_pattern = r'/20\d{6}/[a-f0-9]{32}/c\.html'
    index_scope = 'nea_homepage_recent_news_and_notices_only'


class MIITIndex(ChinaOfficialIndex):
    name, label = 'miit', '工业和信息化部政务公开'
    endpoint = 'https://www.miit.gov.cn/zwgk/index.html'
    content_host, sites = 'www.miit.gov.cn', ('miit.gov.cn', 'www.miit.gov.cn')
    path_pattern = r'/zwgk/zcwj/wjfb/[a-z]+/art/20\d{2}/art_[a-f0-9]{32}\.html'
    index_scope = 'miit_government_disclosure_homepage_recent_documents_only'


class MEEIndex(ChinaOfficialIndex):
    name, label = 'mee', '生态环境部新闻发布'
    endpoint = 'https://www.mee.gov.cn/'
    content_host, sites = 'www.mee.gov.cn', ('mee.gov.cn', 'www.mee.gov.cn')
    path_pattern = r'/ywdt/xwfb/20\d{4}/t20\d{6}_\d+\.shtml'
    index_scope = 'mee_homepage_recent_news_releases_only'


class MEMIndex(ChinaOfficialIndex):
    name, label = 'mem', '应急管理部统计数据'
    endpoint = 'https://www.mem.gov.cn/gk/tjsj/index.shtml'
    content_host, sites = 'www.mem.gov.cn', ('mem.gov.cn', 'www.mem.gov.cn')
    path_pattern = r'/xw/yjglbgzdt/20\d{4}/t20\d{6}_\d+\.shtml'
    index_scope = 'mem_recent_disaster_statistics_page_only'


class PBCIndex(ChinaOfficialIndex):
    name, label = 'pbc', '中国人民银行金融统计'
    endpoint = 'https://www.pbc.gov.cn/diaochatongjisi/116219/116225/index.html'
    content_host, sites = 'www.pbc.gov.cn', ('pbc.gov.cn', 'www.pbc.gov.cn')
    path_pattern = r'/diaochatongjisi/116219/116225/20\d{17}/index\.html'
    index_scope = 'pbc_recent_financial_statistics_page_only'


class GGZYIndex(ChinaOfficialIndex):
    name, label = 'ggzy', '全国公共资源交易平台'
    endpoint = 'https://www.ggzy.gov.cn/'
    content_host, sites = 'www.ggzy.gov.cn', ('ggzy.gov.cn', 'www.ggzy.gov.cn')
    path_pattern = r'/information/deal/html/a/\d+/\d+/20\d{6}/[a-f0-9]+\.html'
    index_scope = 'national_public_resource_trading_homepage_recent_notices_only'


class MOFCOMIndex(ChinaOfficialIndex):
    name, label = 'mofcom', '商务部首页新闻'
    endpoint = 'https://www.mofcom.gov.cn/'
    content_host, sites = 'www.mofcom.gov.cn', ('mofcom.gov.cn', 'www.mofcom.gov.cn')
    path_pattern = r'/syxwfb/art/20\d{2}/art_[a-f0-9]{32}\.html'
    index_scope = 'mofcom_homepage_main_news_only'


class CSRCIndex(ChinaOfficialIndex):
    name, label = 'csrc', '中国证监会首页信息'
    endpoint = 'https://www.csrc.gov.cn/'
    content_host, sites = 'www.csrc.gov.cn', ('csrc.gov.cn', 'www.csrc.gov.cn')
    path_pattern = r'/csrc/c\d+/c\d+/content\.shtml'
    index_scope = 'csrc_homepage_public_information_only'


class CCGPIndex(ChinaOfficialIndex):
    name, label = 'ccgp', '中国政府采购网首页公告'
    endpoint = 'https://www.ccgp.gov.cn/'
    content_host, sites = 'www.ccgp.gov.cn', ('ccgp.gov.cn', 'www.ccgp.gov.cn')
    path_pattern = r'/cggg/[a-z]+/[a-z]+/20\d{4}/t20\d{6}_\d+\.htm'
    index_scope = 'china_government_procurement_homepage_recent_notices_only'


class CASIndex(ChinaOfficialIndex):
    name, label = 'cas', '中国科学院首页科研动态'
    endpoint = 'https://www.cas.cn/'
    content_host, sites = 'www.cas.cn', ('cas.cn', 'www.cas.cn')
    path_pattern = r'/syky/20\d{4}/t20\d{6}_\d+\.shtml'
    index_scope = 'chinese_academy_of_sciences_homepage_research_news_only'


class CGSIndex(ChinaOfficialIndex):
    name, label = 'cgs', '中国地质调查局首页要闻'
    endpoint = 'https://www.cgs.gov.cn/'
    content_host, sites = 'www.cgs.gov.cn', ('cgs.gov.cn', 'www.cgs.gov.cn')
    path_pattern = r'/ywdt/ddyw/20\d{4}/t20\d{6}_\d+\.html'
    index_scope = 'china_geological_survey_homepage_recent_news_only'


class XinhuaIndex(ChinaOfficialIndex):
    name, label = 'xinhua', '新华网首页新闻'
    endpoint = 'https://www.news.cn/'
    content_host, sites = 'www.news.cn', ('news.cn', 'www.news.cn')
    path_pattern = r'/(?:[a-z0-9_-]+/)*20\d{6}/[a-f0-9]{32}/c\.html'
    index_scope = 'xinhua_homepage_recent_news_only'


class CommunityReader(FixedPublic):
    name, label = "community", "Public community original post"
    fetch_endpoint = "https://www.v2ex.com/api/topics/show.json"

    def capabilities(self):
        return {**super().capabilities(), "fetch_hosts": list(COMMUNITY_HOSTS),
                "result_type": "community_original_post", "comments_included": False,
                "fetch_character_limit": {"default": 24000, "min": 1000, "max": 200000}}

    def fetch_payload(self, args):
        if option(args, "highlights") or option(args, "summary"): invalid("Community reader does not generate summaries or highlights.")
        parsed = urllib.parse.urlsplit(args.url)
        host = parsed.hostname
        if host not in COMMUNITY_HOSTS or parsed.port not in (None, 443) or parsed.scheme != "https" or parsed.username or parsed.password:
            invalid("Community reader accepts HTTPS public topic roots on V2EX, discuss.python.org or users.rust-lang.org.")
        parts = parsed.path.strip("/").split("/")
        identifier = None
        if len(parts) >= 2 and parts[0] == "t":
            if host == "www.v2ex.com":
                if len(parts) == 2: identifier = parts[1]
            elif parts[1].isdigit():
                if len(parts) == 2 or (len(parts) == 3 and parts[2] == "1"): identifier = parts[1]
            elif len(parts) == 3 or (len(parts) == 4 and parts[3] == "1"):
                identifier = parts[2]
        if not identifier or not identifier.isdigit() or parsed.fragment or parsed.query:
            invalid("Use the canonical topic-root URL without reply targets, query parameters or fragments.")
        return {"host": host, "id": identifier}

    def access_scope(self, payload):
        return {"www.v2ex.com": "community-v2ex", "discuss.python.org": "community-python", "users.rust-lang.org": "community-rust"}[payload["host"]]

    def build_request(self, payload, key, version, *, fetch=False):
        if not fetch or key: invalid("Community source only supports credential-free reading.")
        host, identifier = payload.get("host"), payload.get("id")
        if host not in COMMUNITY_HOSTS or not isinstance(identifier, str) or not identifier.isdigit(): invalid("Invalid community topic.")
        url = self.fetch_endpoint + "?id=" + identifier if host == "www.v2ex.com" else "https://" + host + "/t/" + identifier + ".json"
        return urllib.request.Request(url, headers={"User-Agent": "xcoze-search/" + version + " (+https://github.com/wjason/xcoze-search)", "Accept": "application/json"})

    def decode_response(self, raw):
        try: data = json.loads(raw)
        except (ValueError, UnicodeError): raise bad_response() from None
        if isinstance(data, list): return {"v2ex_items": data}
        if not isinstance(data, dict): raise bad_response()
        return data

    def normalize_fetch(self, raw, url):
        parsed = self.fetch_payload(type("Args", (), {"url": url})())
        identifier = int(parsed["id"])
        if parsed["host"] == "www.v2ex.com":
            items = raw.get("v2ex_items")
            if not isinstance(items, list) or len(items) != 1 or not isinstance(items[0], dict): raise bad_response()
            topic = items[0]
            if topic.get("id") != identifier: raise bad_response()
            body, title = topic.get("content"), topic.get("title")
            kind, reply_count, attached_replies = "plain_text", topic.get("replies"), 0
        else:
            if raw.get("id") != identifier or raw.get("error_type") or raw.get("errors"): raise bad_response()
            stream = raw.get("post_stream")
            if not isinstance(stream, dict) or not isinstance(stream.get("posts"), list): raise bad_response()
            posts = [p for p in stream["posts"] if isinstance(p, dict) and p.get("post_number") == 1]
            if len(posts) != 1 or posts[0].get("hidden") or posts[0].get("deleted_at") or posts[0].get("user_deleted"): raise bad_response()
            body, title = html_text(posts[0].get("cooked")), raw.get("title")
            kind, reply_count = "plain_text_from_html", raw.get("reply_count")
            attached_replies = sum(1 for p in stream["posts"] if isinstance(p, dict) and p.get("post_number", 0) != 1)
        if not isinstance(body, str) or not body.strip() or not isinstance(title, str) or not title.strip():
            raise SearchError("extraction_failed", "Public community returned no visible original post body.")
        return {"title": title, "content": body, "content_format": kind, "content_kind": "community_original_post",
                "source_url": url, "reply_count": reply_count, "comments_fetched": bool(attached_replies),
                "source_attached_replies": attached_replies, "comments_included": False,
                "thread_complete": False, "completeness_verified": False, "truncated": False}

    def metadata(self, raw, rows, count):
        return {**super().metadata(raw, rows, count), "scope": "original_post_only_no_replies"}


FEEDS = {p.name: p for p in (
    PublisherFeed("cns-scroll", "中新网即时新闻 RSS", "https://www.chinanews.com.cn/rss/scroll-news.xml", "https://www.chinanews.com.cn/rss/"),
    PublisherFeed("cns-finance", "中新网财经 RSS", "https://www.chinanews.com.cn/rss/finance.xml", "https://www.chinanews.com.cn/rss/"),
    PublisherFeed("hk-data", "香港政府开放数据更新 RSS", "https://data.gov.hk/filestore/feeds/data_rss_en.xml", "https://data.gov.hk/en-datasets/search"),
    PublisherFeed("bbc-world", "BBC World RSS", "https://feeds.bbci.co.uk/news/world/rss.xml", "https://www.bbc.co.uk/news/10628494"),
    GovCN())}


def run_feed(args, request_api, version):
    if args.source not in FEEDS or type(args.count) is not int or not 1 <= args.count <= 50:
        invalid("Choose a registered source and --count 1..50.")
    dates(args)
    if len(option(args, "query") or "") > 4096: invalid("Feed query is too long.")
    provider = FEEDS[args.source]
    started = time.monotonic(); budget = RequestBudget(1)
    raw, _ = request_api(provider.name, {}, "", timeout=args.timeout, retries=0, budget=budget)
    try:
        rows, meta = filter_snapshot(provider.records(raw), args)
    except SearchError as error:
        error.attempts = budget.used; raise
    return {"ok": True, "operation": "feed", "version": version, "source": provider.name,
            "retrieved_at": datetime.now(timezone.utc).isoformat(), "query": option(args, "query"),
            "results": rows, "empty": not rows, "metadata": meta, "facts_verified": False,
            "requests": [{"provider": provider.name, "ok": True, "attempts": budget.used,
                          "elapsed_ms": round((time.monotonic() - started) * 1000, 2)}],
            "budget": budget.data(), "execution_summary": {"api_http_attempts": budget.used,
                "keyed_api_attempts": 0, "browser_navigation_attempts": 0, "browser_commands": 0, "browser_http_requests": 0}}
