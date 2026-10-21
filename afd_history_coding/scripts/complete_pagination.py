#!/usr/bin/env python3
"""Complete observed WordPress search pages, preserving earlier results and stable post IDs."""
import concurrent.futures
import html
import json
from pathlib import Path
from discover_candidates import get

ROOT=Path(__file__).resolve().parents[1]


def main():
    logs=[json.loads(line) for line in (ROOT/'logs/directional_searches.jsonl').read_text(encoding='utf-8').splitlines()]
    known={r['query_id'] for r in logs}
    queries=[]
    for record in logs:
        if '_P' in record['query_id']:continue
        total=int(record.get('total_pages') or 0)
        if total>10:raise SystemExit('More than ten pages requires an explicit further collection decision')
        for page in range(2,total+1):
            qid=f"{record['query_id']}_P{page}"
            if qid not in known:
                query={k:record[k] for k in ['site','label','search_expression','time_window','scope_status']}
                query.update(query_id=qid,url=record['url']+f'&page={page}')
                queries.append(query)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(get,queries))
    with (ROOT/'logs/directional_searches.jsonl').open('a',encoding='utf-8') as handle:
        for result,_ in results:handle.write(json.dumps(result,ensure_ascii=False)+'\n')
    path=ROOT/'inputs/discovered_posts.json';discoveries=json.loads(path.read_text(encoding='utf-8'))
    cpath=ROOT/'inputs/source_candidates.json';candidates=json.loads(cpath.read_text(encoding='utf-8'))
    template=next(c for c in candidates if c['source_id'].startswith('P_LV_'))
    added=[]
    for result,posts in results:
        for post in posts:
            sid=f"P_{result['label']}_{post['id']}"
            if sid in discoveries:continue
            discoveries[sid]=dict(source_id=sid,post=post,search_ids=[result['query_id']],archives=[result['archive']],site=result['site'],label=result['label'])
            candidate={**template,'source_id':sid,'title':html.unescape(post['title']['rendered']),
                'website_publication_date':post['date'][:10],
                'publication_date_basis':f"官方WordPress API post.date={post['date']}；原始响应：{result['archive']}；post.id={post['id']}",
                'original_url':post['link'],'version':post['modified'],'source_provenance':result['archive'],'search_id':result['query_id']}
            candidates.append(candidate);added.append(sid)
    path.write_text(json.dumps(discoveries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    cpath.write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(pagination_requests=len(queries),additional_candidates=len(added),unique_candidates=len(discoveries)),ensure_ascii=False))
    for sid in added:
        p=discoveries[sid]['post']
        if not p['title']['rendered'].startswith('Transparenzerklärung'):
            print(sid,p['date'],html.unescape(p['title']['rendered']))


if __name__=='__main__':main()
