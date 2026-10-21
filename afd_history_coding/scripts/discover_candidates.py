#!/usr/bin/env python3
"""Run and archive fixed-site, date-bounded directional searches after the recorded pilot."""
import concurrent.futures
import csv
import datetime as dt
import html as htmllib
import json
from pathlib import Path
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
TERMS=['Geschichte','Gedenken','Luther','Bismarck','Otto','1953','1989','Treuhand','Wiedervereinigung','Würde','Stolz','Transformation','Ostdeutschland']


def get(query):
    time=dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo('Asia/Shanghai')).isoformat()
    result={**query,'executed_at':time,'status':'','total_pages':'','returned_posts':'','error':'','archive':''}
    try:
        request=urllib.request.Request(query['url'],headers={'User-Agent':'Mozilla/5.0 (public academic source verification)'})
        with urllib.request.urlopen(request,timeout=30) as response:
            data=response.read();result['http_status']=response.status
            result['total_pages']=response.headers.get('X-WP-TotalPages','')
            result['total_posts']=response.headers.get('X-WP-Total','')
        filename=f"raw/search_{query['query_id']}_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.json"
        (ROOT/filename).write_bytes(data);result['archive']=filename
        posts=json.loads(data)
        if not isinstance(posts,list):raise ValueError('WordPress response is not a post list')
        result['status']='executed_success';result['returned_posts']=len(posts)
        return result,posts
    except Exception as error:
        result.update(status='failed',error=str(error))
        return result,[]


def main():
    if not (ROOT/'pilot_coding.csv').exists():raise SystemExit('Pilot must precede expansion')
    queries=[]
    for site,label in [('afd-lsa.de','LV'),('afdfraktion-lsa.de','FR')]:
        for term in TERMS:
            params=urllib.parse.urlencode({'search':term,'after':'2025-01-01T00:00:00',
                'before':'2026-09-06T23:59:59','per_page':100,
                '_fields':'id,date,date_gmt,modified,link,title,content,author'})
            queries.append(dict(query_id=f'WP{len(queries)+1:03}',site=site,label=label,
                search_expression=term,url=f'https://{site}/wp-json/wp/v2/posts?{params}',
                time_window='2025-01-01至2026-09-06',scope_status='暂定工作范围'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results=list(executor.map(get,queries))
    logpath=ROOT/'logs/directional_searches.jsonl'
    with logpath.open('a',encoding='utf-8') as log:
        for result,_ in results:log.write(json.dumps(result,ensure_ascii=False)+'\n')
    discoveries={}
    for result,posts in results:
        for post in posts:
            sid=f"P_{result['label']}_{post['id']}"
            if sid not in discoveries:
                discoveries[sid]={'source_id':sid,'post':post,'search_ids':[],
                    'archives':[],'site':result['site'],'label':result['label']}
            discoveries[sid]['search_ids'].append(result['query_id'])
            discoveries[sid]['archives'].append(result['archive'])
    discoveryfile=ROOT/'inputs/discovered_posts.json'
    if discoveryfile.exists():raise SystemExit('Discovery file exists; archive before a new search round')
    discoveryfile.write_text(json.dumps(discoveries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    candidatepath=ROOT/'inputs/source_candidates.json'
    candidates=json.loads(candidatepath.read_text(encoding='utf-8'))
    known={c['source_id'] for c in candidates}
    for sid,d in sorted(discoveries.items()):
        if sid in known:continue
        post=d['post']
        candidates.append(dict(source_id=sid,candidate_role='核心语料候选',
            title=htmllib.unescape(post['title']['rendered']),title_verification='已核官方WordPress API标题；网页正文待核',
            author_or_institution='AfD Landesverband Sachsen-Anhalt' if d['label']=='LV' else 'AfD-Fraktion im Landtag von Sachsen-Anhalt',
            author_verification='官方站点发布机构，具体署名待正文核验',speaker='',speaker_verification='待正文核验',
            material_type='官网文章／新闻稿候选',type_verification='待正文核验',
            document_date='',website_publication_date=post['date'][:10],
            publication_date_basis=f"官方WordPress API post.date={post['date']}；原始响应：{d['archives'][0]}；post.id={post['id']}",
            original_url=post['link'],inclusion_decision='待全文语义筛选，未纳入',
            inclusion_or_exclusion_reason='定向检索候选；关键词命中不等于纳入或赋码',
            duplicate_group='',duplicate_verification='待全文比较',metadata_status='官方API日期／标题已核，正文与立场待核',
            version=post['modified'],version_verification='官方API修改时间；与发布日期分开',
            source_provenance=d['archives'][0],search_id='|'.join(d['search_ids']),search_date='',
            search_expression='详见logs/directional_searches.jsonl与inputs/discovered_posts.json',
            site=d['site'],working_time_window='2025-01-01至2026-09-06',scope_status='暂定工作范围',
            notes='目的性检索；无主题词的文章可能未命中；当前官网版本可能晚于原发表日期，须注意回溯修订'))
    candidatepath.write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (ROOT/'logs/process_runs.jsonl').open('a',encoding='utf-8') as log:
        log.write(json.dumps({'script':'discover_candidates.py','queries_executed':len(queries),
            'queries_successful':sum(r['status']=='executed_success' for r,_ in results),
            'unique_post_candidates':len(discoveries),'selection':'未完成语义筛选；不是已纳入语料数'},ensure_ascii=False)+'\n')
    for sid,d in sorted(discoveries.items()):
        p=d['post'];print(sid,p['date'][:10],htmllib.unescape(p['title']['rendered']))
    print(json.dumps({'executed_queries':len(queries),'unique_candidates':len(discoveries)},ensure_ascii=False))


if __name__=='__main__':main()
