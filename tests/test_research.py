"""Research behavior against observable original text, budgets and source boundaries."""
import io
import os
import tempfile
import unittest
import urllib.error
from unittest.mock import patch
from test_search import x,QueueTransport,args
from native_reader import NativeReader,checked_url
from research_evidence import merge_results,assess,passages,observations
from research_workflow import run_research


def html(term='needle',date='2026-11-01',anchor=''):
    return ('<html><head><title>Original</title><meta name="publishdate" content="'+date+'"></head>'
        '<nav>synthetic-navigation-secret</nav><main><h1 id="'+anchor+'">Topic</h1><p>'+term+' '+
        'Public documentation explains the actual behavior and its limits. '*12+'</p></main></html>').encode()


def rpc(url):
    return {'jsonrpc':'2.0','id':1,'result':{'structuredContent':{'results':[
        {'title':'needle official documentation','url':url,'text':'needle documentation'}]}}}


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.env=patch.dict(os.environ,{'XDG_CACHE_HOME':self.tmp.name},clear=True);self.env.start()
        self.config={'schema_version':2,'providers':{},'search_preferences':{'browser':'off'}}
    def tearDown(self):self.env.stop();self.tmp.cleanup()
    def command(self,*more):return x.parser().parse_args(['research','needle','--strategy','free','--browser','off','--timeout','3',*more])

    def test_reader_extracts_body_anchor_and_page_date_without_sending_credentials(self):
        p=NativeReader();url='https://docs.python.org/3/a.html#method'
        out=p.normalize_fetch(p.decode_response(html(anchor='method')),url)
        self.assertNotIn('synthetic-navigation-secret',out['content']);self.assertEqual(out['publication_date'],'2026-11-01')
        self.assertEqual(out['extraction_scope'],'requested_anchor_on_page');self.assertTrue(out['source_url'].endswith('#method'))
        req=p.build_request(p.fetch_payload(args(url=url)),'synthetic-private','test',fetch=True)
        self.assertIsNone(req.get_header('Authorization'));self.assertIsNone(req.get_header('Cookie'))
        self.assertNotIn('#',req.full_url)
        for bad in ('https://evil.example/a','https://docs.python.org:444/a','https://docs.python.org/a?api_key=secret'):
            with self.assertRaises(x.SearchError):checked_url(bad)

    def test_directory_follows_only_a_published_body_link_and_counts_both_requests(self):
        directory=b'''<html><title>Notice</title><script>var firstLastUrl='/information/deal/html/b/440000/0201/20261101/abcd.html';</script></html>'''
        t=QueueTransport(directory,html())
        with patch.object(x.urllib.request,'build_opener',return_value=t):
            a=x.parser().parse_args(['fetch','https://www.ggzy.gov.cn/information/deal/html/a/440000/x.html','--provider','native-reader','--timeout','5','--strategy','free'])
            out=x.run_fetch(a,self.config)
        self.assertTrue(out['page_body_read']);self.assertEqual(out['attempts'],2);self.assertEqual(out['budget']['attempts'],2)
        self.assertIn('/html/b/',out['source_url']);self.assertIn('/html/a/',out['directory_url'])
        bad={'html':directory.decode().replace('/information/deal/html/b/440000/0201/20261101/abcd.html','https://evil.example/body')}
        with self.assertRaises(x.SearchError):NativeReader().normalize_fetch(bad,'https://www.ggzy.gov.cn/a')

    def test_denial_is_not_body_and_does_not_fan_out_reading(self):
        t=QueueTransport(urllib.error.HTTPError('',403,'',{},io.BytesIO(b'synthetic-private')))
        with patch.object(x.urllib.request,'build_opener',return_value=t):
            a=x.parser().parse_args(['fetch','https://docs.python.org/3/a.html','--strategy','free','--timeout','3'])
            out=x.run_fetch(a,self.config)
        self.assertFalse(out['ok']);self.assertEqual(len(t.requests),1)
        for raw in (b'<html><title>Just a moment</title>verify you are human</html>',b'<html>empty shell</html>'):
            with self.assertRaises(x.SearchError):NativeReader().normalize_fetch(NativeReader().decode_response(raw),'https://docs.python.org/a')

    def test_merge_removes_tracking_duplicates_preserves_versions_and_provenance(self):
        rows=[{'provider':'one','rank':1,'title':'same sufficiently long title','url':'https://a.example/p?version=2&utm_source=a'},
              {'provider':'two','rank':2,'title':'same sufficiently long title','url':'https://a.example/p?version=2#anchor'},
              {'provider':'one','rank':3,'title':'same sufficiently long title','url':'https://a.example/p?version=3'}]
        out=merge_results(rows);self.assertEqual(len(out),2);self.assertEqual(len(out[0]['retrieved_by']),2)
        again=merge_results(out+rows[:1]);self.assertEqual(len(again[0]['retrieved_by']),2)
        self.assertTrue(out[0]['possible_republications']);self.assertEqual(out[0]['source_independence'],'not_established')
        self.assertEqual(len(merge_results([{'url':'http://www.nea.gov.cn/a','title':'Policy'},
                                           {'url':'https://www.nea.gov.cn/a','title':'Policy'}])),1)

    def test_successful_original_stops_without_extra_sources_or_keyed_calls(self):
        t=QueueTransport(rpc('https://docs.python.org/3/one.html'),html())
        self.config['providers']={p:{'api_key':'synthetic-only'} for p in x.PROVIDERS}
        with patch.object(x.urllib.request,'build_opener',return_value=t),patch.object(x,'run_browser_search',side_effect=AssertionError('browser')):
            out=run_research(self.command(),self.config,x)
        self.assertTrue(out['coverage']['enough_for_agent_review']);self.assertEqual(len(t.requests),2)
        self.assertEqual(out['budget']['by_provider'],{'parallel-free':1,'native-reader':1})
        self.assertFalse(out['facts_verified']);self.assertFalse(out['complete'])
        self.assertTrue(out['documents'][0]['passages']);self.assertNotIn('content',out['documents'][0])

    def test_missing_evidence_uses_another_compatible_source_and_preserves_question(self):
        t=QueueTransport(rpc('https://docs.python.org/3/one.html'),html('unrelated'),rpc('https://docs.python.org/3/two.html'),html())
        with patch.object(x.urllib.request,'build_opener',return_value=t):
            out=run_research(self.command('--question','Why does needle work?','--read-count','2'),self.config,x)
        self.assertEqual(out['question'],'Why does needle work?');self.assertTrue(out['coverage']['enough_for_agent_review'])
        self.assertEqual(len(t.requests),4);self.assertEqual(out['results'][0]['url'],'https://docs.python.org/3/two.html')
        self.assertEqual(out['results'][0]['evidence_status'],'original_read')

    def test_request_limit_returns_gap_and_does_not_send_a_read(self):
        t=QueueTransport(rpc('https://docs.python.org/3/one.html'))
        with patch.object(x.urllib.request,'build_opener',return_value=t):out=run_research(self.command('--max-requests','1'),self.config,x)
        self.assertEqual(len(t.requests),1);self.assertIn('no_read_original',out['coverage']['gaps'])
        self.assertIn('request_budget_exhausted',out['coverage']['gaps'])

    def test_dates_use_original_not_list_or_url_dates(self):
        a=args(query='needle',start_date='2026-11-01',end_date='2026-11-30',min_documents=1)
        docs=[{'url':'https://docs.python.org/20261101.html','content':'needle','page_body_read':True,'publication_date':'2026-10-31'}]
        out=assess([{'url':docs[0]['url']}],docs,a)
        self.assertIn('original_publication_date_outside_range',out['gaps']);self.assertFalse(out['enough_for_agent_review'])
        docs[0]['publication_date']=None
        self.assertIn('original_publication_date_unknown',assess([{}],docs,a)['gaps'])

    def test_returned_passages_cover_rare_terms_not_repeated_headings_only(self):
        body='\n'.join(['TaskGroup navigation entry']*20+['When a child fails, remaining tasks are cancelled and an ExceptionGroup is raised.'])
        chosen=passages(body,['taskgroup','exceptiongroup'],count=2)
        text='\n'.join(p['text'] for p in chosen).casefold()
        self.assertIn('exceptiongroup',text);self.assertIn('taskgroup',text)
        doc={'url':'https://docs.python.org/a','page_body_read':True,'content':body,
             'passages':[{'text':'TaskGroup navigation entry'}]}
        out=assess([{}],[doc],args(query='TaskGroup ExceptionGroup'))
        self.assertIn('exceptiongroup',out['missing_terms']);self.assertFalse(out['enough_for_agent_review'])

    def test_deadline_question_returns_actual_labeled_date_not_a_generic_deadline_mention(self):
        body='储能项目：资格以投标截止时间当天查询为准。\n'+('其他资格说明。\n'*10)+'四、提交投标文件截止时间、开标时间和地点\n2026年11月26日 09时00分00秒 （北京时间）\n地点：公开交易平台'
        values=observations(body);self.assertEqual(values[0]['value'],'2026-11-26T09:00')
        self.assertEqual(values[0]['timezone'],'Asia/Shanghai');self.assertIsNone(values[0]['open_for_bidding'])
        excerpts=passages(body,['储能','截止时间'],question='储能项目的截止时间是什么？')
        self.assertIn('2026年11月26日','\n'.join(p['text'] for p in excerpts))

    def test_method_focus_uses_an_existing_page_id_instead_of_guessing_a_url(self):
        page=html().decode().replace('</main>','<h2 id="method.get_or_init">get_or_init</h2><p>'+('OnceLock initialization method. '*10)+'</p></main>')
        p=NativeReader();out=p.normalize_fetch({'html':page},'https://doc.rust-lang.org/std/sync/struct.OnceLock.html',focus_terms=['get_or_init'])
        self.assertTrue(out['source_url'].endswith('#method.get_or_init'))
        out=p.normalize_fetch({'html':page},'https://doc.rust-lang.org/std/sync/struct.OnceLock.html',focus_terms=['not_a_method'])
        self.assertFalse(out['anchor_found']);self.assertNotIn('#',out['source_url'])

    def test_pdf_without_an_existing_extractor_is_an_explicit_gap(self):
        with patch('native_reader.shutil.which',return_value=None),self.assertRaises(x.SearchError) as caught:
            NativeReader().decode_response(b'%PDF-1.7 synthetic')
        self.assertEqual(caught.exception.code,'reader_dependency_missing')

    def test_native_site_cooldowns_do_not_disable_other_official_hosts(self):
        from public_access import pause_status
        t=QueueTransport(urllib.error.HTTPError('',403,'',{},io.BytesIO()))
        with self.assertRaises(x.SearchError):x.request_api('native-reader_fetch',{'url':'https://docs.python.org/a'},'',opener=t,retries=2)
        self.assertIsNotNone(pause_status('native-reader-docs.python.org'))
        self.assertIsNone(pause_status('native-reader-www.nea.gov.cn'))

    def test_valueless_image_alt_does_not_crash_a_whole_source_check(self):
        from content_sources import html_text
        self.assertEqual(html_text('<p>Public<img alt> original</p>'),'Public original')

    def test_notice_attachments_remain_unread_and_keep_the_actual_published_link(self):
        p=NativeReader();body=html().decode().replace('</main>','<a href="/files/policy.pdf">Policy attachment</a></main>')
        out=p.normalize_fetch({'html':body},'https://www.nea.gov.cn/a.html')
        self.assertEqual(out['attachments'][0]['url'],'https://www.nea.gov.cn/files/policy.pdf')
        self.assertFalse(out['attachments_read']);self.assertTrue(out['page_body_read'])


if __name__=='__main__':unittest.main()
