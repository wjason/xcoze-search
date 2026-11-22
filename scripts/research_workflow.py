"""Bounded search/read loop. The host Agent retains semantic judgment."""
from copy import copy
from datetime import datetime, timezone
import time

from search_common import SearchError, RequestBudget
from research_evidence import assess, canonical, merge_results, observations, passages, required_terms


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
            seen.add(key);reads+=1
            reads_this_source+=1
            fetch_args=runtime.parser().parse_args(['fetch',row['url'],'--strategy',route['strategy'],
                '--max-characters',str(args.max_read_characters),'--retries','0'])
            fetch_args.timeout=min(args.timeout,remaining());fetch_args.max_seconds=max(1,int(remaining()))
            fetch_args.focus_terms=terms
            fetch_args.focus_question=getattr(args,'question',None) or args.query
            try:
                fetched=runtime.run_fetch(fetch_args,config,budget=budget)
                seen.add(canonical(fetched.get('source_url') or row['url']))
                doc={k:fetched.get(k) for k in ('title','url','source_url','directory_url','content_kind',
                    'publication_date','publication_date_basis','truncated','extraction_scope','pdf_pages_requested',
                    'requested_anchor','anchor_found','anchor_basis','attachments','attachments_read') if k in fetched}
                doc.update(document_id=row['document_id'],provider=fetched.get('provider'),
                    page_body_read=bool(fetched.get('content','').strip()) and fetched.get('page_body_read',True),
                    content=fetched.get('content',''),search_date=row.get('published_at'),
                    search_date_semantics=row.get('provider_fields',{}).get('publication_semantics'),
                    passages=passages(fetched.get('content',''),terms,question=getattr(args,'question',None) or args.query),
                    observations=observations(fetched.get('content','')),facts_verified=False)
                if doc.get('publication_date') and doc.get('search_date'):
                    doc['search_and_original_dates_differ']=doc['publication_date']!=doc['search_date']
                documents.append(doc)
                events.append({'stage':'read','url':row['url'],'page_body_read':doc['page_body_read'],
                               'requests':fetched.get('requests',[]),'attempts':fetched.get('attempts',0)})
                errors.extend(fetched.get('errors',[]))
            except SearchError as exc:
                errors.append({'stage':'read','url':row['url'],**exc.data()})
            coverage=assess(rows,documents,scope)
            if coverage['enough_for_agent_review']: break
            if len(sources)>1 and reads_this_source>=2: break
        coverage=assess(rows,documents,scope)
        if coverage['enough_for_agent_review']: break
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
        'stop_reason':'ready_for_agent_review' if coverage['enough_for_agent_review'] else 'evidence_gap_or_limit'}
