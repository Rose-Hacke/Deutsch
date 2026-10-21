#!/usr/bin/env python3
"""Fetch candidate URLs with normal TLS verification; never verify metadata by guessing."""
import argparse
import concurrent.futures
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
FIELDS = [
    'source_id', 'candidate_role', 'title', 'title_verification',
    'author_or_institution', 'author_verification', 'speaker', 'speaker_verification',
    'material_type', 'type_verification', 'document_date', 'website_publication_date',
    'publication_date_basis', 'original_url', 'final_url', 'retrieval_attempted_at',
    'retrieved_at', 'local_filename', 'clean_filename', 'sha256', 'inclusion_decision',
    'inclusion_or_exclusion_reason', 'duplicate_group', 'duplicate_verification',
    'readability', 'retrieval_status', 'http_status', 'error', 'metadata_status',
    'version', 'version_verification', 'document_number_clue', 'source_provenance',
    'search_id', 'search_date', 'search_expression', 'site', 'working_time_window',
    'scope_status', 'notes',
]


def fetch(candidate):
    stamp = dt.datetime.now(dt.timezone.utc)
    record = {
        'source_id': candidate['source_id'], 'url': candidate['original_url'],
        'attempted_at': stamp.astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),
        'tls_verification': 'enabled_default_context', 'status': '',
        'http_status': '', 'final_url': '', 'retrieved_at': '', 'raw_path': '',
        'sha256': '', 'error': '', 'content_type': '',
    }
    try:
        request = urllib.request.Request(candidate['original_url'], headers={
            'User-Agent': 'Mozilla/5.0 (public academic source verification)',
        })
        with urllib.request.urlopen(request, timeout=25) as response:
            data = response.read(40 * 1024 * 1024 + 1)
            if len(data) > 40 * 1024 * 1024:
                raise ValueError('Download exceeds 40 MiB limit; manual retrieval required')
            record.update(http_status=response.status, final_url=response.url,
                          content_type=response.headers.get('Content-Type', ''))
        digest = hashlib.sha256(data).hexdigest()
        extension = '.pdf' if data.startswith(b'%PDF-') else (
            '.html' if b'<html' in data[:2000].lower() or 'html' in record['content_type'] else '.bin')
        filename = f"{candidate['source_id']}_{stamp.strftime('%Y%m%dT%H%M%S%fZ')}_{digest[:12]}{extension}"
        target = ROOT / 'raw' / filename
        with target.open('xb') as handle:
            handle.write(data)
        record.update(status='downloaded_unverified', sha256=digest,
                      raw_path=str(target.relative_to(ROOT)),
                      retrieved_at=dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo('Asia/Shanghai')).isoformat())
        if candidate['original_url'].split('?')[0].lower().endswith('.pdf') and extension != '.pdf':
            record['status'] = 'downloaded_content_mismatch_requires_review'
    except Exception as error:
        record['error'] = str(error)
        record['status'] = 'blocked_proxy_403' if 'Tunnel connection failed: 403' in str(error) else 'retrieval_failed'
        if isinstance(error, urllib.error.HTTPError):
            record['http_status'] = error.code
        # A CONNECT proxy rejection is not a website HTTP 403 response.
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-id', action='append', help='Fetch only named candidates')
    args = parser.parse_args()
    candidates = json.loads((ROOT / 'inputs/source_candidates.json').read_text(encoding='utf-8'))
    if args.source_id:
        candidates = [c for c in candidates if c['source_id'] in args.source_id]
        if len(candidates) != len(set(args.source_id)):
            raise SystemExit('Unknown or repeated requested source ID')
    for directory in ['raw', 'clean', 'logs']:
        (ROOT / directory).mkdir(exist_ok=True)
    existing = {}
    manifest = ROOT / 'sources.csv'
    if manifest.exists():
        with manifest.open(encoding='utf-8', newline='') as handle:
            existing = {row['source_id']: row for row in csv.DictReader(handle)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        attempts = list(executor.map(fetch, candidates))
    with (ROOT / 'logs/fetch_attempts.jsonl').open('a', encoding='utf-8') as log:
        for attempt in attempts:
            log.write(json.dumps(attempt, ensure_ascii=False) + '\n')
    for candidate, attempt in zip(candidates, attempts):
        row = {field: '' for field in FIELDS}
        row.update(candidate)
        row.update(existing.get(candidate['source_id'], {}))
        row.update({
            'retrieval_attempted_at': attempt['attempted_at'],
            'retrieval_status': attempt['status'], 'http_status': attempt['http_status'],
            'error': attempt['error'], 'search_date': attempt['attempted_at'][:10],
        })
        if attempt['raw_path']:
            # Prior immutable versions remain in raw/; this field points to the latest retrieval.
            row.update(local_filename=attempt['raw_path'], retrieved_at=attempt['retrieved_at'],
                       sha256=attempt['sha256'], final_url=attempt['final_url'],
                       readability='已下载，待人工核验内容及可读性')
        elif not row['local_filename']:
            row['readability'] = '不可读取：未取得原文'
        existing[candidate['source_id']] = row
    temporary = ROOT / 'logs/sources.next.csv'
    with temporary.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(existing[key] for key in sorted(existing))
    temporary.replace(manifest)
    summary = {
        'executed_at': dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),
        'attempted': len(attempts),
        'downloaded': sum(bool(a['raw_path']) for a in attempts),
        'blocked_or_failed': sum(not bool(a['raw_path']) for a in attempts),
        'metadata_verified_by_this_script': 0,
    }
    with (ROOT / 'logs/process_runs.jsonl').open('a', encoding='utf-8') as handle:
        handle.write(json.dumps({'script': 'collect_sources.py', **summary}, ensure_ascii=False) + '\n')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
