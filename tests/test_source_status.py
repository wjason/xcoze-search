"""Coverage and privacy checks for the published source-status snapshot."""
import json
from pathlib import Path
import unittest
from public_providers import PUBLIC_REGISTRY
from search_providers import REGISTRY
from content_sources import FEEDS
from public_trends import TRENDING
from search_routing import PLATFORMS, NATIVE_PLATFORMS

ROOT = Path(__file__).resolve().parents[1]

class SourceStatusSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads((ROOT / 'evaluations/reports/2026-11-05-source-status.json').read_text(encoding='utf-8'))
        cls.by_kind = {}
        for row in cls.audit['results']:
            cls.by_kind.setdefault(row['kind'], set()).add(row['id'])

    def test_snapshot_covers_current_search_and_scoped_sources(self):
        self.assertEqual(self.by_kind['search'], {n for n,p in PUBLIC_REGISTRY.items() if p.supports_search and n != 'browser'})
        self.assertEqual(self.by_kind['scope'], {n for n in PLATFORMS if n not in NATIVE_PLATFORMS})
        self.assertEqual(self.by_kind['feed'], set(FEEDS))
        self.assertEqual(self.by_kind['trending'], set(TRENDING))
        self.assertEqual(self.by_kind['keyed'], set(REGISTRY))
        self.assertEqual(self.by_kind['keyed_fetch'], {n for n,p in REGISTRY.items() if p.fetch_endpoint})
        self.assertEqual(self.by_kind['browser'], {'360','bing','google'})

    def test_public_snapshot_excludes_account_specific_errors_and_secrets(self):
        rows = self.audit['results']
        keyed = next(x for x in rows if x['kind'] == 'keyed' and x['id'] == 'deepseek')
        self.assertFalse(any('http_status' in error or 'category' in error for error in keyed.get('errors', [])))
        text = json.dumps(self.audit).lower()
        self.assertNotIn('api_key', text)
        self.assertNotIn('authorization', text)
        self.assertTrue(all((r.get('keyed_attempts') or 0) == 0 for r in rows if r['kind'] != 'keyed'))

    def test_bilingual_status_pages_include_search_and_pending(self):
        for filename, phrases in [('source-status.md', ('支持 · 适配通过','待支持','支持 · 本次受限')),
                                  ('source-status.en.md', ('Supported · Passed','Candidates','Supported · Limited'))]:
            text = (ROOT / 'references' / filename).read_text(encoding='utf-8')
            for phrase in phrases: self.assertIn(phrase, text)

if __name__ == '__main__': unittest.main()
