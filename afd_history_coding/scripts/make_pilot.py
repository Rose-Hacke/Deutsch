#!/usr/bin/env python3
"""Record an AI semantic pilot. Decisions below were made by reading German originals, not keyword rules."""
import csv
import datetime as dt
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CODES = ['H1','H2','H3','F1','F2','I1','B1','T1','R1','A1']
ZERO = {
    'H1':'没有具体调用长时段历史人物、事件或文化资源；不能把地点名或一般政策当历史调用',
    'H2':'没有明确DDR、1953年、1989年或可确认的DDR经验；不从笼统革命推定事件',
    'H3':'没有明确统一后转型回溯；不能从今日问题推定统一史',
    'F1':'没有由发言者肯定的不公平待遇、贬损或承认不足主张；一般批评或负面情况不自动符合',
    'F2':'没有明确肯定群体贡献、尊严、自豪或优越性；提到历史人物不自动符合',
    'I1':'没有明确构造共享身份的内群体；地名、党派程序中的wir不自动符合',
    'B1':'没有明确归责或划分对立群体；出现机构或人物名称不自动符合',
    'T1':'没有把过去与当下作可指认的类比、连续性、继承或对照连接',
    'R1':'没有明确AfD维护／继承／代表某群体的资格主张；党名和一般承诺不自动符合',
    'A1':'没有面向公众的参与、投票、加入或传播等要求；政府政策承诺不自动符合',
}


def normalized(text):
    text = re.sub(r'(?<=\w)\s*-\s*\n\s*(?=[a-zäöüß])','',text)
    return re.sub(r'\s+',' ',text.replace('\u00ad','')).strip()


def pdf(sid, pages, start, end):
    records=json.loads((ROOT/f'clean/{sid}_located.json').read_text(encoding='utf-8'))['records']
    raw='\n'.join(records[p-1]['text'] for p in pages)
    lines=[]
    for line in raw.splitlines():
        stripped=line.strip()
        if re.fullmatch(r'\d+',stripped):continue
        if re.fullmatch(r'\(Ausgegeben am \d{2}\.\d{2}\.\d{4}\)',stripped):continue
        if re.fullmatch(r'(?:[IVX]+\.\s+[A-ZÄÖÜẞ\s]+|PRÄAMBEL)\s*\d*',stripped):continue
        lines.append(line)
    text=normalized('\n'.join(lines))
    left=text.index(start); right=text.index(end,left)+len(end)
    return text[left:right],f"PDF:{','.join(map(str,pages))}",str(pages[0]),'pdf'


def web(sid, locators):
    records=json.loads((ROOT/f'clean/{sid}_located.json').read_text(encoding='utf-8'))['records']
    selected=[r['text'] for r in records if r['locator'] in locators]
    assert len(selected)==len(locators)
    return '\n\n'.join(selected),','.join(locators),'','web'


def main():
    # Each entry explicitly represents review of all ten initial codes. Unlisted codes are read-and-rejected, not unprocessed.
    units=[]
    def add(sid, num, selection, cn, topic, ones, questions=None, contexts='', stance='作者／发言者肯定立场'):
        text,locator,page,kind=selection
        units.append(dict(source_id=sid,unit_id=f'{sid}_U{num:03}',section=topic,
            printed_page=page,pdf_page_index=locator.removeprefix('PDF:') if kind=='pdf' else '',
            web_paragraph_locator=locator if kind=='web' else '',german_original=text,chinese_translation=cn,
            context_unit_ids=contexts,context_relation='同一论证段落或相邻段；仅在编码行明确说明时用于判断',
            speaker='Dr. Hans-Thomas Tillschneider' if sid=='S004' else ('Fraktion AfD' if sid=='S003' else 'AfD Landesverband Sachsen-Anhalt'),
            speaker_role='AfD发言者／机构',speaker_stance=stance,source_version='本次获取版；见sources.csv原始文件SHA-256',
            translation_status='AI逐句对照德语，待人工复核',translation_by='AI辅助译文（待研究者审订，非已有人工作业）',
            quotation_verification='AI对照已存文字层／网页段落；无OCR；PDF另作图像抽查',
            analysis_selection_reason='试编码：覆盖清晰、边界及可能反例',segment_status='AI试编码，非人工复核',
            ones=ones,questions=questions or {},reviewed_codes=CODES,topic=topic))

    add('S002',1,pdf('S002',[3],'Wir sind schon sehr unerzogene Bürger','sich ein anderes Volk wählen.'),
        '我们可真是一群不守规矩、忘恩负义、要求多又难应付的公民。布莱希特在1953年6月17日民主德国民众起义遭镇压之际，不是曾如此贴切地表述吗？老牌政党摊上我们可真不走运。我们失去了它们的信任。老牌政党最好把我们解散，另选一个人民。',
        '序言：1953年与当下的反讽类比',
        {'H2':('Volksaufstandes in der DDR am 17. Juni 1953','明确指出DDR民众起义及具体日期，历史事件并非由关键词猜测'),
         'F1':('Es wäre besser, die Altparteien würden uns auflösen und sich ein anderes Volk wählen.','以反讽批评政党排斥不顺从的人民，不是支持解散人民；政治排斥／代表关系倒置'),
         'I1':('Wir sind schon sehr unerzogene Bürger','以反讽的我们公民建构与老牌政党相对的共同体；不限定为东部人'),
         'B1':('Die Altparteien haben es schlecht mit uns erwischt.','把当下老牌政党放到对立一侧；需结合反讽识别立场'),
         'T1':('Wie hat es nicht Bertolt Brecht anlässlich der Niederschlagung','用1953年的布莱希特典故转述当下政党与人民关系；属于类比，不验证当代等同DDR')},
         stance='反讽批评老牌政党；所述解散人民不是作者支持的行动')
    add('S002',2,pdf('S002',[55],'Die AfD-Sachsen-Anhalt wird diese Identitätsstörung','selbstbewusste deutsche Identität fördern.'),
        '萨克森—安哈尔特州AfD将以新的爱国文化政策治愈这种身份认同障碍。文化政策必须把自信还给德国人。我们将通过有针对性的措施及对德国历史积极方面的援引，促进一种不拘束且以健康方式拥有自信的德国认同。',
        '文化导言：AfD作为身份修复者',
        {'F2':('Selbstbewusstsein zurückgeben','明确要求恢复德国人的自信；子类型为尊严／自信的规范目标，不是已实现自豪'),
         'I1':('den Deutschen ihr Selbstbewusstsein','明确以德国人为认同对象；不能改写成东部德国人'),
         'T1':('Bezugnahmen auf die guten Seiten der deutschen Geschichte','把对历史积极方面的援引作为当下身份政策手段'),
         'R1':('Die AfD-Sachsen-Anhalt wird diese Identitätsstörung','党自称能治愈集体认同障碍，并归还德国人自信；超过一般行政政策承诺')},
        {'F1':('diese Identitätsstörung','身份障碍或自信不足不当然等于不公待遇；需与前文归责及象征贬损论述共同复核')})
    add('S002',3,pdf('S002',[56],'Die AfD Sachsen-Anhalt setzt dem eine deutschdenken-Kampagne','Noch viel mehr ließe sich erwähnen.'),
        '萨克森—安哈尔特州AfD以“deutschdenken”运动与之相对，指出该州为德意志民族的发展作出了重要贡献。从亨利一世、奥托一世，经路德，到俾斯麦和尼采：决定性地塑造德国的人物来自萨克森—安哈尔特。今天萨克森—安哈尔特所在的地区在中世纪是德意志帝国的中心。德语最古老的文献《梅泽堡咒语》也出自该州。还可以列举更多。',
        'deutschdenken：地方历史贡献与国家身份',
        {'H1':('Von Heinrich I. und Otto I. über Luther bis hin zu Bismarck und Nietzsche','明确列举长时段人物及文化文本，并叙述地方与国家历史关系；历史断言作为党派主张记录'),
         'F2':('Sachsen-Anhalt Wesentliches zur Entwicklung der deutschen Nation beigetragen hat','明确肯定州的历史贡献，不仅是人物名出现'),
         'I1':('Entwicklung der deutschen Nation','把地方历史放入德意志民族共同历史；内群体指向州与德国的嵌合，解释性较强'),
         'T1':('eine deutschdenken-Kampagne entgegen','以这些历史贡献作为当下替代文化运动的依据；dem需前段文化政策语境')},
        {'R1':('Die AfD Sachsen-Anhalt setzt dem eine deutschdenken-Kampagne entgegen','党实施认同运动可支持代表性解释，但本单元尚无明确守护／代表资格措辞；不把党名自动当代表资格')},contexts='S002_U002')
    add('S002',4,pdf('S002',[57],'Beinahe jeder Ort in Sachsen-Anhalt','dieses große Opfer anerkennen und ehren.'),
        '萨克森—安哈尔特几乎每个地方都有纪念两次世界大战阵亡者的纪念碑。一些地方还保留着纪念1870／71年德法战争或1866年克尼格雷茨战役阵亡者的纪念碑。多数纪念碑，尤其是那些罕见的纪念碑，状况糟糕而可耻，几乎有辱死者纪念。因此我们将设置州级战争纪念碑保护专员，编制全州名录，登记修复需要，并与文保部门合作促使各市镇采取必要保护措施。必要时还可给予财政支持。资助应不带狭隘的政治评判，平等惠及所有纪念碑。阵亡军人为保卫自己的国家献出了生命。我们承认并尊崇这一巨大牺牲，是爱国转向的第一个标志。',
        '战争纪念：牺牲、失敬与修复',
        {'H1':('Gefallenen der beiden Weltkriege','初始H1把历史事件纳入，暂包含战争资源；试编码暴露其与文化人物类的差异，后续需新历史类型'),
         'F1':('das Andenken geradezu entehrenden Zustand','明示纪念状况使死者荣誉受损；象征失敬的对象是阵亡者，非东部选民'),
         'F2':('Gefallene Soldaten haben ihr Leben für die Verteidigung ihres Landes gegeben.','明确肯定阵亡士兵的牺牲；不能把牺牲评价改写成军事实力优越'),
         'T1':('Wir werden deshalb einen Landesbeauftragten','以历史战争纪念碑及其现状为理由提出当下保护制度，deshalb连接直接')},
        {'R1':('dass wir dieses große Opfer anerkennen und ehren','可以理解为记忆守护者主张，也可能只是保护政策；需按收紧后的代表资格规则复核')})
    add('S002',5,pdf('S002',[58],'Gerade Altparteienpolitiker','er ist das bessere Deutschland.'),
        '恰恰是那些以东方代言人自居的老牌政党政治家，把东部德国描绘成具有所谓不利处境和缺陷的地方。他们说，东方经济实力较弱，更易受“民粹主义”影响，民主不如西方稳固。这种看法并不公正地对待东方。东方不是较差的德国，而是更好的德国。',
        '东部形象：转述劣势而否定其评价',
        {'F1':('Diese Sicht wird dem Osten nicht gerecht.','作者肯定的是东部遭错误描绘的象征贬损；前面的物质劣势是带有angeblich及间接引语的对手说法，不能赋为作者赞同'),
         'F2':('er ist das bessere Deutschland','明确宣称东方更好，子类型是优越性，不能降格为一般自豪'),
         'I1':('Der Osten ist kein schlechteres','构造作为德国组成部分的东方共同体，并与西部比较'),
         'B1':('die sich als Anwälte des Ostens aufspielen','否定老牌政党自称东方代理人的资格')},
        stance='否定转述的缺陷框架；肯定东部更好及其被错误评价')
    add('S002',6,pdf('S002',[58],'Die Bürger im Osten haben','Grundlage ihrer Kommunikationsstrategie machen.'),
        '东方公民比西方公民多了一种经历，即经历过一场革命。因此他们在政治上更有反思能力，也更警觉。东方不是德国民主的问题地区，而是它的榜样。东方未受西方消费物质主义和六八运动敌视德国的倾向侵扰，因而比西方保存了更多德国性。AfD州政府将以此作为其传播战略的基础。',
        '革命经验与东部示范地位：事件年份不明',
        {'F2':('politisch reflektierter und wacher','把过去经验解释为今日政治能力优势；子类型为示范／优越性'),
         'I1':('Die Bürger im Osten haben den Bürgern im Westen voraus','明确对比东西部公民'),
         'B1':('Konsummaterialismus des Westens und der Deutschlandfeindlichkeit der 68er-Bewegung','通过对西方／六八运动的负面属性描绘划界'),
         'T1':('durch die Erfahrung einer Revolution hindurchgegangen sind. Deshalb','明确把革命经验与当前政治素养用deshalb连接')},
        {'H2':('Erfahrung einer Revolution','语境很可能指1989年，但本单元未说DDR或年份；保留?，不能自动认定'),
         'R1':('Eine AfD-Landesregierung wird dies zur Grundlage ihrer Kommunikationsstrategie machen.','明确承诺政府传播框架，但是否构成自我代表资格仍待定；不是因为出现AfD就取1')},contexts='S002_U005')
    add('S003',1,pdf('S003',[1],'a) Die Merseburger Zaubersprüche','Preußentum in Sachsen-Anhalt.'),
        'a）《梅泽堡咒语》——我们语言的开端；b）马格德堡的奥托——帝国的中心；c）埃克·冯·雷普高与《萨克森法典》——德国法的形成；d）马丁·路德——德国基督教的复兴；e）弗里德里希·尼采——一种德国哲学的诞生；f）巴特劳赫施泰特歌德剧院——萨克森—安哈尔特的魏玛古典主义；g）阿尔特马克——萨克森—安哈尔特的俾斯麦与普鲁士传统。',
        '提案第二项：七种历史资源',
        {'H1':('a) Die Merseburger Zaubersprüche','通过成组历史人物、文本与文化场所组织州的历史资源'),
         'F2':('die Anfänge unserer Sprache','将地方资源表述为语言、法律和哲学的起源／形成；是贡献叙事而非人物仅被点名'),
         'I1':('unserer Sprache','我们语言指向德语及德国共同体，不是仅指党组织')})
    add('S003',2,pdf('S003',[3],'Sachsen-Anhalt hat mit seiner Geschichte','die Philosophie tiefgreifend prägte.'),
        '萨克森—安哈尔特以自身历史为德国语言、文化和身份的发展提供了重要推动。奥托一世的王权统治、马丁·路德的宗教改革和德语《圣经》翻译，都是影响远超州界的重要里程碑。马格德堡大教堂和维滕贝格等地方象征着德国历史，吸引世界各地的游客。此外，该州一直是思想革新的地方。一个突出例子是在此出生、深刻影响哲学的弗里德里希·尼采。',
        '提案理由：历史贡献及跨地域影响',
        {'H1':('Das Königtum Ottos I., die Reformation durch Martin Luther','点名王权、宗教改革与文化贡献'),
         'F2':('maßgebliche Impulse für die Entwicklung deutscher Sprache, Kultur und Identität','明确肯定州对德国语言、文化和认同的贡献'),
         'T1':('stehen als Symbole deutscher Geschichte und ziehen Besucher aus aller Welt an','以历史符号连接当前旅游吸引力；是功能联系，不足以证明选民被动员')})
    add('S003',3,pdf('S003',[4],'Die Kampagne „#deutschdenken“ bündelt','Hemmungen der letzten Jahrzehnte zu befreien.'),
        '“deutschdenken”运动汇集萨克森—安哈尔特为德国文化和历史所贡献的最重要元素。它表明，我们这个小州对德国认同的贡献比人们或许以为的更多，并利用这一重点，使对德国认同的援引摆脱过去几十年的拘束和顾虑。',
        '提案理由：被低估的贡献与认同解放',
        {'H1':('zur deutschen Kultur und Geschichte beigetragen hat','回指前页具体历史资源；如脱离前页，仅泛称贡献不够，故需关联上下文'),
         'F2':('unser kleines Bundesland mehr zur deutschen Identität beigetraten hat','明确肯定小州超出预期的贡献；保留原文拼写beigetraten'),
         'I1':('unser kleines Bundesland','以我们的小州构造共同体，并嵌入德国认同'),
         'T1':('nutzt diesen Fokus, um die Bezugnahme auf deutsche Identität','明确把历史贡献焦点作为当下解除认同拘束的手段')},
        {'F1':('als man vermuten mag','贡献被低估可以含承认不足，但未明确不公待遇主体；Hemmungen也可能是心理诊断，故保留歧义')},contexts='S003_U002')
    add('S004',1,web('S004',['P024']),
        '再看看与这种重要性相比，奥托一世在马格德堡大教堂的墓穴几乎被隐藏起来，几乎无人走到那里，也没有任何东西提示他的国家意义，就会认识到：“deutschdenken”运动早就该开展了。',
        '议会发言：奥托墓穴与承认不足',
        {'H1':('das Grab Ottos I. im Magdeburger Dom','具体历史人物及纪念场所'),
         'F1':('wie dort nichts auf seine nationale Bedeutung hinweist','以无人关注和无国家意义提示表达纪念承认不足；对象是历史遗产，不直接等于东部选民的不公'),
         'T1':('dann erkennt man: Eine Kampagne „#deutschdenken“ ist längst überfällig.','由纪念状况推出当前运动的必要性')},
        {'F2':('angesichts dieser Bedeutung','本段以其重要性为前提，但贡献内容位于P020—P022；需核对上下文后决定是否同时赋贡献码')})
    add('S004',2,web('S004',['P026']),
        '出自萨克森—安哈尔特的不仅有1806年解体的旧德意志帝国的缔造者。1871年帝国的缔造者奥托·冯·俾斯麦也于1815年出生在萨克森—安哈尔特施滕达尔附近。阿尔特马克被视为普鲁士的摇篮，而该州的前身是1815年成立的普鲁士萨克森省。因此，该州历史与普鲁士历史极为紧密地联系着，AfD萨勒县支部每年夏末以普鲁士节纪念这一联系。',
        '议会发言：普鲁士历史与党组织纪念活动',
        {'H1':('Otto von Bismarck','具体调用俾斯麦、普鲁士与州历史关系'),
         'T1':('woran der AfD-Kreisverband Saalekreis in jedem Spätsommer mit seinem Preußenfest erinnert.','文本用woran把历史关联与当下党组织的周期纪念活动直接连接'),
         'R1':('der AfD-Kreisverband Saalekreis','初始试编码把党组织承担纪念活动解释为历史守护者；后续须检验是否超过一般活动陈述')})
    add('S004',3,web('S004',['P037']),
        '肯定还有更多内容等待发现。我们的主题清单并不自称封闭，而应继续开放补充。若敢于把这些放在一起看，我们这个州就显现为这样的地方：远离较近和最近历史的大场面，在宁静而稍远的过去，奠定了何为德国性的基础。可以说，在萨克森—安哈尔特能够找到隐秘的德国。我们的“deutschdenken”运动邀请人们在该州寻找这个隐秘的德国。因为该州蕴含的德国性比表面看起来更多。',
        '议会发言：隐秘德国与公众探访邀请',
        {'H1':('in etwas fernerer Vergangenheit die Fundamente','回指前文具体历史清单，建构较长时段德国性起源；依赖前述资源段的语境'),
         'F2':('die Fundamente dessen gelegt wurden, was es bedeutet, deutsch zu sein','把州定位为德国性的奠基之地，明确肯定贡献'),
         'I1':('unser Bundesland','把我们州与德国性嵌合，群体指向并非单一东部人'),
         'T1':('Unsere Kampagne „#deutschdenken“ will dazu einladen','将历史起源主张转成当下探访运动的依据'),
         'A1':('sich in Sachsen-Anhalt auf die Suche nach diesem geheimen Deutschland zu machen.','向公众邀请探访与参与文化体验；不是投票号召，也不是单纯政府承诺')},contexts='S004_U002')

    time=dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo('Asia/Shanghai')).isoformat()
    decisions=ROOT/'inputs/pilot_ai_decisions.json'
    if decisions.exists():
        raise SystemExit('Pilot already exists; preserve original decisions instead of overwriting')
    decisions.write_text(json.dumps({'status':'AI试编码；非独立人类编码者','version':'v0.0-pilot',
        'created_at':time,'units':units},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    fields=next(csv.reader((ROOT/'segments.csv').open(encoding='utf-8')))
    with (ROOT/'pilot_segments.csv').open('x',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
        writer.writerows({key:u.get(key,'') for key in fields} for u in units)
    fields=next(csv.reader((ROOT/'coding.csv').open(encoding='utf-8')))
    output=[]
    for u in units:
        assert u['reviewed_codes']==CODES
        for code in CODES:
            value='0';evidence='';reason=ZERO[code];kind='排除判断'
            if code in u['ones']:
                value='1';evidence,reason=u['ones'][code];kind='直接表达或所注上下文解释'
            if code in u['questions']:
                value='?';evidence,reason=u['questions'][code];kind='边界待决'
            if evidence: assert evidence in u['german_original'],(u['unit_id'],code,evidence)
            row={f:'' for f in fields}
            row.update(source_id=u['source_id'],unit_id=u['unit_id'],code=code,value=value,
                german_evidence=evidence,chinese_explanation=reason,
                decision_reason=f"本单元议题：{u['topic']}。{reason}",speaker=u['speaker'],
                speaker_stance=u['speaker_stance'],expression_type=kind,
                context_unit_ids=u['context_unit_ids'],codebook_version='v0.0-pilot',
                coder='AI',coding_status='AI试编码',human_review_status='未人工复核',
                original_ai_value=value,coded_at=time)
            output.append(row)
    with (ROOT/'pilot_coding.csv').open('x',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(output)
    with (ROOT/'logs/process_runs.jsonl').open('a',encoding='utf-8') as handle:
        handle.write(json.dumps({'script':'make_pilot.py','executed_at':time,'pilot_sources':3,
            'pilot_units':len(units),'initial_codes':len(CODES),'judgments':len(output),
            'human_review':False},ensure_ascii=False)+'\n')
    print(json.dumps({'pilot_sources':3,'pilot_units':len(units),'judgments':len(output),'status':'AI试编码'},ensure_ascii=False))


if __name__=='__main__':main()
