#!/usr/bin/env python3
"""Opt-in live browser acceptance. No simulated search responses or user credential files."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import time

import xcoze_search as search

# GitHub is a coverage probe: native GitHub APIs remain the normal route.
# Its missing public-index results are reported, never counted as a pass.
CASES = (
    {'id': 'python_taskgroup', 'query': 'Python TaskGroup',
     'site': 'docs.python.org', 'expected_url': '/library/asyncio-task.html', 'expected_text': 'taskgroup'},
    {'id': 'china_cpi', 'query': '国家统计局 2026年9月 居民消费价格 CPI',
     'site': 'stats.gov.cn', 'expected_url': 'stats.gov.cn', 'expected_text': '消费价格'},
    {'id': 'xinneng_taishan', 'query': '新能泰山 2026年 第三季度 报告',
     'expected_url': 'stock.cfi.cn/', 'expected_text': '2026'},
    {'id': 'agent_browser', 'query': 'agent-browser',
     'site': 'github.com', 'expected_url': 'github.com/vercel-labs/agent-browser', 'expected_text': 'agent-browser', 'required': False},
)


@contextmanager
def isolated_free_run():
    original = search.request_api
    def guard(operation, payload, key, **kwargs):
        name = 'deepseek' if operation == 'fetch' else operation.removesuffix('_fetch')
        if search.get_provider(name).requires_key or key:
            raise AssertionError('Keyed API rejected before transmission.')
        return original(operation, payload, key, **kwargs)
    old_cache = os.environ.get('XDG_CACHE_HOME')
    with tempfile.TemporaryDirectory(prefix='xcoze-live-browser-') as cache:
        os.environ['XDG_CACHE_HOME'] = cache
        search.request_api = guard
        try: yield
        finally:
            search.request_api = original
            if old_cache is None: os.environ.pop('XDG_CACHE_HOME', None)
            else: os.environ['XDG_CACHE_HOME'] = old_cache


def run_case(case, config, *, automatic=False):
    argv = ['search', case['query'], '--strategy', 'free', '--count', '5', '--retries', '0']
    if case.get('site'): argv += ['--site', case['site']]
    if not automatic: argv += ['--provider', 'browser']
    started = time.monotonic()
    output = search.run_search(search.parser().parse_args(argv), config)
    rows = [{k: row.get(k) for k in ('provider', 'title', 'url', 'snippet', 'content_kind')}
            for row in output['results']]
    matches = [row for row in rows if case['expected_url'] in row['url'] and
               case['expected_text'].casefold() in (row['title'] + ' ' + row['snippet']).casefold()]
    browser_requests = [r for r in output['requests'] if r['provider'] == 'browser']
    accepted = bool(matches) and any(r['ok'] and r.get('browser_cleanup_verified') for r in browser_requests)
    result = {'id': case['id'], 'query': case['query'], 'site': case.get('site'),
              'automatic': automatic, 'required': case.get('required', True), 'ok': output['ok'], 'accepted': accepted,
              'elapsed_ms': round((time.monotonic() - started) * 1000, 2),
              'execution_summary': output['execution_summary'], 'requests': output['requests'],
              'errors': output['errors'], 'routing': output.get('routing'), 'sources': rows,
              'matching_sources': len(matches), 'facts_verified': False}
    print(json.dumps({k: result[k] for k in ('id', 'ok', 'accepted', 'elapsed_ms', 'execution_summary')}, ensure_ascii=False), flush=True)
    return result


def execute():
    config = {'schema_version': 2, 'providers': {p: {'api_key': 'synthetic-only'} for p in search.PROVIDERS}}
    report = {'version': search.VERSION, 'tested_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'Real browser/anonymous HTTP only. No response mocks; no user credential file is read. Search summaries are not verified facts.',
              'cases': []}
    with isolated_free_run():
        for case in CASES:
            report['cases'].append(run_case(case, config))
        # A documented source preference, not injected network failure: DDG HTML
        # is really requested, and only a real failure/empty result permits Chrome.
        fallback_config = {**config, 'search_preferences': {'strategy': 'free',
                           'disabled_providers': ['exa-free', 'parallel-free', 'bing']}}
        report['cases'].append(run_case({**CASES[0], 'id': 'real_api_to_browser'}, fallback_config, automatic=True))
    report['keyed_api_attempts'] = sum(c['execution_summary']['keyed_api_attempts'] for c in report['cases'])
    report['ok'] = all(c['accepted'] for c in report['cases'] if c['required']) and report['keyed_api_attempts'] == 0
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', required=True, help='Explicitly enable real browser/network searches')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = execute()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'ok': report['ok'], 'keyed_api_attempts': report['keyed_api_attempts']}, ensure_ascii=False))
    return 0 if report['ok'] else 4


if __name__ == '__main__': raise SystemExit(main())
