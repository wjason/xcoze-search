"""Bounded, keyless searches of public energy and procurement publications."""
from copy import copy
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
import re
import urllib.parse
import urllib.request

from content_sources import filter_snapshot
from native_search import Links, SiteSource, on_host, plain
from search_common import SearchError, invalid, public_url
from search_providers import dates, option, result

CHINA = timezone(timedelta(hours=8))
PROVINCES = dict(zip(
    ('北京 天津 河北 山西 内蒙古 辽宁 吉林 黑龙江 上海 江苏 浙江 安徽 福建 江西 山东 河南 湖北 湖南 广东 广西 海南 重庆 四川 贵州 云南 西藏 陕西 甘肃 青海 宁夏 新疆 兵团').split(),
    ('11 12 13 14 15 21 22 23 31 32 33 34 35 36 37 41 42 43 44 45 46 50 51 52 53 54 61 62 63 64 65 66').split()))
PROVINCES = {name: code + '0000' for name, code in PROVINCES.items()}


def province(value):
    if not value: return None
    if value in PROVINCES.values(): return value
    for suffix in ('壮族自治区', '回族自治区', '维吾尔自治区', '自治区', '省', '市'):
        if value.endswith(suffix): value = value[:-len(suffix)]; break
    if value not in PROVINCES: invalid('--region requires a Chinese province name or its six-digit province code.')
    return PROVINCES[value]


def day(value):
    if value is None or value == '': return None
    if not isinstance(value, str): raise SearchError('invalid_response', 'Invalid publication date.')
    try:
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value): return date.fromisoformat(value).isoformat()
        stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return (stamp.astimezone(CHINA) if stamp.tzinfo else stamp).date().isoformat()
    except ValueError:
        raise SearchError('invalid_response', 'Invalid publication date.') from None


def page_number(args):
    value = option(args, 'page')
    if value is None: return 1
    if type(value) is not int or not 1 <= value <= 100: invalid('--page must be 1..100; pages are never followed automatically.')
    return value


def title_match(title, query):
    # 仓储能力 contains the characters 储能 across a word boundary, but is not energy storage.
    return all(term in (title.replace('仓储能力', '') if term == '储能' else title).casefold()
               for term in query.casefold().split())


def classify(title):
    # A tender word inside an award/cancellation title does not make it an open tender.
    for kind, pattern in (
        ('cancel', '中止|终止|流标|废标'), ('correction', '澄清|更正|变更|补充公告'),
        ('candidate', '候选人|候选供应商'), ('award', '中标(?:结果)?(?:公告|公示)|成交(?:结果)?(?:公告|公示)|结果公示|结果公告'),
        ('tender', '招标公告|采购公告|磋商公告|谈判公告|询价公告|资审公告')):
        if re.search(pattern, title): return kind
    return 'public_notice'


class EnergyArchive(SiteSource):
    name, label = 'nea-archive', '国家能源局公开文件与新闻发布档案'
    sites = ('nea.gov.cn', 'www.nea.gov.cn')
    endpoint = 'https://www.nea.gov.cn/policy/ds_40d365c13659452aa06cdb7268d6192e.json'
    options = frozenset(('site', 'start_date', 'end_date', 'energy_section'))
    max_count = 20
    search_scope = 'finite_published_energy_archives_not_full_site_search'
    ARCHIVES = {
        'policy': endpoint,
        'releases': 'https://www.nea.gov.cn/xwfb/ds_4f3484af7ea244e7ab18d094856c82a6.json',
    }

    def capabilities(self):
        return {**super().capabilities(), 'archive_sections': dict(self.ARCHIVES),
                'query_sent_to_source': False, 'archive_complete': False,
                'documentation_url': 'https://www.nea.gov.cn/policy/zxwj.htm'}

    def section(self, args):
        selected = option(args, 'energy_section')
        if selected and selected not in self.ARCHIVES: invalid('--energy-section must be policy or releases.')
        return selected or ('releases' if re.search('用电量|装机|统计|交易电量|核发|核算|新闻发布', args.query) else 'policy')

    def build_search(self, args):
        self.check_site(args); dates(args)
        return {'section': self.section(args)}

    def build_request(self, payload, key, version, *, fetch=False):
        if fetch: raise SearchError('unsupported_operation', 'Energy archives only search published records.')
        if payload.get('section') not in self.ARCHIVES: invalid('Unknown energy archive.')
        return urllib.request.Request(self.ARCHIVES[payload['section']], headers={
            'User-Agent': 'xcoze-search/' + version, 'Accept': 'application/json'})

    def records(self, raw, section):
        if not isinstance(raw, dict) or not isinstance(raw.get('datasource'), list):
            raise SearchError('invalid_response', 'Unrecognized NEA published archive.')
        rows = []
        for item in raw['datasource']:
            if not isinstance(item, dict): raise SearchError('invalid_response', 'Invalid NEA record.')
            title = plain(item.get('showTitle') or item.get('title'))
            href = item.get('publishUrl')
            if not isinstance(href, str): raise SearchError('invalid_response', 'Missing NEA publication link.')
            url = urllib.parse.urljoin(self.ARCHIVES[section], href)
            if not public_url(url) or not on_host(url, 'nea.gov.cn'): continue
            if not title: continue
            mapped = {'title': title, 'url': url, 'snippet': plain(item.get('summary')),
                      'published_at': day(item.get('publishTime')), 'archive_section': section,
                      'listed_at': day(item.get('publishTime')),
                      'publication_semantics': 'archive_display_date_original_page_and_effective_dates_may_differ',
                      'original_publication_date_verified': False,
                      'page_body_read': False, 'issuing_organization': plain(item.get('sourceText')) or None}
            row = result(self.name, len(rows) + 1, mapped, published='published_at')
            row['content_kind'] = 'official_archive'; rows.append(row)
        return rows

    def normalize_search(self, raw, args):
        section = self.section(args); all_rows = self.records(raw, section)
        matching = copy(args)
        # The publisher has used both 电力统计数据 and 电力工业统计数据.
        # Retain all topic/date terms while allowing that intervening qualifier.
        matching.query = args.query.replace('电力工业统计', '电力 统计').replace('电力统计', '电力 统计')
        rows, meta = filter_snapshot(all_rows, matching)
        # The snapshot includes older records but is not a complete archive or a server query.
        return rows, {**self.metadata({}, all_rows, args.count), **meta,
                      'archive_section': section, 'historical_records': True, 'historical_search': False,
                      'matching_query': matching.query, 'query_rewritten_for_matching': matching.query != args.query,
                      'query_sent_to_source': False, 'archive_complete': False,
                      'date_filter_semantics': 'archive_display_date_not_original_publication_date',
                      'search_scope': self.search_scope, 'page_body_read': False}


class TradingSearch(SiteSource):
    name, label = 'ggzy-search', '全国公共资源交易平台公告检索'
    sites = ('ggzy.gov.cn', 'www.ggzy.gov.cn')
    endpoint = 'https://www.ggzy.gov.cn/information/pubTradingInfo/getTradList'
    method = 'POST'
    options = frozenset(('site', 'start_date', 'end_date', 'region', 'notice_type', 'business', 'trading_source', 'page'))
    max_count = 20
    search_scope = 'public_trading_notice_search_one_page'
    SOURCES = {'province': '1', 'central': '2', 'finance': '3'}
    STAGES = {'engineering': {'tender': '0101', 'award': '0104', 'correction': '0105'},
              'government': {'tender': '0201', 'award': '0202', 'contract': '0203', 'correction': '0204'}}

    def capabilities(self):
        return {**super().capabilities(), 'business_notice_types': self.STAGES,
                'trading_sources': self.SOURCES, 'page_limit': 100, 'automatic_pagination': False,
                'region_scope': 'Chinese province', 'default_time_window': 'website_last_three_months',
                'documentation_url': 'https://www.ggzy.gov.cn/deal/dealList.html'}

    def build_search(self, args):
        self.check_site(args); start, end = dates(args)
        region = province(option(args, 'region'))
        business = option(args, 'business')
        notice = option(args, 'notice_type')
        source = option(args, 'trading_source') or 'province'
        if source not in self.SOURCES: invalid('--trading-source must be province, central or finance.')
        if business not in (None, 'engineering', 'government'): invalid('--business must be engineering or government.')
        if notice and (not business or notice not in self.STAGES[business]):
            raise SearchError('unsupported_option', 'For trading notices, select --business and a compatible --notice-type (tender, award, correction, or government contract).')
        if source != 'province' and (region or notice):
            raise SearchError('unsupported_option', 'Region and notice-type filters are verified only for province-platform notices.')
        payload = {'FINDTXT': args.query, 'SOURCE_TYPE': self.SOURCES[source], 'PAGENUMBER': page_number(args), 'DEAL_TIME': '05'}
        if start or end:
            # Website validation requires both boundaries for a custom range.
            if not start or not end: invalid('Trading search requires both --start-date and --end-date.')
            payload.update(DEAL_TIME='06', TIMEBEGIN=start, TIMEEND=end)
        if region: payload['DEAL_PROVINCE'] = region
        if business: payload['DEAL_CLASSIFY'] = {'engineering': '01', 'government': '02'}[business]
        if notice: payload['DEAL_STAGE'] = self.STAGES[business][notice]
        return payload

    def build_request(self, payload, key, version, *, fetch=False):
        if fetch: raise SearchError('unsupported_operation', 'Trading search does not fetch notice bodies.')
        return urllib.request.Request(self.endpoint, data=urllib.parse.urlencode(payload).encode(), headers={
            'User-Agent': 'xcoze-search/' + version, 'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://www.ggzy.gov.cn/deal/dealList.html'}, method='POST')

    def check_error(self, raw):
        code = raw.get('code')
        if code in (829, 800):
            raise SearchError('access_challenge' if code == 829 else 'source_rate_limited',
                              'Trading website requires verification or a later retry; no verification is attempted.', category='rate_limit')
        if code != 200: raise SearchError('provider_error', 'Trading website rejected the query; refine filters or try later.')

    def normalize_search(self, raw, args):
        self.check_error(raw)
        payload = self.build_search(args)
        data = raw.get('data')
        if not isinstance(data, dict) or not isinstance(data.get('records'), list):
            raise SearchError('invalid_response', 'Unrecognized trading notice response.')
        if data.get('current') != payload['PAGENUMBER']:
            raise SearchError('constraint_not_applied', 'Trading website did not return the requested page.')
        rows, dropped = [], 0
        for index, item in enumerate(data['records'], 1):
            if not isinstance(item, dict): raise SearchError('invalid_response', 'Invalid trading notice.')
            href = item.get('url')
            if not isinstance(href, str): raise SearchError('invalid_response', 'Missing trading notice URL.')
            url = urllib.parse.urljoin('https://www.ggzy.gov.cn/', href)
            if not public_url(url) or not on_host(url, 'ggzy.gov.cn'):
                raise SearchError('invalid_response', 'Trading result is outside the official publication scope.')
            title = plain(item.get('title')); published = day(item.get('publishTime'))
            start, end = dates(args)
            stage=classify(title)
            if (not title_match(title, args.query) or
                (option(args,'notice_type')=='award' and stage in ('candidate','cancel','correction')) or
                ((start or end) and (not published or (start and published < start) or (end and published > end))) or
                (payload.get('DEAL_PROVINCE') and item.get('province') != payload['DEAL_PROVINCE']) or
                (payload.get('DEAL_STAGE') and item.get('informationType') != payload['DEAL_STAGE']) or
                (option(args, 'business') and item.get('businessTypeText') != {'engineering': '工程建设', 'government': '政府采购'}[args.business])):
                dropped += 1; continue
            mapped = {'title': title, 'url': url, 'snippet': '', 'published_at': published,
                      'region': item.get('provinceText'), 'region_code': item.get('province'),
                      'source_platform': item.get('transactionSourcesPlatformText'),
                      'business_type': item.get('businessTypeText'), 'notice_type': item.get('informationTypeText'),
                      'notice_type_code': item.get('informationType'), 'notice_stage': classify(title),
                      'project_number': item.get('tenderProjectCode'), 'buyer': None,
                      'deadline': item.get('deadline'), 'deadline_verified': False, 'page_body_read': False,
                      'open_for_bidding': None, 'trading_source': option(args, 'trading_source') or 'province'}
            row = result(self.name, index, mapped, published='published_at'); row['content_kind'] = 'procurement_notice'
            rows.append(row)
        return rows[:args.count], {**self.metadata({}, rows, args.count),
            'source_row_count': len(data['records']), 'excluded_by_constraints': dropped,
            'source_total': data.get('total'), 'page': data.get('current'), 'source_pages': data.get('pages'),
            'pagination_fetched': False, 'page_body_read': False, 'window_complete': False,
            'default_time_window': None if option(args, 'start_date') else 'website_last_three_months',
            'date_semantics': 'publication_date_not_bid_deadline',
            'filter_semantics': 'website_query_then_all_literal_terms_in_title_and_explicit_constraints'}


class CSGNotices(SiteSource):
    name, label = 'csg', '南方电网公开采购公告列表'
    endpoint = 'https://www.bidding.csg.cn/zbgg/index.jhtml'
    sites = ('bidding.csg.cn', 'www.bidding.csg.cn')
    options = frozenset(('site', 'start_date', 'end_date', 'notice_type', 'page'))
    search_scope = 'one_public_list_page_local_title_filter_not_site_search'
    max_count = 10
    CHANNELS = {'tender': 'zbgg', 'non-tender': 'fzbgg', 'award': 'zbhxrgs',
                'candidate': 'zbhxrgs', 'correction': 'zbhxrgs', 'cancel': 'zbhxrgs'}

    def capabilities(self):
        return {**super().capabilities(), 'notice_types': list(self.CHANNELS),
                'default_notice_type': 'tender', 'page_limit': 100, 'automatic_pagination': False,
                'site_keyword_search': False, 'query_sent_to_source': False,
                'documentation_url': self.endpoint}

    def build_search(self, args):
        self.check_site(args); dates(args)
        kind = option(args, 'notice_type') or 'tender'
        if kind not in self.CHANNELS: raise SearchError('unsupported_option', 'Unsupported Southern Grid notice type.')
        return {'channel': self.CHANNELS[kind], 'page': page_number(args)}

    def build_request(self, payload, key, version, *, fetch=False):
        if fetch: raise SearchError('unsupported_operation', 'This source reads public list pages only.')
        if payload.get('channel') not in self.CHANNELS.values() or type(payload.get('page')) is not int or not 1 <= payload['page'] <= 100:
            invalid('Invalid public notice list.')
        suffix = '' if payload['page'] == 1 else '_' + str(payload['page'])
        url = 'https://www.bidding.csg.cn/' + payload['channel'] + '/index' + suffix + '.jhtml'
        return urllib.request.Request(url, headers={'User-Agent': 'xcoze-search/' + version, 'Accept': 'text/html'})

    def decode_response(self, raw):
        try: html = raw.decode('utf-8') if isinstance(raw, bytes) else raw
        except UnicodeError: raise SearchError('invalid_response', 'Invalid public notice page.') from None
        if not isinstance(html, str): raise SearchError('invalid_response', 'Invalid public notice page.')
        if re.search('访问过于频繁|验证码|访问被拒绝|人机验证', plain(html)):
            raise SearchError('access_challenge', 'Public notice website requires verification; no verification is attempted.', category='rate_limit')
        entries = []
        for fragment in re.findall(r'<li\b[^>]*>(.*?)</li>', html, re.S | re.I):
            parser = Links(); parser.feed(fragment)
            for attrs, text in parser.rows:
                href = attrs.get('href', '')
                if not re.fullmatch(r'/(?:zbgg|fzbgg|zbhxrgs)/\d+\.jhtml', href): continue
                title = plain(attrs.get('title') or text)
                # Read the displayed date node before flattening inline spans: the
                # adjacent numbered badge would otherwise turn 2026-11-16 into ...161.
                date_match = re.search(r'>\s*(20\d{2}-\d{2}-\d{2})\s*<', fragment)
                publisher = next((plain(t) for a, t in parser.rows if 'Blue' in a.get('class', '') and not a.get('href')), None)
                stage=classify(title)
                category=next((plain(t) for a,t in parser.rows if re.fullmatch(r'/(?:zbgg|fzbgg|zbhxrgs)/index\.jhtml',a.get('href',''))),None)
                if stage=='public_notice' and category=='招标公告':stage='tender'
                entries.append({'title': title, 'url': 'https://www.bidding.csg.cn' + href,
                                'snippet': '', 'published_at': day(date_match[1]) if date_match else None,
                                'publisher': publisher, 'notice_stage': stage,
                                'notice_stage_basis':'published_category' if classify(title)=='public_notice' else 'explicit_title',
                                'title_truncated': title.endswith(('...', '…')), 'page_body_read': False,
                                'project_number': None, 'buyer': None, 'deadline': None,
                                'deadline_verified': False, 'open_for_bidding': None})
        if not entries: raise SearchError('invalid_response', 'Public list has no recognized procurement entries; not treated as an empty search.')
        following=re.search(r'<a\b[^>]*href=[\"\']index_(\d+)\.jhtml[\"\'][^>]*>\s*下一页',html,re.I)
        return {'entries': entries,'next_page':int(following[1]) if following else None}

    def normalize_search(self, raw, args):
        payload = self.build_search(args); kind = option(args, 'notice_type') or 'tender'
        all_rows = []
        for i, item in enumerate(raw['entries'], 1):
            row = result(self.name, i, item, published='published_at'); row['content_kind'] = 'procurement_notice'
            all_rows.append(row)
        selected = [r for r in all_rows if (kind == 'non-tender' or r['provider_fields']['notice_stage'] == kind)]
        rows, meta = filter_snapshot(selected, args)
        return rows, {**self.metadata({}, all_rows, args.count), **meta,
                      'source_row_count': len(all_rows), 'notice_type': kind, 'page': payload['page'],
                      'query_sent_to_source': False, 'pagination_fetched': False,
                      'next_page':raw.get('next_page'),
                      'site_keyword_search': False, 'page_body_read': False,
                      'excluded_other_notice_stages': len(all_rows) - len(selected)}


class SearchForm(HTMLParser):
    def __init__(self):super().__init__();self.values={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='input' and a.get('name') in ('q','channelId'):self.values[a['name']]=a.get('value','')


class CSGSearch(CSGNotices):
    name,label='csg-search','南方电网官网关键词搜索'
    endpoint='https://www.bidding.csg.cn/dbsearch.jspx'
    search_scope='published_website_fulltext_search_one_page_original_verification_required'
    CHANNEL_IDS={'zbgg':'52','fzbgg':'57','zbhxrgs':'310'}

    def access_scope(self,payload):return 'csg'

    def capabilities(self):
        return {**super().capabilities(),'site_keyword_search':True,'query_sent_to_source':True,
                'search_scope':self.search_scope,'date_filter_semantics':'returned_page_publication_dates_local_filter'}

    def build_search(self,args):
        payload=super().build_search(args)
        if not args.query.strip() or len(args.query)>50:invalid('Southern Grid website queries must contain 1..50 characters.')
        return {**payload,'query':args.query}

    def build_request(self,payload,key,version,*,fetch=False):
        if fetch:raise SearchError('unsupported_operation','Southern Grid search does not read originals.')
        if payload.get('channel') not in self.CHANNEL_IDS or type(payload.get('page')) is not int or not 1<=payload['page']<=100:
            invalid('Invalid Southern Grid search scope.')
        query=payload.get('query')
        if not isinstance(query,str) or not query.strip() or len(query)>50:invalid('Invalid Southern Grid query.')
        fields={'channelId':self.CHANNEL_IDS[payload['channel']],'q':query,'types':'','org':'','pageNo':payload['page']}
        return urllib.request.Request(self.endpoint+'?'+urllib.parse.urlencode(fields),headers={
            'User-Agent':'xcoze-search/'+version,'Accept':'text/html'})

    def decode_response(self,raw):
        html=raw.decode('utf-8') if isinstance(raw,bytes) else raw
        form=SearchForm();form.feed(html)
        try:decoded=super().decode_response(html)
        except SearchError as exc:
            # An explicit zero-count result is different from an unrecognized shell.
            if exc.code!='invalid_response' or not re.search(r'共\s*0\s*条记录',plain(html)):raise
            decoded={'entries':[],'next_page':None}
        decoded['search_form']=form.values
        pager=re.search(r'共\s*(\d+)\s*条记录\s*(\d+)\s*/\s*(\d+)\s*页',plain(html))
        decoded['current_page']=int(pager[2]) if pager else None
        decoded['source_total']=int(pager[1]) if pager else None
        return decoded

    def normalize_search(self,raw,args):
        payload=self.build_search(args);form=raw.get('search_form',{})
        if form.get('q')!=payload['query'] or form.get('channelId')!=self.CHANNEL_IDS[payload['channel']]:
            raise SearchError('constraint_not_applied','Southern Grid did not echo the requested query and notice channel.')
        if raw.get('current_page') not in (None,payload['page']) or payload['page']>1 and raw.get('current_page')!=payload['page']:
            raise SearchError('constraint_not_applied','Southern Grid did not return the requested search page.')
        kind=option(args,'notice_type') or 'tender'
        eligible=[r for r in raw['entries'] if kind=='non-tender' or r['notice_stage']==kind]
        rows=[]
        for i,item in enumerate(eligible,1):
            mapped={**item,'query_match_basis':'website_fulltext_search_original_not_verified'}
            row=result(self.name,i,mapped,published='published_at');row['content_kind']='procurement_notice';rows.append(row)
        # The website searches beyond truncated titles. Preserve its candidates, then check originals.
        date_args=copy(args);date_args.query=''
        selected,meta=filter_snapshot(rows,date_args)
        return selected,{**self.metadata({},rows,args.count),**meta,'query_sent_to_source':True,
            'site_keyword_search':True,'page_body_read':False,'page':payload['page'],
            'source_row_count':len(raw['entries']),'date_filter_semantics':'returned_page_publication_dates',
            'query_match_basis':'website_fulltext_search_original_not_verified',
            'filter_semantics':'website_fulltext_query_then_explicit_date_and_notice_stage_filters',
            'source_total':raw.get('source_total'),
            'pagination_fetched':False,'next_page':None,'window_complete':False}
