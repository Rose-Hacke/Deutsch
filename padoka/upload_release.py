#!/usr/bin/env python3
"""Upload verified PDF volumes to the prepared GitHub Release and publish it."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def gh(*args):
    return subprocess.run(['gh', *args], check=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archives', type=Path, required=True)
    p.add_argument('--repo', default='Rose-Hacke/Deutsch')
    p.add_argument('--tag', default='padoka-2026-10-21')
    p.add_argument('--publish', action='store_true', help='Publish the existing draft after upload succeeds')
    args = p.parse_args()
    manifest = json.loads((args.archives / 'volumes.json').read_text())
    for volume in manifest:
        path = args.archives / volume['name']
        if path.stat().st_size != volume['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != volume['sha256']:
            raise ValueError(f'Archive checksum mismatch: {path}')
    for volume in manifest:
        gh('release', 'upload', args.tag, str(args.archives / volume['name']),
           '--repo', args.repo, '--clobber')
    for name in ['volumes.json', 'file-volumes.csv', 'SHA256SUMS']:
        gh('release', 'upload', args.tag, str(args.archives / name), '--repo', args.repo, '--clobber')
    if args.publish:
        gh('release', 'edit', args.tag, '--repo', args.repo, '--draft=false')


if __name__ == '__main__':
    main()
