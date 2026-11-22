"""Document identity and explicit evidence gaps, never a semantic truth score."""
from datetime import date
import hashlib
import re
import urllib.parse
from search_quality import STOP

TRACKING = frozenset(('fbclid','gclid','msclkid','spm'))


def canonical(url):
    p = urllib.parse.urlsplit(url)
    from native_reader import HOSTS
    scheme='https' if p.scheme.lower()=='http' and p.hostname in HOSTS else p.scheme.lower()
    query = [(k,v) for k,v in urllib.parse.parse_qsl(p.query,keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in TRACKING]
    return urllib.parse.urlunsplit((scheme,p.netloc.lower(),p.path or '/',urllib.parse.urlencode(sorted(query)),''))


def merge_results(rows):
    merged, groups = [], {}
    for original in rows:
        row = dict(original); key = canonical(row['url'])
        origin = {'provider':row.get('provider'),'rank':row.get('rank'),'url':row['url']}
        origins=original.get('retrieved_by') or [origin]
        if key in groups:
            kept = merged[groups[key]]
            kept['retrieved_by'].extend(o for o in origins if o not in kept['retrieved_by'])
            # Keep richer evidence without changing the published URL or its version.
            for field in ('content','snippet','summary'):
                if len(row.get(field) or '') > len(kept.get(field) or ''): kept[field] = row[field]
        else:
            row.update(document_id=hashlib.sha256(key.encode()).hexdigest()[:16], retrieved_by=list(origins))
            groups[key] = len(merged); merged.append(row)
    titles = {}
    for row in merged:
        title = re.sub(r'\W+','',row.get('title','')).casefold()
        if len(title)>=12: titles.setdefault(title,[]).append(row['document_id'])
    for row in merged:
        title = re.sub(r'\W+','',row.get('title','')).casefold()
        row['possible_republications'] = [i for i in titles.get(title,[]) if i != row['document_id']]
        row['source_independence'] = 'not_established' # Search services are not independent publications.
    return merged


def required_terms(query, supplied=None):
    if supplied: return list(dict.fromkeys(t.casefold().strip() for t in supplied if t.strip()))[:12]
    latin = [t.casefold() for t in re.findall(r'[A-Za-z][A-Za-z0-9_.]*',query)
             if len(t)>2 and t.casefold() not in STOP]
    cjk = re.findall(r'[\u3400-\u9fff]{2,}',re.sub('官方|文档|查询|搜索|最新|近期|是什么|如何|多少',' ',query))
    return list(dict.fromkeys(latin+cjk))[:12]


def assess(rows, documents, args):
    terms = required_terms(args.query, getattr(args,'require_topic',None))
    read = [d for d in documents if d.get('page_body_read') and d.get('content')]
    text = '\n'.join('\n'.join(p['text'] for p in d['passages']) if 'passages' in d else d.get('content','') for d in read).casefold()
    matched = [t for t in terms if t in text]
    missing = [t for t in terms if t not in text]
    gaps = []
    if not rows: gaps.append('no_search_candidates')
    if not read: gaps.append('no_read_original')
    if missing: gaps.append('required_terms_not_in_read_text')
    minimum = getattr(args,'min_documents',1)
    if len({canonical(d.get('source_url') or d['url']) for d in read}) < minimum:
        gaps.append('insufficient_distinct_documents')
    start,end = getattr(args,'start_date',None),getattr(args,'end_date',None)
    dated = 0
    for doc in read:
        if doc.get('requested_anchor') and not doc.get('anchor_found'):gaps.append('requested_anchor_not_found')
        stamp = doc.get('publication_date')
        if stamp:
            try: date.fromisoformat(stamp)
            except ValueError: stamp = None
        if start or end:
            if not stamp:
                gaps.append('original_publication_date_unknown')
            elif (start and stamp < start) or (end and stamp > end): gaps.append('original_publication_date_outside_range')
            else: dated += 1
    return {'assessment':'literal_evidence_coverage_not_fact_verification', 'required_terms':terms,
            'matched_terms':matched, 'missing_terms':missing,'read_documents':len(read),
            'date_confirmed_documents':dated, 'gaps':list(dict.fromkeys(gaps)),
            'enough_for_agent_review':bool(read) and not gaps, 'facts_verified':False,
            'next_actions':(['Review the cited passages and verify the requested claim.'] if not gaps else
                ['Use the preserved scope and filters to reformulate a short query or read another permitted original.'])}


def observations(content):
    """Explicit labels with adjacent dates, not inferred deadlines or active bid status."""
    content='\n'.join(line.strip() for line in content.splitlines() if line.strip())
    found=[]
    pattern=r'(提交投标文件截止时间|递交截止时间|投标截止时间|响应文件提交截止时间)(?!\s*(?:当天|当日|前|后))(?:[^\d\n]{0,60}|[^\d]{0,40}\n\s*)(20\d{2})\s*[-年]\s*(\d{1,2})\s*[-月]\s*(\d{1,2})\s*日?([^\n。；]{0,55})'
    for match in re.finditer(pattern,content):
        try:stamp=date(int(match[2]),int(match[3]),int(match[4])).isoformat()
        except ValueError:continue
        clock=re.search(r'(\d{1,2})\s*[:时]\s*(\d{1,2})',match[5])
        if clock and int(clock[1])<24 and int(clock[2])<60:stamp+='T%02d:%02d'%(int(clock[1]),int(clock[2]))
        if stamp in [f['value'] for f in found]:continue
        found.append({'field':'bid_deadline','value':stamp,'basis':'explicit_labeled_original_text',
            'text':match[0][:200],'line':content[:match.start()].count('\n')+1,
            'timezone':'Asia/Shanghai' if '北京时间' in content[max(0,match.start()-100):match.end()+100] else None,
            'open_for_bidding':None})
        if len(found)>=6:break
    return found


def passages(content, terms, *, count=4, characters=650, question=''):
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    candidates=[]
    for index,line in enumerate(lines):
        if not any(t in line.casefold() for t in terms):continue
        start=max(0,index-2);end=min(len(lines),index+4)
        excerpt='\n'.join(lines[start:end])
        if len(excerpt)>characters:
            # Keep a matched term inside the clipped window rather than truncating it away.
            positions=[excerpt.casefold().find(t) for t in terms if t in line.casefold() and t in excerpt.casefold()]
            offset=max(0,min(positions or [0])-180);start+=excerpt[:offset].count('\n');excerpt=excerpt[offset:offset+characters]
        matches={t for t in terms if t in excerpt.casefold()}
        if matches:candidates.append((matches,start,start+excerpt.count('\n')+1,excerpt))
    selected=[];uncovered=set(terms)
    if re.search('截止|deadline',question,re.I):
        for fact in observations(content)[:1]:
            start=max(0,fact['line']-2);text='\n'.join(lines[start:start+4])[:characters]
            selected.append({'text':text,'line':start+1,'line_end':start+text.count('\n')+1,
                             'matched_terms':[t for t in terms if t in text.casefold()],
                             'kind':'literal_excerpt_not_generated_answer'})
            uncovered-={t for t in terms if t in text.casefold()}
    while candidates and len(selected)<count:
        best=max(candidates,key=lambda c:(len(c[0]&uncovered),len(c[0]),min(len(c[3]),400),-c[1]))
        matches,start,end,excerpt=best;candidates.remove(best)
        if not matches&uncovered and selected:break
        if any(excerpt in p['text'] for p in selected):continue
        selected.append({'text':excerpt,'line':start+1,'line_end':end,
                         'matched_terms':sorted(matches),'kind':'literal_excerpt_not_generated_answer'})
        uncovered-=matches
    return selected
