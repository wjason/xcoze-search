import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
import urllib.error
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from test_search import x,QueueTransport
from native_reader import NativeReader
from research_workflow import run_research,follow_up_links
from research_evidence import passages


ARCHIVE={'datasource':[{'title':'needle policy','publishUrl':'https://www.nea.gov.cn/notice.html','publishTime':'2026-11-01'}]}
PDF=b'%PDF-1.4 synthetic'
TEXT=b'Policy plan page one: needle target 42 MW. '+b'Evidence with a unit. '*10+b'\fSecond page with conditions. '+b'Conditions and limits. '*8+b'\f'

def notice(extra='',body=None):
    return ('<html><head><title>Notice</title><meta name="publishdate" content="2026-11-01"></head><main><p>'+
        (body or 'needle notice. '+('Published notification, not the full plan. '*5))+ '</p>'+extra+'</main></html>').encode()

class FollowUpTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.env=patch.dict(os.environ,{'XDG_CACHE_HOME':self.temp.name},clear=True);self.env.start()
        self.intervals=patch.dict('public_access.INTERVALS',{'nea-archive':0,'native-reader-www.nea.gov.cn':0});self.intervals.start()
        self.config={'providers':{},'search_preferences':{'browser':'off','disabled_providers':['exa','exa-free','parallel-free']}}
    def tearDown(self):self.intervals.stop();self.env.stop();self.temp.cleanup()
    def command(self,*extra):
        return x.parser().parse_args(['research','needle','--question','What is the capacity target?', '--provider','nea-archive','--strategy','free','--browser','off','--require-topic','needle','--require-topic','target','--timeout','3',*extra])
    def run_pdf(self,*extra,binary=True):
        transport=QueueTransport(ARCHIVE,notice('<a href="/plan.pdf">needle plan</a>'),PDF)
        with patch.object(x.urllib.request,'build_opener',return_value=transport),patch('native_reader.shutil.which',return_value='pdftotext' if binary else None),patch('native_reader.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout=TEXT)):
            result=run_research(self.command(*extra),self.config,x)
        return result,transport

    def test_attachment_shares_budget_preserves_notice_date_and_real_page_positions(self):
        result,t=self.run_pdf('--start-date','2026-11-01','--end-date','2026-11-30')
        self.assertEqual(len(t.requests),3);self.assertEqual(result['budget']['attempts'],3)
        parent,child=result['documents'];self.assertTrue(parent['attachments_read'])
        self.assertEqual(child['parent_document_id'],parent['document_id']);self.assertEqual(child['relationship'],'attachment')
        self.assertIsNone(child['publication_date']);self.assertEqual(child['date_context']['parent_publication_date'],'2026-11-01')
        self.assertEqual(child['pdf_pages_extracted'],[1,2]);self.assertEqual(child['passages'][0]['pdf_pages'],[1,2])
        self.assertTrue(result['coverage']['enough_for_agent_review']);self.assertFalse(result['facts_verified'])

    def test_attachment_disabled_or_read_limit_or_request_limit_never_sends_extra_http(self):
        for extra in [('--attachments','off'),('--read-count','1'),('--max-requests','2')]:
            with self.subTest(extra=extra):
                result,t=self.run_pdf(*extra)
                self.assertEqual(len(t.requests),2);self.assertEqual(len(result['documents']),1)
                self.assertFalse(result['documents'][0]['attachments_read'])
                self.assertIn('attachment_follow_up_not_read',result['coverage']['gaps'])

    def test_missing_pdf_tool_preserves_parent_and_does_not_download_or_install(self):
        result,t=self.run_pdf(binary=False)
        self.assertEqual(len(t.requests),2);self.assertEqual(len(result['documents']),1)
        self.assertIn('reader_dependency_missing',[e['code'] for e in result['errors']])

    def test_unneeded_pdf_is_not_fetched_when_notice_already_answers(self):
        transport=QueueTransport(ARCHIVE,notice('<a href="/plan.pdf">needle plan</a>',body='needle target 42 MW. '+('Published values and limitations. '*8)))
        with patch.object(x.urllib.request,'build_opener',return_value=transport):result=run_research(self.command(),self.config,x)
        self.assertEqual(len(transport.requests),2)
        self.assertNotIn('follow_up_reads',result['documents'][0])

    def test_follow_links_are_published_same_host_noncredential_and_nonrecursive(self):
        doc={'url':'https://www.nea.gov.cn/notice','content':'needle notice, attachment','passages':[],
             'attachments':[{'url':'https://evil.example/plan.pdf','title':'needle'},
                            {'url':'https://www.nea.gov.cn/plan.pdf?token=private','title':'needle'},
                            {'url':'https://www.nea.gov.cn/plan.pdf?%74oken=private','title':'needle'},
                            {'url':'https://www.nea.gov.cn/plan.pdf','title':'needle'}]}
        links=follow_up_links(doc,self.command(),['needle','target'])
        self.assertEqual([x['url'] for x in links],['https://www.nea.gov.cn/plan.pdf'])
        self.assertEqual(len(links),1)

    def test_example_follow_up_stops_at_one_level(self):
        parent=notice('<a href="/guide#examples">usage examples</a>')
        child=notice('<a href="/next#examples">more examples</a><pre>const target = needle();\nuse(target);</pre>',body='needle target example. '+('Example details. '*10))
        transport=QueueTransport(ARCHIVE,parent,child)
        with patch.object(x.urllib.request,'build_opener',return_value=transport):
            result=run_research(self.command('--question','How do I use needle?'),self.config,x)
        self.assertEqual(len(transport.requests),3);self.assertEqual(result['documents'][1]['relationship'],'example')
        self.assertNotIn('follow_up_reads',result['documents'][1])

    def test_example_follow_up_can_be_disabled_without_extra_http(self):
        archive={'datasource':[{**ARCHIVE['datasource'][0],'publishUrl':'https://www.nea.gov.cn/notice'+str(i)+'.html'} for i in range(3)]}
        transport=QueueTransport(archive,notice('<a href="/guide#examples">usage examples</a>'))
        args=self.command('--question','How do I use needle?','--context-links','off');args.require_topic=['needle']
        with patch.object(x.urllib.request,'build_opener',return_value=transport):
            result=run_research(args,self.config,x)
        self.assertEqual(len(transport.requests),2)
        self.assertIn('example_follow_up_not_read',result['coverage']['gaps'])
        self.assertEqual(result['stop_reason'],'follow_up_disabled')

    def test_denied_follow_up_keeps_notice_without_other_reader_attempts(self):
        transport=QueueTransport(ARCHIVE,notice('<a href="/plan.pdf">needle plan</a>'),urllib.error.HTTPError('',403,'',{},io.BytesIO(b'denied')))
        with patch.object(x.urllib.request,'build_opener',return_value=transport),patch('native_reader.shutil.which',return_value='pdftotext'):
            result=run_research(self.command(),self.config,x)
        self.assertEqual(len(transport.requests),3);self.assertEqual(len(result['documents']),1)
        self.assertFalse(result['documents'][0]['attachments_read'])

    def test_complete_code_blocks_keep_else_branch_and_are_not_marked_complete_after_clipping(self):
        code='try {\n await fetch(url);\n} catch (err) {\n if (err.name === "TimeoutError") {\n timeout();\n } else if (err.name === "AbortError") {\n userAbort();\n }\n}\n'
        html=notice('<pre>'+code+'</pre>',body='needle example '+('Published context. '*100))
        reader=NativeReader();data=reader.normalize_fetch(reader.decode_response(html),'https://www.nea.gov.cn/guide')
        selected=passages(data['content'],['timeouterror','aborterror'],question='How do the errors differ?',code_blocks=data['code_blocks'])
        block=next(p for p in selected if p['kind']=='literal_code_block')
        self.assertIn('userAbort();',block['text']);self.assertTrue(block['text'].rstrip().endswith('}'));self.assertTrue(block['context_complete'])
        transport=QueueTransport(html)
        with patch.object(x.urllib.request,'build_opener',return_value=transport):
            args=x.parser().parse_args(['fetch','https://www.nea.gov.cn/guide','--provider','native-reader','--strategy','free','--max-characters','1000','--timeout','3'])
            fetched=x.run_fetch(args,self.config)
        self.assertTrue(fetched['truncated']);self.assertEqual(fetched['code_blocks'],[])


if __name__=='__main__':unittest.main()
