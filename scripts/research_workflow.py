"""Bounded search/read loop. The host Agent retains semantic judgment."""
from copy import copy
from datetime import datetime, timezone
import re
import shutil
import time
import urllib.parse

from search_common import SearchError, RequestBudget
from research_evidence import assess, canonical, merge_results, observations, passages, required_terms
from native_reader import checked_url


def follow_up_links(doc,args,terms):
    """Only links the publisher supplied; one same-host PDF and one delegated example at most."""
    source=doc.get('source_url') or doc['url'];host=urllib.parse.urlsplit(source).hostname
    def allowed(link):
        try:return urllib.parse.urlsplit(checked_url(link['url'])).hostname==host and canonical(link['url'])!=canonical(source)
        except (SearchError,KeyError,TypeError,ValueError):return False
    question=getattr(args,'question',None) or args.query
    text='\n'.join(p['text'] for p in doc.get('passages',[])).casefold()
    from research_evidence import contains_term
    missing=any(not contains_term(text,t) for t in terms)
    selected=[]
    detail=bool(re.search('目标|装机|预算|条件|细则|多少|金额|capacity|target|threshold|requirement',question,re.I))
    sparse_notice=len(doc.get('content',''))<1600 and bool(re.search('现予印发|附件|attached|attachment',doc.get('content',''),re.I))
    has_number=bool(re.search(r'\d+(?:\.\d+)?\s*(?:亿|万)?\s*(?:千瓦|兆瓦|GW|MW|%|亿元|万元)',text,re.I))
    if missing or detail and sparse_notice and not has_number:
        pdfs=[link for link in doc.get('attachments',[]) if allowed(link) and re.search(r'\.pdf(?:$|\?)',link['url'],re.I)]
        scored=[(sum(contains_term(link.get('title',''),t) for t in terms),link) for link in pdfs]
        if scored:
            score,link=max(scored,key=lambda pair:pair[0])
            if score or len(scored)==1:selected.append({**link,'relationship':'attachment','reason':'missing_detail_in_original','enabled':getattr(args,'attachments','auto')!='off'})
    has_example=any(p.get('kind')=='literal_code_block' and p.get('context_complete') and len(p['text'])>80 and all(contains_term(p['text'],t) for t in terms) for p in doc.get('passages',[]))
    if not has_example and re.search('如何|怎么|怎样|取消|示例|how|abort|example|implement',question,re.I):
        examples=[link for link in doc.get('related_reading',[]) if allowed(link)]
        if examples:selected.append({**examples[0],'relationship':'example','reason':'publisher_delegated_example','enabled':getattr(args,'context_links','auto')!='off'})
    return selected


def run_research(args,config,runtime):
    started=time.monotonic(); budget=RequestBudget(args.max_requests)
    scope=runtime.scoped_args(args); route=runtime.plan(scope,config,runtime.credential)
    requested=getattr(args,'provider','auto')
    sources=route['execution_candidates']
    # An explicit provider/list remains explicit; automatic mode can continue only within the original plan.
    if requested!='auto': sources=requested.split(',') if requested not in ('both','all') else route['execution_candidates']
    rows=[]; documents=[]; events=[]; errors=[]; seen=set(); reads=0
    terms=required_terms(args.query,getattr(args,'require_topic',None))
    coverage=assess([],[],scope)
    def remaining(): return args.max_seconds-(time.monotonic()-started)
    def follow_up_disabled():
        return bool(coverage['gaps']) and all(g.endswith('_follow_up_not_read') for g in coverage['gaps']) and any(
            r['status']=='disabled' for d in documents for r in d.get('follow_up_reads',[]))
    followed=set()
    def read_original(row,parent=None,link=None):
        nonlocal reads
        key=canonical(row['url'])
        if key in seen or reads>=args.read_count or remaining()<1 or not budget.data()['remaining']:return None
        seen.add(key);reads+=1
        fetch_args=runtime.parser().parse_args(['fetch',row['url'],'--strategy',route['strategy'],
            '--max-characters',str(args.max_read_characters),'--retries','0'])
        if parent is not None:fetch_args.provider='native-reader'
        fetch_args.timeout=min(args.timeout,remaining());fetch_args.max_seconds=max(1,int(remaining()))
        fetch_args.focus_terms=terms;fetch_args.focus_question=getattr(args,'question',None) or args.query
        try:
            if link and link['relationship']=='attachment' and not shutil.which('pdftotext'):
                raise SearchError('reader_dependency_missing','Attachment text needs an existing pdftotext; no software is installed.')
            fetched=runtime.run_fetch(fetch_args,config,budget=budget)
            seen.add(canonical(fetched.get('source_url') or row['url']))
            doc={k:fetched.get(k) for k in ('title','url','source_url','directory_url','content_kind',
                'publication_date','publication_date_basis','truncated','extraction_scope','pdf_pages_requested',
                'pdf_pages_extracted','requested_anchor','anchor_found','anchor_basis','attachments','attachments_read','related_reading') if k in fetched}
            doc.update(document_id=row['document_id'],provider=fetched.get('provider'),
                page_body_read=bool(fetched.get('content','').strip()) and fetched.get('page_body_read',True),
                content=fetched.get('content',''),search_date=row.get('published_at'),
                search_date_semantics=row.get('provider_fields',{}).get('publication_semantics'),
                passages=passages(fetched.get('content',''),terms,question=fetch_args.focus_question,
                    code_blocks=fetched.get('code_blocks'),pdf_page_spans=fetched.get('pdf_page_spans')),
                observations=observations(fetched.get('content','')),facts_verified=False)
            if parent is not None:
                doc.update(relationship=link['relationship'],parent_document_id=parent['document_id'],parent_url=parent.get('source_url') or parent['url'],
                    date_context={'basis':'parent_page_date_not_child_publication_date','parent_publication_date':parent.get('publication_date')},
                    follow_up_reason=link['reason'])
                if not doc.get('title'):
                    doc.update(title=link.get('title',''),title_basis='published_link_text')
            if doc.get('publication_date') and doc.get('search_date'):
                doc['search_and_original_dates_differ']=doc['publication_date']!=doc['search_date']
            documents.append(doc)
            events.append({'stage':'follow_up' if parent else 'read','url':row['url'],'page_body_read':doc['page_body_read'],
                           'relationship':link['relationship'] if link else None,'requests':fetched.get('requests',[]),'attempts':fetched.get('attempts',0)})
            errors.extend(fetched.get('errors',[]))
            return doc
        except SearchError as exc:
            errors.append({'stage':'follow_up' if parent else 'read','url':row['url'],**exc.data()})
            return None
    for source in sources:
        if remaining()<1 or not budget.data()['remaining']: break
        one=copy(scope);one.provider=source;one.timeout=min(args.timeout,8,remaining());one.retries=0
        # Keep the strategy resolved for this task, including a hard free boundary.
        one.strategy=route['strategy'] if requested=='auto' else getattr(args,'strategy',None)
        try:
            result=runtime.run_search(one,config,budget=budget)
            rows=merge_results(rows+result['results']); errors.extend(result.get('errors',[]))
            events.append({'stage':'search','provider':source,'count':len(result['results']),
                           'requests':result.get('requests',[])})
            # Only follow the finite list's actual published next-page link on a true empty window.
            # Explicit user pages are never replaced or expanded.
            if source=='csg' and not getattr(scope,'page',None) and not result['results'] and not result.get('errors'):
                for unused in range(getattr(args,'page_count',2)-1):
                    next_page=next((r.get('next_page') for r in result.get('requests',[]) if r.get('next_page')),None)
                    if not next_page or remaining()<1 or not budget.data()['remaining']:break
                    one.page=next_page;one.timeout=min(args.timeout,8,remaining())
                    result=runtime.run_search(one,config,budget=budget)
                    rows=merge_results(rows+result['results']);errors.extend(result.get('errors',[]))
                    events.append({'stage':'search_next_page','provider':source,'page':next_page,
                                   'count':len(result['results']),'requests':result.get('requests',[])})
                    if result['results'] or result.get('errors'):break
        except SearchError as exc:
            errors.append({'provider':source,**exc.data()});continue
        reads_this_source=0
        for row in rows:
            key=canonical(row['url'])
            if key in seen or reads>=args.read_count or remaining()<1 or not budget.data()['remaining']: continue
            reads_this_source+=1
            doc=read_original(row)
            if doc and doc['provider']=='native-reader':
                for link in follow_up_links(doc,args,terms):
                    kind=link['relationship']
                    if kind in followed:continue
                    followed.add(kind)
                    record={k:link[k] for k in ('url','relationship','reason')}
                    doc.setdefault('follow_up_reads',[]).append(record)
                    if not link['enabled']:
                        record['status']='disabled';continue
                    child_row=merge_results([{'url':link['url'],'title':link.get('title','')}])[0]
                    child=read_original(child_row,doc,link)
                    record['status']='read' if child and child['page_body_read'] else 'not_read'
                    if child:record['document_id']=child['document_id']
                successful={canonical(r['url']) for r in doc.get('follow_up_reads',[]) if r['relationship']=='attachment' and r['status']=='read'}
                if successful:
                    doc['read_attachments']=[a['url'] for a in doc.get('attachments',[]) if canonical(a['url']) in successful]
                    doc['attachments_read']=all(canonical(a['url']) in successful for a in doc.get('attachments',[]))
            coverage=assess(rows,documents,scope)
            if coverage['enough_for_agent_review'] or follow_up_disabled(): break
            if len(sources)>1 and reads_this_source>=2: break
        coverage=assess(rows,documents,scope)
        if coverage['enough_for_agent_review'] or follow_up_disabled(): break
        # If reading budget is exhausted, extra links cannot close a missing-body gap.
        if reads>=args.read_count: break
    if remaining()<1: coverage['gaps']=list(dict.fromkeys(coverage['gaps']+['time_budget_exhausted']))
    if not budget.data()['remaining'] and coverage['gaps']: coverage['gaps'].append('request_budget_exhausted')
    if not rows and any(e['stage']=='search_next_page' for e in events):
        coverage['gaps'].append('bounded_list_window_exhausted')
    # Bodies remain separate from search summaries. Agent-facing output uses short cited passages by default.
    for doc in documents:
        doc['read_characters']=len(doc.pop('content',''))
    by_id={d['document_id']:d for d in documents if d['page_body_read']}
    by_original={canonical(d.get('source_url') or d['url']):d for d in documents if d['page_body_read']}
    for row in rows:
        doc=by_id.get(row['document_id']) or by_original.get(canonical(row['url']))
        row['evidence_status']='original_read' if doc else 'search_only'
        row['evidence_term_matches']=len(set(t for p in (doc or {}).get('passages',[]) for t in p['matched_terms']))
    rows.sort(key=lambda r:(r['evidence_status']!='original_read',-r['evidence_term_matches']))
    for index,row in enumerate(rows,1): row['research_rank']=index
    return {'ok':bool(rows),'operation':'research','version':runtime.VERSION,
        'question':getattr(args,'question',None) or args.query,'query':args.query,
        'retrieved_at':datetime.now(timezone.utc).isoformat(),'results':rows,'documents':documents,
        'coverage':coverage,'events':events,'errors':errors,'routing':runtime.public_plan(route),
        'budget':budget.data(),'elapsed_ms':round(1000*(time.monotonic()-started),2),
        'partial':bool(coverage['gaps']),'complete':False,'facts_verified':False,
        'stop_reason':'ready_for_agent_review' if coverage['enough_for_agent_review'] else 'follow_up_disabled' if follow_up_disabled() else 'evidence_gap_or_limit'}
