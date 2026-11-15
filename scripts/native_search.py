"""Keyless first-party indexes and site-search clients. No browser or SDK."""
from datetime import date as calendar_date, datetime, timedelta, timezone
from html.parser import HTMLParser
import json
import re
import urllib.parse
import urllib.request

from search_common import SearchError, public_url
from search_providers import Provider, option, result
from search_quality import STOP


def plain(value):
    if value is None: return ''
    if not isinstance(value, str): raise SearchError('invalid_response', 'Invalid site text field.')
    class Text(HTMLParser):
        def __init__(self): super().__init__(); self.parts = []; self.hidden = 0
        def handle_starttag(self, tag, attrs):
            if tag in ('script', 'style'): self.hidden += 1
        def handle_endtag(self, tag):
            if tag in ('script', 'style'): self.hidden = max(0, self.hidden - 1)
        def handle_data(self, data):
            if not self.hidden: self.parts.append(data)
    parser = Text(); parser.feed(value)
    return ' '.join(''.join(parser.parts).split())


def on_host(url, domain):
    host = urllib.parse.urlsplit(url).hostname or ''
    return host == domain or host.endswith('.' + domain)


class Links(HTMLParser):
    def __init__(self): super().__init__(); self.rows = []; self.anchor = None
    def handle_starttag(self, tag, attrs):
        if tag == 'a': self.anchor = [dict(attrs), '']
    def handle_data(self, value):
        if self.anchor is not None: self.anchor[1] += value
    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor is not None:
            self.rows.append(self.anchor); self.anchor = None


def words(text):
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text)
    values = set()
    for token in re.findall(r'[a-z0-9_]+', text.casefold()):
        if len(token) <= 1 or token in STOP: continue
        if len(token) > 4 and token.endswith('ies'): token = token[:-3] + 'y'
        elif len(token) > 4 and token.endswith('s') and not token.endswith('ss'): token = token[:-1]
        values.add(token)
    return values


class SiteSource(Provider):
    requires_key = False
    auth_header = None
    method = 'GET'
    max_count = 10
    options = frozenset(('site',))
    search_scope = 'official_site_search'

    def capabilities(self):
        return {**super().capabilities(), 'access': 'keyless', 'search_scope': self.search_scope,
                'sites': list(self.sites), 'availability': 'public_endpoint_network_dependent'}

    def metadata(self, raw, rows, count):
        return {**super().metadata(raw, rows, count), 'access': 'keyless', 'user_api_key_used': False}

    def build_request(self, payload, key, version, *, fetch=False):
        if fetch: raise SearchError('unsupported_operation', 'This source only searches.')
        return urllib.request.Request(self.endpoint + '?' + urllib.parse.urlencode(payload), headers={
            'User-Agent': 'xcoze-search/' + version, 'Accept': 'application/json,text/html;q=0.9'})

    def check_site(self, args):
        site = option(args, 'site')
        if site is not None and site not in self.sites:
            raise SearchError('unsupported_option', 'The selected site is outside this source scope.')


class NavigationDocs(SiteSource):
    name, label = 'site-docs', 'Kubernetes and Rust official documentation indexes'
    endpoint = 'https://kubernetes.io/docs/concepts/'
    sites = ('kubernetes.io', 'doc.rust-lang.org')
    options = frozenset(('site', 'language'))
    search_scope = 'official_navigation_or_standard_library_item_index'
    indexes = {'kubernetes.io': 'https://kubernetes.io/docs/concepts/',
               'doc.rust-lang.org': 'https://doc.rust-lang.org/std/all.html'}

    def build_search(self, args):
        self.check_site(args)
        if option(args, 'site') not in self.indexes:
            raise SearchError('unsupported_option', 'Choose a supported documentation --site.')
        if option(args, 'language') not in (None, 'en', 'en-US', 'en-us'):
            raise SearchError('unsupported_option', 'These documentation indexes only support English.')
        if re.search(r'\bv?\d+\.\d+(?:\.\d+)?\b', args.query):
            raise SearchError('unsupported_option', 'The current index cannot guarantee a requested version.')
        return {'site': args.site}

    def build_request(self, payload, key, version, *, fetch=False):
        if fetch or payload.get('site') not in self.indexes:
            raise SearchError('invalid_input', 'Invalid documentation index destination.')
        return urllib.request.Request(self.indexes[payload['site']], headers={
            'User-Agent': 'xcoze-search/' + version, 'Accept': 'text/html'})

    def decode_response(self, raw):
        parser = Links(); parser.feed(raw.decode('utf-8', 'replace'))
        return {'links': parser.rows}

    def normalize_search(self, raw, args):
        site = args.site
        base = 'https://kubernetes.io' if site == 'kubernetes.io' else 'https://doc.rust-lang.org/std/'
        query = re.sub(r'-?site:\S+', ' ', args.query, flags=re.I)
        terms = words(query) - {'kubernetes', 'k8s', 'rust', 'std', 'library'}
        identifiers = {s.casefold() for s in re.findall(r'[A-Za-z][A-Za-z0-9_]*', query)}
        compounds = [words(s) for s in re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', query)]
        procedural = bool(re.search(r'\b(?:configure|create|deploy|troubleshoot)\b', query, re.I))
        catalog = {}
        for attrs, title in raw['links']:
            href = attrs.get('href', '')
            url = urllib.parse.urljoin(base, href)
            if not title.strip() or not public_url(url): continue
            path = urllib.parse.urlsplit(url).path
            if site == 'kubernetes.io':
                if not url.startswith('https://kubernetes.io/docs/') or '/_print/' in path: continue
            elif not url.startswith('https://doc.rust-lang.org/std/') or not path.endswith('.html') or path.endswith('/all.html'):
                continue
            catalog.setdefault(url, ' '.join(title.split()))
        if not catalog:
            raise SearchError('invalid_response', 'Official documentation index contained no recognizable entries.')
        known_symbols = identifiers & {t.split('::')[-1].casefold() for t in catalog.values()} if site == 'doc.rust-lang.org' else set()
        ranked = []
        for position, (url, title) in enumerate(catalog.items()):
            title_words = words(title)
            matched = terms & words(title + ' ' + url)
            if not matched: continue
            symbol = title.split('::')[-1].casefold()
            if known_symbols and symbol not in known_symbols: continue
            score = 3 * len(terms & title_words) + len(matched)
            if site == 'kubernetes.io':
                if not procedural and '/concepts/' in url: score += 10
                score += 15 * sum(bool(c) and c <= title_words for c in compounds)
            elif symbol in known_symbols: score += 50
            ranked.append((score, len(urllib.parse.urlsplit(url).path) if known_symbols else position, url, title, matched))
        ranked.sort(key=lambda r: (-r[0], r[1]))
        rows = []
        for _, _, url, title, matched in ranked[:args.count]:
            row = result(self.name, len(rows) + 1, {'title': title, 'url': url,
                         'snippet': 'Official index matches: ' + ', '.join(sorted(matched)),
                         'index_url': self.indexes[site], 'page_body_read': False})
            row['content_kind'] = 'documentation_index'; rows.append(row)
        return rows, {**self.metadata({}, rows, args.count), 'index_entries': len(catalog),
                      'query_sent_to_source': False, 'page_body_read': False,
                      'search_scope': self.search_scope}


class GoDocs(SiteSource):
    name, label = 'go-docs', 'Go standard library package and symbol search'
    endpoint = 'https://pkg.go.dev/search'
    sites = ('pkg.go.dev',)
    options = frozenset(('site', 'language'))
    search_scope = 'go_standard_library_package_and_symbol_search'

    def build_search(self, args):
        self.check_site(args)
        if option(args, 'language') not in (None, 'en', 'en-US', 'en-us'):
            raise SearchError('unsupported_option', 'Go documentation search only supports English.')
        if re.search(r'\b(?:go|v)?\d+\.\d+(?:\.\d+)?\b', args.query):
            raise SearchError('unsupported_option', 'The search adapter cannot guarantee a requested Go version.')
        query = re.sub(r'-?site:\S+|\bpkg\.go\.dev\b', ' ', args.query, flags=re.I)
        tokens = re.findall(r'[A-Za-z][A-Za-z0-9_/]*(?:\.[A-Za-z][A-Za-z0-9_]*)*', query)
        symbols = [s for s in tokens if re.search(r'(?:^|\.)[A-Z][A-Za-z0-9_]+$', s) and s not in ('Go', 'API')]
        if symbols:
            chosen = max(symbols, key=len)
            if '.' not in chosen:
                position = tokens.index(chosen)
                package = tokens[position - 1] if position else ''
                if package and re.fullmatch(r'[A-Z][A-Za-z0-9_]+', package):
                    chosen = package + '.' + chosen
                    package = tokens[position - 2] if position > 1 else ''
                if package and re.fullmatch(r'[a-z][a-z0-9_/]*', package) and package not in STOP:
                    chosen = package.rsplit('/', 1)[-1] + '.' + chosen
            elif '/' in chosen.split('.')[0]:
                chosen = chosen.rsplit('/', 1)[-1]
            return {'q': chosen, 'm': 'symbol'}
        cleaned = ' '.join(t for t in tokens if t.casefold() not in STOP | {'go', 'golang', 'api'})
        if not cleaned: raise SearchError('unsupported_option', 'Specify a Go package or symbol.')
        return {'q': cleaned, 'm': 'package'}

    def decode_response(self, raw):
        class Cards(Links):
            def __init__(self):
                super().__init__(); self.depth = 0; self.chip = 0; self.chip_text = ''; self.start = 0; self.standard = False; self.accepted = []; self.seen = 0
            def handle_starttag(self, tag, attrs):
                data = dict(attrs)
                if tag == 'div':
                    if self.depth: self.depth += 1
                    elif 'SearchSnippet' in data.get('class', '').split():
                        self.depth = 1; self.start = len(self.rows); self.standard = False; self.seen += 1
                if self.depth and tag == 'span':
                    if self.chip: self.chip += 1
                    elif 'go-Chip' in data.get('class', '').split(): self.chip = 1; self.chip_text = ''
                super().handle_starttag(tag, attrs)
            def handle_data(self, value):
                if self.chip: self.chip_text += value
                super().handle_data(value)
            def handle_endtag(self, tag):
                super().handle_endtag(tag)
                if tag == 'span' and self.chip:
                    self.chip -= 1
                    if not self.chip and ' '.join(self.chip_text.split()).casefold() == 'standard library': self.standard = True
                if tag == 'div' and self.depth:
                    self.depth -= 1
                    if not self.depth and self.standard: self.accepted.extend(self.rows[self.start:])
        text = raw.decode('utf-8', 'replace'); parser = Cards(); parser.feed(text)
        entries = []
        for attrs, title in parser.accepted:
            if attrs.get('data-test-id') != 'snippet-title': continue
            url = urllib.parse.urljoin('https://pkg.go.dev', attrs.get('href', ''))
            path = urllib.parse.urlsplit(url).path.strip('/')
            if not url.startswith('https://pkg.go.dev/') or not re.fullmatch(r'[a-z][a-z0-9_/]*(?:@go\d+\.\d+(?:\.\d+)?)?', path): continue
            entries.append({'title': ' '.join(title.split()) + ' — ' + path, 'url': url,
                            'snippet': 'Go standard library search result; read the document for API behavior.'})
        if not entries and not parser.seen and not re.search(r'No (?:packages|symbols|results)|did not match|No results', text, re.I):
            raise SearchError('invalid_response', 'Unrecognized Go package search page.')
        return {'results': entries}

    def normalize(self, raw, count):
        rows = [result(self.name, i, item) for i, item in enumerate(raw['results'][:count], 1)]
        for row in rows: row['content_kind'] = 'documentation_index'
        return rows, self.metadata({}, rows, count)


class CninfoSearch(SiteSource):
    name, label = 'cninfo', 'CNINFO public disclosure search'
    endpoint = 'https://www.cninfo.com.cn/new/fulltextSearch/full'
    sites = ('cninfo.com.cn',)
    search_scope = 'public_disclosure_fulltext_index_not_live_quotes'

    def build_search(self, args):
        self.check_site(args)
        payload = {'searchkey': args.query, 'pageNum': 1, 'pageSize': args.count,
                   'isfulltext': 'true', 'sortName': 'nothing', 'sortType': 'desc'}
        if '上市公司' in args.query:
            payload['searchkey'] = args.query.replace('上市公司', '').strip() or args.query
            payload['type'] = 'szb,cyb,hzb,kcb,bjs,hke'
        return payload

    def normalize(self, raw, count):
        entries = raw.get('announcements')
        if entries is None and raw.get('totalRecordNum') == 0: entries = []
        if not isinstance(entries, list): raise SearchError('invalid_response', 'Missing CNINFO disclosure results.')
        rows = []
        for entry in entries[:count]:
            if not isinstance(entry, dict): raise SearchError('invalid_response', 'Invalid CNINFO disclosure.')
            path = entry.get('adjunctUrl')
            if not isinstance(path, str) or not re.fullmatch(r'finalpage/\d{4}-\d{2}-\d{2}/[A-Za-z0-9_.-]+\.PDF', path, re.I):
                raise SearchError('invalid_response', 'Invalid CNINFO document destination.')
            millis = entry.get('announcementTime'); date = None
            if type(millis) in (int, float):
                try: date = datetime.fromtimestamp(millis / 1000, timezone(timedelta(hours=8))).date().isoformat()
                except (ValueError, OverflowError, OSError): raise SearchError('invalid_response', 'Invalid disclosure date.') from None
            item = {'title': plain(entry.get('announcementTitle')), 'url': 'https://static.cninfo.com.cn/' + path,
                    'snippet': plain(entry.get('announcementContent')), 'published': date,
                    'security_code': entry.get('secCode'), 'security_name': plain(entry.get('secName')),
                    'market': entry.get('pageColumn'),
                    'announcement_id': entry.get('announcementId'), 'page_body_read': False}
            rows.append(result(self.name, len(rows) + 1, item, published='published'))
        return rows, self.metadata({'total': raw.get('totalRecordNum'), 'pagination_fetched': False}, rows, count)


class StatisticsSearch(SiteSource):
    name, label = 'nbs-search', 'National Bureau of Statistics site search'
    endpoint = 'https://api.so-gov.cn/query/s'
    sites = ('stats.gov.cn', 'www.stats.gov.cn')
    method = 'POST'
    search_scope = 'official_site_selected_search_backend_not_statistical_database'

    def build_search(self, args):
        self.check_site(args)
        return {'siteCode': 'bm36000002', 'tab': '', 'qt': args.query, 'page': 1, 'pageSize': 10}

    def build_request(self, payload, key, version, *, fetch=False):
        if fetch: raise SearchError('unsupported_operation', 'This source only searches.')
        return urllib.request.Request(self.endpoint, data=urllib.parse.urlencode(payload).encode(), headers={
            'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'xcoze-search/' + version,
            'Accept': 'application/json'})

    def normalize(self, raw, count):
        if raw.get('ok') is not True or not isinstance(raw.get('resultDocs'), list):
            raise SearchError('provider_error', 'Statistics site search returned no valid result collection.')
        rows = []
        for entry in raw['resultDocs'][:count]:
            item = entry.get('data') if isinstance(entry, dict) else None
            if not isinstance(item, dict): raise SearchError('invalid_response', 'Invalid statistics search result.')
            url = item.get('url')
            if not isinstance(url, str) or not public_url(url) or not on_host(url, 'stats.gov.cn'):
                raise SearchError('invalid_response', 'Statistics search returned a destination outside its site.')
            date = item.get('docDate')
            if date is not None and (not isinstance(date, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date)):
                raise SearchError('invalid_response', 'Invalid statistics publication date.')
            if date:
                try: calendar_date.fromisoformat(date)
                except ValueError: raise SearchError('invalid_response', 'Invalid statistics publication date.') from None
            value = {'title': plain(item.get('titleO') or item.get('title')), 'url': url,
                     'snippet': plain(item.get('summary')), 'published': date,
                     'page_body_read': False, 'date_semantics': 'site_search_publication_date_not_statistical_period'}
            rows.append(result(self.name, len(rows) + 1, value, published='published'))
        return rows, self.metadata({'total_hits': raw.get('totalHits'), 'search_backend': 'api.so-gov.cn',
                                   'pagination_fetched': False}, rows, count)

    def normalize_search(self, raw, args):
        rows, meta = self.normalize(raw, 10)
        # A date followed by a day is a publication-date cue, not a statistical month.
        pattern = r'(?<!\d)(20\d{2})年\s*(1[0-2]|0?[1-9])月(?!\s*\d{1,2}日)'
        wanted = {(year, int(month)) for year, month in re.findall(pattern, args.query)}
        excluded = 0
        if len(wanted) == 1:
            matched, unknown = [], []
            for row in rows:
                observed = {(year, int(month)) for year, month in re.findall(pattern, row['title'])}
                if observed & wanted: matched.append(row)
                elif observed: excluded += 1
                else: unknown.append(row)
            rows = matched + unknown
        topic = re.sub(r'国家统计局|最新|近期|最近|官方|20\d{2}年|\d{1,2}月(?:份)?|\d{1,2}日', ' ', args.query)
        chinese_terms = re.findall(r'[\u3400-\u9fff]{2,}', topic)
        latin_terms = {s.casefold() for s in re.findall(r'[A-Za-z]{2,}', topic)}
        def title_score(row):
            title = row['title'].casefold()
            return sum(len(term) for term in chinese_terms if term in title) + 3 * sum(term in title for term in latin_terms)
        if len(wanted) == 1:
            # Keep known matching periods ahead of undated titles, then prefer topic matches.
            rows.sort(key=lambda row: (-bool(re.findall(pattern, row['title'])), -title_score(row)))
        else:
            rows.sort(key=lambda row: -title_score(row))
        rows = rows[:args.count]
        return rows, {**meta, 'shown_count': len(rows), 'excluded_conflicting_title_period_count': excluded,
                      'title_period_filter_applied': len(wanted) == 1}
