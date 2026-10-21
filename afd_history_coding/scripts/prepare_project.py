#!/usr/bin/env python3
"""Create the recorded inputs and empty analysis schemas without overwriting research data."""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
WINDOW = '2025-01-01至2026-09-06'


def csv_if_missing(name, fields, rows=()):
    target = ROOT / name
    if target.exists():
        return
    with target.open('x', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    now = dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo('Asia/Shanghai')).isoformat()
    definitions = [
        ('S001', '检索入口', '州党竞选材料入口（网页题名待核验）', 'AfD萨克森—安哈尔特州党部（用户提供的机构线索）', '网页入口候选', 'https://afd-lsa.de/landtagswahl/', ''),
        ('S002', '核心语料候选', '2026年州党纲领候选PDF（正式题名待核验）', 'AfD萨克森—安哈尔特州党部（用户提供的机构线索）', '竞选／执政纲领候选', 'https://afd-lsa.de/wp-content/uploads/2026/07/AfD_Sachsen-Anhalt_Regierungsprogramm_2026_230726-web.pdf', ''),
        ('S003', '核心语料候选', '#deutschdenken - Ein neues Markenzeichen für Sachsen-Anhalt（用户提供的题名线索）', 'AfD州议会党团（提案作者待核验）', '议会提案候选，不能视为已通过政策', 'https://padoka.landtag.sachsen-anhalt.de/files/drs/wp8/drs/d5478aan.pdf', '8/5478（用户线索，待核验）'),
        ('S004', '核心语料候选', '相关议会发言入口（题名与议题待核验）', '萨克森—安哈尔特州议会（发布平台，发言者待核验）', '议会发言转写候选', 'https://www.landtag.sachsen-anhalt.de/plenarsitzungen/transkript?cHash=fb7e15cdb97fc01656004283a0cd0ea5&tx_lsasessions_transcript%5Bspeaker%5D=16437', ''),
        ('S005', '检索入口', '州议会文献入口（网页题名待核验）', '萨克森—安哈尔特州议会（用户提供的机构线索）', '文献检索入口候选', 'https://www.landtag.sachsen-anhalt.de/dokumente/neue-doku', ''),
        ('S006', '检索入口', '州党官网入口（网页题名待核验）', 'AfD萨克森—安哈尔特州党部（用户提供的机构线索）', '官网入口候选', 'https://afd-lsa.de/', ''),
        ('S007', '检索入口', '州议会党团官网入口（网页题名待核验）', 'AfD萨克森—安哈尔特州议会党团（用户提供的机构线索）', '官网入口候选', 'https://afdfraktion-lsa.de/', ''),
        ('M001', '方法文献线索，非核心语料', 'Qualitative Content Analysis: Demarcation, Varieties, Developments（用户线索，待核验）', 'Mayring，2019（用户线索，未核验）', '学术论文候选', 'https://www.qualitative-research.net/index.php/fqs/article/view/3343', ''),
        ('M002', '方法文献线索，非核心语料', 'Text as Data: The Promise and Pitfalls of Automatic Content Analysis Methods for Political Texts（用户线索，待核验）', 'Grimmer与Stewart，2013（用户线索，未核验）', '学术论文候选', 'https://doi.org/10.1093/pan/mps028', ''),
    ]
    candidates = []
    for sid, role, title, author, kind, url, number in definitions:
        candidates.append({
            'source_id': sid, 'candidate_role': role, 'title': title,
            'title_verification': '未核验，仅为用户提供的线索或入口标签',
            'author_or_institution': author, 'author_verification': '未核验',
            'speaker': '', 'speaker_verification': '未核验',
            'material_type': kind, 'type_verification': '未核验',
            'document_date': '', 'website_publication_date': '', 'publication_date_basis': '',
            'original_url': url, 'retrieved_at': '', 'local_filename': '', 'clean_filename': '',
            'inclusion_decision': '入口不作为独立文本' if role == '检索入口' else '待原文核验，未纳入',
            'inclusion_or_exclusion_reason': '此条为查找材料的入口；不能计为独立自我表达文本' if role == '检索入口' else ('学术方法资料，与党派自我表达语料分开；未核验前不作实际使用参考文献' if sid.startswith('M') else '作者、日期、版本及正文均需核验；不能凭用户描述、URL或文件名纳入'),
            'duplicate_group': '', 'duplicate_verification': '无正文，尚未比较；不同URL不代表独立来源',
            'metadata_status': '未核验', 'version': '', 'version_verification': '未核验',
            'document_number_clue': number,
            'source_provenance': 'inputs/task_request.txt；不是已获取原文',
            'search_id': f'DIRECT_{sid}', 'search_expression': '直接打开用户提供的入口；未执行站内主题检索',
            'site': urlsplit(url).hostname, 'working_time_window': WINDOW if sid.startswith('S') else '方法文献不适用语料时间窗',
            'scope_status': '暂定工作范围',
            'notes': '不得从网址路径或文件名推断发布日期；获取失败不能判定不存在、无相关内容或不在时间窗',
        })
    candidate_file = ROOT / 'inputs/source_candidates.json'
    if not candidate_file.exists():
        candidate_file.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    csv_if_missing('segments.csv', [
        'source_id', 'unit_id', 'section', 'printed_page', 'pdf_page_index',
        'web_paragraph_locator', 'german_original', 'chinese_translation',
        'context_unit_ids', 'context_relation', 'speaker', 'speaker_role',
        'speaker_stance', 'source_version', 'translation_status', 'translation_by',
        'quotation_verification', 'analysis_selection_reason', 'segment_status',
    ])
    csv_if_missing('coding.csv', [
        'source_id', 'unit_id', 'code', 'value', 'german_evidence',
        'chinese_explanation', 'decision_reason', 'subtype', 'group_referent',
        'boundary_target', 'historical_event', 'speaker', 'speaker_stance',
        'expression_type', 'context_unit_ids', 'context_link_reason',
        'codebook_version', 'coder', 'coding_status', 'human_review_status',
        'original_ai_value', 'human_value', 'revision_reason', 'coded_at',
    ])
    active_codes = [
        ('H1', '长时段历史人物与文化资源'), ('H2', 'DDR统治与反抗经验'),
        ('H3', '统一后转型记忆'), ('F1', '不公待遇或象征贬损'),
        ('F2', '贡献、尊严、自豪或优越性'), ('I1', '内群体建构'),
        ('B1', '责任归属或他者划界'), ('T1', '历史与当下连接'),
        ('R1', '政党代表资格'), ('A1', '政治行动号召'),
    ]
    csv_if_missing('inputs/active_codes.csv', ['code', 'name', 'codebook_version', 'empirical_status'],
        [dict(code=k, name=v, codebook_version='v0.1-prepilot', empirical_status='初始理论规则；未进行真实材料试编码') for k, v in active_codes])
    requests = [
        ('S001', '来源', '', '取得入口页面后定位独立竞选文本，不把入口计为语料', '先核验原始网址、机构和站内链接；暂不能作语义判断'),
        ('S002', '来源', '', '核验正式标题、作者、落款日期、网站发布日期及全文版本', '核对封面和版权／落款页；逐页检查历史内容，不能从文件名读出日期'),
        ('S003', '来源', '', '核验提案号8/5478、提案人、日期、正文及理由', '查原始PDF每页；另查议程和表决记录，不能将提案写成政策'),
        ('S004', '来源', '', '核验发言人、党籍、会议日期、议题和段落边界', '区分AfD正文、主席发言、他党插话、引语与被否定立场；speaker参数不是已核验姓名'),
        ('S005', '来源', '', '取得议会检索页面并核查发言与提案的来源关系', '相同讲话的转写／视频／转载应同组，不能按URL重复计数'),
        ('S006', '来源', '', '取得州党站点并执行定向检索', '保留只有自豪、只有不满、二者兼有及二者皆无的候选；核验日期'),
        ('S007', '来源', '', '取得党团站点并执行定向检索', '核验机构、日期和全文；保留无历史—当下连接的反例候选'),
        ('M001', '方法文献', '', '实际阅读全文，核验作者、年份、题名、期刊及DOI', 'DOI线索10.17169/fqs-20.3.3343；当前不能写作已使用参考文献'),
        ('M002', '方法文献', '', '实际阅读可获取内容，核验作者、年份、题名与出处', 'DOI线索10.1093/pan/mps028；当前不能据此补写页码或直接引文'),
        ('', '规则', 'H1|F2|I1', '人物提及与自豪、内群体建构之间的区分需真实材料试验', 'codebook.md对应条目；示例均为虚构，不是已赋码单元'),
        ('', '规则', 'F1|F2|T1|R1', '同文档共现是否真正连接、群体指向是否一致，需要逐段核对', '跨段链接必须给实际unit_id；不能把散落证据拼成完整叙事链'),
        ('', '候选新代码', 'H4（未启用）', '是否增设战争、国家暴力与灾难记忆历史类型', '此建议来自任务的覆盖要求，不是材料归纳结果；待原文决定拆分、合并或放弃'),
        ('', '研究范围', '', '有提纲时核验时间窗、篇幅与任务分工；当前默认继续', '目前只读到任务说明，2025-01-01至2026-09-06均须标注暂定工作范围'),
        ('', '试编码与人工复核', '全部代码', '原文到位后选择约10—15个意义单元，尽量涵盖三种材料类型', '随后将全部?、新代码、较强推断及覆盖各代码／类型的抽样单元加入复核队列；目前没有可供人工复核的实证编码'),
    ]
    csv_if_missing('review_queue.csv', [
        'review_id', 'review_scope', 'priority', 'source_id', 'unit_id', 'codes',
        'question', 'context_to_check', 'required_action', 'status', 'human_decision',
    ], [dict(review_id=f'Q{i:03}', review_scope=scope,
             priority='P0' if sid else 'P1', source_id=sid, unit_id='', codes=codes,
             question=q, context_to_check=context,
             required_action='先恢复访问或提供原文后对照核验' if sid else '保留为待原文／待人工判断的事项',
             status='待办；非已完成编码复核', human_decision='')
        for i, (sid, scope, codes, q, context) in enumerate(requests, 1)])
    csv_if_missing('inventory.csv', ['item_id', 'filename_or_item', 'material_nature', 'readable', 'is_primary_corpus', 'missing_or_limitation'], [
        dict(item_id='I001', filename_or_item='inputs/task_request.txt（原上传文件名：已粘贴的文本.txt）', material_nature='用户任务说明，唯一已提供的研究文件；本地副本不另算一份材料', readable='是，全文读取', is_primary_corpus='否', missing_or_limitation='包含网址和方法文献线索，但没有德语原文'),
        dict(item_id='I002', filename_or_item='论文提纲（未提供）', material_nature='预期研究设计文件', readable='不存在于本任务可访问文件', is_primary_corpus='否', missing_or_limitation='不能访问其他对话；按任务说明使用暂定工作范围'),
        dict(item_id='I003', filename_or_item='既有德语语料／既有编码表（未提供）', material_nature='预期试编码输入', readable='不存在于本任务可访问文件', is_primary_corpus='尚无', missing_or_limitation='没有可先行试编码的现有原文'),
        dict(item_id='I004', filename_or_item='/workspace/Deutsch（研究开始前）', material_nature='已有Git仓库：main含初始空提交', readable='是；研究开始前无已跟踪项目文件', is_primary_corpus='否', missing_or_limitation='未发现研究提纲、参考文献或原始材料'),
    ])
    groups = [
        ('长时段与文化贡献', 'Otto OR Heinrich OR Luther OR Bismarck OR Geschichte'),
        ('DDR与反抗', 'DDR OR "1953" OR "17. Juni" OR "1989" OR "friedliche Revolution"'),
        ('统一与转型', 'Wende OR Wiedervereinigung OR Treuhand OR Transformation'),
        ('纪念与其他历史', 'Erinnerung OR Gedenken OR Jahrestag OR Krieg OR Nationalsozialismus'),
        ('评价与共同体补充', 'Heimat OR Anerkennung OR Würde OR Stolz OR Leistung OR Ostdeutschland OR Ostdeutsche OR Sachsen-Anhalt'),
    ]
    query_rows = []
    sites = ['afd-lsa.de', 'afdfraktion-lsa.de', 'www.landtag.sachsen-anhalt.de', 'padoka.landtag.sachsen-anhalt.de']
    for site in sites:
        for label, terms in groups:
            query_rows.append(dict(query_id=f'PLAN{len(query_rows)+1:03}', site=site,
                scope_status='暂定工作范围', time_window=WINDOW, topic=label,
                search_expression=f'site:{site} ({terms})', execution_status='计划，未执行：原始站点连接受阻',
                search_date='', results_count='', note='实际检索时记录所用引擎或站内检索、检索日期和命中项；不能将该计划写成已完成检索'))
    csv_if_missing('search_queries.csv', ['query_id', 'site', 'scope_status', 'time_window', 'topic', 'search_expression', 'execution_status', 'search_date', 'results_count', 'note'], query_rows)
    request_path = ROOT / 'inputs/task_request.txt'
    with (ROOT / 'logs/process_runs.jsonl').open('a', encoding='utf-8') as handle:
        handle.write(json.dumps({'script': 'prepare_project.py', 'executed_at': now,
            'input_sha256': hashlib.sha256(request_path.read_bytes()).hexdigest(),
            'new_candidate_definitions': len(candidates), 'empirical_segments_created': 0,
            'code_judgments_created': 0}, ensure_ascii=False) + '\n')
    print(json.dumps({'candidate_urls': len(candidates), 'empirical_segments': 0, 'coding_judgments': 0,
        'review_tasks': len(requests), 'planned_searches_not_executed': len(query_rows)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
