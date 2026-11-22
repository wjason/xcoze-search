"""Read bounded public originals on a fixed set of official sites; stdlib only."""
from datetime import datetime
from html.parser import HTMLParser
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
import urllib.parse
import urllib.request

from search_common import SearchError, public_url
from search_providers import Provider, option

HOSTS = frozenset(('docs.python.org', 'pandas.pydata.org', 'docs.sqlalchemy.org',
    'developer.mozilla.org', 'kubernetes.io', 'doc.rust-lang.org', 'pkg.go.dev',
    'www.nea.gov.cn', 'nea.gov.cn', 'zfxxgk.nea.gov.cn', 'www.stats.gov.cn', 'stats.gov.cn',
    'www.ggzy.gov.cn', 'ggzy.gov.cn', 'www.bidding.csg.cn', 'bidding.csg.cn',
    'static.cninfo.com.cn'))
VOID = frozenset(('meta', 'link', 'img', 'br', 'hr', 'input', 'source', 'wbr', 'area', 'base', 'embed', 'param', 'track', 'col'))


def checked_url(url):
    if not public_url(url): raise SearchError('invalid_input', 'A public original URL is required.')
    p = urllib.parse.urlsplit(url)
    if p.hostname not in HOSTS or p.port not in (None, 80, 443):
        raise SearchError('unsupported_operation', 'This URL is outside the fixed native-reader sites.')
    if p.query and re.search(r'(?:token|key|auth|signature|password)=', p.query, re.I):
        raise SearchError('invalid_input', 'Do not submit credential-bearing URLs.')
    # Preserve the published path; transport uses HTTPS, never an arbitrary host.
    return urllib.parse.urlunsplit(('https', p.hostname, p.path or '/', p.query, ''))


class ArticleParser(HTMLParser):
    def __init__(self, focus=None):
        super().__init__(); self.stack = []; self.parts = []; self.selected = []; self.title = []
        self.meta = {}; self.links = []; self.anchor = None; self.groups = []
        self.focus=focus;self.focused=False;self.focus_parts=[]
        self.ids=[]
        self.in_focus=False;self.focus_depth=0;self.focus_tag=None

    def handle_starttag(self, tag, pairs):
        a = dict(pairs)
        if a.get('id'):self.ids.append(a['id'])
        if self.in_focus and self.focus.startswith('method.') and a.get('id','').startswith('method.') and a['id']!=self.focus:self.in_focus=False
        if self.in_focus and ((self.focus_tag=='dt' and tag=='dt' and len(self.stack)+1<=self.focus_depth) or
            (self.focus_tag in ('h1','h2','h3','h4','h5','h6') and tag in ('h1','h2','h3','h4','h5','h6') and tag<=self.focus_tag)):
            self.in_focus=False
        if self.focus and a.get('id')==self.focus:
            self.focused=True;self.in_focus=True;self.focus_depth=len(self.stack)+1;self.focus_tag=tag
        if tag == 'meta':
            self.meta[(a.get('name') or a.get('property') or '').lower()] = a.get('content', '')
        hidden = bool(self.stack and self.stack[-1][1]) or tag in ('script','style','nav','footer','header','noscript','svg','form') or 'hidden' in a or a.get('aria-hidden') == 'true'
        marker = (a.get('id','') + ' ' + a.get('class','')).lower()
        chosen = not hidden and (tag in ('main','article') or bool(re.search(r'\b(?:trs_editor|ucap-content|article-content|articlebody|contentbody|detail-content|markdown-body|document|wyzw|zoom|content-main)\b', marker)))
        if tag not in VOID: self.stack.append((tag, hidden, chosen))
        if chosen: self.groups.append(len(self.selected))
        if tag in ('p','div','li','br','h1','h2','h3','pre','tr','section'):
            self.parts.append('\n'); self.selected.append('\n')
            if self.in_focus: self.focus_parts.append('\n')
        if tag == 'a' and not hidden: self.anchor = [a.get('href',''), []]

    def handle_endtag(self, tag):
        if self.in_focus and not self.focus.startswith('method.') and tag==self.focus_tag and self.focus_tag in ('section','article','div') and len(self.stack)==self.focus_depth:self.in_focus=False
        if tag == 'a' and self.anchor is not None:
            self.links.append((self.anchor[0], ''.join(self.anchor[1]).strip())); self.anchor = None
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag: del self.stack[i:]; break
        if tag in ('p','div','li','h1','h2','h3','pre','tr','section'): self.parts.append('\n'); self.selected.append('\n')
        if tag in ('p','div','li','h1','h2','h3','pre','tr','section') and self.in_focus: self.focus_parts.append('\n')

    def handle_data(self, text):
        if self.stack and self.stack[-1][1]: return
        if any(t[0] == 'title' for t in self.stack): self.title.append(text); return
        if any(t[0] == 'head' for t in self.stack): return
        self.parts.append(text)
        if self.in_focus: self.focus_parts.append(text)
        if any(t[2] for t in self.stack): self.selected.append(text)
        if self.anchor is not None: self.anchor[1].append(text)


def cleaned(text):
    return '\n'.join(' '.join(line.split()) for line in text.splitlines() if line.strip())


class NativeReader(Provider):
    name, label = 'native-reader', 'Official-site native original reader'
    endpoint = fetch_endpoint = 'https://docs.python.org/'
    supports_search, requires_key, auth_header = False, False, None
    method = 'GET'

    def access_scope(self,payload):
        return 'native-reader-'+urllib.parse.urlsplit(checked_url(payload['url'])).hostname

    def capabilities(self):
        return {**super().capabilities(), 'access': 'keyless', 'search_scope': 'reading_only',
                'supported_hosts': sorted(HOSTS), 'pdf_text_extractor_available': bool(shutil.which('pdftotext')),
                'pdf_pages_requested': 10, 'documentation_url': 'https://github.com/wjason/xcoze-search'}

    def fetch_payload(self, args):
        if option(args, 'highlights') or option(args, 'summary'):
            raise SearchError('unsupported_option', 'Native reading does not generate highlights or summaries.')
        return {'url': checked_url(args.url)}

    def build_request(self, payload, key, version, *, fetch=False):
        if not fetch: raise SearchError('unsupported_operation', 'This adapter only reads originals.')
        return urllib.request.Request(checked_url(payload.get('url')), headers={
            'User-Agent': 'xcoze-search/' + version, 'Accept': 'text/html,application/pdf;q=0.9'})

    def decode_response(self, raw):
        if raw.startswith(b'%PDF'):
            binary = shutil.which('pdftotext')
            if not binary: raise SearchError('reader_dependency_missing', 'PDF text needs an existing pdftotext or a permitted host reader; no software is installed.')
            with tempfile.TemporaryDirectory(prefix='xcoze-pdf-') as folder:
                path = Path(folder) / 'original.pdf'; path.write_bytes(raw)
                try:
                    job = subprocess.run([binary, '-f','1','-l','10','-enc','UTF-8',str(path),'-'],
                        capture_output=True, timeout=10, check=False, env={k:v for k,v in __import__('os').environ.items() if k in ('PATH','SYSTEMROOT','WINDIR','LANG','TMPDIR','TEMP','TMP')})
                except (OSError, subprocess.TimeoutExpired): raise SearchError('extraction_failed', 'Bounded PDF extraction failed.') from None
                if job.returncode or len(job.stdout) > 2_000_000: raise SearchError('extraction_failed', 'PDF text could not be extracted within limits.')
                text = cleaned(job.stdout.decode('utf-8','replace'))
            if len(text) < 100: raise SearchError('extraction_failed', 'PDF has insufficient readable text; it may require OCR.')
            return {'pdf_text': text}
        try: html = raw.decode('utf-8-sig')
        except UnicodeError: raise SearchError('invalid_response', 'Original is not supported UTF-8 HTML.') from None
        if '<html' not in html.lower(): raise SearchError('invalid_response', 'Original is not recognizable HTML.')
        return {'html': html}

    def normalize_fetch(self, raw, url, focus_terms=None, question=''):
        source = checked_url(url)
        if 'pdf_text' in raw:
            return {'title': '', 'content': raw['pdf_text'], 'summary':'', 'highlights':[],
                'source_url': source, 'content_kind':'pdf_text', 'page_body_read':True,
                'pdf_pages_requested':[1,10], 'completeness_verified':False, 'truncated':True,
                'publication_date':None, 'publication_date_basis':None}
        html = raw['html']; fragment=urllib.parse.unquote(urllib.parse.urlsplit(url).fragment)
        parser = ArticleParser(fragment); parser.feed(html)
        anchor_basis='requested_url' if fragment else None
        if not fragment and re.search(r'默认.*拒绝|default.*deny',question,re.I):
            hints=['default','deny']+(['ingress'] if re.search('入站|入向|ingress',question,re.I) else ['egress'] if re.search('出站|出向|egress',question,re.I) else [])
            matches=[i for i in parser.ids if all(h in i.casefold() for h in hints)]
            if matches:
                fragment=matches[0];parser=ArticleParser(fragment);parser.feed(html)
                anchor_basis='published_heading_matched_question'
        if not fragment and focus_terms:
            matches=[i for i in parser.ids for term in focus_terms
                     if i.casefold()=='method.'+term or
                     urllib.parse.urlsplit(source).hostname=='pkg.go.dev' and len(term)>3 and i.casefold()==term.rsplit('.',1)[-1]]
            if matches:
                fragment=matches[0];parser=ArticleParser(fragment);parser.feed(html)
                anchor_basis='published_id_matched_focus_term'
        title = ' '.join(''.join(parser.title).split()); visible = cleaned(''.join(parser.parts))
        if re.search('访问过于频繁|访问被拒绝|人机验证|请输入验证码|Access Denied|Just a moment|verify you are human', title + '\n' + visible[:700], re.I):
            raise SearchError('access_challenge', 'Original requires verification or denied access; no verification is attempted.', category='access')
        if urllib.parse.urlsplit(source).hostname in ('ggzy.gov.cn','www.ggzy.gov.cn'):
            link = re.search(r"\bfirstLastUrl\s*=\s*['\"]([^'\"]+)['\"]", html)
            if link:
                target = checked_url(urllib.parse.urljoin(source, link[1]))
                if urllib.parse.urlsplit(target).hostname != urllib.parse.urlsplit(source).hostname or not re.fullmatch(r'/information/deal/html/b/[\w/-]+\.html',urllib.parse.urlsplit(target).path):
                    raise SearchError('invalid_response','Notice directory has an unsupported body link.')
                return {'title':title, 'content':'', 'summary':'', 'highlights':[], 'content_kind':'notice_directory',
                        'page_body_read':False, 'linked_body_url':target, 'source_url':source, 'completeness_verified':False}
        selected = cleaned(''.join(parser.selected))
        body = selected if len(selected) >= 100 else visible
        if parser.focused and len(cleaned(''.join(parser.focus_parts)))>=100:
            body=cleaned(''.join(parser.focus_parts))
        if len(body) < 100 or re.search('暂无数据|暂无内容',body) and len(body) < 250:
            raise SearchError('extraction_failed','Original contains insufficient readable body text.')
        stamp, basis = None, None
        for name in ('article:published_time','publishdate','pubdate','date','dc.date','dc.date.issued'):
            value = parser.meta.get(name)
            if value:
                try: stamp = datetime.fromisoformat(value.replace('Z','+00:00')).date().isoformat(); basis = 'page_meta:' + name; break
                except ValueError: pass
        if stamp is None:
            match = re.search(r'(?:发布时间|发布日期)\s*[：:]?\s*(20\d{2}-\d{2}-\d{2})',visible)
            if match:
                try: stamp = datetime.fromisoformat(match[1]).date().isoformat(); basis = 'labeled_page_text'
                except ValueError: pass
        links = [{'url':urllib.parse.urljoin(source,href),'title':text} for href,text in parser.links
                 if public_url(urllib.parse.urljoin(source,href))]
        attachments=[link for link in links if re.search(r'\.(?:pdf|docx?|xlsx?)(?:$|\?)',link['url'],re.I)][:10]
        return {'title':title, 'content':body, 'summary':'', 'highlights':[], 'source_url':source,
                'content_kind':'official_original', 'page_body_read':True, 'completeness_verified':False,
                'extraction_scope':'requested_anchor_on_page' if parser.focused else 'article_container' if len(selected)>=100 else 'visible_page',
                'requested_anchor':fragment or None, 'anchor_found':parser.focused,
                'anchor_basis':anchor_basis,
                'publication_date':stamp, 'publication_date_basis':basis, 'outbound_links':(attachments+links)[:40],
                'attachments':attachments,'attachments_read':False,
                **({'source_url':source+'#'+urllib.parse.quote(fragment,safe='.:_-')} if parser.focused else {})}

    def metadata(self, raw, rows, count):
        return {'access':'keyless', 'user_api_key_used':False, 'cost':None}
