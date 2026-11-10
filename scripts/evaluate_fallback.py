#!/usr/bin/env python3
"""Exa-quota injection: simulated recovery by default; optional live keyless API/browser checks."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import time
from unittest.mock import patch
import urllib.parse

import xcoze_search as search
import browser_search

QUOTA = {'jsonrpc': '2.0', 'id': 1, 'result': {'isError': True, 'content': [{'type': 'text', 'text': 'Free MCP quota exceeded'}]}}
GOOD = {'jsonrpc': '2.0', 'id': 1, 'result': {'structuredContent': {'results': [
    {'title': 'Python TaskGroup docs', 'url': 'https://docs.python.org/3/library/asyncio-task.html'}]}}}
BAD_RSS = b'<rss><channel><item><title>Windows help</title><link>https://microsoft.com/help</link></item></channel></rss>'
CHALLENGE = b'<form id="challenge-form">verify you are human</form>'
BROWSER_FIXTURE = {'results': [{'title': 'Python asyncio TaskGroup docs', 'url': 'https://docs.python.org/3/library/asyncio-task.html', 'snippet': 'Synthetic recovery fixture'}],
                   'browser_engine': 'bing', 'browser_navigation_attempts': 1, 'browser_commands': 4, 'browser_http_requests': None,
                   'browser_cleanup_verified': True}
QUERY = 'Python asyncio TaskGroup documentation'


class Reply:
    status = 200
    def __init__(self, raw): self.raw = raw if isinstance(raw, bytes) else json.dumps(raw).encode()
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def read(self, n): return self.raw[:n]


class Transport:
    def __init__(self, responses): self.responses, self.calls = list(responses), []
    def open(self, request, timeout):
        host = urllib.parse.urlsplit(request.full_url).hostname
        if host not in ('mcp.exa.ai', 'www.bing.com', 'html.duckduckgo.com'):
            raise AssertionError('A non-keyless endpoint was attempted.')
        self.calls.append({'host': host, 'authorization_header_present': request.get_header('Authorization') is not None})
        if not self.responses: raise AssertionError('Unexpected additional API attempt.')
        return Reply(self.responses.pop(0))


@contextmanager
def free_api_guard():
    original = search.request_api
    seen = []
    def guarded(operation, payload, key, **kwargs):
        name = 'deepseek' if operation == 'fetch' else operation.removesuffix('_fetch')
        if search.get_provider(name).requires_key:
            raise AssertionError('Paid API call rejected by fault-test guard before transmission.')
        if key: raise AssertionError('A key was supplied to a keyless request.')
        seen.append(name)
        return original(operation, payload, key, **kwargs)
    with patch.object(search, 'request_api', side_effect=guarded): yield seen


def run_case(label, responses, config, *, live_browser=False, cache=None):
    args = search.parser().parse_args(['search', QUERY, '--strategy', 'free', '--count', '3', '--timeout', '8', '--max-seconds', '35'])
    started = time.perf_counter(); transport = Transport(responses)
    with patch.object(search.urllib.request, 'build_opener', return_value=transport), free_api_guard() as seen:
        if live_browser:
            output = search.run_search(args, config)
        else:
            with patch('search_routing.browser_available', return_value=True), patch.object(search, 'run_browser_search', return_value=BROWSER_FIXTURE) as local:
                output = search.run_search(args, config)
    return {'case': label, 'mode': 'free', 'browser_execution': 'live' if live_browser else 'simulated',
            'ok': output['ok'], 'elapsed_ms': round((time.perf_counter()-started)*1000, 2),
            'api_calls': seen, 'simulated_transport': transport.calls, 'routing': output.get('routing'),
            'execution_summary': output.get('execution_summary'), 'requests': [{k: r.get(k) for k in (
                'provider', 'ok', 'attempts', 'elapsed_ms', 'execution', 'browser_navigation_attempts', 'browser_commands', 'browser_cleanup_verified')} for r in output.get('requests', [])],
            'errors': output.get('errors'), 'sources': [{k: r.get(k) for k in ('provider', 'title', 'url', 'content_kind')} for r in output.get('results', [])]}


def execute(*, live_api=False, live_browser=False):
    # Keep the older simulated Exa → RSS/HTML → browser sequence reproducible.
    config = {'schema_version': 2, 'providers': {p: {'api_key': 'synthetic-only'} for p in search.PROVIDERS},
              'search_preferences': {'disabled_providers': ['parallel-free']}}
    report = {'version': search.VERSION, 'tested_at': datetime.now(timezone.utc).isoformat(),
              'live_api_requested': live_api, 'live_browser_requested': live_browser,
              'scope': 'Fault injection and routing safety; synthetic results are not live retrieval evidence. Browser subrequest counts are unknown.',
              'cases': [], 'keys': 'Synthetic only; user credential file is never read.'}
    overrides = {env: 'synthetic-only' for values in search.ENV_KEYS.values() for env in values}
    with tempfile.TemporaryDirectory(prefix='xcoze-fault-') as root, patch.dict(os.environ, {**overrides, 'XDG_CACHE_HOME': root}), \
            patch.object(search, 'read_config', side_effect=AssertionError('User credentials must not be read.')):
        report['cases'].append(run_case('healthy_api_no_browser', [GOOD], config))
        # Drop only this test's short pacing state; no real quota state or user cache is changed.
        path = Path(root)/'xcoze-search/public-access/exa-free.json'
        if path.exists(): path.unlink()
        report['cases'].append(run_case('quota_exhausted_browser_recovers', [QUOTA, BAD_RSS], config))
        report['cases'].append(run_case('paused_exa_skipped_next_query', [BAD_RSS, CHALLENGE], config))
        if live_browser:
            report['cases'].append(run_case('live_browser_after_injected_quota', [BAD_RSS, CHALLENGE], config, live_browser=True))
        if live_api:
            with tempfile.TemporaryDirectory(prefix='xcoze-api-probe-') as fresh, patch.dict(os.environ, {'XDG_CACHE_HOME': fresh}), free_api_guard() as seen:
                args = search.parser().parse_args(['search', QUERY, '--strategy', 'free', '--browser', 'off', '--max-sources', '1', '--count', '3', '--timeout', '8', '--retries', '0'])
                started = time.perf_counter(); output = search.run_search(args, config)
                report['live_api'] = {'ok': output['ok'], 'elapsed_ms': round((time.perf_counter()-started)*1000, 2),
                    'api_calls': seen, 'execution_summary': output.get('execution_summary'), 'errors': output.get('errors'),
                    'sources': [{k: r.get(k) for k in ('provider', 'title', 'url')} for r in output.get('results', [])]}
    report['free_mode_safety_passed'] = (all(c['execution_summary']['keyed_api_attempts'] == 0 for c in report['cases'])
                                       and report.get('live_api', {}).get('execution_summary', {}).get('keyed_api_attempts', 0) == 0)
    report['healthy_api_browser_starts'] = report['cases'][0]['execution_summary']['browser_navigation_attempts']
    report['simulated_recovery_passed'] = report['cases'][1]['ok'] and report['cases'][2]['ok']
    report['live_browser_usable'] = next((c['ok'] and any(s['provider']=='browser' for s in c['sources']) for c in report['cases'] if c['browser_execution']=='live'), None)
    report['ok'] = report['free_mode_safety_passed'] and report['healthy_api_browser_starts'] == 0 and report['simulated_recovery_passed']
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--live-api', action='store_true', help='One real anonymous API query, never keyed services')
    p.add_argument('--live-browser', action='store_true', help='After simulated API failures, launch one isolated local browser search')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    report = execute(live_api=args.live_api, live_browser=args.live_browser)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('ok','free_mode_safety_passed','healthy_api_browser_starts','simulated_recovery_passed','live_browser_usable')}, ensure_ascii=False))
    return 0 if report['ok'] else 4


if __name__ == '__main__': raise SystemExit(main())
