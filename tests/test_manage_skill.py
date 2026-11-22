import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec=importlib.util.spec_from_file_location('manager',Path(__file__).resolve().parents[1]/'scripts/manage_skill.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class ManagerTests(unittest.TestCase):
    def test_versions_use_numeric_order_and_never_offer_a_downgrade(self):
        self.assertTrue(m.is_newer('0.10.0','0.9.1'));self.assertFalse(m.is_newer('0.9.1','0.10.0'))
        self.assertFalse(m.is_newer('0.10.0','0.10.0'))
    def package(self,base,version='0.10.0',tamper=False,extra=None):
        files={'SKILL.md':b'---\nname: xcoze-search\n---\n','scripts/xcoze_search.py':('VERSION = "'+version+'"\n').encode()}
        manifest={'version':version,'files':{n:hashlib.sha256(b).hexdigest() for n,b in files.items()}}
        archive=base/'package.zip'
        with zipfile.ZipFile(archive,'w') as z:
            for n,b in files.items():z.writestr('xcoze-search/'+n,b+b'tampered' if tamper and n=='SKILL.md' else b)
            z.writestr('xcoze-search/manifest.json',json.dumps(manifest))
            if extra:z.writestr(extra,b'bad')
        return archive

    def test_verified_update_preserves_custom_install_files_in_backup_and_keeps_config(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'XDG_CACHE_HOME':folder}):
            root=Path(folder);target=root/'skill';target.mkdir();(target/'SKILL.md').write_text('---\nname: xcoze-search\n---\n')
            (target/'local.txt').write_text('custom edit');config=root/'config.json';config.write_text('synthetic-private-config')
            out=m.install_archive(self.package(root),target)
            self.assertEqual(m.version_at(target),'0.10.0');self.assertEqual((Path(out['backup'])/'local.txt').read_text(),'custom edit')
            self.assertEqual(config.read_text(),'synthetic-private-config');self.assertFalse(out['config_changed'])

    def test_bad_hash_and_zip_traversal_never_replace_existing_skill(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'XDG_CACHE_HOME':folder}):
            root=Path(folder);target=root/'skill';target.mkdir();(target/'SKILL.md').write_text('---\nname: xcoze-search\n---\noriginal')
            for options in ({'tamper':True},{'extra':'xcoze-search/../../outside'}):
                with self.assertRaises(ValueError):m.install_archive(self.package(root,**options),target)
                self.assertIn('original',(target/'SKILL.md').read_text())
            self.assertFalse((root/'outside').exists())

    def test_other_skill_and_git_working_tree_cannot_be_replaced(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);target=root/'skill';target.mkdir();(target/'SKILL.md').write_text('name: unrelated')
            with self.assertRaises(ValueError):m.install_archive(self.package(root),target)
            (target/'SKILL.md').write_text('name: xcoze-search');(target/'.git').mkdir()
            with self.assertRaises(ValueError):m.install_archive(self.package(root),target)


if __name__=='__main__':unittest.main()
