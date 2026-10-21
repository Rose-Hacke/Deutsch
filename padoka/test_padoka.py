import hashlib
import importlib.util
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('padoka', Path(__file__).with_name('padoka.py'))
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

HTML = '''<div class="efxRecordRepeater">
<!-- 'ID' => [{'main' => 'D-20'}, {'main' => 'D-10'}] -->
<input value="lsa.lissh:D-20">
<h3>Über Bildung &amp; Kultur</h3>
<span class="h6">Antrag AfD 03.02.2025 Drucksache 8/1234 (3 S.)</span>
<a href="/files/drs/wp8/test.pdf"><span class="icon-text">Dokument</span></a>
<a href="https://unrelated.example/file.pdf">External</a>
</div>'''


def test_parse_stable_ids_unicode_and_public_links():
    r, = p.parse_report(HTML)
    assert r['record_id'] == 'D-10'
    assert r['source_ids'] == ['D-10', 'D-20']
    assert r['title'] == 'Über Bildung & Kultur'
    assert r['document_date'] == '2025-02-03'
    assert r['document_number'] == '8/1234'
    assert r['electoral_period'] == 8
    assert list(r['attachments']) == [p.BASE + 'files/drs/wp8/test.pdf']
    assert 'sprompt-free.1=ID%3DD-10' in r['source_url']


def test_ambiguous_dates_are_not_invented():
    r, = p.parse_report(HTML.replace('03.02.2025', '03.02.2025 / 04.02.2025'))
    assert r['document_date'] is None
    assert r['date_candidates'] == ['2025-02-03', '2025-02-04']


def test_information_document_number():
    r, = p.parse_report(HTML.replace('8/1234', '8/eu301'))
    assert r['document_number'] == '8/eu301'


def test_missing_stable_identifier_fails():
    with pytest.raises(ValueError):
        p.parse_report('<div class="efxRecordRepeater"><h3>Changed page</h3></div>')


def test_sqlite_dedup_and_fulltext(tmp_path):
    con = p.database(tmp_path)
    con.execute("INSERT INTO queries(query_key,date_from,date_to,periods,sref,observed_at) "
                "VALUES('q','2025-01-01','2026-10-21','[8,9]','query','now')")
    r = p.parse_report(HTML)
    p.save_records(con, r, 'q')
    p.save_records(con, r, 'q')
    assert con.execute('SELECT count(*) FROM records').fetchone()[0] == 1
    assert con.execute('SELECT count(*) FROM record_files').fetchone()[0] == 1
    assert con.execute("SELECT record_id FROM records_fts WHERE records_fts MATCH 'Kultur'").fetchone()[0] == 'D-10'
    assert not con.execute('PRAGMA foreign_key_check').fetchall()


def test_download_rejects_html_and_removes_partial_file(tmp_path, monkeypatch):
    class Response:
        status_code = 200
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def iter_content(self, size): yield b'<html>Access error</html>'
    class Session:
        def get(self, *args, **kwargs): return Response()
    monkeypatch.setattr(p._local, 'session', Session(), raising=False)
    result = p.fetch_file(tmp_path, p.BASE + 'files/one.pdf', 0)
    assert result['status'] == 'failed'
    assert not list(tmp_path.rglob('*.part'))
    assert not list(tmp_path.rglob('*.pdf'))


def test_download_checks_pdf_hash(tmp_path, monkeypatch):
    body = b'%PDF-1.4\nexample'
    class Response:
        status_code = 200
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def iter_content(self, size): yield body
    class Session:
        def get(self, *args, **kwargs): return Response()
    monkeypatch.setattr(p._local, 'session', Session(), raising=False)
    result = p.fetch_file(tmp_path, p.BASE + 'files/one.pdf', 0)
    assert result['sha256'] == hashlib.sha256(body).hexdigest()
    assert (tmp_path / result['local_path']).read_bytes() == body


def test_incremental_archive_covers_every_file_once(tmp_path):
    root, out = tmp_path / 'root', tmp_path / 'out'
    con = p.database(root)
    (root / 'files').mkdir()
    def add_file(i):
        body = b'%PDF-1.4\n' + bytes([i])
        relative = f'files/{i}.pdf'
        (root / relative).write_bytes(body)
        con.execute('INSERT INTO files(url,status,local_path,sha256,byte_count) VALUES(?,?,?,?,?)',
                    (p.BASE + relative, 'downloaded', relative, hashlib.sha256(body).hexdigest(), len(body)))
        con.commit()
    for i in [1, 2]: add_file(i)
    command = [sys.executable, str(Path(__file__).with_name('package_archive.py')),
               '--root', str(root), '--out', str(out), '--incremental']
    subprocess.run(command, check=True, capture_output=True)
    first = (out / 'padoka-pdfs-001.zip').read_bytes()
    add_file(3)
    subprocess.run(command, check=True, capture_output=True)
    assert (out / 'padoka-pdfs-001.zip').read_bytes() == first
    manifest = json.loads((out / 'volumes.json').read_text())
    assert sum(v['files'] for v in manifest) == 3
    with (out / 'file-volumes.csv').open(encoding='utf-8-sig') as f:
        mapping = list(csv.DictReader(f))
    assert len(mapping) == len({v['local_path'] for v in mapping}) == 3
