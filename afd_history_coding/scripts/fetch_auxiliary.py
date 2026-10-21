#!/usr/bin/env python3
"""Archive directly inspected metadata and literature pages; do not count these as core texts."""
import datetime as dt
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
URLS={
    'A001':'https://afd-lsa.de/wp-json/wp/v2/media?search=Regierungsprogramm&per_page=100&_fields=id,date,modified,title,source_url',
    'A002':'https://www.landtag.sachsen-anhalt.de/suchergebnis/?q=deutschdenken',
    'A003':'https://afd-lsa.de/transparenzerklaerung-regierungsprogramm-lv/',
    'M003':'https://www.qualitative-research.net/index.php/fqs/article/view/3343/4557',
    'A004':'https://afdfraktion-lsa.de/wp-json/wp/v2/posts?per_page=5&_fields=id,date,link,title',
    'A005':'https://afdfraktion-lsa.de/wp-json/wp/v2/posts?search=1953&per_page=100&_fields=id,date,link,title',
    'A006':'https://padoka.landtag.sachsen-anhalt.de/portal/browse.tt.html',
    'A007':'https://afdfraktion-lsa.de/wp-json/wp/v2/posts?before=2026-09-06T23%3A59%3A59&per_page=1&_fields=id,date,link,title',
    'M004':'https://www.qualitative-research.net/index.php/fqs/article/download/3343/4557?inline=1',
}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--ids',nargs='*')
    args=parser.parse_args()
    records=[]
    for aid,url in URLS.items():
        if args.ids and aid not in args.ids:continue
        row=dict(auxiliary_id=aid,url=url,attempted_at=dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),status='',raw_path='',error='')
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (public academic source verification)'})
            with urllib.request.urlopen(request,timeout=25) as response:
                data=response.read();ctype=response.headers.get('Content-Type','');row['final_url']=response.url
            sha=hashlib.sha256(data).hexdigest()
            ext='.json' if 'json' in ctype else ('.pdf' if data.startswith(b'%PDF-') else '.html')
            path=f'raw/{aid}_{dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")}_{sha[:12]}{ext}'
            with (ROOT/path).open('xb') as handle:handle.write(data)
            row.update(status='downloaded',raw_path=path,sha256=sha)
        except Exception as error:row.update(status='failed',error=str(error))
        records.append(row)
    with (ROOT/'logs/auxiliary_fetches.jsonl').open('a',encoding='utf-8') as handle:
        for record in records:handle.write(json.dumps(record,ensure_ascii=False)+'\n')
    print(json.dumps(records,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
