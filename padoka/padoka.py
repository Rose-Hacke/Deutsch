#!/usr/bin/env python3
"""Reproducible PADOKA document catalog, downloads and SQLite full-text search."""
import argparse
import concurrent.futures
import csv
import gzip
import hashlib
import json
import re
import shutil
import sqlite3
import subprocess
import threading
import time
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup, Comment
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = 'https://padoka.landtag.sachsen-anhalt.de/'
PORTAL = BASE + 'portal/'
SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS records(
 record_id TEXT PRIMARY KEY, source_ids TEXT NOT NULL, title TEXT NOT NULL,
 citation TEXT NOT NULL, document_date TEXT, date_candidates TEXT NOT NULL,
 document_number TEXT, electoral_period INTEGER, source_url TEXT NOT NULL,
 first_seen TEXT NOT NULL, last_seen TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS files(
 url TEXT PRIMARY KEY, status TEXT NOT NULL DEFAULT 'pending', local_path TEXT,
 sha256 TEXT, byte_count INTEGER, downloaded_at TEXT, http_status INTEGER,
 attempts INTEGER NOT NULL DEFAULT 0, error TEXT, text_status TEXT, page_count INTEGER);
CREATE TABLE IF NOT EXISTS record_files(
 record_id TEXT NOT NULL REFERENCES records(record_id),
 url TEXT NOT NULL REFERENCES files(url), label TEXT,
 PRIMARY KEY(record_id,url));
CREATE TABLE IF NOT EXISTS queries(
 query_key TEXT PRIMARY KEY, date_from TEXT NOT NULL, date_to TEXT NOT NULL,
 periods TEXT NOT NULL, sref TEXT NOT NULL, source_hits INTEGER,
 fetched_hits INTEGER, expected_records INTEGER, parsed_records INTEGER DEFAULT 0,
 next_start INTEGER DEFAULT 0, completed INTEGER DEFAULT 0,
 observed_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS query_records(
 query_key TEXT NOT NULL REFERENCES queries(query_key),
 record_id TEXT NOT NULL REFERENCES records(record_id),
 PRIMARY KEY(query_key,record_id));
CREATE TABLE IF NOT EXISTS evidence(
 path TEXT PRIMARY KEY, sha256 TEXT NOT NULL, fetched_at TEXT NOT NULL,
 query_key TEXT NOT NULL, start_offset INTEGER NOT NULL, record_count INTEGER NOT NULL);
CREATE VIRTUAL TABLE IF NOT EXISTS records_fts USING fts5(record_id UNINDEXED,title,citation);
CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(url UNINDEXED,body);
CREATE INDEX IF NOT EXISTS records_date ON records(document_date);
CREATE INDEX IF NOT EXISTS files_status ON files(status);
CREATE INDEX IF NOT EXISTS record_files_url ON record_files(url);
'''


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def database(root):
    root = Path(root)
    (root / 'data').mkdir(parents=True, exist_ok=True)
    target = root / 'data/padoka.sqlite'
    compressed = target.with_suffix('.sqlite.gz')
    if not target.exists() and compressed.exists():
        temporary = target.with_suffix('.restore.part')
        try:
            with gzip.open(compressed, 'rb') as source, temporary.open('wb') as out:
                shutil.copyfileobj(source, out)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
    con = sqlite3.connect(target, timeout=60)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def session():
    s = requests.Session()
    s.headers['User-Agent'] = 'PadokaResearchArchive/1.0 (public documents; resumable, rate-limited)'
    s.mount('https://', HTTPAdapter(max_retries=Retry(
        total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=['GET'], respect_retry_after_header=True)))
    return s


def expression(start, end, periods):
    return (f'((/WP ({";".join(map(str, periods))}) OR WP="") AND '
            f'(/DAT,DDAT,SDAT {start.replace("-", " ")} : {end.replace("-", " ")})) '
            'AND TYP=DOKDBE NOT (1SPERI,SPERI=JA)')


def public_file(url):
    u = urlsplit(url)
    return u.scheme == 'https' and u.netloc == urlsplit(BASE).netloc and u.path.startswith('/files/')


def parse_report(content):
    soup = BeautifulSoup(content, 'html.parser')
    result = []
    for node in soup.select('.efxRecordRepeater'):
        selection = node.select_one('input[value^="lsa.lissh:D-"]')
        if selection is None:
            raise ValueError('Record without a stable PADOKA document identifier')
        ids = {selection['value'].split(':', 1)[1]}
        # Read identifiers from the published debug comment as data, never evaluate Perl.
        for comment in node.find_all(string=lambda x: isinstance(x, Comment)):
            match = re.search(r"'ID'\s*=>\s*\[(.*?)\]", str(comment), re.S)
            if match:
                ids.update(re.findall(r"'main'\s*=>\s*'(D-\d+)'", match[1]))
        ids = sorted(ids, key=lambda x: int(x[2:]))
        citation = ' '.join(x.get_text(' ', strip=True) for x in node.select('span.h6')).strip()
        heading = node.select_one('h3')
        title = heading.get_text(' ', strip=True) if heading else citation
        dates = []
        for d in re.findall(r'\b\d{2}\.\d{2}\.\d{4}\b', citation):
            try:
                iso = datetime.strptime(d, '%d.%m.%Y').date().isoformat()
                if iso not in dates:
                    dates.append(iso)
            except ValueError:
                pass
        number = re.search(r'\b([1-9]/(?:[A-Za-zÄÖÜäöüß]+/)?[A-Za-zÄÖÜäöüß]*\d+(?:v\d+)?)\b', citation)
        attachments = {}
        for link in node.select('a[href]'):
            url = urljoin(PORTAL, link['href']).split('#', 1)[0]
            if public_file(url):
                label = link.select_one('.icon-text')
                attachments[url] = label.get_text(' ', strip=True) if label else link.get_text(' ', strip=True)
        # Use the website's published expert-search field and a stable source ID.
        source_url = PORTAL + 'browse.tt.html?' + urlencode({
            'type': 'generic2', 'action': 'link', 'slab-free.1': 'FREI',
            'sprompt-free.1': f'ID={ids[0]}'})
        result.append(dict(record_id=ids[0], source_ids=ids, title=title,
                           citation=citation, document_date=dates[0] if len(dates) == 1 else None,
                           date_candidates=dates, document_number=number[1] if number else None,
                           electoral_period=int(number[1][0]) if number else None,
                           source_url=source_url, attachments=attachments))
    return result


def save_records(con, records, key):
    stamp = now()
    for r in records:
        con.execute('''INSERT INTO records VALUES(?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(record_id) DO UPDATE SET source_ids=excluded.source_ids,
        title=excluded.title,citation=excluded.citation,document_date=excluded.document_date,
        date_candidates=excluded.date_candidates,document_number=excluded.document_number,
        electoral_period=excluded.electoral_period,source_url=excluded.source_url,last_seen=excluded.last_seen''',
                    (r['record_id'], json.dumps(r['source_ids']), r['title'], r['citation'],
                     r['document_date'], json.dumps(r['date_candidates']), r['document_number'],
                     r['electoral_period'], r['source_url'], stamp, stamp))
        con.execute('DELETE FROM records_fts WHERE record_id=?', (r['record_id'],))
        con.execute('INSERT INTO records_fts VALUES(?,?,?)', (r['record_id'], r['title'], r['citation']))
        con.execute('INSERT OR IGNORE INTO query_records VALUES(?,?)', (key, r['record_id']))
        for url, label in r['attachments'].items():
            con.execute('INSERT OR IGNORE INTO files(url) VALUES(?)', (url,))
            con.execute('INSERT OR REPLACE INTO record_files VALUES(?,?,?)', (r['record_id'], url, label))


def crawl(args):
    root = Path(args.root)
    con = database(root)
    s = session()
    periods = [int(x) for x in args.periods.split(',')]
    start, end = date.fromisoformat(args.start).isoformat(), date.fromisoformat(args.end).isoformat()
    if start > end:
        raise ValueError('Start date is later than end date')
    expr = expression(start, end, periods)
    key = hashlib.sha256(expr.encode()).hexdigest()[:16]
    q = con.execute('SELECT * FROM queries WHERE query_key=?', (key,)).fetchone()
    if q and q['completed'] and not args.refresh:
        print('Catalog already complete; use --refresh to query the source again.', flush=True)
        return
    con.execute('''INSERT INTO queries(query_key,date_from,date_to,periods,sref,observed_at)
                   VALUES(?,?,?,?,?,?) ON CONFLICT(query_key) DO NOTHING''',
                (key, start, end, json.dumps(periods), expr, now()))
    con.commit()
    payload = {'action': 'SearchAndDisplay', 'sources': ['lsa.lissh'], 'dataSet': '2',
               'report': {'rhl': 'main', 'rhlmode': 'add', 'format': 'generic2-short',
                          'mime': 'html', 'sort': 'WEBSO1/D WEBSO2'}}
    if args.search_id:
        payload['id'] = args.search_id
    else:
        payload['search'] = {'lines': {'2': ';'.join(map(str, periods)),
                                      '9': datetime.strptime(start, '%Y-%m-%d').strftime('%d.%m.%Y'),
                                      '10': datetime.strptime(end, '%Y-%m-%d').strftime('%d.%m.%Y')},
                             'serverrecordname': 'generic2Search', 'parsed': expr, 'sref': expr,
                             'json': [{'t': '"true"', 'tn': 'term', 'sf': 'NOJSON', 'op': 'eq'}]}
    snapshot = None
    for _ in range(120):
        res = s.post(PORTAL + 'browse.tt.json', json=payload, timeout=90)
        res.raise_for_status()
        info = res.json()
        if info.get('error'):
            raise RuntimeError(str(info['error']))
        sources = info.get('sources', {})
        for source in sources.values():
            if source.get('error'):
                raise RuntimeError(f'Source error: {source}')
        source = sources.get('lsa.lissh', {})
        print(f"Search: {info.get('fetched_hits')} / {source.get('hits')} source records; "
              f"{info.get('item_count')} displayed records; {source.get('status')}", flush=True)
        if source.get('status') == 'stopped' and info.get('report_id'):
            snapshot = info
            break
        if source.get('status') == 'stopped' and source.get('hits') == 0:
            snapshot = dict(info, item_count=0)
            break
        if info.get('search_id'):
            payload.pop('search', None)
            payload['id'] = info['search_id']
        else:
            raise RuntimeError('No search ID in server response')
        time.sleep(2)
    if snapshot is None:
        raise RuntimeError('Source search did not complete; no completeness claim made')
    expected = int(snapshot['item_count'])
    if int(snapshot.get('fetched_hits', 0)) < int(source.get('hits', 0)):
        raise RuntimeError('Source returned an incomplete result set')
    con.execute('''UPDATE queries SET source_hits=?,fetched_hits=?,expected_records=?,
                   parsed_records=0,next_start=0,completed=0,observed_at=? WHERE query_key=?''',
                (source.get('hits'), snapshot.get('fetched_hits'), expected, now(), key))
    con.execute('DELETE FROM query_records WHERE query_key=?', (key,))
    con.commit()
    metadata = root / 'evidence' / key / 'search-response.json'
    metadata.parent.mkdir(parents=True, exist_ok=True)
    metadata.write_text(json.dumps({k: v for k, v in snapshot.items()
                                   if k not in ['search_id', 'report_id']}, ensure_ascii=False, indent=2) + '\n')
    con.execute('INSERT OR REPLACE INTO evidence VALUES(?,?,?,?,?,?)',
                (metadata.relative_to(root).as_posix(), hashlib.sha256(metadata.read_bytes()).hexdigest(),
                 now(), key, -1, expected))
    con.commit()
    total = 0
    for offset in range(0, expected, args.page_size):
        res = s.get(PORTAL + 'report.tt.html', params={
            'report_id': snapshot['report_id'], 'start': offset, 'chunksize': args.page_size}, timeout=90)
        res.raise_for_status()
        records = parse_report(res.content)
        needed = min(args.page_size, expected - offset)
        if len(records) != needed:
            raise RuntimeError(f'Pagination mismatch at {offset}: {len(records)} != {needed}')
        evidence = root / 'evidence' / key / f'{offset:06}.html.gz'
        evidence.parent.mkdir(parents=True, exist_ok=True)
        with gzip.GzipFile(filename=str(evidence), mode='wb', mtime=0) as f:
            f.write(res.content)
        save_records(con, records, key)
        con.execute('INSERT OR REPLACE INTO evidence VALUES(?,?,?,?,?,?)',
                    (evidence.relative_to(root).as_posix(), hashlib.sha256(evidence.read_bytes()).hexdigest(),
                     now(), key, offset, len(records)))
        total += len(records)
        con.execute('UPDATE queries SET parsed_records=?,next_start=? WHERE query_key=?',
                    (total, offset + len(records), key))
        con.commit()
        print(f'Catalog: {total}/{expected}', flush=True)
        time.sleep(args.delay)
    unique = con.execute('SELECT count(*) FROM query_records WHERE query_key=?', (key,)).fetchone()[0]
    if total != expected or unique != expected:
        raise RuntimeError(f'Incomplete catalog: expected {expected}, parsed {total}, unique {unique}')
    con.execute('UPDATE queries SET completed=1 WHERE query_key=?', (key,))
    con.commit()
    print(f'Catalog complete: {expected} displayed records', flush=True)


_local = threading.local()
_rate_lock = threading.Lock()
_last_request = 0.0


def fetch_file(root, url, delay):
    global _last_request
    if not public_file(url):
        return dict(url=url, status='failed', error='URL is outside public PADOKA files')
    if not hasattr(_local, 'session'):
        _local.session = session()
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', urlsplit(url).path.rsplit('/', 1)[-1])[:100]
    relative = 'files/' + hashlib.sha256(url.encode()).hexdigest()[:20] + '_' + safe_name
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + '.part')
    try:
        with _rate_lock:
            wait = delay - (time.monotonic() - _last_request)
            if wait > 0:
                time.sleep(wait)
            _last_request = time.monotonic()
        with _local.session.get(url, stream=True, timeout=(20, 120), allow_redirects=False) as res:
            if res.status_code != 200:
                return dict(url=url, status='failed', http_status=res.status_code,
                            error=f'HTTP {res.status_code}; redirects are not followed')
            digest = hashlib.sha256()
            size = 0
            prefix = b''
            with part.open('wb') as f:
                for chunk in res.iter_content(262144):
                    if not chunk:
                        continue
                    if size == 0:
                        prefix = chunk[:1024]
                    size += len(chunk)
                    if size > 500 * 1024 * 1024:
                        raise ValueError('File exceeds 500 MiB download limit')
                    digest.update(chunk)
                    f.write(chunk)
            if b'%PDF-' not in prefix:
                raise ValueError('Response is not a PDF; not archived as a document')
        part.replace(target)
        return dict(url=url, status='downloaded', local_path=relative, sha256=digest.hexdigest(),
                    byte_count=size, downloaded_at=now(), http_status=200, error=None)
    except Exception as ex:
        return dict(url=url, status='failed', error=f'{type(ex).__name__}: {str(ex)[:400]}')
    finally:
        part.unlink(missing_ok=True)


def download(args):
    root = Path(args.root)
    con = database(root)
    urls = []
    for row in con.execute('SELECT * FROM files ORDER BY url'):
        if row['status'] == 'downloaded' and row['local_path']:
            p = root / row['local_path']
            if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256']:
                continue
        urls.append(row['url'])
    if args.limit:
        urls = urls[:args.limit]
    print(f'Downloading {len(urls)} pending/failed files with {args.workers} workers', flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch_file, root, url, args.delay): url for url in urls}
        for n, future in enumerate(concurrent.futures.as_completed(futures), 1):
            item = future.result()
            columns = [k for k in item if k != 'url']
            con.execute('UPDATE files SET ' + ','.join(k + '=?' for k in columns) +
                        ', attempts=attempts+1 WHERE url=?', [item[k] for k in columns] + [item['url']])
            con.commit()
            if n % 50 == 0 or item['status'] != 'downloaded' or n == len(urls):
                print(f"Files: {n}/{len(urls)}; last={item['status']} {item.get('error', '')}", flush=True)


def extract(args):
    root = Path(args.root)
    con = database(root)
    if not shutil.which('pdftotext'):
        raise RuntimeError('Install poppler-utils to provide pdftotext')
    rows = con.execute("SELECT * FROM files WHERE status='downloaded' AND text_status IS NULL").fetchall()
    for n, row in enumerate(rows, 1):
        try:
            p = subprocess.run(['pdftotext', '-enc', 'UTF-8', '-layout', str(root / row['local_path']), '-'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        except subprocess.TimeoutExpired:
            con.execute("UPDATE files SET text_status='timeout' WHERE url=?", (row['url'],))
            con.commit()
            continue
        body = p.stdout.decode('utf-8', errors='replace').replace('\x00', '')
        status = ('partial' if p.returncode else 'extracted') if body.strip() else (
            'error' if p.returncode else 'empty_scan_or_no_text')
        con.execute('DELETE FROM files_fts WHERE url=?', (row['url'],))
        if body.strip():
            con.execute('INSERT INTO files_fts VALUES(?,?)', (row['url'], body))
        con.execute('UPDATE files SET text_status=?,page_count=? WHERE url=?',
                    (status, body.count('\f') or None, row['url']))
        if n % 50 == 0 or n == len(rows):
            con.commit()
            print(f'Text: {n}/{len(rows)}', flush=True)
    con.commit()


def export(args):
    root = Path(args.root)
    con = database(root)
    out = root / 'data'
    for name in ['records', 'files', 'record_files', 'queries', 'evidence']:
        cur = con.execute('SELECT * FROM ' + name)
        with (out / f'{name}.csv').open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([x[0] for x in cur.description])
            writer.writerows(cur)
    summary = {
        'generated_at_utc': now(),
        'source': PORTAL + 'browse.tt.html',
        'queries': [dict(r) for r in con.execute('SELECT * FROM queries')],
        'records': con.execute('SELECT count(*) FROM records').fetchone()[0],
        'records_without_public_file': con.execute('SELECT count(*) FROM records r WHERE NOT EXISTS '
                                                  '(SELECT 1 FROM record_files rf WHERE rf.record_id=r.record_id)').fetchone()[0],
        'files_by_status': dict(con.execute('SELECT status,count(*) FROM files GROUP BY status')),
        'text_by_status': dict(con.execute("SELECT coalesce(text_status,'pending'),count(*) FROM files GROUP BY text_status")),
        'downloaded_bytes': con.execute("SELECT coalesce(sum(byte_count),0) FROM files WHERE status='downloaded'").fetchone()[0],
        'integrity_check': con.execute('PRAGMA integrity_check').fetchone()[0],
        'foreign_key_errors': [tuple(r) for r in con.execute('PRAGMA foreign_key_check')],
    }
    con.execute("INSERT INTO records_fts(records_fts) VALUES('optimize')")
    con.execute("INSERT INTO files_fts(files_fts) VALUES('optimize')")
    con.commit()
    con.execute('VACUUM')
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    (out / 'schema.sql').write_text(SCHEMA)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def search(args):
    con = database(args.root)
    sql = '''SELECT record_id,title,citation,document_date,source_url FROM records WHERE record_id IN (
             SELECT record_id FROM records_fts WHERE records_fts MATCH ?
             UNION SELECT rf.record_id FROM files_fts ft JOIN record_files rf ON rf.url=ft.url
             WHERE files_fts MATCH ?) ORDER BY document_date DESC LIMIT ?'''
    for row in con.execute(sql, (args.query, args.query, args.limit)):
        print(json.dumps(dict(row), ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(Path(__file__).resolve().parent))
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('crawl')
    p.add_argument('--start', default='2025-01-01')
    p.add_argument('--end', default=date.today().isoformat())
    p.add_argument('--periods', default='9,8')
    p.add_argument('--page-size', type=int, default=200)
    p.add_argument('--delay', type=float, default=0.5)
    p.add_argument('--search-id', help=argparse.SUPPRESS)
    p.add_argument('--refresh', action='store_true')
    p.set_defaults(func=crawl)
    p = commands.add_parser('download')
    p.add_argument('--workers', type=int, choices=range(1, 5), default=3)
    p.add_argument('--delay', type=float, default=0.35)
    p.add_argument('--limit', type=int, default=0)
    p.set_defaults(func=download)
    commands.add_parser('extract').set_defaults(func=extract)
    commands.add_parser('export').set_defaults(func=export)
    p = commands.add_parser('search')
    p.add_argument('query')
    p.add_argument('--limit', type=int, default=20)
    p.set_defaults(func=search)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
