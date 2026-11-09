"""Official public indexes, result semantics and shared-process pacing; no network."""
import gzip
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import urllib.parse

from test_search import x, args, QueueTransport, ds
from public_providers import PUBLIC_REGISTRY as PUBLIC, OPEN_SOURCES, partial_date
import public_access

WIKI = {'query': {'general': {'wikiid': 'zhwiki'}, 'search': [
    {'title': '风力发电', 'snippet': '<span>风能</span>发电', 'timestamp': '2026-11-01T00:00:00Z'}]}}
SE = {'items': [{'title': 'TaskGroup &amp; cancellation', 'link': 'https://stackoverflow.com/questions/123/example',
                 'creation_date': 1767225600, 'body': '<p>Question <code>example</code></p>',
                 'owner': {'display_name': 'Example', 'link': 'https://stackoverflow.com/users/1/example'},
                 'content_license': 'CC BY-SA 4.0', 'is_answered': True}], 'quota_remaining': 299, 'quota_max': 300}
ATOM = b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/abs/2601.12345v2</id><title>Example paper</title><summary>Abstract only.</summary><published>2026-01-01T00:00:00Z</published><updated>2026-02-01T00:00:00Z</updated><author><name>Example Author</name></author></entry></feed>'''
CROSSREF = {'status': 'ok', 'message': {'total-results': 1, 'items': [
    {'DOI': '10.1234/example', 'title': ['Example'], 'published': {'date-parts': [[2026]]},
     'abstract': '<jats:p>Abstract only</jats:p>', 'score': 12}]}}
NPM = {'objects': [{'package': {'name': '@example/tool', 'version': '1.2.0', 'description': 'Example tool',
                               'date': '2026-11-01'}, 'score': {'final': .9}}], 'total': 1}
CRATES = {'crates': [{'name': 'example_tool', 'description': 'Example', 'max_version': '2.0.0-beta.1',
                      'max_stable_version': '1.9.0', 'updated_at': '2026-11-01'}], 'meta': {'total': 1}}
GL = [{'path_with_namespace': 'example/tool', 'web_url': 'https://gitlab.com/example/tool',
       'description': 'Example', 'created_at': '2020-01-01', 'last_activity_at': '2026-11-01'}]
EPMC = {'hitCount': 1, 'resultList': {'result': [{'source': 'MED', 'id': '123', 'title': 'Example',
         'firstPublicationDate': '2026-11-01', 'abstractText': '<p>Abstract only</p>'}]}}
HF = [{'id': 'example/model', 'pipeline_tag': 'text-generation', 'gated': 'auto', 'private': False}]
FIXTURES = {'wikipedia': WIKI, 'stackexchange': SE, 'arxiv': ATOM, 'crossref': CROSSREF,
            'npm': NPM, 'crates': CRATES, 'gitlab': GL, 'europepmc': EPMC, 'huggingface': HF,
            'openlibrary': {'docs': [{'key':'/works/OL1W','title':'A book','author_name':['An author'],'first_publish_year':2020}]},
            'datacite': {'data': [{'attributes': {'doi':'10.1234/example','titles':[{'title':'Dataset'}],'publicationYear':2025}}]},
            'zenodo': {'hits': {'hits': [{'id':1,'metadata':{'title':'A dataset','description':'<p>Summary</p>','publication_date':'2025-01-01'}}]}},
            'wikidata': {'search': [{'id':'Q1','label':'Universe','description':'All space and time'}]},
            'nasa': {'collection': {'items': [{'data': [{'nasa_id':'ABC-1','title':'Space','description':'A photo','date_created':'2025-01-01'}]}]}},
            'federalregister': {'results':[{'title':'Rule','html_url':'https://www.federalregister.gov/documents/2025/01/01/example','publication_date':'2025-01-01','abstract':'Rule summary'}]},
            'worldbank': {'page_metadata':{},'observations':[{'indicator':{'id':'SP.POP.TOTL','value':'Population'},'country':{'id':'CN','value':'China'},'date':'2025','value':1}]},
            'usgs': {'features':[{'properties':{'title':'M 2.5 - Somewhere','url':'https://earthquake.usgs.gov/earthquakes/eventpage/example','time':1767225600000,'mag':2.5},'geometry':{'coordinates':[1,2,3]}}]}}


class OpenSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'XDG_CACHE_HOME': self.tmp.name}, clear=True)
        self.env.start()

    def tearDown(self):
        self.env.stop(); self.tmp.cleanup()

    def test_new_sources_use_fixed_public_endpoints_no_auth_and_normalize_without_fulltext(self):
        for provider in OPEN_SOURCES:
            with self.subTest(provider=provider.name):
                raw = FIXTURES[provider.name]
                raw = (json.dumps([raw['page_metadata'], raw['observations']]).encode() if provider.name == 'worldbank' else raw if isinstance(raw, bytes) else json.dumps(raw).encode())
                transport = QueueTransport(raw)
                with patch.object(x.urllib.request, 'build_opener', return_value=transport):
                    output = x.run_search(args(provider=provider.name, query='CN,SP.POP.TOTL' if provider.name == 'worldbank' else '2.5,day' if provider.name == 'usgs' else 'wind'), {'providers': {}})
                self.assertTrue(output['ok'])
                self.assertEqual(output['budget']['attempts'], 1)
                row = output['results'][0]
                self.assertEqual(row['content_kind'], provider.result_kind)
                self.assertEqual(row['content'], '')
                self.assertIsNone(transport.requests[0].get_header('Authorization'))
                self.assertIn('github.com/wjason/xcoze-search', transport.requests[0].get_header('User-agent'))

    def test_every_platform_routes_native_first_even_with_a_paid_key(self):
        config = {'providers': {'deepseek': {'api_key': 'synthetic-only'}}}
        for provider in OPEN_SOURCES:
            for strategy in ('smart', 'free', 'balanced'):
                route = x.plan(args(platform=provider.name, strategy=strategy, query='CN,SP.POP.TOTL' if provider.name == 'worldbank' else '2.5,day' if provider.name == 'usgs' else 'wind'), config, x.credential)
                self.assertEqual(route['candidates'][0], provider.name)
                self.assertFalse(route['complementary_search'])
                if strategy == 'free': self.assertNotIn('deepseek', route['candidates'])

    def test_platform_catalog_distinguishes_index_search_and_never_executes_tools_or_reads_keys(self):
        with patch.object(x, 'read_config', side_effect=AssertionError('no credentials')), \
                patch.object(x.subprocess, 'run', side_effect=AssertionError('no command execution')), \
                patch.object(x, 'request_api', side_effect=AssertionError('no network')), \
                redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(x.main(['platforms']), 0)
        report = json.loads(stdout.getvalue())
        rows = {r['platform']: r for r in report['platforms']}
        self.assertEqual(rows['bilibili']['coverage'], 'public_index_only')
        self.assertFalse(rows['bilibili']['transcripts_integrated'])
        self.assertEqual(rows['npm']['native_provider'], 'npm')
        self.assertFalse(rows['github']['comment_threads_integrated'])
        self.assertTrue(all(not t['live_verified'] for t in report['local_tools']))
        route = x.plan(args(platform='youtube'), {'providers': {}}, x.credential)
        self.assertIsNone(route['specialized_source'])
        self.assertIn('site:youtube.com', route['payloads']['exa-free']['arguments']['query'])

    def test_chinese_wikipedia_url_and_language_constraints_are_preserved(self):
        p = PUBLIC['wikipedia']
        scoped = x.scoped_args(args(query='风力发电', platform='wikipedia'))
        payload = p.search_payload(scoped)
        req = p.build_request(payload, '', 'test')
        self.assertEqual(urllib.parse.urlsplit(req.full_url).hostname, 'zh.wikipedia.org')
        self.assertNotIn('_language', req.full_url)
        rows, _ = p.normalize(WIKI, 3)
        self.assertTrue(rows[0]['url'].startswith('https://zh.wikipedia.org/wiki/'))
        self.assertEqual(rows[0]['snippet'], '风能发电')
        self.assertIsNone(rows[0]['published_at'])
        for flags in ({'language': 'de'}, {'site': 'evil.example'}, {'language': 'en', 'site': 'zh.wikipedia.org'}):
            with self.assertRaises(x.SearchError): p.search_payload(args(**flags))
        with self.assertRaises(x.SearchError): p.normalize({'query': {'search': []}}, 3)

    def test_stackexchange_questions_are_not_answers_and_dates_are_creation_dates(self):
        p = PUBLIC['stackexchange']
        route = x.plan(args(platform='stackexchange', site='superuser.com', start_date='2026-01-01', end_date='2026-01-01'), {'providers': {}}, x.credential)
        payload = route['payloads']['stackexchange']
        self.assertEqual(payload['site'], 'superuser')
        self.assertEqual(payload['todate'] - payload['fromdate'], 86399)
        rows, meta = p.normalize(SE, 3)
        self.assertEqual(rows[0]['title'], 'TaskGroup & cancellation')
        self.assertFalse(rows[0]['provider_fields']['answers_fetched'])
        self.assertEqual(rows[0]['provider_fields']['content_license'], 'CC BY-SA 4.0')
        self.assertEqual(meta['usage']['quota_remaining'], 299)
        with self.assertRaises(x.SearchError) as caught:
            p.check_error({'error_id': 502, 'error_name': 'throttle_violation', 'error_message': 'secret-body'})
        self.assertNotIn('secret-body', str(caught.exception))
        self.assertEqual(caught.exception.category, 'rate_limit')

    def test_arxiv_dates_abstract_and_feed_errors_have_separate_semantics(self):
        p = PUBLIC['arxiv']
        payload = p.search_payload(args(start_date='2026-01-01', end_date='2026-11-03'))
        self.assertIn('submittedDate:[202601010000 TO 202611032359]', payload['search_query'])
        rows, _ = p.normalize(p.decode_response(ATOM), 3)
        self.assertEqual(rows[0]['summary'], 'Abstract only.')
        self.assertEqual(rows[0]['published_at'], '2026-01-01T00:00:00Z')
        self.assertEqual(rows[0]['provider_fields']['updated'], '2026-02-01T00:00:00Z')
        with self.assertRaises(x.SearchError): p.decode_response(ATOM.replace(b'/abs/2601.12345v2', b'/api/errors#bad'))
        with self.assertRaises(x.SearchError): p.decode_response(b'<html>challenge</html>')

    def test_crossref_dates_keep_precision_and_identifiers_and_abstracts_remain_metadata(self):
        p = PUBLIC['crossref']
        for parts, expected in [([2026], '2026'), ([2026, 2], '2026-02'), ([2026, 2, 3], '2026-02-03'), ([2026, 2, 30], None)]:
            self.assertEqual(partial_date({'published': {'date-parts': [parts]}}), expected)
        rows, _ = p.normalize(CROSSREF, 3)
        self.assertEqual(rows[0]['published_at'], '2026')
        self.assertEqual(rows[0]['url'], 'https://doi.org/10.1234/example')
        self.assertEqual(rows[0]['summary'], 'Abstract only')
        self.assertIsNone(rows[0]['score'])
        payload = p.search_payload(args(start_date='2026-01-01'))
        self.assertEqual(payload['filter'], 'from-pub-date:2026-01-01')

    def test_crossref_bare_doi_uses_exact_filter_and_keeps_dates(self):
        provider = PUBLIC['crossref']
        exact = provider.search_payload(args(query='10.1234/Example', start_date='2026-01-01'))
        self.assertEqual(exact['filter'], 'doi:10.1234/example,from-pub-date:2026-01-01')
        self.assertNotIn('query.bibliographic', exact)
        title = provider.search_payload(args(query='Example paper about 10.1234/example'))
        self.assertIn('query.bibliographic', title)

    def test_project_and_package_update_dates_are_not_article_dates(self):
        for name in ('npm', 'crates', 'gitlab', 'huggingface'):
            p = PUBLIC[name]; raw = FIXTURES[name]
            if name in ('gitlab', 'huggingface'): raw = p.decode_response(json.dumps(raw).encode())
            rows, _ = p.normalize(raw, 3)
            self.assertIsNone(rows[0]['published_at'])
            self.assertIn('date_semantics', rows[0]['provider_fields'])
            with self.assertRaises(x.SearchError): p.search_payload(args(start_date='2026-01-01'))
        self.assertEqual(PUBLIC['gitlab'].search_payload(args())['order_by'], 'star_count')

    def test_europepmc_date_and_abstract_are_not_fulltext_or_clinical_validation(self):
        p = PUBLIC['europepmc']; rows, _ = p.normalize(EPMC, 3)
        self.assertEqual(rows[0]['summary'], 'Abstract only')
        self.assertEqual(rows[0]['url'], 'https://europepmc.org/article/MED/123')
        self.assertIn('may_be_inferred', rows[0]['provider_fields']['date_semantics'])
        self.assertIn('FIRST_PDATE:[2026-01-01 TO 9999-12-31]', p.search_payload(args(start_date='2026-01-01'))['query'])

    def test_gzip_is_decoded_with_a_decompressed_size_limit(self):
        raw = json.dumps(NPM).encode(); budget = x.RequestBudget(2)
        transport = QueueTransport(gzip.compress(raw))
        with patch.object(x.urllib.request, 'build_opener', return_value=transport):
            data, attempts = x.request_api('npm', {'text': 'fixture'}, '', retries=0, budget=budget)
        self.assertEqual(data, NPM); self.assertEqual(attempts, 1)
        with patch.object(x, 'MAX_RESPONSE', 50), patch.object(x.urllib.request, 'build_opener', return_value=QueueTransport(gzip.compress(b'x' * 500))), patch.object(public_access.time, 'time', return_value=10**10):
            with self.assertRaises(x.SearchError) as caught: x.request_api('npm', {'text': 'other'}, '', retries=0)
        self.assertEqual(caught.exception.code, 'response_too_large')
        broken = b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff\xff' + b'\x00' * 8
        with patch.object(x.urllib.request, 'build_opener', return_value=QueueTransport(broken)):
            with self.assertRaises(x.SearchError) as caught:
                x.request_api('bing', {'q': 'fixture'}, '', retries=0)
        self.assertEqual(caught.exception.code, 'invalid_response')

    def test_long_reading_is_opt_in_keeps_default_and_rejects_unsupported_sources_before_network(self):
        raw = {'code': 200, 'data': {'title': 'Long document', 'content': 'x' * 68000}}
        for limit, expected, truncated in [(None, 24000, True), (100000, 68000, False)]:
            with patch.object(x, 'request_api', return_value=(raw, 1)):
                out = x.run_fetch(args(provider='jina', url='https://example.com', max_characters=limit), {'providers': {}})
            self.assertEqual(out['returned_characters'], expected)
            self.assertEqual(len(out['content']), expected)
            self.assertEqual(out['truncated'], truncated)
            self.assertFalse(out['completeness_verified'])
        with patch.object(x, 'request_api') as request:
            with self.assertRaises(x.SearchError):
                x.run_fetch(args(provider='deepseek', url='https://example.com', max_characters=100000), {'providers': {}})
            request.assert_not_called()
        self.assertEqual(PUBLIC['exa-free'].fetch_payload(args(url='https://example.com', max_characters=100000))['arguments']['maxCharacters'], 100000)

    def test_local_cooldown_counts_no_http_and_free_fallback_stays_keyless(self):
        config = {'providers': {'deepseek': {'api_key': 'synthetic-only'}}}
        with patch.object(public_access.time, 'time', return_value=100):
            with public_access.request_slot('npm', 'https://registry.npmjs.org/?text=reserved'): pass
            transport = QueueTransport({'jsonrpc': '2.0', 'id': 1, 'result': {'structuredContent': {
                'results': [{'title': 'Npm', 'url': 'https://www.npmjs.com/package/example'}]}}})
            with patch.object(x.urllib.request, 'build_opener', return_value=transport):
                output = x.run_search(args(platform='npm', strategy='free'), config)
        self.assertTrue(output['ok']); self.assertTrue(output['partial'])
        self.assertEqual(output['budget']['attempts'], 1)
        self.assertEqual(output['requests'][0]['attempts'], 0)
        self.assertEqual(output['errors'][0]['code'], 'source_cooldown')
        self.assertIsNone(transport.requests[0].get_header('Authorization'))


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'XDG_CACHE_HOME': self.tmp.name}, clear=True); self.env.start()
    def tearDown(self):
        self.env.stop(); self.tmp.cleanup()

    def test_short_pacing_wait_uses_remaining_socket_timeout_without_extra_http(self):
        clock = [100.0]
        class Transport(QueueTransport):
            def __init__(self):
                super().__init__(NPM, NPM); self.timeouts = []
            def open(self, req, timeout):
                self.timeouts.append(timeout)
                return super().open(req, timeout)
        transport = Transport(); budget = x.RequestBudget(2)
        def advance(seconds): clock[0] += seconds
        with patch.object(public_access.time, 'time', side_effect=lambda: clock[0]), \
                patch.object(public_access.time, 'monotonic', side_effect=lambda: clock[0]), \
                patch.object(public_access.time, 'sleep', side_effect=advance):
            x.request_api('npm', {'text': 'one'}, '', opener=transport, budget=budget, retries=0, timeout=5)
            x.request_api('npm', {'text': 'two'}, '', opener=transport, budget=budget, retries=0, timeout=5)
        self.assertEqual(transport.timeouts, [5, 4])
        self.assertEqual(budget.used, 2)

    def test_persisted_arxiv_spacing_and_os_lock_prevent_parallel_calls(self):
        with patch.object(public_access.time, 'time', return_value=100):
            with public_access.request_slot('arxiv', 'https://export.arxiv.org/?q=private-query'):
                with self.assertRaises(x.SearchError) as caught:
                    with public_access.request_slot('arxiv', 'https://export.arxiv.org/?q=other'): pass
                self.assertEqual(caught.exception.code, 'source_busy')
            with self.assertRaises(x.SearchError):
                with public_access.request_slot('arxiv', 'https://export.arxiv.org/?q=other'): pass
        with patch.object(public_access.time, 'time', return_value=103):
            with public_access.request_slot('arxiv', 'https://export.arxiv.org/?q=other'): pass
        self.assertNotIn('private-query', ''.join(p.read_text(errors='replace') for p in public_access.cache_root().iterdir()))

    def test_stackexchange_backoff_and_duplicate_window_survive_new_calls(self):
        url = 'https://api.stackexchange.com/search?q=private-query'
        with patch.object(public_access.time, 'time', return_value=100):
            with public_access.request_slot('stackexchange', url) as slot: slot.observe({'backoff': 10})
        with patch.object(public_access.time, 'time', return_value=111):
            with self.assertRaises(x.SearchError):
                with public_access.request_slot('stackexchange', url): pass
            with public_access.request_slot('stackexchange', url + '-different'): pass
        with patch.object(public_access.time, 'time', return_value=161):
            with public_access.request_slot('stackexchange', url): pass
        data = (public_access.cache_root() / 'stackexchange.json').read_text()
        self.assertNotIn('private-query', data); self.assertNotIn('api.stackexchange', data)

    def test_http_retry_after_is_persisted_and_quota_zero_stops_until_next_utc_day(self):
        with patch.object(public_access.time, 'time', return_value=100):
            with self.assertRaises(urllib.error.HTTPError) as caught:
                with public_access.request_slot('crates', 'https://crates.io/?q=test'):
                    raise urllib.error.HTTPError('', 429, '', {'Retry-After': '30'}, io.BytesIO())
            caught.exception.close()
            state = json.loads((public_access.cache_root() / 'crates.json').read_text())
            self.assertEqual(state['not_before'], 130)
            with public_access.request_slot('npm', 'https://registry.npmjs.org/?text=test') as slot:
                slot.defer('Thu, 01 Jan 1970 00:02:10 GMT')
            self.assertEqual(json.loads((public_access.cache_root() / 'npm.json').read_text())['not_before'], 130)
            with public_access.request_slot('stackexchange', 'https://api.stackexchange.com/?q=test') as slot:
                slot.observe({'quota_remaining': 0})
        with patch.object(public_access.time, 'time', return_value=200):
            with self.assertRaises(x.SearchError):
                with public_access.request_slot('stackexchange', 'https://api.stackexchange.com/?q=other'): pass

    def test_corrupt_state_fails_without_network_or_silent_policy_reset(self):
        root = public_access.cache_root(); root.mkdir(parents=True); (root / 'npm.json').write_text('broken')
        with patch.object(x.urllib.request, 'build_opener', return_value=QueueTransport()) as transport:
            with self.assertRaises(x.SearchError) as caught:
                x.request_api('npm', {'text': 'fixture'}, '', retries=0)
        self.assertEqual(caught.exception.code, 'public_access_state_error')
        self.assertEqual(caught.exception.attempts, 0)


if __name__ == '__main__': unittest.main()

class AdditionalPublicSourceTests(unittest.TestCase):
    def test_new_sources_reject_unsupported_filters_and_invalid_records(self):
        for name in ('openlibrary', 'datacite', 'zenodo', 'wikidata'):
            with self.subTest(provider=name):
                with self.assertRaises(x.SearchError):
                    PUBLIC[name].search_payload(args(query='wind energy', start_date='2026-01-01'))
                with self.assertRaises(x.SearchError):
                    PUBLIC[name].normalize({}, 3)
        with self.assertRaises(x.SearchError):
            PUBLIC['openlibrary'].normalize({'docs': [{'key': '/works/../../evil', 'title': 'Bad'}]}, 3)
        with self.assertRaises(x.SearchError):
            PUBLIC['wikidata'].search_payload(args(query='wind', language='fr'))

    def test_results_are_metadata_and_never_duplicate_raw_record_lists(self):
        for name in ('openlibrary', 'datacite', 'zenodo', 'wikidata'):
            with self.subTest(provider=name):
                rows, meta = PUBLIC[name].normalize(FIXTURES[name], 3)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]['content'], '')
                for field in ('docs', 'data', 'hits', 'search'):
                    self.assertNotIn(field, meta['provider_metadata'])

class OfficialGlobalSourcesTests(unittest.TestCase):
    def test_federal_register_document_number_and_keyword_order(self):
        provider = PUBLIC['federalregister']
        exact = provider.search_payload(args(query='2025-02305'))
        request = provider.build_request(exact, '', 'test')
        self.assertEqual(request.full_url, 'https://www.federalregister.gov/api/v1/documents/2025-02305.json')
        item = {**FIXTURES['federalregister']['results'][0], 'document_number': '2025-02305'}
        rows, _ = provider.normalize(item, 5)
        self.assertEqual(rows[0]['provider_fields']['document_number'], '2025-02305')
        for intent, expected in (('reference', 'relevance'), ('current', 'newest')):
            payload = provider.search_payload(args(query='AI Action Plan', intent=intent))
            self.assertEqual(payload['order'], expected)
            self.assertEqual(payload['conditions[term]'], 'AI Action Plan')

    def test_world_bank_uses_exact_country_indicator_and_preserves_observation(self):
        provider = PUBLIC['worldbank']
        request = provider.build_request(provider.search_payload(args(query='CN,SP.POP.TOTL')), '', 'test')
        self.assertTrue(request.full_url.startswith('https://api.worldbank.org/v2/country/CN/indicator/SP.POP.TOTL?'))
        rows, meta = provider.normalize(FIXTURES['worldbank'], 1)
        self.assertEqual(rows[0]['provider_fields']['year'], '2025')
        self.assertEqual(rows[0]['provider_fields']['value'], 1)
        self.assertIsNone(rows[0]['published_at'])
        self.assertNotIn('observations', meta['provider_metadata'])
        for query in ('China population', '../secret,SP.POP.TOTL', 'CN,../../path'):
            with self.assertRaises(x.SearchError): provider.search_payload(args(query=query))

    def test_official_sources_have_public_links_and_no_raw_duplicate_results(self):
        for name in ('nasa', 'federalregister'):
            rows, meta = PUBLIC[name].normalize(FIXTURES[name], 1)
            self.assertTrue(rows[0]['url'].startswith('https://'))
            self.assertEqual(rows[0]['content'], '')
            self.assertNotIn('collection', meta['provider_metadata'])
            self.assertNotIn('results', meta['provider_metadata'])
        with self.assertRaises(x.SearchError):
            PUBLIC['federalregister'].normalize({'results':[{'html_url':'https://evil.example/page'}]}, 1)

class EarthquakeSourceTests(unittest.TestCase):
    def test_feed_is_bounded_and_event_time_is_distinct(self):
        provider = PUBLIC['usgs']
        req = provider.build_request(provider.search_payload(args(query='2.5,day')), '', 'test')
        self.assertEqual(req.full_url, provider.endpoint + '2.5_day.geojson')
        rows, meta = provider.normalize(FIXTURES['usgs'], 1)
        self.assertEqual(rows[0]['provider_fields']['event_time'], '2026-01-01T00:00:00Z')
        self.assertIsNone(rows[0]['published_at'])
        self.assertNotIn('features', meta['provider_metadata'])
        for bad in ('Taiwan', '../private,day', '5,century'):
            with self.assertRaises(x.SearchError): provider.search_payload(args(query=bad))
