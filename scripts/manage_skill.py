#!/usr/bin/env python3
"""Check/install/update this Skill, with verified files and recoverable replacement."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile
import uuid

REPO = 'wjason/xcoze-search'
API = 'https://api.github.com/repos/' + REPO + '/releases?per_page=20'


def is_newer(candidate,current):
    return current is None or tuple(map(int,candidate.split('.')))>tuple(map(int,current.split('.')))


def version_at(folder):
    path=folder/'scripts/xcoze_search.py'
    if not path.exists(): return None
    for node in ast.parse(path.read_text(encoding='utf-8')).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='VERSION' for t in node.targets):
            value=ast.literal_eval(node.value)
            if isinstance(value,str) and re.fullmatch(r'\d+\.\d+\.\d+',value): return value
    raise ValueError('Cannot identify installed version.')


def default_target():
    return Path(os.environ.get('CODEX_HOME') or Path.home()/'.codex')/'skills/xcoze-search'


def download(url,limit=25_000_000):
    request=urllib.request.Request(url,headers={'User-Agent':'xcoze-search-updater','Accept':'application/vnd.github+json' if url==API else 'application/octet-stream'})
    with urllib.request.urlopen(request,timeout=20) as response: data=response.read(limit+1)
    if len(data)>limit: raise ValueError('Release response exceeds the download limit.')
    return data


def latest_release(stable=False):
    rows=json.loads(download(API,2_000_000))
    if not isinstance(rows,list): raise ValueError('Unrecognized GitHub releases response.')
    rows=[r for r in rows if not r.get('draft') and (not stable or not r.get('prerelease'))
          and re.fullmatch(r'v\d+\.\d+\.\d+',r.get('tag_name',''))]
    if not rows: raise ValueError('No matching published release is available.')
    # Published release chronology, not lexicographic version strings.
    rows.sort(key=lambda r:r.get('published_at') or '',reverse=True)
    return rows[0]


def validate_tree(folder):
    manifest_path=folder/'manifest.json'
    if not manifest_path.is_file(): raise ValueError('Package has no integrity manifest.')
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    if not (folder/'SKILL.md').is_file() or not re.search(r'^name:\s*xcoze-search\s*$',(folder/'SKILL.md').read_text(encoding='utf-8'),re.M):
        raise ValueError('Package is not the xcoze-search Skill.')
    if manifest.get('version')!=version_at(folder) or not isinstance(manifest.get('files'),dict):
        raise ValueError('Manifest and runtime versions do not match.')
    actual={str(p.relative_to(folder).as_posix()) for p in folder.rglob('*') if p.is_file()}
    if actual != set(manifest['files'])|{'manifest.json'}: raise ValueError('Package contains missing or unexpected files.')
    for name,digest in manifest['files'].items():
        relative=PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or '\\' in name: raise ValueError('Unsafe manifest path.')
        path=folder.joinpath(*relative.parts)
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('Package file failed integrity verification.')
    return manifest


def install_archive(archive,target):
    target=Path(target).expanduser().absolute()
    if target.is_symlink() or target.parent.is_symlink() or (target/'.git').exists():
        raise ValueError('Target must be a real Skill folder, not a symlink or a Git working tree.')
    if target.exists() and (not (target/'SKILL.md').is_file() or not re.search(r'^name:\s*xcoze-search\s*$',(target/'SKILL.md').read_text(encoding='utf-8'),re.M)):
        raise ValueError('Refusing to replace a directory that is not this Skill.')
    target.parent.mkdir(parents=True,exist_ok=True)
    backup=None
    with tempfile.TemporaryDirectory(prefix='.xcoze-stage-',dir=target.parent) as staging:
        stage=Path(staging)
        with zipfile.ZipFile(archive) as package:
            infos=package.infolist()
            if len(infos)>500 or sum(i.file_size for i in infos)>40_000_000: raise ValueError('Package exceeds extraction limits.')
            for item in infos:
                name=PurePosixPath(item.filename)
                if name.is_absolute() or '..' in name.parts or '\\' in item.filename or name.parts[0]!='xcoze-search' or (item.external_attr>>16)&0o170000==0o120000:
                    raise ValueError('Unsafe archive member.')
            package.extractall(stage)
            if os.name=='posix':
                for item in infos:
                    extracted=stage/item.filename
                    if extracted.is_file(): extracted.chmod(((item.external_attr>>16)&0o777) or 0o644)
        prepared=stage/'xcoze-search';manifest=validate_tree(prepared)
        if target.exists():
            # Preserve local edits and custom files in the backup, outside the Agent's discovery directory.
            cache=Path(os.environ.get('XDG_CACHE_HOME') or Path.home()/'.cache')/'xcoze-search/backups'
            cache.mkdir(parents=True,exist_ok=True)
            backup=cache/('skill-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8])
            shutil.copytree(target,backup,symlinks=True)
            old=stage/'previous';target.rename(old)
        else: old=None
        try: prepared.rename(target)
        except OSError:
            if old is not None: old.rename(target)
            raise
    return {'ok':True,'version':manifest['version'],'target':str(target),'backup':str(backup) if backup else None,
            'config_changed':False,'message':'Reload the Agent or start a new session to discover updated instructions.'}


def update(target,stable=False):
    release=latest_release(stable);version=release['tag_name'][1:]
    current=version_at(target)
    if not is_newer(version,current): return {'ok':True,'version':current,'published_version':version,'updated':False,'target':str(target)}
    expected_name='xcoze-search-skill-v'+version+'.zip'
    urls={a['name']:a['browser_download_url'] for a in release.get('assets',[])}
    if expected_name not in urls or 'SHA256SUMS.txt' not in urls: raise ValueError('Published release is missing its complete package or checksums.')
    prefix='https://github.com/'+REPO+'/releases/download/'+release['tag_name']+'/'
    if any(not urls[name].startswith(prefix) for name in (expected_name,'SHA256SUMS.txt')): raise ValueError('Unexpected release asset URL.')
    checks=download(urls['SHA256SUMS.txt'],65536).decode('utf-8')
    match=re.search(r'^([0-9a-f]{64})\s+'+re.escape(expected_name)+r'\s*$',checks,re.M)
    data=download(urls[expected_name])
    if not match or hashlib.sha256(data).hexdigest()!=match[1]: raise ValueError('Release archive checksum does not match.')
    with tempfile.TemporaryDirectory(prefix='xcoze-update-') as folder:
        archive=Path(folder)/expected_name;archive.write_bytes(data)
        result=install_archive(archive,target)
    return {**result,'updated':True,'release':release['html_url'],'prerelease':release.get('prerelease',False)}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('check','install','update','restore'))
    parser.add_argument('--target',type=Path,default=default_target())
    parser.add_argument('--source',type=Path,help='Verified local Skill ZIP for install, or a backup directory for restore')
    parser.add_argument('--offline',action='store_true')
    parser.add_argument('--stable',action='store_true',help='Exclude preview releases; default includes published previews')
    args=parser.parse_args(argv)
    try:
        if args.action=='check':
            current=version_at(args.target);out={'ok':True,'installed_version':current,'target':str(args.target),'network_requests':0}
            if not args.offline:
                release=latest_release(args.stable);out.update(latest_version=release['tag_name'][1:],release=release['html_url'],
                    update_available=is_newer(release['tag_name'][1:],current),prerelease=release.get('prerelease',False),network_requests=1)
        elif args.action=='install':
            if args.source is None: raise ValueError('install requires --source Skill ZIP.')
            out=install_archive(args.source,args.target)
        elif args.action=='update':
            if args.offline: raise ValueError('update needs network access; use install --source for an offline package.')
            out=update(args.target,args.stable)
        else:
            if args.source is None or not (args.source/'SKILL.md').is_file() or not version_at(args.source) or any(p.is_symlink() for p in args.source.rglob('*')): raise ValueError('restore requires a valid backup folder without symlinks.')
            # Build a local verified archive of the preserved tree without executing its code.
            with tempfile.TemporaryDirectory(prefix='xcoze-restore-') as folder:
                copy=Path(folder)/'copy';shutil.copytree(args.source,copy,symlinks=False)
                files={p.relative_to(copy).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in copy.rglob('*') if p.is_file() and p.name!='manifest.json'}
                (copy/'manifest.json').write_text(json.dumps({'version':version_at(copy),'files':files}))
                archive=Path(folder)/'restore.zip'
                with zipfile.ZipFile(archive,'w') as z:
                    for p in copy.rglob('*'):
                        if p.is_file(): z.write(p,'xcoze-search/'+p.relative_to(copy).as_posix())
                out=install_archive(archive,args.target)
        print(json.dumps(out,ensure_ascii=False,indent=2));return 0
    except (ValueError,OSError,zipfile.BadZipFile,urllib.error.URLError,SyntaxError) as error:
        code='local_permission_denied' if isinstance(error,PermissionError) else 'network_error' if isinstance(error,urllib.error.URLError) else 'invalid_package_or_target'
        print(json.dumps({'ok':False,'error':code,'message':'Version check or installation failed; existing configuration was not changed. Inspect network, package integrity or target permissions for this error category.'}));return 1


if __name__=='__main__': raise SystemExit(main())
