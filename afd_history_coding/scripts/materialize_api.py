#!/usr/bin/env python3
"""Link each full official API post body to its immutable original search-response archive."""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from lxml import html
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]


def main():
    with (ROOT/'sources.csv').open(encoding='utf-8',newline='') as handle:
        reader=csv.DictReader(handle);fields=reader.fieldnames;rows=list(reader)
    byid={x['source_id']:x for x in rows}
    candidates={x['source_id']:x for x in json.loads((ROOT/'inputs/source_candidates.json').read_text(encoding='utf-8'))}
    discoveries=json.loads((ROOT/'inputs/discovered_posts.json').read_text(encoding='utf-8'))
    attempts={r['query_id']:r for r in map(json.loads,(ROOT/'logs/directional_searches.jsonl').read_text(encoding='utf-8').splitlines())}
    for sid,entry in sorted(discoveries.items()):
        post=entry['post'];row={k:'' for k in fields};row.update(candidates[sid]);row.update(byid.get(sid,{}))
        archive=entry['archives'][0]
        at=attempts[entry['search_ids'][0]]['executed_at']
        row.update(local_filename=archive,sha256=hashlib.sha256((ROOT/archive).read_bytes()).hexdigest(),
            retrieval_status='downloaded_official_api_body',readability='官方API正文可读；单条post.id见发布日期依据',
            retrieved_at=at,retrieval_attempted_at=at,search_date=at[:10])
        doc=html.fromstring('<div>'+post['content']['rendered']+'</div>')
        for node in doc.xpath('.//script|.//style'):node.drop_tree()
        records=[]
        for node in doc.xpath('.//p|.//h1|.//h2|.//h3|.//li[not(.//p)]'):
            text=' '.join(node.text_content().split())
            if text:records.append(dict(locator=f'P{len(records)+1:03}',text=text,
                selector=f'官方WordPress API post.id={post["id"]} content.rendered',html_tag=node.tag))
        if not records and doc.text_content().strip():records=[dict(locator='P001',text=' '.join(doc.text_content().split()))]
        filename=f'clean/{sid}_located.json'
        (ROOT/filename).write_text(json.dumps(dict(source_id=sid,raw_path=archive,raw_sha256=row['sha256'],
            api_post_id=post['id'],records=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (ROOT/f'clean/{sid}.txt').write_text('\n\n'.join(f"[{p['locator']}]\n{p['text']}" for p in records)+'\n',encoding='utf-8')
        row['clean_filename']=filename;byid[sid]=row
    with (ROOT/'sources.csv').open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(byid[k] for k in sorted(byid))
    now=dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo('Asia/Shanghai')).isoformat()
    with (ROOT/'logs/process_runs.jsonl').open('a',encoding='utf-8') as handle:
        handle.write(json.dumps(dict(script='materialize_api.py',executed_at=now,
            archived_post_bodies=len(discoveries),semantic_inclusions_made=0),ensure_ascii=False)+'\n')
    print(json.dumps(dict(official_api_bodies=len(discoveries),candidate_records=len(byid)),ensure_ascii=False))


if __name__=='__main__':main()
