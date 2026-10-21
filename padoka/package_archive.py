#!/usr/bin/env python3
"""Create independently extractable PDF ZIP volumes and a checksum manifest."""
import argparse
import csv
import hashlib
import json
import sqlite3
import zipfile
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--volume-mib', type=int, default=90)
    p.add_argument('--incremental', action='store_true', help='Append volumes without repacking existing files')
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(args.root / 'data/padoka.sqlite')
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT url,local_path,sha256,byte_count FROM files "
                       "WHERE status='downloaded' ORDER BY local_path").fetchall()
    manifest = []
    mapping = []
    manifest_path = args.out / 'volumes.json'
    if args.incremental and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        for volume in manifest:
            path = args.out / volume['name']
            if hashlib.sha256(path.read_bytes()).hexdigest() != volume['sha256']:
                raise ValueError(f'Volume checksum mismatch: {path}')
            with zipfile.ZipFile(path) as z:
                mapping.extend(dict(row, volume=volume['name'])
                               for row in json.loads(z.read('volume-manifest.json')))
        packed = {row['local_path']: row['sha256'] for row in mapping}
        for row in rows:
            if row['local_path'] in packed and row['sha256'] != packed[row['local_path']]:
                raise ValueError(f"Previously packaged file changed: {row['local_path']}")
        rows = [row for row in rows if row['local_path'] not in packed]
    batches, batch, total = [], [], 0
    for row in rows:
        if batch and total + row['byte_count'] > args.volume_mib * 1024 * 1024:
            batches.append(batch)
            batch, total = [], 0
        batch.append(dict(row))
        total += row['byte_count']
    if batch:
        batches.append(batch)
    for i, batch in enumerate(batches, len(manifest) + 1):
        path = args.out / f'padoka-pdfs-{i:03}.zip'
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            z.writestr('volume-manifest.json', json.dumps(batch, ensure_ascii=False, indent=2))
            for row in batch:
                source = args.root / row['local_path']
                if hashlib.sha256(source.read_bytes()).hexdigest() != row['sha256']:
                    raise ValueError(f'Checksum mismatch: {source}')
                z.write(source, row['local_path'])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest.append(dict(name=path.name, files=len(batch), bytes=path.stat().st_size, sha256=digest))
        mapping.extend(dict(row, volume=path.name) for row in batch)
        print(path.name, len(batch), path.stat().st_size, flush=True)
    (args.out / 'volumes.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (args.out / 'SHA256SUMS').write_text(''.join(f"{x['sha256']}  {x['name']}\n" for x in manifest))
    with (args.out / 'file-volumes.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['url','local_path','sha256','byte_count','volume'])
        writer.writeheader()
        writer.writerows(sorted(mapping, key=lambda x: x['local_path']))


if __name__ == '__main__':
    main()
