#!/usr/bin/env python3
"""Check public adapters through the runtime, with one attempt per action."""
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import xcoze_search as search
from content_sources import FEEDS
from public_trends import TRENDING

BEIJING = timezone(timedelta(hours=8))
SEARCH = {
    'bing': 'Python asyncio TaskGroup documentation',
    'duckduckgo': 'Python asyncio TaskGroup documentation',
    'exa-free': 'Python asyncio TaskGroup documentation',
    'github': 'microsoft/markitdown', 'hackernews': 'SQLite',
    'wikipedia': '协调世界时', 'stackexchange': 'asyncio TaskGroup',
    'arxiv': 'retrieval augmented generation', 'crossref': 'deep learning Lecun',
    'npm': 'typescript', 'crates': 'serde', 'gitlab': 'inkscape',
    'europepmc': 'protein structure prediction', 'huggingface': 'Qwen',
    'openlibrary': 'Pride and Prejudice', 'datacite': 'climate change',
    'zenodo': 'climate change', 'wikidata': 'Beijing', 'nasa': 'Artemis I launch',
    'federalregister': 'artificial intelligence', 'worldbank': 'CN,SP.POP.TOTL',
    'usgs': '2.5,week', 'govcn': '政策', 'ndrc': '通知', 'nbs': '经济',
    'nea': '能源', 'miit': '工业', 'mee': '生态', 'mem': '安全', 'pbc': '金融',
    'ggzy': '交易', 'mofcom': '商务', 'csrc': '证监', 'ccgp': '采购',
    'cas': '研究', 'cgs': '地质', 'xinhua': '中国',
}
SCOPES = {
    'zhihu': 'Python asyncio', 'xiaohongshu': '上海 咖啡', 'weibo': '人工智能',
    'youtube': 'SQLite tutorial', 'bilibili': 'Python 教程', 'reddit': 'SQLite',
    'twitter': 'Python release', 'v2ex': 'Python', 'douban': '三体',
    'china-data': '国内生产总值', 'cma-data': '地面气象数据', 'china-weather': '北京 天气',
    'cninfo': '年度报告', 'sse': '上市公司 公告', 'szse': '上市公司 公告',
    'bse': '上市公司 公告', 'china-standards': '信息安全 标准',
    'china-laws': '中华人民共和国 民法典', 'cnsa': '嫦娥六号',
    'scidb': '气候 数据集', 'ceic': '地震 速报', 'nmefc': '海洋 预报', 'hko': '天文台 天气',
}
FETCH = {
    'github': 'https://github.com/microsoft/markitdown',
    'hackernews': 'https://news.ycombinator.com/item?id=27016630',
    'jina': 'https://docs.python.org/3/library/asyncio-task.html',
    'exa-free': 'https://docs.python.org/3/library/asyncio-task.html',
    'community-python': 'https://discuss.python.org/t/109869',
    'community-rust': 'https://users.rust-lang.org/t/forum-code-formatting-and-syntax-highlighting/42214',
    'community-v2ex': 'https://www.v2ex.com/t/1254349',
}


def probes():
    for source, query in SEARCH.items():
        yield 'search', source, ['search', query, '--provider', source, '--count', '1']
    for source in FEEDS:
        yield 'feed', source, ['feed', '--source', source, '--count', '1']
    for platform in TRENDING:
        yield 'trending', platform, ['trending', '--platform', platform, '--count', '1']
    for source, url in FETCH.items():
        provider = 'community' if source.startswith('community-') else source
        yield 'fetch', source, ['fetch', url, '--provider', provider]
    for platform, query in SCOPES.items():
        yield 'scope', platform, ['search', query, '--platform', platform,
                                  '--provider', 'exa-free', '--count', '1']


def check(kind, source, argv, timeout):
    started = time.monotonic()
    if kind in {'search', 'scope', 'fetch'}:
        argv = argv + ['--strategy', 'free', '--max-requests', '1', '--retries', '0']
    args = search.parser().parse_args(argv + ['--timeout', str(timeout)])
    original = search.request_api

    def public_request(operation, payload, key, **options):
        name = operation.removesuffix('_fetch')
        if operation == 'fetch' or key or search.get_provider(name).requires_key:
            raise AssertionError('Keyed request blocked by public-source audit.')
        return original(operation, payload, key, **options)

    def public_credential(provider, config):
        if search.get_provider(provider).requires_key:
            raise search.SearchError('missing_api_key', 'Keyed providers are outside this audit.')
        return '', 'not_required'

    try:
        with patch.object(search, 'request_api', public_request), \
                patch.object(search, 'credential', public_credential):
            config = {'schema_version': 2, 'providers': {}}
            if kind == 'feed':
                result = search.run_feed(args, public_request, search.VERSION)
            elif kind == 'trending':
                result = search.run_trending(args, public_request, search.VERSION)
            elif kind == 'fetch':
                result = search.run_fetch(args, config)
            else:
                result = search.run_search(args, config)
        if kind == 'fetch':
            count = int(bool(result.get('content', '').strip()) or result.get('content_kind') == 'discussion_item')
        else:
            count = len(result['results'])
        errors = result.get('errors', [])
        attempts = result.get('budget', {}).get('attempts', result.get('attempts', 0))
    except search.SearchError as exc:
        count, errors, attempts = 0, [exc.data()], exc.attempts
    state = 'limited' if errors else 'passed' if count else 'empty'
    return {'kind': kind, 'id': source, 'status': state, 'count': count,
            'attempts': attempts, 'elapsed_ms': round(1000 * (time.monotonic() - started)),
            'errors': [{k: e[k] for k in ('code', 'http_status') if k in e} for e in errors]}


def summary(report, baseline):
    rows = report['results']
    counts = Counter(row['status'] for row in rows)
    previous = {(r['kind'], r['id']): r['status'] for r in baseline['results']}
    changed = [r for r in rows if previous.get((r['kind'], r['id'])) not in (None, r['status'])]
    lines = [
        '## 公开来源巡检 / Public source check', '',
        f"Checked {report['checked_at']} · {report['environment']} · "
        f"{counts['passed']} passed · {counts['limited']} limited · {counts['empty']} empty", '',
        f"Baseline / 对照快照 {baseline['checked_at']} · {len(changed)} status changes", '',
        '| Action | Source | Status | Baseline | HTTP attempts | Detail |',
        '|---|---|---|---|---:|---|',
    ]
    for r in rows:
        before = previous.get((r['kind'], r['id']), '—')
        detail = ', '.join(f"{e['code']} {e.get('http_status') or ''}".strip() for e in r['errors'])
        lines.append(f"| {r['kind']} | {r['id']} | {r['status']} | {before} | {r['attempts']} | {detail} |")
    lines += ['', 'One sample per action. Results reflect this runner and time. '
              'API keys and browser engines are outside this check.']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Send the public sample requests')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--summary', type=Path)
    parser.add_argument('--baseline', type=Path, default=ROOT / 'evaluations/reports/2026-11-05-source-status.json')
    parser.add_argument('--timeout', type=int, choices=range(1, 16), default=8, metavar='1..15')
    parser.add_argument('--environment', choices=('local', 'github-actions'), default='local')
    args = parser.parse_args()
    started = datetime.now(BEIJING).isoformat(timespec='seconds')
    cases = list(probes())
    baseline = json.loads(args.baseline.read_text(encoding='utf-8')) if args.summary and args.live else None
    rows = [check(kind, source, command, args.timeout) for kind, source, command in cases] if args.live else []
    report = {'schema_version': 1, 'live': args.live, 'environment': args.environment,
              'started_at': started, 'checked_at': datetime.now(BEIJING).isoformat(timespec='seconds'),
              'planned_actions': len(cases), 'http_attempts': sum(r['attempts'] for r in rows),
              'results': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    if baseline is not None:
        with args.summary.open('a', encoding='utf-8') as stream:
            stream.write(summary(report, baseline))
    print(json.dumps({'live': args.live, 'planned_actions': len(cases),
                      'statuses': Counter(row['status'] for row in rows)}))


if __name__ == '__main__':
    main()
