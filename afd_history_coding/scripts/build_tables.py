#!/usr/bin/env python3
"""Generate review tasks and descriptive tables from real coded units, preserving unresolved values."""
import csv
import itertools
import json
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def read(name):
    with (ROOT/name).open(encoding='utf-8',newline='') as handle:return list(csv.DictReader(handle))


def write(name,rows,fields=None):
    with (ROOT/name).open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields or list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    sources={r['source_id']:r for r in read('sources.csv')};units={r['unit_id']:r for r in read('segments.csv')}
    coding=read('coding.csv');codes=[r['code'] for r in read('inputs/active_codes.csv')]
    values={(r['unit_id'],r['code']):r['value'] for r in coding}
    core={sid for sid,row in sources.items() if row['inclusion_decision']=='纳入核心（暂定工作范围内）'}
    selected={u['source_id'] for u in units.values()}
    tables=[];categories=[];source_matrix=[];cooccurrence=[]
    for dataset,sids in [('核心_日期已核_暂定工作范围',core),('全部已编码_含日期待核补充',selected)]:
        uids=[uid for uid,u in units.items() if u['source_id'] in sids]
        source_values={}
        for sid in sorted(sids):
            matrix=dict(dataset=dataset,source_id=sid,independent_source_group=sources[sid]['duplicate_group'],
                selected_unit_count=sum(u['source_id']==sid for u in units.values()))
            for code in codes:
                vals=[values[uid,code] for uid in uids if units[uid]['source_id']==sid]
                status='1' if '1' in vals else '?' if '?' in vals else '' if '' in vals else '0'
                source_values[sid,code]=status;matrix[code]=status
            source_matrix.append(matrix)
        for code in codes:
            count=Counter(values[uid,code] for uid in uids)
            sc=Counter(source_values[sid,code] for sid in sids)
            resolved=count['1']+count['0'];resolved_sources=sc['1']+sc['0']
            tables.append(dict(dataset=dataset,code=code,independent_sources=len(sids),
                selected_units=len(uids),unit_1=count['1'],unit_0=count['0'],unit_question=count['?'],unit_blank=count[''],
                resolved_unit_denominator=resolved,share_1_among_resolved_units=round(count['1']/resolved,6) if resolved else '',
                source_1=sc['1'],source_0=sc['0'],source_question=sc['?'],resolved_source_denominator=resolved_sources))
        for level,items in [('unit',uids),('source',sorted(sids))]:
            groups=Counter()
            for item in items:
                first,second=(values[item,'F1'],values[item,'F2']) if level=='unit' else (source_values[item,'F1'],source_values[item,'F2'])
                label=('F1与F2都有' if first==second=='1' else '只有F1' if first=='1' and second=='0' else '只有F2' if first=='0' and second=='1' else 'F1与F2均无' if first==second=='0' else '至少一项待决／未处理')
                groups[label]+=1
            for label in ['只有F1','只有F2','F1与F2都有','F1与F2均无','至少一项待决／未处理']:
                categories.append(dict(dataset=dataset,level=level,category=label,count=groups[label],
                    all_items_denominator=len(items),resolved_items_denominator=len(items)-groups['至少一项待决／未处理'],
                    interpretation='同单位或同来源的码存在性；同来源共现不等于语义连接；单位多重编码与来源数分开'))
        for a,b in itertools.combinations(codes,2):
            resolved=[uid for uid in uids if values[uid,a] in ['0','1'] and values[uid,b] in ['0','1']]
            cooccurrence.append(dict(dataset=dataset,code_a=a,code_b=b,both_1_units=sum(values[uid,a]==values[uid,b]=='1' for uid in resolved),
                pair_resolved_unit_denominator=len(resolved),selected_units=len(uids),independent_sources=len(sids),
                note='同单元共现，只作样本描述；不直接解释为机制或总体比例'))
    write('code_distribution.csv',tables);write('f1_f2_comparison.csv',categories)
    write('source_code_matrix.csv',source_matrix);write('code_cooccurrence.csv',cooccurrence)
    questions=[];seen=set()
    def queue(scope,sid,uid,code,question,context,priority='P1'):
        key=(scope,sid,uid,code)
        if key in seen:return
        seen.add(key);questions.append(dict(review_id=f'Q{len(questions)+1:03}',review_scope=scope,priority=priority,
            source_id=sid,unit_id=uid,codes=code,question=question,context_to_check=context,
            required_action='对照原始德语及定位填写决定与理由；保留AI原值；规则改变时回溯同类单元',
            status='待人工复核',human_decision=''))
    queue('来源日期','S004','','','确认会议日期；不得沿用提案日期','S004原始HTML；PADOKA动态检索；8/5478议题对应的正式议程／会议记录','P0')
    queue('来源版本','S002','','','核对当前PDF与原定分析版本；上传日期不等于采纳日期','A001媒体库附件1977；S002印记；P_LV_1129只是4月采纳消息','P0')
    queue('研究范围','','','','有提纲时确认暂定工作范围及约6000字篇幅；当前未提供提纲','inputs/task_request.txt；2025-01-01至2026-09-06均为暂定','P2')
    queue('方法文献','M002','','','Grimmer与Stewart线索仍未读，不能加入实际使用参考文献','M002获取失败日志；可选补读，不阻碍已有Mayring支撑的初稿','P2')
    for row in coding:
        uid=row['unit_id'];sid=row['source_id'];code=row['code']
        context=f"{units[uid]['pdf_page_index'] or units[uid]['web_paragraph_locator']}；上下文：{row['context_unit_ids']}；德语证据：{row['german_evidence']}"
        if row['value']=='?':queue('全部疑问值',sid,uid,code,row['chinese_explanation'],context,'P0')
        if row['value']=='1' and code in ['H4','N1']:queue('新增代码适用',sid,uid,code,row['chinese_explanation'],context)
        if row['value']=='1' and ('推断' in row['expression_type'] or '上下文' in row['expression_type']):queue('上下文／推断',sid,uid,code,row['chinese_explanation'],context)
        if row['value']=='1' and code=='R1':queue('代表对象与资格',sid,uid,code,'检查其是否超出一般承诺，并核对代表对象是德国、东方、州居民、宗教还是党组织',context)
    # Coverage samples include every code and every selected source; these are planned human checks, not completed checks.
    for code in codes:
        sample=next((r for r in coding if r['code']==code and r['value']=='1'),next(r for r in coding if r['code']==code))
        queue('覆盖代码抽查',sample['source_id'],sample['unit_id'],code,'抽查定义、德语证据、中文译文及排除边界；不是独立编码者结果',sample['chinese_explanation'])
    for sid in sorted(selected):
        sample=next(u for u in units.values() if u['source_id']==sid)
        queue('覆盖来源与译文抽查',sid,sample['unit_id'],'全部代码／译文','核对完整德语意义单元、说话人、否定／反讽／引语与中文译文',sample['pdf_page_index'] or sample['web_paragraph_locator'])
    write('review_queue.csv',questions)
    pilot=read('pilot_coding.csv');pilot_units=read('pilot_segments.csv')
    heading=['# AI试编码表与修订记录','', '真实来源3份、材料类型3种、意义单元12个、初始代码10个、判断120项。S004会议日期未核，仅为探路补充，不能冒充已定年核心语料。全部为AI试编码，没有人类复核。','', '|unit_id|H1|H2|H3|F1|F2|I1|B1|T1|R1|A1|','|---|'+'---|'*10]
    pv={(r['unit_id'],r['code']):r['value'] for r in pilot}
    pc=['H1','H2','H3','F1','F2','I1','B1','T1','R1','A1']
    heading.extend('|'+u['unit_id']+'|'+'|'.join(pv[u['unit_id'],c] for c in pc)+'|' for u in pilot_units)
    heading+=['','原文、译文与每项理由见pilot_segments.csv、pilot_coding.csv。表中0为阅读后排除；?为保留疑问。',
        '', '修订：S002_U004战争纪念从H1移入新增H4；S004_U002的R1从1改0，举办纪念活动本身不足以明确代表资格。模糊革命、低估是否等于不公、产品名Stolz是否等于自豪等疑问保留。补完分页后新增N1并回查既有单元；完整版本记录见codebook.md。AI反复检查不是独立编码者一致性检验。']
    (ROOT/'pilot_report.md').write_text('\n'.join(heading)+'\n',encoding='utf-8')
    summary=dict(candidate_records=len(sources),discovered_post_candidates=sum(k.startswith('P_') for k in sources),
        core_sources=len(core),supplementary_sources=len(selected-core),all_coded_sources=len(selected),
        core_units=sum(u['source_id'] in core for u in units.values()),supplementary_units=sum(u['source_id'] not in core for u in units.values()),
        all_units=len(units),codes=len(codes),judgments=len(coding),questions=sum(r['value']=='?' for r in coding),
        blank_judgments=sum(r['value']=='' for r in coding),review_tasks=len(questions),human_review_completed=0,
        search_requests=len((ROOT/'logs/directional_searches.jsonl').read_text().splitlines()),
        codebook_version='v0.3',working_time_window='暂定工作范围：2025-01-01至2026-09-06')
    (ROOT/'logs/analysis_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':main()
