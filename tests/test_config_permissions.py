import io
import json
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch
from test_search import x

class ConfigPermissionTests(unittest.TestCase):
    def test_config_read_denied_is_specific_and_redacted(self):
        with patch.object(x, 'check_config_path', side_effect=PermissionError('secret path')):
            with self.assertRaises(x.SearchError) as caught:
                x.read_config()
        self.assertEqual(caught.exception.code, 'config_permission_denied')
        self.assertNotIn('secret path', str(caught.exception))

    def test_config_read_io_error_is_not_bad_json(self):
        with patch.object(x, 'check_config_path', side_effect=OSError('private details')):
            with self.assertRaises(x.SearchError) as caught:
                x.read_config()
        self.assertEqual(caught.exception.code, 'config_io_error')
        self.assertNotIn('private details', str(caught.exception))

    def test_config_save_denied_is_specific(self):
        with patch.object(x, '_save_config', side_effect=PermissionError('secret')):
            with self.assertRaises(x.SearchError) as caught:
                x.save_config({'schema_version': 2, 'providers': {}})
        self.assertEqual(caught.exception.code, 'config_permission_denied')

    def test_other_local_permission_does_not_claim_config(self):
        with patch.object(x, 'read_config', side_effect=PermissionError('private')), redirect_stderr(io.StringIO()) as out:
            self.assertEqual(x.main(['status']), 1)
        error = json.loads(out.getvalue())['error']
        self.assertEqual(error['code'], 'local_permission_denied')
        self.assertNotIn('private', out.getvalue())

if __name__ == '__main__': unittest.main()
