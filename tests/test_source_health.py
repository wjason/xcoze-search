import json
from datetime import datetime,timezone
from pathlib import Path
import tempfile
import unittest
from source_health import load_snapshot,pack_snapshot
from unittest.mock import patch,MagicMock
from source_health import refresh_snapshot


class SourceHealthTests(unittest.TestCase):
    def test_explicit_refresh_writes_only_public_cache_and_preserves_it_on_invalid_data(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'cache.json'
            valid={'schema_version':1,'checked_at':'2026-11-22T00:00:00+00:00','results':[{'kind':'search','id':'docs','status':'passed','query':'private'}]}
            response=MagicMock();response.__enter__.return_value.read.return_value=json.dumps(valid).encode()
            with patch('source_health.cache_path',return_value=target),patch('source_health.urllib.request.urlopen',return_value=response) as request:
                self.assertEqual(refresh_snapshot()['network_requests'],1)
                request.assert_called_once();saved=target.read_bytes();self.assertNotIn(b'private',saved)
                response.__enter__.return_value.read.return_value=b'{"schema_version":1,"results":[]}'
                with self.assertRaises(ValueError):refresh_snapshot()
                self.assertEqual(target.read_bytes(),saved)

    def test_local_status_uses_newer_public_cache_without_network(self):
        with tempfile.TemporaryDirectory() as folder:
            cache=Path(folder)/'cache.json'
            pack_snapshot({'checked_at':'2099-01-01T00:00:00+00:00','results':[{'kind':'search','id':'cache','status':'passed'}]},cache)
            with patch('source_health.cache_path',return_value=cache),patch('source_health.urllib.request.urlopen') as request:
                result=load_snapshot();request.assert_not_called()
                self.assertIn(('search','cache'),result['actions']);self.assertTrue(result['stale'])

    def test_old_future_and_missing_checks_are_not_current_availability(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'health.json'
            self.assertTrue(load_snapshot(path)['stale'])
            for stamp,expected in [('2026-11-21T00:00:00+00:00',False),('2026-11-01T00:00:00+00:00',True),('2026-11-24T00:00:00+00:00',True)]:
                path.write_text(json.dumps({'schema_version':1,'checked_at':stamp,'results':[{'kind':'search','id':'docs','status':'passed','count':1}]}))
                result=load_snapshot(path,now=datetime(2026,11,22,tzinfo=timezone.utc))
                self.assertEqual(result['actions'][('search','docs')]['stale'],expected)

    def test_published_snapshot_discards_queries_account_checks_and_error_bodies(self):
        raw={'checked_at':'2026-11-22T00:00:00+00:00','results':[
            {'kind':'keyed','id':'deepseek','status':'limited','error':'private'},
            {'kind':'search','id':'docs','status':'passed','count':1,'query':'private','errors':['private-body']}]}
        with tempfile.TemporaryDirectory() as folder:
            out=pack_snapshot(raw,Path(folder)/'health.json')
            self.assertEqual(len(out['results']),1);self.assertNotIn('private',json.dumps(out))


if __name__=='__main__':unittest.main()
