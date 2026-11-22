#!/usr/bin/env python3
"""Validate manual answer-support reviews against returned passage references; no network or model API."""
import argparse
import json
from pathlib import Path


def review(corpus,results,reviews):
    cases={c['id']:c for c in corpus['cases'] if not c.get('expected_gap')}
    records={r['id']:r for r in results['records']}
    judgments={r['id']:r for r in reviews['reviews']}
    if len(judgments)!=len(reviews['reviews']) or set(judgments)!=set(cases):
        raise ValueError('Exactly one manual review is required for every positive task.')
    rows=[]
    for ident,case in cases.items():
        judgment=judgments[ident];requirements={r['id'] for r in case['answer_requirements']}
        covered=set(judgment['covered_requirements'])
        if not covered<=requirements:raise ValueError('Unknown requirement: '+ident)
        docs={d['document_id']:d for d in records[ident]['result'].get('documents',[])}
        references=judgment.get('evidence',[])
        if covered and not references:raise ValueError('Supported requirements need returned passage references: '+ident)
        for ref in references:
            doc=docs.get(ref['document_id'])
            if not doc or not doc.get('page_body_read') or type(ref['passage']) is not int or not 1<=ref['passage']<=len(doc.get('passages',[])):
                raise ValueError('Invalid original/passage reference: '+ident)
        if not judgment.get('finding') or not judgment.get('finding_en'):raise ValueError('A bilingual review finding is required: '+ident)
        rows.append({**judgment,'status':'supported' if covered==requirements else 'partial' if covered else 'unsupported',
                     'missing_requirements':sorted(requirements-covered)})
    return {'schema_version':1,'review_method':'manual_agent_review_of_returned_passages_against_explicit_requirements',
            'independent_review':False,'semantic_judgment_automated':False,
            'summary':{'tasks':len(rows),'supported':sum(r['status']=='supported' for r in rows),
                       'partial':sum(r['status']=='partial' for r in rows),'unsupported':sum(r['status']=='unsupported' for r in rows)},
            'reviews':rows}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('corpus','results','reviews','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--run',choices=('baseline','final'),default='final')
    a=p.parse_args();load=lambda path:json.loads(path.read_text(encoding='utf-8'))
    results=load(a.results);reviews=load(a.reviews)
    result=review(load(a.corpus),results.get(a.run,results),reviews.get(a.run,reviews))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['summary']))


if __name__=='__main__':main()
