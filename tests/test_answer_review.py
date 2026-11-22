import copy
import importlib.util
from pathlib import Path
import unittest
import sys
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from native_reader import NativeReader
from research_evidence import contains_term,passages,observations,assess

spec=importlib.util.spec_from_file_location('review_research',Path(__file__).resolve().parents[1]/'evaluations/review_research.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class AnswerEvidenceTests(unittest.TestCase):
    def test_identifier_substrings_do_not_satisfy_requested_operations(self):
        self.assertFalse(contains_term('AbortController constructor','abort'))
        self.assertFalse(contains_term('get_or_init','get'))
        self.assertTrue(contains_term('controller.abort() cancels a request','abort'))
        doc={'url':'https://example.org','content':'AbortController constructor','page_body_read':True}
        result=assess([{}],[doc],SimpleNamespace(query='abort',require_topic=['abort']))
        self.assertFalse(result['enough_for_agent_review']);self.assertTrue(result['answer_review_required'])

    def test_exception_question_preserves_general_rule_as_well_as_exception_type(self):
        text='TaskGroup creates tasks.\nThe first time a task fails\nwith an exception other than CancelledError,\nthe remaining tasks are cancelled.\nOnce all tasks finish, exceptions form an ExceptionGroup.\n'+'\n'.join(['Other API reference.']*20)+'\nTaskGroup handles KeyboardInterrupt specially with ExceptionGroup differences.'
        out=passages(text,['taskgroup','exceptiongroup'],question='一个任务失败后其他任务怎样？')
        combined='\n'.join(p['text'] for p in out)
        self.assertIn('remaining tasks are cancelled',combined);self.assertIn('Once all tasks finish',combined)

    def test_method_focus_does_not_mix_next_methods_opposite_semantics(self):
        html='<title>Reference</title><main><section id="method.get"><p>'+('get returns None and never blocks. '*8)+'</p></section><section id="method.set"><p>'+('set may block. '*20)+'</p></section></main>'
        out=NativeReader().normalize_fetch({'html':html},'https://doc.rust-lang.org/std/sync/struct.OnceLock.html',focus_terms=['get'])
        self.assertIn('never blocks',out['content']);self.assertNotIn('set may block',out['content'])
        self.assertTrue(out['source_url'].endswith('#method.get'))

    def test_rust_header_and_adjacent_description_are_one_method(self):
        html='<title>API</title><main><section id="method.get"><h4>get</h4></section><div class="docblock"><p>'+('Returns None and never blocks. '*8)+'</p></div><section id="method.set"><h4>set</h4></section><div>'+('May block. '*20)+'</div></main>'
        out=NativeReader().normalize_fetch({'html':html},'https://doc.rust-lang.org/std/sync/struct.OnceLock.html',focus_terms=['get'])
        self.assertIn('never blocks',out['content']);self.assertNotIn('May block',out['content'])

    def test_mdn_symbol_query_prefers_returned_overview_over_constructor(self):
        from documentation_search import MDN
        raw={'documents':[{'mdn_url':'/en-US/docs/Web/API/AbortController/AbortController','title':'Constructor'},
                          {'mdn_url':'/en-US/docs/Web/API/AbortController','title':'Overview'}]}
        rows,_=MDN().normalize_search(raw,SimpleNamespace(query='AbortController',count=2))
        self.assertEqual(rows[0]['title'],'Overview')

    def test_deadline_types_remain_distinct_even_when_times_are_equal(self):
        body='招标文件获取时间\n获取结束时间：2026年11月26日18时00分\n投标文件递交截止时间：2026年11月26日18时00分\n'
        out=observations(body)
        self.assertEqual({x['field'] for x in out},{'document_acquisition_deadline','bid_deadline'})
        self.assertEqual(len(out),2)

    def test_actual_default_deny_heading_excludes_other_sections(self):
        body='<title>Network Policies</title><main><h2 id="default-deny-all-ingress-traffic">Default deny ingress</h2><p>'+('podSelector {} policyTypes Ingress no ingress rules. '*8)+'</p><h2 id="allow-all">Allow all</h2><p>'+('allow all traffic. '*8)+'</p></main>'
        out=NativeReader().normalize_fetch({'html':body},'https://kubernetes.io/policy',question='默认拒绝所有入站怎么设置？')
        self.assertIn('podSelector',out['content']);self.assertNotIn('allow all traffic',out['content'])

    def test_manual_review_cannot_promote_missing_criteria_or_invent_references(self):
        corpus={'cases':[{'id':'A','answer_requirements':[{'id':'1'},{'id':'2'}]}]}
        result={'records':[{'id':'A','result':{'documents':[{'document_id':'d','page_body_read':True,'passages':[{'line':1}]}]}}]}
        reviews={'reviews':[{'id':'A','covered_requirements':['1'],'finding':'部分支持','finding_en':'Partial support','evidence':[{'document_id':'d','passage':1}]}]}
        self.assertEqual(module.review(corpus,result,reviews)['summary']['partial'],1)
        wrong=copy.deepcopy(reviews);wrong['reviews'][0]['evidence'][0]['passage']=2
        with self.assertRaises(ValueError):module.review(corpus,result,wrong)
        with self.assertRaises(ValueError):module.review(corpus,result,{'reviews':[]})


if __name__=='__main__':unittest.main()
