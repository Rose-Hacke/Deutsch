#!/usr/bin/env python3
"""Fail on broken provenance, missing decisions, incorrect evidence, or missing review tasks."""
import csv
import datetime as dt
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo
from make_pilot import normalized

ROOT=Path(__file__).resolve().parents[1]


def read(name):
    with (ROOT/name).open(encoding='utf-8',newline='') as handle:return list(csv.DictReader(handle))


def canonical(text):
    return re.sub(r'[\s\-\u00ad]','',text)


def main():
    errors=[];checks=Counter()
    def require(condition,message,category):
        checks[category]+=1
        if not condition:errors.append(message)
    sources=read('sources.csv');segments=read('segments.csv');coding=read('coding.csv');queue=read('review_queue.csv')
    codes={r['code'] for r in read('inputs/active_codes.csv')}
    smap={r['source_id']:r for r in sources};umap={r['unit_id']:r for r in segments}
    require(len(smap)==len(sources),'duplicate source IDs','unique_ids')
    require(len(umap)==len(segments),'duplicate unit IDs','unique_ids')
    pairs=[(r['unit_id'],r['code']) for r in coding]
    require(len(pairs)==len(set(pairs)),'duplicate unit-code rows','complete_decisions')
    require(set(pairs)=={(u,c) for u in umap for c in codes},'missing/extra unit-code combinations','complete_decisions')
    sha_seen={}
    for source in sources:
        local=source['local_filename']
        if local:
            require((ROOT/local).is_file(),f"missing raw: {source['source_id']}",'raw_archives')
            if (ROOT/local).is_file():
                digest=sha_seen.setdefault(local,hashlib.sha256((ROOT/local).read_bytes()).hexdigest())
                require(digest==source['sha256'],f"hash mismatch: {source['source_id']}",'raw_archives')
        if source['inclusion_decision']=='纳入核心（暂定工作范围内）':
            date=source['document_date'] or source['website_publication_date']
            require(bool(date) and '2025-01-01'<=date<='2026-09-06',f"core date not verified/in range: {source['source_id']}",'scope')
            require(bool(source['publication_date_basis']),f"missing date basis: {source['source_id']}",'scope')
    for unit in segments:
        uid=unit['unit_id'];sid=unit['source_id']
        require(sid in smap,f'missing source for {uid}','foreign_keys')
        require(bool(unit['german_original']) and bool(unit['chinese_translation']),f'missing bilingual text {uid}','bilingual_units')
        require('AI' in unit['translation_status'] and '待人工复核' in unit['translation_status'],f'translation falsely reviewed {uid}','review_status')
        for context in unit['context_unit_ids'].split('|'):
            if context:require(context in umap,f'bad context {uid}: {context}','foreign_keys')
        located=json.loads((ROOT/smap[sid]['clean_filename']).read_text(encoding='utf-8'))['records']
        if unit['pdf_page_index']:
            page_ids=[int(p) for p in unit['pdf_page_index'].split(',')]
            context='\n'.join(located[p-1]['text'] for p in page_ids)
            # Remove only recurring page/header/distribution lines before checking character sequence.
            lines=[]
            for line in context.splitlines():
                s=line.strip()
                if re.fullmatch(r'\d+',s):continue
                if re.fullmatch(r'\(Ausgegeben am \d{2}\.\d{2}\.\d{4}\)',s):continue
                if re.fullmatch(r'(?:[IVX]+\.\s+[A-ZÄÖÜẞ\s]+|PRÄAMBEL)\s*\d*',s):continue
                lines.append(line)
            reference=normalized('\n'.join(lines))
        else:
            locators=unit['web_paragraph_locator'].split(',')
            records={r['locator']:r['text'] for r in located}
            require(all(p in records for p in locators),f'bad paragraph locator {uid}','locators')
            reference='\n\n'.join(records.get(p,'') for p in locators)
        require(canonical(unit['german_original']) in canonical(reference),f'German unit not found at recorded locator: {uid}','german_provenance')
    for row in coding:
        uid=row['unit_id'];code=row['code'];value=row['value']
        require(value in ['0','1','?',''],f'invalid value {uid}/{code}','complete_decisions')
        require(row['source_id']==umap[uid]['source_id'],f'wrong source {uid}/{code}','foreign_keys')
        if value in ['1','?']:
            require(bool(row['german_evidence']) and row['german_evidence'] in umap[uid]['german_original'],f'evidence mismatch {uid}/{code}','exact_evidence')
        if value=='0':require(bool(row['decision_reason']),f'missing zero exclusion {uid}/{code}','exclusion_reasons')
        require(bool(row['chinese_explanation']),f'missing explanation {uid}/{code}','explanations')
        require(row['human_review_status']=='未人工复核' and row['human_value']=='',f'false human review {uid}/{code}','review_status')
        require(row['codebook_version']=='v0.3',f'version mismatch {uid}/{code}','versions')
        if value=='?' or (value=='1' and (code in ['H4','N1'] or '推断' in row['expression_type'] or '上下文' in row['expression_type'])):
            require(any(q['unit_id']==uid and q['codes']==code for q in queue),f'missing review task {uid}/{code}','review_coverage')
    for row in read('narrative_chains.csv'):
        for uid in row['unit_ids'].split('|'):require(uid in umap,f'chain {row["chain_id"]} missing unit {uid}','narrative_links')
    selected={r['source_id'] for r in segments}
    groups=[smap[sid]['duplicate_group'] for sid in selected]
    require(len(groups)==len(set(groups)),'selected sources contain exact duplicates','deduplication')
    require(len(read('pilot_segments.csv'))==12 and len(read('pilot_coding.csv'))==120,'pilot sizes changed','versions')
    core={sid for sid,s in smap.items() if s['inclusion_decision']=='纳入核心（暂定工作范围内）'}
    for row in read('f1_f2_comparison.csv'):
        expected=len(core) if row['level']=='source' else sum(u['source_id'] in core for u in segments)
        if row['dataset'].startswith('核心'):require(int(row['all_items_denominator'])==expected,'bad F1/F2 denominator','denominators')
    report=dict(executed_at=dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),
        status='passed' if not errors else 'failed',checks_by_category=dict(checks),errors=errors,
        sources=len(sources),units=len(segments),judgments=len(coding),
        human_review_completed=False,meaning_limit='脚本核对溯源及数据结构，不证明翻译语义和研究解释正确；人工复核仍待进行')
    (ROOT/'logs/validation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    if errors:raise SystemExit(1)


if __name__=='__main__':main()
