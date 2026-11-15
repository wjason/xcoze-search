"""Local exports of search results. Standard library only, no network or credentials."""
import csv
import html
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
from urllib.parse import urlsplit

from search_common import SearchError, public_url

MAX_SNAPSHOT = 32 * 1024 * 1024


def validate_result(data):
    if (not isinstance(data, dict) or data.get('operation') != 'search'
            or not isinstance(data.get('query'), str)
            or not isinstance(data.get('results'), list) or len(data['results']) > 1000):
        raise SearchError('invalid_result_file', 'Expected a saved xcoze search result.')
    for row in data['results']:
        if (not isinstance(row, dict) or not isinstance(row.get('title'), str)
                or not isinstance(row.get('url'), str) or not public_url(row['url'])
                or not isinstance(row.get('provider'), str)):
            raise SearchError('invalid_result_file', 'Invalid saved search result row.')
        for name in ('summary', 'snippet', 'content', 'published_at', 'content_kind'):
            if row.get(name) is not None and not isinstance(row[name], str):
                raise SearchError('invalid_result_file', 'Invalid saved result text field.')
        if row.get('highlights') is not None and (not isinstance(row['highlights'], list)
                or any(not isinstance(value, str) for value in row['highlights'])):
            raise SearchError('invalid_result_file', 'Invalid saved result highlights.')
    return data


def load_result(path):
    with Path(path).expanduser().open('rb') as stream:
        raw = stream.read(MAX_SNAPSHOT + 1)
    if len(raw) > MAX_SNAPSHOT:
        raise SearchError('invalid_result_file', 'Saved result exceeds 32 MiB.')
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeError):
        raise SearchError('invalid_result_file', 'Saved result is not valid JSON.') from None
    return validate_result(data)


def destination(path):
    target = Path(path).expanduser().absolute()
    if os.path.lexists(target):
        raise SearchError('output_exists', 'Output directory already exists; choose a new directory.')
    if not target.name:
        raise SearchError('invalid_output_path', 'Choose a new output directory.')
    return target


def markdown(data, language):
    en = language == 'en'

    def text(value):
        cleaned = ' '.join(str(value or '').split())
        escaped = html.escape(cleaned, quote=False)
        for char in ('\\', '`', '*', '_', '[', ']', '|', '#'):
            escaped = escaped.replace(char, '\\' + char)
        return escaped

    unknown = 'Not provided' if en else '未提供'
    rows = data['results']
    domains = {urlsplit(r['url']).hostname for r in rows}
    lines = ['# xcoze search', '',
             ('Query: ' if en else '查询：') + text(data['query']),
             ('Retrieved: ' if en else '检索时间：') + text(data.get('retrieved_at') or unknown),
             ('Result count: ' if en else '结果条数：') + str(len(rows)),
             ('Source domains: ' if en else '来源域名数：') + str(len(domains)), '',
             ('Order follows the saved results. Repeated URLs retain their provider attribution.'
              if en else '按已保存的结果顺序排列，同一链接保留各来源的归属。'),
             ('Dates retain source precision. Missing publication dates remain unknown.'
              if en else '日期保留来源精度，缺少发布日期时标记为未提供。'), '',
             '| # | Provider | Rank | Title | URL | Published | Type |' if en else
             '| 序号 | 来源 | 原排名 | 标题 | 链接 | 发布日期 | 内容类型 |',
             '|---:|---|---:|---|---|---|---|']
    for n, row in enumerate(rows, 1):
        url = row['url'].replace('<', '%3C').replace('>', '%3E').replace('|', '%7C')
        lines.append('| ' + ' | '.join([str(n), text(row['provider']), text(row.get('rank')),
                                      text(row['title']), '<' + url + '>',
                                      text(row.get('published_at') or unknown),
                                      text(row.get('content_kind') or unknown)]) + ' |')
    if not rows:
        lines += ['', 'No results were returned.' if en else '本次没有返回结果。']
    lines += ['', '## Excerpts' if en else '## 结果摘录', '']
    for n, row in enumerate(rows, 1):
        excerpt = row.get('summary') or row.get('snippet') or '\n'.join(row.get('highlights') or []) or row.get('content') or ''
        excerpt = ' '.join(str(excerpt).split())
        clipped = len(excerpt) > 600
        lines += [f"### {n}. {text(row['title'])}", '', text(excerpt[:600]) or unknown]
        if clipped:
            lines += ['Excerpt shortened to 600 characters.' if en else '摘录节选前 600 字符。']
        lines += ['']
    lines += ['## Review status' if en else '## 核验状态', '',
              'These excerpts come from search results. Open the original pages to verify claims and dates.'
              if en else '摘录来自搜索结果，需要核对的事实和日期请打开原文检查。',
              ('Saved errors or partial results: ' if en else '原结果中的错误或部分成功：') +
              (('yes' if en else '是') if data.get('errors') or data.get('partial') or not data.get('ok')
               else ('no' if en else '否')), '']
    return '\n'.join(lines)


def links_csv(data):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream)
    writer.writerow(['index', 'provider', 'provider_rank', 'title', 'url', 'published_at', 'content_kind'])

    def cell(value):
        value = str(value if value is not None else '')
        if value.lstrip('\ufeff \t\r\n').startswith(('=', '+', '-', '@')) or value.startswith(('\t', '\r', '\n')):
            value = "'" + value
        return value

    for n, row in enumerate(data['results'], 1):
        writer.writerow([n, *[cell(row.get(k)) for k in
                              ('provider', 'rank', 'title', 'url', 'published_at', 'content_kind')]])
    return '\ufeff' + stream.getvalue()


def export_result(data, output_dir, language='zh'):
    validate_result(data)
    if language not in ('zh', 'en'):
        raise SearchError('invalid_input', 'Report language must be zh or en.')
    target = Path(output_dir).expanduser().absolute()
    payloads = {
        'results.json': (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8'),
        'report.md': markdown(data, language).encode('utf-8'),
        'links.csv': links_csv(data).encode('utf-8'),
    }
    if len(payloads['results.json']) > MAX_SNAPSHOT:
        raise SearchError('invalid_result_file', 'Search result exceeds the 32 MiB export limit.')
    # Re-exporting an unchanged snapshot is read-only. Other existing content is preserved.
    if os.path.lexists(target):
        if (target.is_symlink() or not target.is_dir()
                or {p.name for p in target.iterdir()} != set(payloads)
                or any((target / name).is_symlink() or not (target / name).is_file()
                       or (target / name).stat().st_size != len(value)
                       or (target / name).read_bytes() != value for name, value in payloads.items())):
            raise SearchError('output_exists', 'Output directory contains different files; choose a new directory.')
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix='.xcoze-export-', dir=target.parent))
        try:
            for name, value in payloads.items():
                with (stage / name).open('xb') as stream:
                    os.chmod(stage / name, 0o600)
                    stream.write(value)
            # Reserve the destination exclusively, then publish each finished file.
            try:
                target.mkdir(mode=0o700)
            except FileExistsError:
                raise SearchError('output_exists', 'Output directory already exists; choose a new directory.') from None
            try:
                for name in payloads:
                    (stage / name).replace(target / name)
            except BaseException:
                for name in payloads:
                    (target / name).unlink(missing_ok=True)
                target.rmdir()
                raise
        finally:
            shutil.rmtree(stage)
    return {'ok': True, 'operation': 'export', 'network_requests': 0,
            'result_count': len(data['results']), 'original_ok': data.get('ok'),
            'files': {name: str(target / name) for name in payloads}}
