"""Result persistence and offline reuse, using synthetic public-source fixtures."""
import copy
import csv
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_search import x
import result_exports as exports


def snapshot():
    return {'ok': True, 'operation': 'search', 'query': '官方文档',
            'retrieved_at': '2026-11-15T08:00:00Z', 'requests': [{'provider': 'synthetic'}],
            'errors': [], 'results': [
                {'provider': 'first', 'rank': 3, 'title': '文档', 'url': 'https://example.com/docs',
                 'snippet': '摘要', 'content_kind': 'excerpts', 'published_at': None},
                {'provider': 'second', 'rank': 1, 'title': '=HYPERLINK("bad")',
                 'url': 'https://example.com/docs', 'summary': 'x' * 700,
                 'published_at': '2026-11', 'content_kind': 'search_summary'}]}


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = x.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_round_trip_and_repeat_export_without_network_or_credentials(self):
        data = snapshot()
        original = copy.deepcopy(data)
        saved = exports.export_result(data, self.root / 'zh')
        source = Path(saved['files']['results.json'])
        self.assertEqual(exports.load_result(source), original)
        self.assertEqual(data, original)
        times = {p.name: p.stat().st_mtime_ns for p in source.parent.iterdir()}
        with patch.object(x, 'read_config', side_effect=AssertionError('credentials read')), \
                patch.object(x, 'request_api', side_effect=AssertionError('network')), \
                patch.object(x, 'run_search', side_effect=AssertionError('search')):
            code, out, err = self.cli(['export', '--input', str(source), '--output-dir', str(source.parent)])
            self.assertEqual((code, err), (0, ''))
            self.assertEqual(json.loads(out)['network_requests'], 0)
            code, out, err = self.cli(['export', '--input', str(source), '--output-dir', str(self.root / 'en'), '--language', 'en'])
            self.assertEqual((code, err), (0, ''))
        self.assertEqual(times, {p.name: p.stat().st_mtime_ns for p in source.parent.iterdir()})
        self.assertIn('Query:', (self.root / 'en' / 'report.md').read_text())
        self.assertEqual(json.loads((self.root / 'en' / 'results.json').read_text()), original)

    def test_order_duplicate_attribution_missing_dates_and_csv_formula(self):
        result = exports.export_result(snapshot(), self.root / 'results')
        raw = Path(result['files']['links.csv']).read_bytes()
        self.assertTrue(raw.startswith(b'\xef\xbb\xbf'))
        rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
        self.assertEqual([r['provider'] for r in rows], ['first', 'second'])
        self.assertEqual([r['provider_rank'] for r in rows], ['3', '1'])
        self.assertEqual(rows[0]['url'], rows[1]['url'])
        self.assertEqual(rows[0]['published_at'], '')
        self.assertEqual(rows[1]['published_at'], '2026-11')
        self.assertTrue(rows[1]['title'].startswith("'="))
        report = Path(result['files']['report.md']).read_text()
        self.assertIn('未提供', report)
        self.assertIn('前 600 字符', report)
        self.assertIn('来源域名数：1', report)
        for dangerous in ('  =SUM(1)', '\ufeff+SUM(1)', '\tplain', '\rplain', '-1', '@cmd'):
            data = snapshot()
            data['results'][0]['title'] = dangerous
            row = list(csv.DictReader(io.StringIO(exports.links_csv(data).lstrip('\ufeff'))))[0]
            self.assertEqual(row['title'], "'" + dangerous)

    def test_markup_is_escaped_and_partial_status_preserved(self):
        data = snapshot()
        data['partial'] = True
        data['errors'] = [{'code': 'timeout'}]
        data['results'][0]['title'] = '<script>run</script> [fake](x) | col\n# heading'
        data['results'][0]['url'] = 'https://example.com/<tag>|path'
        report = exports.markdown(data, 'en')
        self.assertNotIn('<script>', report)
        self.assertNotIn('[fake](x)', report)
        self.assertNotIn('\n# heading', report)
        self.assertIn('%3Ctag%3E%7Cpath', report)
        self.assertIn('Saved errors or partial results: yes', report)

    def test_invalid_inputs_are_rejected(self):
        cases = [[], {'operation': 'fetch'}, snapshot(), snapshot(), snapshot()]
        cases[2]['results'][0]['url'] = 'http://127.0.0.1/a'
        cases[3]['results'][0]['highlights'] = [5]
        cases[4]['results'][0]['summary'] = {'bad': 'shape'}
        for data in cases:
            with self.subTest(data=data), self.assertRaises(x.SearchError):
                exports.export_result(data, self.root / 'invalid')
        source = self.root / 'input.json'
        for raw in (b'not json', b'\xff', b'[]'):
            source.write_bytes(raw)
            with self.assertRaises(x.SearchError):
                exports.load_result(source)
        source.write_bytes(b' ' * 65)
        with patch.object(exports, 'MAX_SNAPSHOT', 64), self.assertRaises(x.SearchError):
            exports.load_result(source)
        self.assertFalse((self.root / 'invalid').exists())

    def test_existing_content_and_symlinks_are_preserved(self):
        target = self.root / 'existing'
        target.mkdir()
        (target / 'keep.txt').write_text('keep')
        with self.assertRaises(x.SearchError) as caught:
            exports.export_result(snapshot(), target)
        self.assertEqual(caught.exception.code, 'output_exists')
        self.assertEqual((target / 'keep.txt').read_text(), 'keep')
        exports.export_result(snapshot(), self.root / 'same')
        with self.assertRaises(x.SearchError):
            exports.export_result(snapshot(), self.root / 'same', 'en')
        if os.name != 'nt':
            link = self.root / 'link'
            link.symlink_to(self.root / 'same', target_is_directory=True)
            with self.assertRaises(x.SearchError):
                exports.export_result(snapshot(), link)

    def test_publish_failure_cleans_partial_export_and_staging(self):
        replace = Path.replace
        calls = []

        def fail_second(path, target):
            calls.append(target)
            if len(calls) == 2:
                raise OSError('synthetic disk failure')
            return replace(path, target)

        with patch.object(Path, 'replace', fail_second), self.assertRaises(OSError):
            exports.export_result(snapshot(), self.root / 'out')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_search_saves_once_and_existing_path_blocks_before_search(self):
        target = self.root / 'search'
        with patch.object(x, 'read_config', return_value={}), \
                patch.object(x, 'run_search', return_value=snapshot()) as search:
            code, out, err = self.cli(['search', 'test', '--output-dir', str(target)])
            self.assertEqual((code, err), (0, ''))
            self.assertEqual(search.call_count, 1)
            self.assertIn('saved_files', json.loads(out))
        with patch.object(x, 'read_config', side_effect=AssertionError('too late')), \
                patch.object(x, 'run_search', side_effect=AssertionError('search repeated')):
            code, out, err = self.cli(['search', 'test', '--output-dir', str(target)])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(err)['error']['code'], 'output_exists')

    def test_save_failure_preserves_completed_search_json(self):
        with patch.object(x, 'read_config', return_value={}), \
                patch.object(x, 'run_search', return_value=snapshot()) as search, \
                patch.object(x, 'export_result', side_effect=PermissionError('private system details')):
            code, out, err = self.cli(['search', 'test', '--output-dir', str(self.root / 'out')])
        self.assertEqual(code, 1)
        self.assertEqual(err, '')
        data = json.loads(out)
        self.assertEqual(data['results'], snapshot()['results'])
        self.assertEqual(data['export_error']['code'], 'export_failed')
        self.assertEqual(data['export_error']['cause'], 'local_permission_denied')
        self.assertNotIn('private system details', out)
        self.assertEqual(search.call_count, 1)

    def test_plan_with_output_option_never_writes(self):
        with patch.object(x, 'read_config', return_value={'providers': {}}), \
                patch.object(x, 'request_api', side_effect=AssertionError('network')):
            code, out, err = self.cli(['plan', 'test', '--output-dir', str(self.root / 'out')])
        self.assertEqual((code, err), (0, ''))
        self.assertEqual(json.loads(out)['network_requests'], 0)
        self.assertFalse((self.root / 'out').exists())


if __name__ == '__main__':
    unittest.main()
