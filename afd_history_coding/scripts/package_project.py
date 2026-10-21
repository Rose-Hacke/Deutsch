#!/usr/bin/env python3
"""Create a reproducible file manifest and a ZIP beside the project after successful validation."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    report=json.loads((ROOT/'logs/validation_report.json').read_text(encoding='utf-8'))
    if report['status']!='passed':raise SystemExit('Validation must pass before packaging')
    files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='MANIFEST.sha256']
    manifest=''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n' for p in sorted(files))
    (ROOT/'MANIFEST.sha256').write_text(manifest,encoding='utf-8')
    files.append(ROOT/'MANIFEST.sha256')
    target=ROOT.parent/(ROOT.name+'.zip')
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path in sorted(files):archive.write(path,arcname=str(Path(ROOT.name)/path.relative_to(ROOT)))
    with zipfile.ZipFile(target) as archive:
        corrupt=archive.testzip()
        if corrupt:raise SystemExit('Corrupt archive member: '+corrupt)
    print(json.dumps(dict(zip_path=str(target),bytes=target.stat().st_size,files=len(files),zip_integrity='passed'),ensure_ascii=False))


if __name__=='__main__':main()
