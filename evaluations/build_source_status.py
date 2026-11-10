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

AUDIT = ROOT / 'evaluations/reports/2026-11-05-source-status.json'
CANDIDATES = ROOT / 'research/free-sources-2026-11.data.json'
SCOPED_ZH = {'zhihu':'知乎','xiaohongshu':'小红书','weibo':'微博','youtube':'YouTube','bilibili':'B 站','reddit':'Reddit','twitter':'X','v2ex':'V2EX','douban':'豆瓣','china-data':'国家数据','cma-data':'中国气象数据中心','china-weather':'中国天气网','cninfo':'巨潮资讯','sse':'上海证券交易所','szse':'深圳证券交易所','bse':'北京证券交易所','china-standards':'国家标准公开系统','china-laws':'国家法律法规数据库','cnsa':'国家航天局','scidb':'科学数据银行','ceic':'中国地震台网','nmefc':'国家海洋预报台','hko':'香港天文台'}
FETCH_ZH = {'github':'GitHub README','hackernews':'Hacker News 单条','jina':'Jina Reader','exa-free':'Exa MCP 网页阅读','community-python':'Python 社区主帖','community-rust':'Rust 社区主帖','community-v2ex':'V2EX 社区主帖'}
LABEL_EN = {'wikipedia':'Wikipedia (English / Chinese)', 'govcn':'China government latest policy', 'ndrc':'NDRC notices', 'nbs':'National Bureau of Statistics releases', 'nea':'National Energy Administration news', 'miit':'Ministry of Industry and Information Technology notices', 'mee':'Ministry of Ecology and Environment news', 'mem':'Ministry of Emergency Management statistics', 'pbc':'People’s Bank of China statistics', 'ggzy':'National Public Resource Trading Platform notices', 'mofcom':'Ministry of Commerce news', 'csrc':'China Securities Regulatory Commission information', 'ccgp':'China Government Procurement notices', 'cas':'Chinese Academy of Sciences research news', 'cgs':'China Geological Survey news', 'xinhua':'Xinhua news', 'cns-scroll':'China News Service latest RSS', 'cns-finance':'China News Service finance RSS', 'hk-data':'DATA.GOV.HK updates RSS', 'bbc-world':'BBC World RSS', 'yuanbao':'Tencent Yuanbao', 'bocha':'Bocha'}
FETCH_EN = {'github':'GitHub README','hackernews':'Hacker News item','jina':'Jina Reader','exa-free':'Exa MCP page reading','community-python':'Python community post','community-rust':'Rust community post','community-v2ex':'V2EX community post'}
# When a candidate becomes supported, update this set along with its adapter.
EXCLUDE = {'S007','S039','S040','S041','S042','S043','S044','S045','S046','S047','S048','S049','S050','S051','S052','S053','S054','S057','S062','S067','S073','S078','S116','S126','S131','S138','S139','S144','S145','S146','S147'}
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
    args=parser.parse_args()
    audit_path=args.audit.resolve()
    audit_rel=audit_path.relative_to(ROOT)
    audit=json.loads(audit_path.read_text()); by={(r['kind'],r['id']):r for r in audit['results']}
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
            text+='Checked: '+checked+' (Beijing time). Account-specific details and credentials are not published. [Sanitized test results](../'+str(audit_rel)+').\n'
        else:
            text='# 来源支持状态\n\n**简体中文** | [English](source-status.en.md)\n\n[返回来源列表](sources.md)\n\n'
            text+='每行对应一项具体能力。**支持 · 适配通过**表示本次环境中的实际样例返回了内容；它不是持续可用或准确率保证。受限、无命中和待配置仍表示已支持，但本次未验证成功。搜索与阅读分别记录。\n\n'
            text+='检查时间：'+checked+'，北京时间。公开记录不包含凭据和账号专属错误详情。[查看脱敏测试结果](../'+str(audit_rel)+')。\n'
        workflow = 'https://github.com/wjason/xcoze-search/actions/workflows/source-check.yml'
        local_check = '../evaluations/reports/2026-11-09-public-source-check.json'
        if english:
            text += f'\n[Latest scheduled checks]({workflow}) · [November 9 local check]({local_check}). The tables below retain the full support snapshot, including browser and keyed actions.\n'
        else:
            text += f'\n[查看持续巡检]({workflow}) · [11 月 9 日本地巡检]({local_check})。下表保留完整支持快照，包括浏览器与带 Key 的能力。\n'
        def table(title, items):
            nonlocal text
            text+='\n## '+title+'\n\n'+('| Source or action | Status |\n|---|---|\n' if english else '| 来源或能力 | 状态 |\n|---|---|\n')
            for title_,kind,name in items:
                row = by.get((kind, name))
                status = label_status(row, english)
                if row is None and (kind, name) == ('search', 'parallel-free'):
                    suffix = '.en' if english else ''
                    label = 'Supported · Passed Nov 10' if english else '支持 · 11 月 10 日实测通过'
                    status = f'[{label}](../evaluations/reports/2026-11-10-parallel-no-exa{suffix}.md)'
                text+='| '+title_.replace('|','&#124;')+' | '+status+' |\n'
        table('Search sources' if english else '搜索来源',[((LABEL_EN.get(n, PUBLIC_REGISTRY[n].label) if english else PUBLIC_REGISTRY[n].label),'search',n) for n in searches])
        table('Page and community reading' if english else '网页与社区阅读',[((FETCH_EN if english else FETCH_ZH).get(n, PUBLIC_REGISTRY[n].label if n in PUBLIC_REGISTRY else n),'fetch',n) for n in readers])
        table('Feeds and snapshots' if english else '订阅与栏目',[((LABEL_EN.get(n, FEEDS[n].label) if english else FEEDS[n].label),'feed',n) for n in FEEDS])
        table('Community trends' if english else '社区热点',[(TRENDING[n].label,'trending',n) for n in TRENDING])
        table('Site-scoped web search' if english else '网站定向搜索',[(SCOPED_ZH.get(n,n) + ' (`'+PLATFORMS[n]+'`)' if not english else n+' (`'+PLATFORMS[n]+'`)','scope',n) for n in scopes])
        table('Browser search' if english else '浏览器搜索',[(n,'browser',n) for n in ('360','bing','google')])
        table('Services using your API key' if english else '使用自己 Key 的服务',[((LABEL_EN.get(n, REGISTRY[n].label) if english else REGISTRY[n].label),'keyed',n) for n in REGISTRY])
        table('Page reading with an API key' if english else '使用 Key 的网页读取',[((LABEL_EN.get(n, REGISTRY[n].label) if english else REGISTRY[n].label) + (' · Fetch/Extract' if english else ' · 网页读取'),'keyed_fetch',n) for n,p in REGISTRY.items() if p.fetch_endpoint])
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
