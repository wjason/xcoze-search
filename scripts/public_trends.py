"""Keyless platform snapshots. These feeds are not keyword search or full-text readers."""
from datetime import datetime, timezone
import json
import re
import time
import urllib.parse

from public_providers import PublicProvider, clean_html, record_array
from search_common import SearchError, RequestBudget, invalid
from search_providers import result


def response_error():
    return SearchError("invalid_response", "Unrecognized public trending feed; no snapshot obtained.")


class PublicTrend(PublicProvider):
    supports_search = False
    supports_trending = True
    availability = "experimental_public_endpoint"
    max_count = 50

    def capabilities(self):
        return {**super().capabilities(), "trending": True, "platform": self.platform,
                "search_scope": "none_trending_only",
                "feed_scope": self.feed_scope, "documentation_url": self.documentation_url,
                "note": "Current endpoint snapshot only; not keyword search, history, comments or verified facts."}

    def check_error(self, raw):
        super().check_error(raw)
        if "code" in raw and raw["code"] not in (0, "0"):
            raise SearchError("provider_error", "Public platform rejected the feed request.")

    def build_request(self, payload, key, version, *, fetch=False):
        if fetch or key: invalid("Trending feeds accept neither credentials nor fetch operations.")
        req = super().build_request(payload, "", version)
        req.add_header("User-Agent", "xcoze-search/" + version + " (+https://github.com/wjason/xcoze-search)")
        return req

    def build_trending(self, count):
        return {}

    def normalize(self, raw, count):
        rows = self.records(raw)
        for row in rows:
            row["content_kind"] = "trending_item"
        return rows[:count], {"returned_count": len(rows), "shown_count": min(len(rows), count),
                              "cost": None, "usage": None, "access": "keyless",
                              "user_api_key_used": False, "feed_scope": self.feed_scope,
                              "rank_semantics": "endpoint_order_before_local_filtering",
                              "upstream_updated_at": raw.get("timestamp") if self.platform == "bilibili" else None,
                              "upstream_updated_at_semantics": "raw_source_timestamp_not_publication",
                              "snapshot_complete": False, "comments_fetched": False,
                              "facts_verified": False}


class BilibiliTrending(PublicTrend):
    name, label, platform = "bilibili-trending", "Bilibili public hotwords", "bilibili"
    endpoint = "https://s.search.bilibili.com/main/hotword"
    feed_scope = "public_hotword_list_not_video_search_or_video_popularity_ranking"
    documentation_url = "https://github.com/newsnext/newsnow/blob/main/server/sources/bilibili.ts"

    def build_trending(self, count):
        return {"limit": count}

    def records(self, raw):
        rows = []
        for rank, item in enumerate(record_array(raw, "list"), 1):
            stats = item.get("stat_datas") or {}
            if not isinstance(stats, dict): raise response_error()
            if str(stats.get("is_commercial", "0")).lower() in ("1", "true"): continue
            keyword, title = item.get("keyword"), item.get("show_name") or item.get("keyword")
            if not isinstance(keyword, str) or not keyword.strip() or not isinstance(title, str) or not title.strip():
                raise response_error()
            mapped = {"title": title, "url": "https://search.bilibili.com/all?" + urllib.parse.urlencode({"keyword": keyword}),
                      "snippet": "", "keyword": keyword, "heat_score": item.get("heat_score"),
                      "heat_scale": "bilibili_native_heat_score", "native_position": item.get("pos"),
                      "commercial_marker": stats.get("is_commercial"), "destination_kind": "platform_search",
                      "publication_time_known": False}
            rows.append(result(self.name, rank, mapped))
        return rows


class ZhihuTrending(PublicTrend):
    name, label, platform = "zhihu-trending", "Zhihu public hot list", "zhihu"
    endpoint = "https://www.zhihu.com/api/v3/feed/topstory/hot-list-web"
    feed_scope = "public_hot_question_list_not_answers_or_keyword_search"
    documentation_url = "https://github.com/newsnext/newsnow/blob/main/server/sources/zhihu.ts"

    def build_trending(self, count):
        return {"limit": count, "desktop": "true"}

    def records(self, raw):
        rows = []
        for rank, item in enumerate(record_array(raw, "data"), 1):
            target = item.get("target")
            if not isinstance(target, dict): raise response_error()
            try:
                url, title = target["link"]["url"], target["title_area"]["text"]
                if not isinstance(title, str) or not title.strip(): raise response_error()
                if not isinstance(url, str) or not re.fullmatch(r"https://(?:www\.)?zhihu\.com/question/\d+/?", url):
                    raise response_error()
                excerpt = target.get("excerpt_area", {}).get("text", "")
                metric = target.get("metrics_area", {}).get("text")
                specific = item.get("feed_specific") or {}
                mapped = {"title": title, "url": url, "snippet": clean_html(excerpt),
                          "heat_text": metric, "heat_scale": "zhihu_native_display_text",
                          "answer_count": specific.get("answer_count"), "answers_fetched": False,
                          "destination_kind": "question", "publication_time_known": False}
                rows.append(result(self.name, rank, mapped))
            except (KeyError, TypeError, AttributeError):
                raise response_error() from None
        return rows


class V2EXTrending(PublicTrend):
    name, label, platform = "v2ex-trending", "V2EX public hot topics", "v2ex"
    endpoint = "https://www.v2ex.com/api/topics/hot.json"
    availability = "official_public_api_rate_limited"
    feed_scope = "public_hot_topics_not_full_site_search_or_replies"
    documentation_url = "https://www.v2ex.com/p/7v9TEc53"

    def decode_response(self, raw):
        try: data = json.loads(raw)
        except (ValueError, UnicodeError): raise response_error() from None
        if not isinstance(data, list): raise response_error()
        return {"items": data}

    def records(self, raw):
        rows = []
        for rank, item in enumerate(record_array(raw, "items"), 1):
            identifier = item.get("id")
            if type(identifier) is not int or identifier <= 0: raise response_error()
            if not isinstance(item.get("title"), str) or not item["title"].strip(): raise response_error()
            created = item.get("created")
            try:
                published = datetime.fromtimestamp(created, timezone.utc).isoformat() if type(created) is int else None
            except (ValueError, OverflowError, OSError): raise response_error() from None
            node = item.get("node") or {}
            if not isinstance(node, dict): raise response_error()
            mapped = {"title": item.get("title"), "url": "https://www.v2ex.com/t/" + str(identifier),
                      "snippet": "", "published_at": published, "topic_id": identifier,
                      "reply_count": item.get("replies"), "node": node.get("name"),
                      "replies_fetched": False, "body_fetched": False, "destination_kind": "topic",
                      "date_semantics": "created_is_topic_publication_not_ranking_update"}
            rows.append(result(self.name, rank, mapped, published="published_at"))
        return rows


TRENDING = {p.platform: p for p in (BilibiliTrending(), ZhihuTrending(), V2EXTrending())}
TREND_PROVIDERS = {p.name: p for p in TRENDING.values()}


def run_trending(args, request_api, version, *, budget=None):
    if args.platform not in TRENDING: invalid("Unsupported trending platform.")
    provider = TRENDING[args.platform]
    if type(args.count) is not int or not 1 <= args.count <= provider.max_count: invalid("--count must be 1..50.")
    budget = budget or RequestBudget(1)
    before = budget.used
    started = time.monotonic()
    raw, _ = request_api(provider.name, provider.build_trending(args.count), "", timeout=args.timeout,
                         retries=0, budget=budget)
    try:
        rows, metadata = provider.normalize(raw, args.count)
    except SearchError as error:
        error.attempts = budget.used - before
        raise
    return {"ok": True, "operation": "trending", "version": version, "platform": args.platform,
            "provider": provider.name, "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "results": rows, "empty": not rows, "facts_verified": False,
            "feed_scope": provider.feed_scope, "metadata": metadata,
            "requests": [{"provider": provider.name, "ok": True, "attempts": budget.used - before,
                          "elapsed_ms": round((time.monotonic() - started) * 1000, 2)}],
            "budget": budget.data(), "execution_summary": {"api_http_attempts": budget.used - before,
                "keyed_api_attempts": 0, "browser_navigation_attempts": 0, "browser_commands": 0,
                "browser_http_requests": 0}}
