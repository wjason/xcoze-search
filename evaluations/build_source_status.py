#!/usr/bin/env python3
"""Render bilingual support tables from a sanitized live audit and the provider registry."""
import argparse
import json
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from public_providers import PUBLIC_REGISTRY
from search_providers import REGISTRY
from content_sources import FEEDS
from public_trends import TRENDING
from search_routing import PLATFORMS, NATIVE_PLATFORMS
from source_health import SNAPSHOT, load_snapshot

AUDIT = ROOT / 'evaluations/reports/2026-11-05-source-status.json'
CANDIDATES = ROOT / 'research/free-sources-2026-11.data.json'
SCOPED_ZH = {'zhihu':'知乎','xiaohongshu':'小红书','weibo':'微博','youtube':'YouTube','bilibili':'B 站','reddit':'Reddit','twitter':'X','v2ex':'V2EX','douban':'豆瓣','china-data':'国家数据','cma-data':'中国气象数据中心','china-weather':'中国天气网','cninfo':'巨潮资讯','sse':'上海证券交易所','szse':'深圳证券交易所','bse':'北京证券交易所','china-standards':'国家标准公开系统','china-laws':'国家法律法规数据库','cnsa':'国家航天局','scidb':'科学数据银行','ceic':'中国地震台网','nmefc':'国家海洋预报台','hko':'香港天文台'}
FETCH_ZH = {'github':'GitHub README','hackernews':'Hacker News 单条','jina':'Jina Reader','exa-free':'Exa MCP 网页阅读','community-python':'Python 社区主帖','community-rust':'Rust 社区主帖','community-v2ex':'V2EX 社区主帖'}
LABEL_EN = {'wikipedia':'Wikipedia (English / Chinese)', 'govcn':'China government latest policy', 'ndrc':'NDRC notices', 'nbs':'National Bureau of Statistics releases', 'nea':'National Energy Administration news', 'miit':'Ministry of Industry and Information Technology notices', 'mee':'Ministry of Ecology and Environment news', 'mem':'Ministry of Emergency Management statistics', 'pbc':'People’s Bank of China statistics', 'ggzy':'National Public Resource Trading Platform notices', 'mofcom':'Ministry of Commerce news', 'csrc':'China Securities Regulatory Commission information', 'ccgp':'China Government Procurement notices', 'cas':'Chinese Academy of Sciences research news', 'cgs':'China Geological Survey news', 'xinhua':'Xinhua news', 'cns-scroll':'China News Service latest RSS', 'cns-finance':'China News Service finance RSS', 'hk-data':'DATA.GOV.HK updates RSS', 'bbc-world':'BBC World RSS', 'yuanbao':'Tencent Yuanbao', 'bocha':'Bocha'}
FETCH_EN = {'github':'GitHub README','hackernews':'Hacker News item','jina':'Jina Reader','exa-free':'Exa MCP page reading','community-python':'Python community post','community-rust':'Rust community post','community-v2ex':'V2EX community post'}
LABEL_ZH = {'docs':'Python / pandas / SQLAlchemy 文档索引', 'mdn':'MDN 英文文档',
            'site-docs':'Kubernetes / Rust 官方文档索引', 'go-docs':'Go 标准库包与符号',
            'cninfo':'巨潮资讯公告', 'nbs-search':'国家统计局站内搜索',
            'nea-archive':'国家能源局公开文件与发布档案', 'ggzy-search':'公共资源公告检索', 'csg':'南网公开采购列表'}
LABEL_EN.update({'nea-archive':'NEA published document and release archives',
                 'ggzy-search':'Public trading notice search', 'csg':'Southern Grid public procurement lists'})
FETCH_ZH['native-reader']='官方站点原生读取'
FETCH_EN['native-reader']='Native official-site original reader'
# When a candidate becomes supported, update this set along with its adapter.
EXCLUDE = {'S007','S039','S040','S041','S042','S043','S044','S045','S046','S047','S048','S049','S050','S051','S052','S053','S054','S057','S062','S067','S073','S078','S116','S126','S131','S138','S139','S144','S145','S146','S147'}
EXCLUDE.add('S021')  # Python documentation now has a tested index adapter.


def supplement_recent(by):
    """Merge dated focused checks without changing the historical audit file."""
    for filename, section, field in (
        ('2026-11-16-keyless-search.data.json', 'acceptance', 'records'),
        ('2026-11-16-native-search.data.json', 'focused', 'cases'),
        ('2026-11-16-energy-procurement.data.json', 'focused', 'cases'),
    ):
        path = ROOT / 'evaluations/reports' / filename
        if not path.exists(): continue
        report = json.loads(path.read_text(encoding='utf-8'))
        for check in report.get('source_checks', []):
            by[(check['kind'], check['id'])] = {**check, 'checked_at': report['checked_at']}
        groups = {}
        for row in report[section][field]:
            groups.setdefault(row.get('source') or row.get('provider'), []).append(row)
        for source, rows in groups.items():
            passed = all(row.get('ok') and row.get('results') for row in rows)
            by[('search', source)] = {'status': 'passed' if passed else 'limited',
                                      'checked_at': report['checked_at'],
                                      'errors': [e for row in rows for e in row.get('errors', [])]}
GROUPS = {'web':('通用搜索','Web search'),'docs':('技术文档','Technical docs'),'news':('新闻','News'),'cn-official':('中国政务','China government'),'global-official':('国际政务','International government'),'academic':('科研','Research'),'tech':('软件与代码','Software and code'),'community':('社区','Communities'),'knowledge':('知识与素材','Knowledge and media'),'archive':('档案','Archives'),'data':('环境与能源','Environment and energy'),'restricted':('平台接口','Platform APIs'),'patents':('专利','Patents'),'finance':('金融','Finance'),'podcasts':('音频','Audio')}

def label_status(row, english=False):
    if not row: return 'Supported · Not tested' if english else '支持 · 待验证'
    state = row.get('status')
    labels = {'passed':('支持 · 适配通过','Supported · Passed'), 'limited':('支持 · 本次受限','Supported · Limited'),
              'empty':('支持 · 本次无命中','Supported · No hits'), 'not_tested':('支持 · 待验证','Supported · Not tested'),
              'not_configured':('支持 · 待配置验证','Supported · Key needed'), 'error':('支持 · 本次受限','Supported · Limited')}
    text=labels.get(state,('支持 · 待验证','Supported · Not tested'))[int(english)]
    error=(row.get('errors') or [{}])[0]
    code=error.get('code') or row.get('error')
    http=error.get('http_status')
    if state == 'limited' and code and code != 'account_check_failed':
        reasons = {'irrelevant_results': ('结果不相关', 'irrelevant results'),
                   'access_challenge': ('出现验证', 'access challenge'),
                   'http_error': ('访问受限', 'access denied'),
                   'extraction_failed': ('未取得正文', 'content unavailable'),
                   'browser_no_results': ('未取得结果', 'no usable results'),
                   'source_cooldown': ('暂时冷却', 'cooldown'),
                   'timeout': ('请求超时', 'timed out')}
        reason = reasons.get(code, ('请求失败', 'request failed'))[int(english)]
        text += ' (' + reason + (', HTTP '+str(http) if http else '') + ')'
    return text

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit', type=Path, default=AUDIT, help='Sanitized audit JSON inside the repository')
    parser.add_argument('--latest', type=Path, default=SNAPSHOT, help='Latest sanitized public check; historical keyed checks remain separate')
    args=parser.parse_args()
    audit_path=args.audit.resolve()
    audit_rel=audit_path.relative_to(ROOT)
    audit=json.loads(audit_path.read_text()); by={(r['kind'],r['id']):r for r in audit['results']}
    supplement_recent(by)
    health=load_snapshot(args.latest)
    for key,row in health['actions'].items():
        existing=by.get(key,{})
        if (row.get('checked_at') or '') >= (existing.get('checked_at') or audit['checked_at']): by[key]=row
    checked=datetime.fromisoformat(audit['checked_at']).strftime('%Y-%m-%d %H:%M')
    candidates=json.loads(CANDIDATES.read_text())['entries']
    pending=[e for e in candidates if e.get('integration')=='candidate' and e['id'] not in EXCLUDE and e['category'] in GROUPS]
    searches=[n for n,p in PUBLIC_REGISTRY.items() if p.supports_search and n!='browser']
    readers=[n for n,p in PUBLIC_REGISTRY.items() if p.fetch_endpoint and n!='community']
    readers += ['community-python','community-rust','community-v2ex']
    scopes=[n for n in PLATFORMS if n not in NATIVE_PLATFORMS]
    for english in (False,True):
        out=ROOT/('references/source-status.en.md' if english else 'references/source-status.md')
        if english:
            text='# Source support status\n\n[简体中文](source-status.md) | **English**\n\n[Back to sources](sources.en.md)\n\n'
            text+='Each row describes a specific action. **Supported · Passed** means the live sample returned content in this environment; it is not an uptime or accuracy guarantee. Limited, no hits and key needed retain supported status but were not verified successfully. Searches and page reading are checked separately.\n\n'
            text+='Historical full snapshot: '+checked+' (Beijing time). Account-specific details and credentials are not published. [Sanitized test results](../'+str(audit_rel)+').\n'
        else:
            text='# 来源支持状态\n\n**简体中文** | [English](source-status.en.md)\n\n[返回来源列表](sources.md)\n\n'
            text+='每行对应一项具体能力。**支持 · 适配通过**表示本次环境中的实际样例返回了内容；它不是持续可用或准确率保证。受限、无命中和待配置仍表示已支持，但本次未验证成功。搜索与阅读分别记录。\n\n'
            text+='历史完整快照：'+checked+'，北京时间。公开记录不包含凭据和账号专属错误详情。[查看脱敏测试结果](../'+str(audit_rel)+')。\n'
        if health['checked_at']:
            text+=('\nLatest public check: ' if english else '\n最近公开巡检：')+health['checked_at']+(' · Samples expire after seven days. ' if english else ' · 样例七天后标记过期。')+('[Public snapshot](source-health.json).\n' if english else '[公开状态数据](source-health.json)。\n')
        workflow = 'https://github.com/wjason/xcoze-search/actions/workflows/source-check.yml'
        local_check = '../evaluations/reports/2026-11-09-public-source-check.json'
        if english:
            text += f'\n[Latest scheduled checks]({workflow}) · [November 9 local check]({local_check}). The tables below retain the full support snapshot, including browser and keyed actions.\n'
        else:
            text += f'\n[查看持续巡检]({workflow}) · [11 月 9 日本地巡检]({local_check})。下表保留完整支持快照，包括浏览器与带 Key 的能力。\n'
        suffix = '.en' if english else ''
        recent = f'../evaluations/reports/2026-11-16-native-search{suffix}.md'
        text += (f'\n[November 16 focused checks]({recent}) supplement the historical snapshot. Updated rows show their own check date.\n' if english else f'\n[11 月 16 日专项检查]({recent})补充历史快照，更新行单独标明检查日期。\n')
        industry = f'../evaluations/reports/2026-11-16-energy-procurement{suffix}.md'
        text += (f'\n[Energy and procurement checks]({industry}) cover NEA archives, trading queries and Southern Grid list pages without Exa or Parallel.\n' if english else f'\n[能源电力与招投标实测]({industry})覆盖能源局档案、公共资源查询和南网列表，运行时禁用 Exa、Parallel。\n')
        def table(title, items):
            nonlocal text
            text+='\n## '+title+'\n\n'+('| Source or action | Scope | Last checked | Status |\n|---|---|---|---|\n' if english else '| 来源或能力 | 适配范围 | 最近检查 | 状态 |\n|---|---|---|---|\n')
            for title_,kind,name in items:
                row = by.get((kind, name))
                status = label_status(row, english)
                stamp=(row.get('checked_at') or audit['checked_at'])[:10] if row else '—'
                if row and row.get('stale'): status += ' · ' + ('Check expired' if english else '检查已过期')
                if row is None and (kind, name) == ('search', 'parallel-free'):
                    suffix = '.en' if english else ''
                    label = 'Supported · Passed Nov 10' if english else '支持 · 11 月 10 日实测通过'
                    status = f'[{label}](../evaluations/reports/2026-11-10-parallel-no-exa{suffix}.md)'
                scope={'fetch':('原文或单帖读取','Original or single-post reading'), 'feed':('当前订阅窗口','Current feed window'),
                       'trending':('公开榜单快照','Public trending snapshot'), 'scope':('网站公开索引','Public site index'),
                       'search':('搜索结果与来源链接','Search results and source links'),
                       'keyed':('需配置对应服务 Key','Requires this service key'), 'keyed_fetch':('需配置 Key 的正文读取','Keyed original reading'),
                       'browser':('本机可选浏览器','Optional local browser')}.get(kind,('见来源说明','See source guide'))[int(english)]
                if name in ('nea-archive','csg'): scope=('有限档案/指定列表页','Finite archive / requested list page')[int(english)]
                if name in ('docs','site-docs'): scope=('官方文档目录与索引','Official document navigation/index')[int(english)]
                text+='| '+title_.replace('|','&#124;')+' | '+scope+' | '+stamp+' | '+status+' |\n'
        table('Search sources' if english else '搜索来源',[((LABEL_EN.get(n, PUBLIC_REGISTRY[n].label) if english else LABEL_ZH.get(n, PUBLIC_REGISTRY[n].label)),'search',n) for n in searches])
        table('Page and community reading' if english else '网页与社区阅读',[((FETCH_EN if english else FETCH_ZH).get(n, PUBLIC_REGISTRY[n].label if n in PUBLIC_REGISTRY else n),'fetch',n) for n in readers])
        table('Feeds and snapshots' if english else '订阅与栏目',[((LABEL_EN.get(n, FEEDS[n].label) if english else FEEDS[n].label),'feed',n) for n in FEEDS])
        table('Community trends' if english else '社区热点',[(TRENDING[n].label,'trending',n) for n in TRENDING])
        table('Site-scoped web search' if english else '网站定向搜索',[(SCOPED_ZH.get(n,n) + ' (`'+PLATFORMS[n]+'`)' if not english else n+' (`'+PLATFORMS[n]+'`)','scope',n) for n in scopes])
        table('Browser search' if english else '浏览器搜索',[(n,'browser',n) for n in ('360','bing','google')])
        table('Services using your API key' if english else '使用自己 Key 的服务',[((LABEL_EN.get(n, REGISTRY[n].label) if english else REGISTRY[n].label),'keyed',n) for n in REGISTRY])
        table('Page reading with an API key' if english else '使用 Key 的网页读取',[((LABEL_EN.get(n, REGISTRY[n].label) if english else REGISTRY[n].label) + (' · Fetch/Extract' if english else ' · 网页读取'),'keyed_fetch',n) for n,p in REGISTRY.items() if p.fetch_endpoint])
        text += ('\n## Pending industry capabilities\n\n| Capability | Status |\n|---|---|\n| CCGP full-site keyword search | Planned · Access-frequency warning in live check |\n| Southern Grid full-site keyword search | Planned · HTTP 403 in live check |\n| State Grid search | Planned · Not verified |\n\nPublic homepage/list capabilities remain listed separately above.\n' if english else '\n## 待支持的行业能力\n\n| 能力 | 状态 |\n|---|---|\n| 政府采购网全站关键词搜索 | 待支持 · 实测出现访问频繁提示 |\n| 南网全站关键词搜索 | 待支持 · 实测 HTTP 403 |\n| 国家电网搜索 | 待支持 · 尚未验证 |\n\n已支持的首页和公开列表能力在上方单独列出。\n')
        text+='\n## '+('Candidates' if english else '待支持的候选')+'\n\n'
        text+=('The following are research candidates, not a promise of support or availability. Items partially covered by existing adapters are omitted here; their current capabilities are listed above. [Full research](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md).\n' if english else '以下为调研候选，后续会根据价值和可行性逐步评估。已有部分搜索能力的来源不在此重复列出；当前能力见上表。[完整调研](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.md)。\n')
        for group,(zh,en) in GROUPS.items():
            items=[e for e in pending if e['category']==group]
            if not items:continue
            text+='\n<details>\n<summary>'+ (en if english else zh)+' ('+str(len(items))+')</summary>\n\n'
            text+=('| Candidate | Status |\n|---|---|\n' if english else '| 候选来源 | 状态 |\n|---|---|\n')
            for e in items:
                name=e['name'].replace('|','&#124;').replace('[','\\[').replace(']','\\]')
                url=e['source_url'].replace(' ','%20').replace(')','%29')
                text+='| ['+name+']('+url+') | '+('Planned' if english else '待支持')+' |\n'
            text+='\n</details>\n'
        out.write_text(text)
    print('Rendered statuses for',len(searches),'search providers,',len(scopes),'site scopes and',len(pending),'candidates')

if __name__=='__main__':main()
