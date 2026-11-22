"""Dated action-level public-source availability, separate from adapter support."""
from datetime import datetime, timezone
import json
import re
import os
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
SNAPSHOT=ROOT/'references/source-health.json'


def cache_path():
    return Path(os.environ.get('XDG_CACHE_HOME') or Path.home()/'.cache')/'xcoze-search/source-health.json'


def load_snapshot(path=SNAPSHOT,now=None,max_age_days=7):
    now=now or datetime.now(timezone.utc)
    if Path(path)==SNAPSHOT:
        try:
            cached=json.loads(cache_path().read_text(encoding='utf-8'))
            bundled=json.loads(SNAPSHOT.read_text(encoding='utf-8'))
            if cached.get('schema_version')==1 and cached.get('checked_at','')>bundled.get('checked_at',''):path=cache_path()
        except (OSError,ValueError,TypeError,AttributeError):pass
    try:
        raw=json.loads(Path(path).read_text(encoding='utf-8'))
        if raw.get('schema_version')!=1 or not isinstance(raw.get('results'),list): raise ValueError
    except (OSError,ValueError,TypeError,AttributeError):
        return {'checked_at':None,'stale':True,'max_age_days':max_age_days,'actions':{},'snapshot_available':False}
    actions={}
    for row in raw['results']:
        if not isinstance(row,dict) or not isinstance(row.get('id'),str):continue
        if row.get('kind') not in ('search','fetch','scope','documentation','feed','trending'): continue
        stamp=row.get('checked_at') or raw.get('checked_at')
        try:
            parsed=datetime.fromisoformat(stamp.replace('Z','+00:00'))
            if parsed.tzinfo is None: raise ValueError
            age=(now-parsed.astimezone(timezone.utc)).total_seconds()
            stale=age<0 or age>max_age_days*86400
        except (ValueError,AttributeError,TypeError): stale=True
        actions[(row['kind'],row['id'])]={'status':row.get('status','not_tested'),
            'checked_at':stamp,'stale':stale,'sample_only':True,'count':row.get('count',0),
            'errors':row.get('errors',[])}
    return {'checked_at':raw.get('checked_at'),'stale':not actions or all(a['stale'] for a in actions.values()),
            'max_age_days':max_age_days,'actions':actions,'snapshot_available':True}


def public_health():
    snapshot=load_snapshot()
    return {k:v for k,v in snapshot.items() if k!='actions'}|{'actions':[
        {'kind':kind,'id':source,**row} for (kind,source),row in snapshot['actions'].items()]}


def sample_health(source,kind='search'):
    return load_snapshot()['actions'].get((kind,source),
        {'status':'not_tested','checked_at':None,'stale':True,'sample_only':True,'count':None})


def pack_snapshot(report,path=SNAPSHOT):
    """Keep only public probe metadata: never raw bodies, queries or account errors."""
    rows=[]
    for row in report['results']:
        if not isinstance(row,dict):continue
        if row.get('kind') in ('keyed','keyed_fetch','browser'): continue
        kept={k:row[k] for k in ('kind','id','status','count','attempts','elapsed_ms','checked_at') if k in row}
        kept['errors']=[{k:e[k] for k in ('code','http_status') if k in e} for e in row.get('errors',[])
                        if isinstance(e,dict) and isinstance(e.get('code'),str) and re.fullmatch(r'[A-Za-z0-9_.]{1,80}',e['code'])]
        rows.append(kept)
    output={'schema_version':1,'checked_at':report['checked_at'],'environment':report.get('environment'),
            'max_age_days':7,'scope':'one public sample per action; not uptime or accuracy', 'results':rows}
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return output


def refresh_snapshot():
    """One explicit public metadata request; never change an installed manifest or user config."""
    req=urllib.request.Request('https://raw.githubusercontent.com/wjason/xcoze-search/main/references/source-health.json',
        headers={'User-Agent':'xcoze-search-health','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=8) as response:raw=response.read(1_000_001)
    if len(raw)>1_000_000:raise ValueError('Public status snapshot exceeds its limit.')
    report=json.loads(raw)
    if not isinstance(report,dict) or report.get('schema_version')!=1 or not isinstance(report.get('results'),list):raise ValueError('Invalid public status snapshot.')
    try:
        stamp=datetime.fromisoformat(report['checked_at'].replace('Z','+00:00'))
        if stamp.tzinfo is None:raise ValueError
    except (KeyError,ValueError,TypeError,AttributeError):raise ValueError('Invalid public status timestamp.') from None
    target=cache_path();target.parent.mkdir(parents=True,exist_ok=True)
    temporary=target.with_suffix('.tmp.json')
    pack_snapshot(report,temporary);temporary.replace(target)
    return {'ok':True,'operation':'refresh_sources','network_requests':1,'checked_at':report['checked_at'],'config_changed':False}
