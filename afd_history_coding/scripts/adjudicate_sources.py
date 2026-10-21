#!/usr/bin/env python3
"""Persist source-level decisions and their verification evidence; dates are never parsed from filenames."""
import csv
import hashlib
import json
from pathlib import Path
from lxml import html

ROOT=Path(__file__).resolve().parents[1]


def main():
    with (ROOT/'sources.csv').open(encoding='utf-8',newline='') as handle:
        reader=csv.DictReader(handle);fields=reader.fieldnames;rows=list(reader)
    sources={r['source_id']:r for r in rows}
    units=list(csv.DictReader((ROOT/'segments.csv').open(encoding='utf-8',newline='')))
    selected={r['source_id'] for r in units}
    aux={}
    for record in map(json.loads,(ROOT/'logs/auxiliary_fetches.jsonl').read_text(encoding='utf-8').splitlines()):aux[record['auxiliary_id']]=record
    for sid,record in aux.items():
        row={f:'' for f in fields}
        row.update(source_id=sid,candidate_role='方法文献版本' if sid.startswith('M') else '来源核验辅助资料／检索入口',
            title={'A001':'官方WordPress媒体库：执政纲领附件元数据','A002':'州议会站内deutschdenken查询返回页（无可解析结果）',
                'A003':'Transparenzerklärung: LV – Regierungsprogramm LTW26','A004':'党团官网最新文章API记录（均晚于暂定时间窗）',
                'A005':'党团官网1953无日期过滤查询（空列表）','A006':'PADOKA文献检索界面','A007':'党团官网2026-09-06以前文章查询（空列表）',
                'M003':'Mayring 2019 英文全文浏览容器（非独立论文）','M004':'Mayring 2019 英文HTML全文'}[sid],
            title_verification='已查看返回内容',author_or_institution='Philipp Mayring' if sid.startswith('M') else '原始站点发布机构，见网址及所存内容',
            author_verification='M004文首作者已核' if sid.startswith('M') else '原始官方站点核验资料',
            material_type='学术论文全文／浏览容器' if sid.startswith('M') else '元数据／公开声明／检索页面',type_verification='已核',
            original_url=record['url'],final_url=record.get('final_url',''),retrieval_attempted_at=record['attempted_at'],
            retrieved_at=record['attempted_at'] if record['status']=='downloaded' else '',local_filename=record.get('raw_path',''),
            sha256=record.get('sha256',''),readability='可读取；容器M003仅有iframe链接' if record['status']=='downloaded' else '无法获取',
            retrieval_status=record['status'],error=record['error'],inclusion_decision='方法背景，非党派语料' if sid.startswith('M') else '排除核心语料：辅助核验资料／入口',
            inclusion_or_exclusion_reason='同一论文不同呈现，不能作为多份独立方法文献' if sid.startswith('M') else '用于查元数据或检索能力，不是独立党派政治自我表达文本',
            duplicate_group='DG_MAYRING_2019' if sid.startswith('M') else f'DG_{sid}',duplicate_verification='同一论文已核' if sid.startswith('M') else '独立核验对象，非核心计数',
            source_provenance='logs/auxiliary_fetches.jsonl',search_id=f'AUX_{sid}',search_date=record['attempted_at'][:10],
            search_expression='直接打开实际发现的链接／官方API元数据接口',site=record['url'].split('/')[2],
            working_time_window='2025-01-01至2026-09-06（核心语料）；方法文献不受此限',scope_status='暂定工作范围')
        if sid=='M004':
            row.update(website_publication_date='2019-09-26',publication_date_basis='M001论文落地页Published；M004文首Volume 20 No.3 Art.16，2019年9月',
                metadata_status='全文已阅读：§1—30；作者、题名、期刊、年份、文章号及DOI已核',clean_filename='clean/M004.txt')
        sources[sid]=row
    for sid in ['S001','S005','S006','S007']:
        row=sources[sid]
        tree=html.fromstring((ROOT/row['local_filename']).read_bytes())
        row.update(title=' '.join(tree.xpath('string(//title)').split()),title_verification='已核网页title',
            inclusion_decision='排除核心语料：检索入口',inclusion_or_exclusion_reason='入口不计独立党派文本；所发现的PDF／文章另建来源',
            duplicate_group=f'DG_{sid}',duplicate_verification='入口不作语料计数',metadata_status='入口可访问，未将其中聚合／导航内容编码')
    sources['S002'].update(title='Das Land zuerst. Regierungsprogramm der AfD Sachsen-Anhalt zur Landtagswahl 2026',
        title_verification='PDF封面（PDF页序1）',author_or_institution='AfD Landesverband Sachsen-Anhalt',
        author_verification='PDF页序257 Impressum及258出版／政治广告说明；V.i.S.d.P.不是唯一作者',
        speaker='机构文本，不适用单一发言人',speaker_verification='已核',material_type='州党2026执政／竞选纲领',type_verification='PDF封面已核',
        document_date='',website_publication_date='2026-07-23',publication_date_basis='A001官方媒体库：附件id=1977，date=2026-07-23T20:50:23，source_url与所下载PDF完全一致；这是附件发布记录，不是从URL推日期，不是纲领采纳日期',
        inclusion_decision='纳入核心（暂定工作范围内）',inclusion_or_exclusion_reason='州党公开自我表达；附件公开日期在暂定时间窗；含长时段文化、DDR、战争记忆及反例段',
        duplicate_group='DG_S002',duplicate_verification='本轮只编码当前完整PDF，未把摘要、音频或上传缩略图另算独立来源',
        metadata_status='题名、机构、附件日期已核；PDF本身无明确落款日期',
        version='媒体库附件1977；本次获取SHA-256见sha256栏；258页',version_verification='已核附件date及modified均为2026-07-23T20:50:23；不能证明URL下字节从未被替换',
        notes='与S003/S004属于同一deutschdenken议题系列，但不是同一讲话转载；P_LV_1129为4月采纳消息，不能据此认定4月稿与本PDF完全相同。编码为定向段落样本，不是整份258页逐句穷尽。')
    sources['S003'].update(title='#deutschdenken - Ein neues Markenzeichen für Sachsen-Anhalt',title_verification='PDF页序1标题',
        author_or_institution='Fraktion AfD im Landtag von Sachsen-Anhalt',author_verification='PDF页序1 Fraktion AfD；页序4 Oliver Kirchner，Fraktionsvorsitz',
        speaker='机构提案；落款Oliver Kirchner',speaker_verification='已核',material_type='议会提案（Antrag）及理由（Begründung）',type_verification='PDF页序1明确Antrag',
        document_date='2025-05-06',website_publication_date='',publication_date_basis='文件落款06.05.2025；文件分发标记Ausgegeben am 07.05.2025；网页发布日期未单独查得',
        inclusion_decision='纳入核心（暂定工作范围内）',inclusion_or_exclusion_reason='文件日期在暂定时间窗；AfD党团公开提案；包含具体历史资源与认同政策',
        duplicate_group='DG_S003',duplicate_verification='与S004共享议题与部分措辞；提案与发言为不同文类和表达，不按同一讲话转载处理；解释时不将其当独立事件验证',
        metadata_status='提案号8/5478、作者、文件日期、分发日期及4页全文已核',version='官方四页PDF，本次获取SHA-256见sha256栏',version_verification='原PDF已存档',
        notes='只证明提出了议案，不证明通过、实施或产生效果。第4页原文beigetraten拼写已与页面图像核对，未擅改。')
    sources['S004'].update(title='#deutschdenken - Ein neues Markenzeichen für Sachsen-Anhalt，TOP 7议会发言及问答',
        title_verification='网页transcript-wrapper标题与Antrag Fraktion AfD – Drs.8/5478',author_or_institution='发布：Landtag Sachsen-Anhalt；分析：AfD议员自我表达',
        author_verification='官方议会转写，发言者标签明确',speaker='Dr. Hans-Thomas Tillschneider (AfD)',speaker_verification='原网页P007等发言人标签，非URL参数猜测',
        material_type='议会发言及问答；非全体辩论混合语料',type_verification='官方转写及角色标签已核',document_date='',website_publication_date='',
        publication_date_basis='页面未提供可核日期；与8/5478有明确议题联系，但不能据提案日期替代发言日期；A002检索页无可解析结果，A006为动态检索界面',
        inclusion_decision='补充试编码（会议日期待核，不计核心分母）',inclusion_or_exclusion_reason='可确定AfD发言者及正文；时间窗归属尚不能核验，保留探路细读与译文但与已定年核心分开',
        duplicate_group='DG_S004',duplicate_verification='同页全部问答为同一来源，不按发言段数或问答次数增加独立文本数',
        metadata_status='发言者、角色与议题已核；会议日期待核',version='获取日官方网页转写；见SHA-256',version_verification='本次原始HTML及123个正文／角色段落已保留',
        notes='只编码Hans-Thomas Tillschneider的选定主张。主席、其他党派及插话仅保留为上下文；尚未核验会议日期，不能在论文写成已纳入时间窗核心文本。')
    discoveries=json.loads((ROOT/'inputs/discovered_posts.json').read_text(encoding='utf-8'))
    duplicate_hashes={}
    for sid,entry in discoveries.items():
        text=' '.join(html.fromstring('<div>'+entry['post']['content']['rendered']+'</div>').text_content().split())
        digest=hashlib.sha256(text.encode()).hexdigest();duplicate_hashes[sid]=digest
    speakers={'P_LV_1129':'Martin Reichardt','P_LV_1235':'Martin Reichardt | Ulrich Siegmund','P_LV_1342':'Martin Reichardt',
        'P_LV_2306':'Dr. Hans-Thomas Tillschneider | Martin Reichardt','P_LV_2381':'Martin Reichardt','P_LV_2446':'Martin Reichardt | Oliver Kirchner',
        'P_LV_2731':'Martin Reichardt','P_LV_2855':'Martin Reichardt','P_LV_1227':'Dr. Hans-Thomas Tillschneider（署名文章）',
        'P_LV_1203':'Dr. Hans-Thomas Tillschneider','P_LV_1132':'Dr. Hans-Thomas Tillschneider','P_LV_725':'Dr. Hans-Thomas Tillschneider',
        'P_LV_682':'Dr. Hans-Thomas Tillschneider','P_LV_679':'Martin Reichardt','P_LV_432':'未列个人署名，州党机构文本',
        'P_LV_1218':'Dr. Hans-Thomas Tillschneider','P_LV_1290':'Dr. Hans-Thomas Tillschneider | Martin Reichardt'}
    for sid,entry in discoveries.items():
        row=sources[sid];post=entry['post']
        row.update(author_or_institution='AfD Landesverband Sachsen-Anhalt',author_verification='州党官方域名／网站品牌与官方API发布记录；具体引语发言者另列',
            duplicate_group=f'DG_API_{duplicate_hashes[sid][:16]}',duplicate_verification='按官方API全文纯文本SHA-256进行精确重复检查；近似改写不自动视为独立事件',
            version=post['modified'],version_verification='官方API modified；本次内容版本，不保证自原发布日起未修订')
        if sid in selected:
            row.update(material_type='署名政治评论' if sid=='P_LV_1227' else '州党新闻稿／机构声明',type_verification='已阅读全文及署名／引语结构',
                speaker=speakers[sid],speaker_verification='逐条核对正文Dazu erklärt、补充发言或gez.署名；未署名则不虚构姓名',
                inclusion_decision='纳入核心（暂定工作范围内）',inclusion_or_exclusion_reason='日期在暂定时间窗；含研究问题相关历史／身份／记忆策略，或作为不满、自豪、代表、行动但无历史连接的对照',
                metadata_status='官方API题名、date、modified、链接及完整正文已核；日期是网站发布日，不等同文中事件日',
                notes='编码单位是明确登记的主张段；不把民调、暴力归责或历史引语归属作为已独立核实的事实。检索到的党派公开表达，不代表选民实际接受。')
        elif post['title']['rendered'].startswith('Transparenzerklärung'):
            row.update(material_type='政治广告透明度／合规披露',type_verification='官方API完整正文含EU2024/900、赞助者、金额或投放期等法定字段',
                inclusion_decision='排除核心：合规元数据文类',inclusion_or_exclusion_reason='检索命中主要来自行政披露与地名／wurde等字形；不将法律格式、地址中的Lutherstadt或广告日期当历史动员文本；若附有真实广告正文需另建候选，本轮未据投放名称推断其内容',
                metadata_status='可读全文及文类已核；未做政治叙事赋码',notes='按文类排除，不是因为没有F1/F2而排除；保留所有记录及原API存档。')
        else:
            row.update(inclusion_decision='本轮未纳入：待进一步全文筛选／补充对照',inclusion_or_exclusion_reason='定向目的性样本未穷尽所有同类政策与选举消息；未纳入不等于判定没有历史内容。P_LV_1224及811已读但本轮未取样，其余需继续读全文',
                metadata_status='API日期／标题／全文已存；尚未完成研究问题导向语义筛选',notes='保留候选，不把未处理记为0，不纳入编码分母。')
    sources['M001'].update(title='Qualitative Content Analysis: Demarcation, Varieties, Developments',title_verification='落地页及M004全文文首',
        author_or_institution='Philipp Mayring',author_verification='文首／作者栏',website_publication_date='2019-09-26',publication_date_basis='落地页Published 2019-09-26；全文2019年9月，Vol.20 No.3 Art.16',
        inclusion_decision='实际使用的方法参考文献（全文见M004）',inclusion_or_exclusion_reason='已读全文§1—30；用于规则、锚例、边界、试用修订和单位定义；非AfD语料',
        duplicate_group='DG_MAYRING_2019',duplicate_verification='M001摘要／元数据、M003容器、M004全文为同一论文',metadata_status='作者、年份、题名、期刊、文章号及DOI已核，非仅凭用户线索引用')
    sources['M002'].update(inclusion_decision='方法线索待核验，未作实际使用参考文献',inclusion_or_exclusion_reason='DOI访问遭代理拒绝，未取得正文或核验出版信息；不虚构页码、引文或阅读状态',duplicate_group='DG_M002',duplicate_verification='尚未取得正文')
    with (ROOT/'sources.csv').open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(sources[sid] for sid in sorted(sources))
    coverage=[]
    for sid in sorted(selected):
        subset=[u for u in units if u['source_id']==sid]
        coverage.append(dict(source_id=sid,inclusion_status=sources[sid]['inclusion_decision'],
            selected_units=len(subset),selected_unit_ids='|'.join(u['unit_id'] for u in subset),
            coded_coverage='选定意义单元全部逐码完成AI初编；不是长文逐句穷尽',
            original_context=sources[sid]['clean_filename'],
            limitation='全文已提取并作历史词定位；深读相关章节及反例页，其他258页内容未作穷尽语义编码' if sid=='S002' else '选定主张及相关上下文；来源全文另存'))
    with (ROOT/'selection_audit.csv').open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(coverage[0]));writer.writeheader();writer.writerows(coverage)
    print(json.dumps(dict(candidate_records=len(sources),core_sources=sum('纳入核心（' in r['inclusion_decision'] for r in sources.values()),
        supplementary_sources=sum('补充试编码' in r['inclusion_decision'] for r in sources.values()),
        legal_disclosures_excluded=sum(r['inclusion_decision']=='排除核心：合规元数据文类' for r in sources.values()),
        pending_posts=sum(r['inclusion_decision'].startswith('本轮未纳入') for r in sources.values())),ensure_ascii=False))


if __name__=='__main__':main()
