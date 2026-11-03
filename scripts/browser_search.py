"""Lazy, isolated local search through an existing agent-browser executable."""
import base64
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time
import urllib.parse
import uuid

from search_common import SearchError, public_url
from search_providers import Provider, result, option
from public_access import request_slot

ENGINES = {'google': 'https://www.google.com/search', 'bing': 'https://www.bing.com/search'}
ENV_ALLOW = frozenset(('PATH', 'HOME', 'USERPROFILE', 'LOCALAPPDATA', 'APPDATA', 'SystemRoot', 'SYSTEMROOT',
                       'WINDIR', 'TMP', 'TEMP', 'TMPDIR', 'LANG', 'LC_ALL', 'DISPLAY', 'WAYLAND_DISPLAY', 'XDG_RUNTIME_DIR'))
MAX_OUTPUT = 128 * 1024
# Fixed DOM inspection only: no script/command is taken from a search page.
EXTRACT = r'''(() => {
 const challenge = !!document.querySelector('iframe[src*="recaptcha"],form[action*="/sorry/"],#captcha,#b_captcha');
 const text = document.body ? document.body.innerText.slice(0, 900) : '';
 const nodes = location.hostname.endsWith('bing.com') ? Array.from(document.querySelectorAll('#b_results li.b_algo h2 a')) : Array.from(document.querySelectorAll('#search h3')).map(h => h.closest('a')).filter(Boolean);
 return {url: location.href, title: document.title, challenge, text,
   results: nodes.slice(0, 10).filter(a => !a.closest('#tads,#tadsb,.b_ad,[data-text-ad]')).map(a => {
     const card = a.closest('li.b_algo') || a.closest('div.MjjYud') || a.parentElement;
     const snippet = card && card.querySelector('.b_caption p,.VwiC3b,.IsZvec,[data-sncf]');
     return {title: a.innerText.slice(0, 500), url: a.href, snippet: snippet ? snippet.innerText.slice(0, 700) : ''};
   })};
})()'''
READY = "document.querySelector('#search h3,#b_results li.b_algo h2 a,iframe[src*=recaptcha],#captcha,#b_captcha') !== null || /unusual traffic|captcha|人机验证|安全验证/i.test(document.title)"


def available():
    return bool(shutil.which('agent-browser'))


def browser_environment():
    env = {k: v for k, v in os.environ.items() if k in ENV_ALLOW}
    env.update(AGENT_BROWSER_IDLE_TIMEOUT_MS='20000', AGENT_BROWSER_DEFAULT_TIMEOUT='6000')
    return env


def unwrap_url(url):
    try: parsed = urllib.parse.urlsplit(url)
    except ValueError: return ''
    query = urllib.parse.parse_qs(parsed.query)
    if parsed.hostname in ('www.google.com', 'google.com') and parsed.path == '/url':
        url = (query.get('q') or query.get('url') or [''])[0]
    elif parsed.hostname in ('www.bing.com', 'bing.com') and parsed.path.startswith('/ck/a'):
        encoded = query.get('u', [''])[0]
        if encoded.startswith('a1'):
            try: url = base64.urlsafe_b64decode(encoded[2:] + '=' * (-len(encoded[2:]) % 4)).decode('utf-8')
            except (ValueError, UnicodeError): return ''
    return url if public_url(url) else ''


def parse_page(data, engine):
    if not isinstance(data, dict) or not isinstance(data.get('results'), list):
        raise SearchError('invalid_response', 'Unrecognized browser search DOM.', category='response')
    host = urllib.parse.urlsplit(str(data.get('url') or '')).hostname
    if host not in (('www.google.com', 'google.com') if engine == 'google' else ('www.bing.com', 'bing.com')):
        raise SearchError('browser_navigation_blocked', 'Search navigation left the selected engine; no results accepted.', category='access')
    title, text = str(data.get('title') or ''), str(data.get('text') or '')
    import re
    challenge_title = not data['results'] and re.fullmatch(r'(?:captcha|安全验证|人机验证)(?:\s*[-|:].*)?', title, re.I)
    if data.get('challenge') or challenge_title or re.search(r'our systems have detected unusual traffic|verify you are human', text, re.I):
        raise SearchError('access_challenge', 'Search engine requires verification; browser search stopped without solving it.', category='access')
    rows = []
    for item in data['results']:
        if not isinstance(item, dict) or not isinstance(item.get('title'), str):
            raise SearchError('invalid_response', 'Invalid browser search row.', category='response')
        url = unwrap_url(str(item.get('url') or ''))
        if not url or urllib.parse.urlsplit(url).hostname in ('www.google.com', 'google.com', 'www.bing.com', 'bing.com'): continue
        title = ' '.join(item['title'].split())
        if title: rows.append({'title': title, 'url': url, 'snippet': str(item.get('snippet') or '')[:700]})
    if not rows:
        raise SearchError('browser_no_results', 'No verified result rows were extracted; an empty shell is not proof of no matches.', category='response')
    return rows


def command(argv, *, env, deadline, input_text=None):
    remaining = deadline - time.monotonic()
    if remaining <= 0: raise SearchError('browser_timeout', 'Local browser search exceeded its time budget.', category='network')
    with tempfile.TemporaryFile() as output:
        cwd = str(Path(argv[argv.index('--config') + 1]).parent) if '--config' in argv else None
        process = subprocess.Popen(argv, stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
                                   stdout=output, stderr=subprocess.DEVNULL, env=env, shell=False,
                                   start_new_session=os.name != 'nt', cwd=cwd)
        try:
            process.communicate(input=input_text.encode() if input_text is not None else None, timeout=remaining)
        except subprocess.TimeoutExpired:
            if os.name != 'nt':
                try: os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError: pass
            else: process.kill()
            process.wait(timeout=2)
            raise SearchError('browser_timeout', 'Local browser search exceeded its time budget.', category='network') from None
        output.seek(0); raw = output.read(MAX_OUTPUT + 1)
    if len(raw) > MAX_OUTPUT: raise SearchError('response_too_large', 'Browser output exceeded the bounded result size.')
    try: data = json.loads(raw)
    except (ValueError, UnicodeError): raise SearchError('browser_failed', 'Local browser command returned no valid JSON; inspect its installation.', category='configuration') from None
    if process.returncode != 0 or not isinstance(data, dict) or data.get('success') is not True:
        raise SearchError('browser_failed', 'Local browser command failed; no upstream error text retained.', category='network')
    return data.get('data')


def search(payload, *, timeout=15, engine='bing'):
    with request_slot('browser', 'local-browser-search'):
        return _search(payload, timeout=timeout, engine=engine)


def _search(payload, *, timeout=15, engine='bing'):
    exe = shutil.which('agent-browser')
    if not exe: raise SearchError('browser_unavailable', 'Optional agent-browser is not installed; no dependency was installed automatically.', category='configuration')
    if engine not in ENGINES: raise SearchError('invalid_input', 'Choose google or bing for local browser search.')
    start = time.monotonic(); deadline = start + timeout
    env = browser_environment(); navigations = 0; commands = 0; cleanup_ok = False; output = None; failure = None
    with tempfile.TemporaryDirectory(prefix='xcoze-browser-') as temporary:
        config = Path(temporary) / 'agent-browser.json'; config.write_text('{}\n', encoding='utf-8')
        base = [exe, '--config', str(config), '--session', 'xcoze-search-' + uuid.uuid4().hex,
                '--json', '--engine', 'chrome', '--headed', 'false']
        try:
            url = ENGINES[engine] + '?' + urllib.parse.urlencode({'q': payload['query']})
            navigations = 1; commands += 1
            opened = command(base + ['open', url], env=env, deadline=deadline)
            # Detect an obvious challenge before waiting for results.
            if isinstance(opened, dict) and (str(opened.get('title', '')).lower().startswith('captcha') or
                                            '/sorry/' in str(opened.get('url', ''))):
                raise SearchError('access_challenge', 'Search engine requires verification; no challenge was solved.', category='access')
            commands += 1
            command(base + ['wait', '--fn', READY], env=env, deadline=deadline)
            commands += 1
            data = command(base + ['eval', '--stdin'], env=env, deadline=deadline, input_text=EXTRACT)
            page = data.get('result') if isinstance(data, dict) else None
            if isinstance(page, str):
                try: page = json.loads(page)
                except ValueError: page = None
            rows = parse_page(page, engine)
            output = {'results': rows[:payload['count']], 'browser_engine': engine,
                    'browser_navigation_attempts': navigations, 'browser_commands': commands + 1,
                    'browser_http_requests': None, 'browser_time_budget_seconds': timeout}
            return output
        except SearchError as error:
            failure = error
            error.browser_navigation_attempts = navigations
            error.browser_commands = commands + 1
            raise
        except OSError:
            error = SearchError('browser_unavailable', 'Cannot execute the optional local browser tool.', category='configuration')
            failure = error
            error.browser_navigation_attempts = navigations; error.browser_commands = commands + 1
            raise error from None
        finally:
            try:
                command(base + ['close'], env=env, deadline=time.monotonic() + 6)
                cleanup_ok = True
            except (SearchError, OSError): pass
            if output is not None: output['browser_cleanup_verified'] = cleanup_ok
            if failure is not None: failure.browser_cleanup_verified = cleanup_ok
            # The private session also has a 20-second idle shutdown if close failed.


class Browser(Provider):
    name, label = 'browser', 'Local browser search (optional)'
    requires_key, auth_header, method = False, None, 'LOCAL_BROWSER'
    options = frozenset(('site',))
    max_count = 10

    def build_search(self, args):
        query = args.query + (' site:' + args.site if option(args, 'site') else '')
        self.validate_query(query)
        return {'query': query, 'count': args.count}

    def build_request(self, *a, **kw):
        raise SearchError('unsupported_operation', 'Local browser search is not an HTTP API adapter.')

    def normalize(self, raw, count):
        rows = [result(self.name, i, item) for i, item in enumerate(raw['results'], 1)]
        meta = self.metadata(raw, rows, count)
        return rows[:count], {**meta, 'execution': 'local_browser', 'browser_engine': raw['browser_engine'],
                              'browser_navigation_attempts': raw['browser_navigation_attempts'],
                              'browser_commands': raw['browser_commands'], 'browser_http_requests': None,
                              'browser_cleanup_verified': raw.get('browser_cleanup_verified', False),
                              'user_api_key_used': False}

    def capabilities(self):
        return {**super().capabilities(), 'access': 'keyless', 'availability': 'optional_local_tool',
                'search_scope': 'public_search_engine_results', 'execution': 'local_browser',
                'starts_only_when_called': True, 'required_executable': 'agent-browser'}
