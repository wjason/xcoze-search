#!/usr/bin/env python3
"""Research task checks: retrieval, read originals, date/gap behavior and latency."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import statistics
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import xcoze_search as x
from research_workflow import run_research


def execute(cases,live=False,timeout=8,review_output=None):
    commands=[]
    for c in cases:
        command=['research',c['query'],'--question',c['question'],'--strategy','free','--browser','off',
                 '--timeout',str(timeout),'--count','3','--read-count','3','--max-seconds','35','--max-requests',str(c.get('max_requests',8))]
        for key in ('platform','energy_section','notice_type','business','region','start_date','end_date'):
            if c.get(key):command.extend(['--'+key.replace('_','-'),c[key]])
        for term in c['require_topic']:command.extend(['--require-topic',term])
        commands.append(x.parser().parse_args(command))
    if not live:return {'ok':True,'live':False,'questions':len(cases),'network_requests':0,'keyless':True,'without_exa':True,'without_parallel':True}
    original=x.request_api
    def guard(operation,payload,key,**kwargs):
        name=operation.removesuffix('_fetch')
        if name in ('exa','exa-free','parallel-free') or key or x.get_provider(name).requires_key:
            raise AssertionError('Research audit blocked a forbidden service before transmission.')
        return original(operation,payload,key,**kwargs)
    config={'schema_version':2,'providers':{},'search_preferences':{
        'strategy':'free','browser':'off','disabled_providers':['exa','exa-free','parallel-free']}}
    records=[];private_records=[]
    with patch.object(x,'request_api',side_effect=guard),patch.object(x,'read_config',side_effect=AssertionError('No credentials in audit')),patch.object(x,'run_browser_search',side_effect=AssertionError('No browser')):
        for c,a in zip(cases,commands):
            try:result=run_research(a,config,x)
            except x.SearchError as e:result={'ok':False,'error':e.data(),'documents':[],'coverage':{'gaps':['request_failed']},'results':[],'elapsed_ms':0}
            if review_output is not None:
                private_records.append({'id':c['id'],'question':c['question'],'result':json.loads(json.dumps(result))})
            # The public artifact contains markers and source links, never full originals.
            for doc in result.get('documents',[]):
                doc['passage_markers']=[t for t in c['require_topic'] if any(t.casefold() in p['text'].casefold() for p in doc.get('passages',[]))]
                doc['passages']=[{'line':p['line'],'matched_terms':p['matched_terms']} for p in doc.get('passages',[])]
            for row in result.get('results',[]):
                for field in ('content','snippet','summary','provider_fields','highlights'):row.pop(field,None)
            expected_gap=c.get('expected_gap')
            row={'id':c['id'],'question':c['question'],'expected_gap':expected_gap,'result':result,
                 'gap_check_passed':expected_gap in result['coverage']['gaps'] if expected_gap else None,
                 'semantic_answer_accuracy_measured':False}
            records.append(row)
            print(json.dumps({'id':c['id'],'read':len(result.get('documents',[])),'gaps':result['coverage']['gaps'],'ms':result['elapsed_ms']},ensure_ascii=False),flush=True)
    if review_output is not None:
        review_output.parent.mkdir(parents=True,exist_ok=True)
        review_output.write_text(json.dumps(private_records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    positive=[r for r in records if not r['expected_gap']];negative=[r for r in records if r['expected_gap']]
    return {'ok':True,'schema_version':1,'live':True,'checked_at':datetime.now(timezone.utc).isoformat(),
        'version':x.VERSION,'conditions':{'keyless':True,'without_exa':True,'without_parallel':True,'browser':'off','host_search_used':False},
        'summary':{'positive_tasks':len(positive),'retrieved':sum(bool(r['result'].get('results')) for r in positive),
            'read_original':sum(any(d.get('page_body_read') for d in r['result']['documents']) for r in positive),
            'literal_evidence_covered':sum(r['result']['coverage'].get('enough_for_agent_review',False) for r in positive),
            'negative_gap_cases':len(negative),'correctly_reported_gaps':sum(bool(r['gap_check_passed']) for r in negative),
            'median_ms':statistics.median(r['result']['elapsed_ms'] for r in positive),
            'http_attempts':sum(r['result'].get('budget',{}).get('attempts',0) for r in records),
            'keyed_api_attempts':0,'exa_parallel_attempts':0,'browser_navigations':0,
            'semantic_answer_accuracy_measured':False},'cases':cases,'records':records}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live',action='store_true')
    p.add_argument('--corpus',type=Path,default=ROOT/'evaluations/research-cases.json');p.add_argument('--output',type=Path,required=True)
    p.add_argument('--timeout',type=int,choices=range(1,16),default=8)
    p.add_argument('--review-output',type=Path,help='Optional private local excerpts for manual answer review; do not publish full page text')
    args=p.parse_args();out=execute(json.loads(args.corpus.read_text(encoding='utf-8'))['cases'],args.live,args.timeout,args.review_output)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out.get('summary',out),ensure_ascii=False))


if __name__=='__main__':main()
