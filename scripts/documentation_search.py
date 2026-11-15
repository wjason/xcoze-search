"""Search fixed official documentation indexes without a search-service key."""
import json
import re
import urllib.parse
import urllib.request

from search_common import SearchError, public_url
from search_providers import Provider, option, result
from search_quality import STOP, focus_terms

DOC_SITES = {
    'docs.python.org': 'https://docs.python.org/3/',
    'pandas.pydata.org': 'https://pandas.pydata.org/docs/',
    'docs.sqlalchemy.org': 'https://docs.sqlalchemy.org/en/20/',
}


def index_variants(term, vocabulary):
    """Look up a few English suffix variants used by static indexes; no semantic expansion."""
    if term in vocabulary: return [term]
    variants = {term[:-1] if term.endswith('e') else term}
    for suffix in ('ation', 'ion', 'ing', 'ed', 'es', 's', 'al', 'er', 'y'):
        if term.endswith(suffix) and len(term) - len(suffix) >= 3:
            stem = term[:-len(suffix)]
            variants.update((stem, stem + 'e', stem + 'i'))
            if len(stem) > 3 and stem[-1] == stem[-2]: variants.add(stem[:-1])
    return sorted(s for s in variants if s in vocabulary)


class OfficialDocs(Provider):
    name, label = 'docs', 'Official Sphinx documentation indexes'
    endpoint = 'https://docs.python.org/3/searchindex.js'
    requires_key = False
    auth_header = None
    method = 'GET'
    options = frozenset(('site', 'language'))
    max_count = 20
    sites = tuple(DOC_SITES)

    def capabilities(self):
        return {**super().capabilities(), 'access': 'keyless', 'sites': DOC_SITES,
                'search_scope': 'fixed_official_documentation_indexes',
                'query_processing': 'local_keyword_and_symbol_matching',
                'note': 'Downloads the official search index; no page bodies or search-service key.'}

    def build_search(self, args):
        site = option(args, 'site')
        if option(args, 'language') not in (None, 'en', 'en-US', 'en-us'):
            raise SearchError('unsupported_option', 'This documentation index only supports English.')
        if site not in DOC_SITES:
            raise SearchError('unsupported_option', 'Select a supported official documentation --site; inspect capabilities.')
        if re.search(r'\b[123]\.\d+(?:\.\d+)?\b', args.query):
            raise SearchError('unsupported_option', 'The fixed documentation index cannot guarantee a requested version; use another search source.')
        return {'site': site}

    def build_request(self, payload, key, version, *, fetch=False):
        if fetch or payload.get('site') not in DOC_SITES:
            raise SearchError('invalid_input', 'Unsupported official documentation index.')
        return urllib.request.Request(DOC_SITES[payload['site']] + 'searchindex.js', headers={
            'User-Agent': 'xcoze-search/' + version, 'Accept': 'application/javascript,text/javascript'})

    def decode_response(self, raw):
        try:
            text = raw.decode('utf-8').strip().removesuffix(';')
            if not text.startswith('Search.setIndex(') or not text.endswith(')'):
                raise ValueError
            data = json.loads(text[len('Search.setIndex('):-1])
            if (not isinstance(data, dict) or not isinstance(data.get('docnames'), list)
                    or not isinstance(data.get('titles'), list)
                    or len(data['docnames']) != len(data['titles'])
                    or any(not isinstance(data.get(k), dict) for k in ('terms', 'titleterms', 'objects'))):
                raise ValueError
            return data
        except (ValueError, UnicodeError):
            raise SearchError('invalid_response', 'Unrecognized official documentation search index.') from None

    def normalize_search(self, raw, args):
        from html import unescape
        base = DOC_SITES[args.site]
        query = re.sub(r'-?site:\S+', ' ', args.query, flags=re.I)
        terms = {t.casefold() for t in re.findall(r'[A-Za-z][A-Za-z0-9_]*', query)
                 if t.casefold() not in STOP and t.casefold() not in ('python', 'pandas', 'sqlalchemy')}
        focus = {part for term in focus_terms(query) for part in term.split('.') if part in terms}
        scores, matched, best_objects, focus_docs = {}, {}, {}, set()
        count = len(raw['docnames'])

        def valid_id(i):
            return type(i) is int and 0 <= i < count

        for field, weight in (('terms', 1), ('titleterms', 3)):
            for term in terms:
                ids = []
                for variant in index_variants(term, raw[field]):
                    posting = raw[field][variant]
                    posting = [posting] if type(posting) is int else posting
                    if not isinstance(posting, list):
                        raise SearchError('invalid_response', 'Invalid documentation index postings.')
                    ids.extend(posting)
                ids = set(ids) if all(type(i) is int for i in ids) else ids
                for i in ids:
                    if not valid_id(i):
                        raise SearchError('invalid_response', 'Invalid documentation index document number.')
                    scores[i] = scores.get(i, 0) + weight
                    matched.setdefault(i, set()).add(term)
                    if term in focus: focus_docs.add(i)
        for prefix, entries in raw['objects'].items():
            if isinstance(entries, dict):  # Older Sphinx index format.
                entries = [[*value, name] for name, value in entries.items() if isinstance(value, list)]
            if not isinstance(prefix, str) or not isinstance(entries, list):
                raise SearchError('invalid_response', 'Invalid documentation objects.')
            for entry in entries:
                if (not isinstance(entry, list) or len(entry) != 5 or not valid_id(entry[0])
                        or not isinstance(entry[3], str) or not isinstance(entry[4], str)):
                    raise SearchError('invalid_response', 'Invalid documentation object entry.')
                i, _, _, anchor, name = entry
                full = (prefix + '.' if prefix else '') + name
                components = set(full.casefold().split('.'))
                hits = terms & components
                if not hits: continue
                focus_hit = any(term in full.casefold() for term in focus)
                boost = 8 * len(hits) + 20 * (name.casefold() in terms) + 40 * focus_hit
                matched.setdefault(i, set()).update(hits)
                if focus_hit: focus_docs.add(i)
                if boost > best_objects.get(i, (0, '', ''))[0]:
                    best_objects[i] = (boost, full, full if anchor == '' else '' if anchor == '-' else anchor)
                scores[i] = max(scores.get(i, 0), boost)
        ordered = sorted((i for i in scores if not focus or i in focus_docs), key=lambda i: (-scores[i], i))
        rows = []
        for i in ordered[:args.count]:
            doc, title = raw['docnames'][i], raw['titles'][i]
            if (not isinstance(doc, str) or not re.fullmatch(r'[A-Za-z0-9_./-]+', doc)
                    or doc.startswith('/') or '..' in doc.split('/') or not isinstance(title, str)):
                raise SearchError('invalid_response', 'Invalid documentation destination.')
            obj = best_objects.get(i)
            anchor = urllib.parse.quote(obj[2], safe='._-') if obj else ''
            url = base + doc + '.html' + ('#' + anchor if anchor else '')
            item = {'title': unescape(re.sub('<[^>]*>', '', title)) + (' — ' + obj[1] if obj else ''),
                    'url': url, 'snippet': 'Official search index matches: ' + ', '.join(sorted(matched[i])),
                    'index_url': base + 'searchindex.js', 'page_body_read': False}
            row = result(self.name, len(rows) + 1, item)
            row['content_kind'] = 'documentation_index'
            rows.append(row)
        return rows, {**self.metadata({}, rows, args.count), 'index_documents': count,
                      'query_sent_to_source': False, 'page_body_read': False}


class MDN(Provider):
    name, label = 'mdn', 'MDN Web Docs public search'
    endpoint = 'https://developer.mozilla.org/api/v1/search'
    requires_key = False
    auth_header = None
    method = 'GET'
    options = frozenset(('site', 'language'))
    max_count = 10

    def capabilities(self):
        return {**super().capabilities(), 'access': 'keyless', 'search_scope': 'mdn_english_documentation'}

    def build_search(self, args):
        if option(args, 'language') not in (None, 'en', 'en-US', 'en-us'):
            raise SearchError('unsupported_option', 'This MDN adapter only supports English.')
        if option(args, 'site') not in (None, 'developer.mozilla.org'):
            raise SearchError('unsupported_option', 'MDN only searches developer.mozilla.org.')
        return {'q': args.query, 'locale': 'en-US'}

    def build_request(self, payload, key, version, *, fetch=False):
        if fetch:
            raise SearchError('unsupported_operation', 'MDN adapter only searches documentation.')
        return urllib.request.Request(self.endpoint + '?' + urllib.parse.urlencode(payload), headers={
            'User-Agent': 'xcoze-search/' + version, 'Accept': 'application/json'})

    def normalize(self, raw, count):
        if not isinstance(raw.get('documents'), list):
            raise SearchError('invalid_response', 'Missing MDN search documents.')
        rows = []
        for item in raw['documents'][:count]:
            path = item.get('mdn_url') if isinstance(item, dict) else None
            if not isinstance(path, str) or not path.startswith('/en-US/docs/') or not public_url('https://developer.mozilla.org' + path):
                raise SearchError('invalid_response', 'Invalid MDN document link.')
            rows.append(result(self.name, len(rows) + 1, {**item, 'url': 'https://developer.mozilla.org' + path}, snippet='summary'))
        return rows, self.metadata({'metadata': raw.get('metadata')}, rows, count)
