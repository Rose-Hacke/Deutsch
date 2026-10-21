#!/usr/bin/env python3
"""Export explicit AI semantic decisions; no keyword-to-code inference is performed."""
import csv
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from make_pilot import pdf, web, ZERO

ROOT=Path(__file__).resolve().parents[1]
CODES=['H1','H2','H3','H4','F1','F2','I1','B1','T1','R1','A1','N1']
ZERO['H4']='没有明确调用战争、殖民、NS或其他非DDR政治暴力历史；当下暴力和辱骂性Nazi标签不是历史叙述'
ZERO['N1']='没有明确为选择、替换、拒绝或优先某种记忆方式提出正当化理由；普通历史提及与一般政策承诺不足'


def web_slice(sid,locators,start=None,end=None):
    text,locator,page,kind=web(sid,locators)
    if start:text=text[text.index(start):]
    if end:text=text[:text.index(end)+len(end)]
    return text,locator,page,kind


def main():
    pilot=json.loads((ROOT/'inputs/pilot_ai_decisions.json').read_text(encoding='utf-8'))
    units=pilot['units']
    for unit in units:
        unit['ones'].pop('R1',None) if unit['unit_id']=='S004_U002' else None
        if unit['unit_id']=='S002_U004':
            unit['ones'].pop('H1')
            unit['ones']['H4']=['Gefallenen der beiden Weltkriege','新增历史类型：两次世界大战、1866及1870/71年战争的纪念；不把这些全归为文化人物资源']
        unit['reviewed_codes']=CODES
        unit['group_referent']={'S002_U001':'公民／人民，非特指东部', 'S002_U002':'德国人',
            'S002_U003':'州的历史贡献者—德意志民族', 'S002_U004':'阵亡士兵及其纪念共同体',
            'S002_U005':'东部德国人与西部的比较', 'S002_U006':'东部德国人与西部的比较',
            'S003_U001':'德语共同体', 'S003_U002':'州历史资源，非明确当代内群体',
            'S003_U003':'州居民／德国人嵌合', 'S004_U001':'奥托遗产与国家纪念',
            'S004_U002':'地方—普鲁士历史联系，党组织作为活动者',
            'S004_U003':'州与德国认同的嵌合'}[unit['unit_id']]
        unit['f2_type']={'S002_U002':'尊严／自信（规范目标）','S002_U003':'历史贡献','S002_U004':'牺牲／荣誉',
            'S002_U005':'优越性','S002_U006':'示范／优越性','S003_U001':'起源／文化贡献',
            'S003_U002':'历史贡献','S003_U003':'历史贡献','S004_U003':'历史奠基贡献'}.get(unit['unit_id'],'')
        unit['f1_type']='尊重／承认' if unit['unit_id']!='S002_U001' else '政治排斥／代表关系'
        unit['ai_revision_reason']='H4新增后逐码回溯检查；R1按明确代表资格标准收紧'
    units[2]['context_unit_ids']='S002_U010|S002_U002'
    units[8]['context_unit_ids']='S003_U002'
    units[9]['context_unit_ids']='S004_U013'
    units[11]['context_unit_ids']='S004_U002|S004_U008'

    def add(sid,n,selection,cn,topic,ones=None,questions=None,contexts='',group='',f2='',f1='尊重／承认',speaker=None,stance='发言者／作者肯定立场；历史断言为党派叙述，不作外部事实认证'):
        text,locator,page,kind=selection
        units.append(dict(source_id=sid,unit_id=f'{sid}_U{n:03}',section=topic,printed_page=page,
            pdf_page_index=locator.removeprefix('PDF:') if kind=='pdf' else '',web_paragraph_locator=locator if kind=='web' else '',
            german_original=text,chinese_translation=cn,context_unit_ids=contexts,
            context_relation='见编码行具体回指；保留定位记录中的完整相邻段落',
            speaker=speaker or ('Dr. Hans-Thomas Tillschneider' if sid=='S004' else 'Fraktion AfD' if sid=='S003' else 'AfD Landesverband Sachsen-Anhalt'),
            speaker_role='AfD发言者／机构',speaker_stance=stance,source_version='本次获取版本；原文及版本证据见sources.csv',
            translation_status='AI逐句对照德语，待人工复核',translation_by='AI辅助译文（待研究者审订）',
            quotation_verification='已对照存档文字层／网页或官方API段落；PDF另作图像抽查；非人类复核',
            analysis_selection_reason='研究问题相关论证或明确反例；定向段落样本，非整份长文逐句穷尽',segment_status='AI初编，待人工复核',
            ones=ones or {},questions=questions or {},reviewed_codes=CODES,topic=topic,group_referent=group,
            f2_type=f2,f1_type=f1,ai_revision_reason='按v0.2进行首轮AI初编'))

    add('S002',7,pdf('S002',[54],'Wir unterstellen den Altparteien allerdings auch nicht','gezielte Arbeit an den kulturellen Voraussetzungen geheilt werden.'),
        '但我们并不认定老牌政党想伤害我们，也避免提出不能真正增进理解的过度论战指控。其破坏性行为的原因与其说是恶意，不如说是拘束和软弱：没有能力捍卫德国利益，且有一种伤害自己的强迫冲动。民族受虐倾向和缺乏自信又有文化前提。因此，当前困境的最终根源在文化，只能通过有针对性地改变文化前提来治愈。',
        '文化导言：否认恶意而归因于文化弱势',
        {'I1':('deutsche Interessen zu verteidigen','以德国共同利益界定受损共同体'),
         'B1':('weniger ein böser Wille, als eher Hemmung und Schwäche','归责为老牌政党的文化软弱，明确否定恶意动机；不把被否定的伤害意图当其主张')},group='德国共同体与老牌政党',stance='肯定文化软弱归因；明确否定老牌政党主观想伤害我们的断言')
    add('S002',8,pdf('S002',[54,55],'Eine Vergangenheitsbewältigung','dem Einfluss der Regenbogenideologie hilflos ausgeliefert.'),
        '一种与真正克服过去恰恰相反、让罪责情结永续存在的“反思过去”，如今使民族自豪普遍被视为可疑，捍卫自身利益被认为不体面，政治家也回避对我们1933年前丰富历史作任何积极援引。一种从西德六八运动开始的摧毁传统的传统，掏空了我们的文化遗产，堵塞了稳定民族认同形成的可能。德国失去自我维护的力量，因而无助地暴露于彩虹意识形态的影响之下。',
        '文化导言：罪责记忆与民族自信受损的因果叙述',
        {'H1':('von der 68er-Bewegung','具体调用西德六八文化运动及文化传统毁损的历史叙述'),
         'F1':('Nationalstolz grundsätzlich als anrüchig gilt','作者主张民族自豪被贬为可疑、维护利益被斥不体面；是象征贬损，不是物质分配'),
         'F2':('unsere reiche Geschichte vor 1933','肯定1933年前历史丰富；与自豪受贬直接处于同一因果论证'),
         'I1':('unser kulturelles Erbe','构造拥有共同文化遗产的德国我们'),
         'B1':('Eine Tradition der Traditionsvernichtung','把六八运动／文化政治视为认同损伤的责任来源'),
         'T1':('hat mittlerweile dazu geführt','把记忆实践与六八历史解释为当下自豪／利益捍卫受抑的原因')},
        {'H4':('Verewigung eines Schuldkomplexes','很可能涉及NS罪责记忆，但此段未明确其历史对象；不从1933这个边界独自补成NS事件叙述')},
        group='德国人及国家文化遗产',f2='历史文化价值',f1='尊重／承认')
    add('S002',9,pdf('S002',[55],'Angesichts der verkorksten und unattrak','Fremde zu integrieren.'),
        '面对老牌政党呈现的那种扭曲而没有吸引力的身份认同，很难责怪外国人不愿融入其中。哪个理性而稳定的土耳其人或叙利亚人愿意成为一个自我憎恨、懊丧的“彩虹德国人”？唯有AfD能向外国人示范一种具有吸引力、让人愿意加入的德国认同。我们必须先与自己和解，然后才谈得上整合外来者。',
        '文化导言：排他性认同示范能力主张',
        {'F2':('eine deutsche Identität vorleben, die attraktiv ist','肯定一种有吸引力的德国认同；是规范性自我价值目标，不是选民已接受'),
         'I1':('Wir müssen mit uns selbst ins Reine kommen','将德国我们与外来者置于不同位置'),
         'B1':('wie sie die Altparteien vorleben','将负面认同归于老牌政党，另划分德国人／外国人'),
         'R1':('Allein die AfD kann','明确以唯有AfD宣称独特的集体认同示范与修复能力')},
        contexts='S002_U002|S002_U008',group='德国人；外国人作为整合对象',f2='尊严／自信（规范目标）')
    add('S002',10,pdf('S002',[56],'Die Landesregierung betreibt unter dem Titel','Politik der Identitätslosigkeit auf die Spitze.'),
        '州政府以“moderndenken”为名开展形象运动，试图从包豪斯推导该州认同。然而，包豪斯建筑学校一向试图避免任何民族扎根的迹象。“moderndenken”运动因而把缺乏身份认同的政治推向了极致。',
        'deutschdenken前提：反对包豪斯认同来源',
        {'H1':('aus dem Bauhaus die Identität des Landes Sachsen-Anhalt abzuleiten','调用具体建筑学校传统，作为被否定的身份资源；H1不表示作者赞同该资源'),
         'I1':('Identität des Landes Sachsen-Anhalt','明确讨论州共同身份及民族扎根'),
         'B1':('Die moderndenken-Kampagne treibt','将州政府的包豪斯运动置于对立位置'),
         'T1':('Dabei war gerade die Bauhaus-Architekturschule immer bestrebt','以建筑学校的历史属性解释当前形象运动的身份后果')},
        {'F1':('Politik der Identitätslosigkeit','可被理解为剥夺认同的指控，也可能仅为不认同其文化路线；不把所有政策批评都判不公')},group='州居民—德国民族认同')
    add('S002',11,pdf('S002',[56],'Dass eine Landesregierung angesichts','ein neues nationales Selbstbewusstsein angestoßen werden.'),
        '面对如此丰富的德国历史，州政府却只能选取一所存在争议的建筑学校，本身就是我们所批评并将治愈的认同障碍的明显表现。我们的“deutschdenken”运动将联结并自信展示该州能够提供的最美好的德国历史实例。通过纳入学校、推出新的爱国旅游方案、颁发奖项和举行纪念活动，将推动新的民族自信。',
        'deutschdenken手段：学校、旅游与纪念活动',
        {'H1':('dieser Überfülle an großer deutscher Geschichte','明确回指S002_U003刚列出的具体历史资源'),
         'F2':('ein neues nationales Selbstbewusstsein','明确民族自信的规范目标；不是宣称已实现'),
         'I1':('nationales Selbstbewusstsein','将州文化政策嵌入德国民族共同身份'),
         'B1':('zu keinem anderen Stoff als einer umstrittenen Architekturschule greift','批评州政府的历史资源选择'),
         'T1':('Durch Einbeziehung der Schulen','把选取的历史资源通过具体制度与旅游渠道用于当前认同塑造'),
         'R1':('die wir kritisieren und die wir heilen werden','政党自称治愈州／国家认同障碍；结合前段AfD具名，记录明确回指')},
        contexts='S002_U003|S002_U010',group='州居民与德国人',f2='尊严／自信（规范目标）')
    add('S002',12,pdf('S002',[56,57],'In Magdeburg befindet sich das „Deutsche Zentrum Kulturgutverluste“','Wir werden diesen Zuschuss komplett streichen.'),
        '马格德堡设有“德国文化财产损失中心”。那里所谓的“来源研究”检查博物馆藏品在殖民时期、纳粹时期及苏占区／民主德国时期是否被非法取得。其问题在于，即使旧所有者或继承人未要求返还，也在毫无起因的情况下开展这些调查。有受害者提出要求时，当然应当弥补不法行为；但对全部博物馆藏品作无具体起因的普遍怀疑，并搜寻已无人申诉的违法行为，只是在人工维持一种我们终于应当放下的罪责感。构造殖民罪责尤其荒谬。该州目前每年向该中心补助73500欧元。我们将完全取消这一补助。',
        '来源研究：附有补偿限定的罪责记忆批评',
        {'H2':('in der SBZ/DDR','明确回溯苏占区／DDR时期非法取得财物的核查；非1989记忆'),
         'H4':('während der Kolonialzeit, der NS-Zeit','明确列举殖民与NS历史对象，不能据其批评推断作者赞同历史非法行为'),
         'F1':('der anlasslose Generalverdacht gegen alle Museumsbestände','作者将对全部藏品的普遍怀疑描为无根据；对象是共享遗产／博物馆，非东部物质弱势'),
         'I1':('eines Schuldgefühls, das wir endlich ablegen sollten','构造应摆脱共同罪责感的我们；群体指向德国认同语境，需人工核对'),
         'B1':('dienen nur der künstlichen Aufrechterhaltung eines Schuldgefühls','把研究实践归为维持罪责感的责任者'),
         'T1':('Wir werden diesen Zuschuss komplett streichen.','围绕具体历史取得争议，推出当下取消资助；同一连续论证且有明确dabei／dienen指涉')},
        group='德国文化遗产共同体／博物馆',stance='批评普遍调查与罪责维持；同时明确支持有受害者要求时弥补不法')
    add('S002',13,pdf('S002',[58],'In Sachsen-Anhalt verfügen viele Städte','mit großen Fragezeichen behaftet.'),
        '萨克森—安哈尔特许多城市拥有良好的老建筑存量，尤其在历史内城。保护这些能够塑造认同并提供住房的老建筑，如今在上一次修缮过去二三十年后，面临很大的不确定性。',
        '老建筑：有历史属性但无明确转型回溯的反例',
        {},{'I1':('identitätsstiftenden','明确说建筑塑造认同，但未指认共同体；是否足以构成内群体建构待核'),
            'T1':('20 bis 30 Jahre nach der letzten Sanierung','有建筑与维修时间关系，但是否足以构成研究问题所要求的历史—当下叙事连接不清；不可直接说统一后转型')},group='未明确指认身份群体')
    add('S002',14,pdf('S002',[59],'Öffentliche Gebäude, die nach 1990','müssen historische Identität widerspiegeln.'),
        '1990年后在萨克森—安哈尔特建成的公共建筑往往极其丑陋。花费巨资，却造出毫无意味的方块或其他冰冷、没有传统的几何形式。例如马格德堡奥古斯特—倍倍尔堤的“正弦曲线”建筑，或大教堂广场的北德意志州银行建筑。我们将终结这种状况，在州建筑法中加入规范，要求由州或市镇建设并服务公共目的的建筑采用一种得到认可的建筑传统。应避免没有传统的构造，优先使用耐久的地方材料。我们在此参照唐纳德·特朗普首个任期中的一项行政命令。公共建筑必须被多数居民视为美，也必须反映历史认同。',
        '建筑政策：1990年时间标记不自动等于统一后转型',
        {'T1':('müssen historische Identität widerspiegeln','要求当前公共建筑继承历史形式，以历史身份作为设计规范')},
        {'H3':('nach 1990','明确说1990年以后，但未把建筑变化与统一／转型经历相连；年代标记与转型记忆之间留?')},group='州居民；公共建筑的历史认同')
    add('S002',15,pdf('S002',[61],'Wir bekennen uns zur kulturellen Identität unserer Heimat.','hat der Ortschaftsrat per Abstimmung zu beschließen.'),
        '我们认同家乡的文化身份。与传播左派不良精神的政治教育中心不同，我们将资助强化乡土感和民族认同的活动，其中包括保存习俗与传统。为此，州每年按每位居民五欧元向村镇提供不指定用途的习俗传统经费。具体在广泛的习俗传统维护范围内如何使用，由村镇议会表决决定。',
        '乡土传统：财政工具与身份延续',
        {'I1':('kulturellen Identität unserer Heimat','明确以家乡及民族认同构造内群体'),
         'B1':('Statt einer Landeszentrale für politische Bildung, die linken Ungeist verbreitet','把现有政治教育机构设为相反路线'),
         'T1':('Brauchtum und Traditionen erhalten werden müssen','明确以保留传统为当下财政措施的目的；延续关系直接，但未列具体历史事件')},group='乡土共同体与德国民族认同')
    add('S002',16,pdf('S002',[66],'Jedes Jahr zahlt das Land Sachsen-Anhalt','zu einer allgemeinen Kirchenförderung entwickelt.'),
        '该州每年向大型征收教会税的教会支付四千多万欧元所谓“国家给付”。这些付款归根到底是对1803年被征收教产的补偿。1919年生效的魏玛宪法已要求终结这些给付，但至今未执行。原始理由——1806年消亡的德意志民族神圣罗马帝国的一项法律行为——在现实考量中早已失效，交易基础已多次消失。事实上，国家给付已由征收补偿变成一般教会资助。',
        '教会给付：制度历史解释，非受辱共同体叙事',
        {'H1':('die 1919 in Kraft getretene Weimarer Reichsverfassung','具体追溯1803年征收、1919年宪制与历史政治实体'),
         'T1':('von einer Enteignungsentschädigung zu einer allgemeinen Kirchenförderung entwickelt','以历史法律基础的演变论证当下制度性质，属于过去—现在连续性／断裂解释')},group='教会给付制度；未构造受损东部共同体')
    add('S002',17,pdf('S002',[151],'Der heimische Tourismus','zu neuer Blüte zu verhelfen.'),
        '本地旅游是该州重要而有前景的经济因素。对于以乡村为主的州，它创造收入、为本地专业人才留下来提供前景，也能发展地方基础设施。多数州的国内旅游蓬勃发展，萨克森—安哈尔特却陷于黯淡停滞。对此负责的是CDU领导的州政府。它任职以来未能妥善促进旅游，也未能利用地方文化特点与历史烙印。AfD领导的州政府将围绕新的“deutschdenken”运动制定并落实协调的方案，使该州旅游重新繁荣。',
        '旅游：经济政策替代解释',
        {'B1':('Verantwortlich dafür ist die CDU-geführte Landesregierung.','明确将旅游停滞归责CDU政府；不把停滞本身自动编码为不公')},
        {'T1':('die historische Prägung des Landes zu nutzen','有概括历史资源的政策利用，却未在此段指认特定过去；与文化章节的连接须按明确同名运动回指复核')},
        contexts='S002_U003|S002_U011',group='州经济／地方就业；不是明确的东部受辱身份')
    add('S002',18,pdf('S002',[200],'Die AfD-Sachsen-Anhalt bekennt sich ohne Wenn und Aber','regelmäßig befahren werden.'),
        '萨克森—安哈尔特州AfD明确支持以传统内燃机汽车作为出行基础。同时，我们将继续扩建公共短途客运，作为私人汽车的合理补充而非替代。将停止拆减车站，例如采尔布斯特和罗斯劳之间的于特里豪车站。只要可能、合理且不违反公民利益，也将恢复停用铁路。路德城维滕贝格与艾伦堡之间的海德铁路，必须跨州纳入萨克森—安哈尔特和萨克森的公共短途客运并定期运行。',
        '关键词反例：Lutherstadt只是交通地名',{},group='普通交通政策；Luther不是历史调用')
    add('S002',19,pdf('S002',[219],'Unseren Bürgern in Sachsen-Anhalt','Neutralität und Ausgewogenheit zu verpflichten.'),
        '不需要向我们萨克森—安哈尔特的公民解释什么是民主！我们不需要受照管的意见，而要真正的多元！媒体必须再次反映全部意见，而非只反映编辑会议自己的理想图景。因此，作为政府，我们将推动公共广播及接受公款资助的电台遵守政治中立与平衡。',
        '无历史的公民能力与被居高临下对待框架',
        {'F1':('Wir brauchen keine betreute Meinung','拒绝对公民意见的居高临下管理，属于象征／政治承认主张'),
         'F2':('muss man Demokratie nicht erklären','肯定州公民的民主理解能力；未提供历史经验作为理由，不能默补1989'),
         'I1':('Unseren Bürgern in Sachsen-Anhalt','明确构造州公民共同体'),
         'B1':('nicht nur, was gerade in Redaktionssitzungen dem eigenen Wunschbild entspricht','把编辑部偏好与公民多元意见置于对立')},group='萨克森—安哈尔特州公民',f2='公民能力肯定')
    add('S002',20,pdf('S002',[4],'Keine Sorge!','Es ist vielleicht unsere letzte Chance.'),
        '别担心！老牌政党的专政目前还不是现实。9月6日还不是由它们挑选新的人民，尽管它们愿意如此，而是由人民，也就是我们，决定哪些政党应代表我们的利益。我们还能够这样做。只要还能够，我们就应该去做。这或许是我们最后的机会。',
        '序言：对1953类比的限定与投票号召',
        {'F1':('wenn sie es auch gerne wollten','把让政党选择人民描述为其意愿及将来威胁，但明确说尚非现实'),
         'I1':('das Volk, also wir','明确把我们等同人民，非特指东部'),
         'B1':('die Altparteien ein neues Volk','将老牌政党与人民选择权置于潜在对立'),
         'T1':('Am 6. September wählen noch nicht die Altparteien ein neues Volk','直接延续前页布莱希特1953典故，并强调当下尚未成为专政，不能说作者宣布当下等同DDR'),
         'A1':('Und wir sollten es tun, solange wir es noch können.','明确劝公众利用仍存在的选举选择权')},
        contexts='S002_U001',group='公民／人民',f1='政治排斥威胁',stance='肯定选举必要；明确否定当下已是老牌政党专政')

    # More proposal and transcript units and press-release contrasts are recorded below.
    extend_units(add)
    extend_later(add)
    memory_justifications={
        'S002_U002':('Bezugnahmen auf die guten Seiten der deutschen Geschichte','明确以历史积极方面为身份修复资源，提出选择准则'),
        'S002_U004':('ohne kleingeistige politische Wertungen','要求各类阵亡纪念碑平等获支持，为超越政治区分的纪念选择作辩护'),
        'S002_U008':('unsere reiche Geschichte vor 1933','反对将民族自豪贬低的罪责框架，并主张重视1933年前历史；记忆重心的规范正当化'),
        'S002_U010':('Politik der Identitätslosigkeit','以民族扎根为判断历史资源的尺度，否定包豪斯作为州认同来源；需联系下一单元的替代运动'),
        'S002_U011':('zu keinem anderen Stoff als einer umstrittenen Architekturschule','明确批判历史资源选择过窄，要求选取丰富德国历史以提升自信'),
        'S002_U012':('künstlichen Aufrechterhaltung eines Schuldgefühls','以反对无根据集体罪责、承认具体受害者补偿的限定，为缩减来源研究辩护'),
        'S003_U004':('grundsätzlich bejahender, unbelasteter, respektvoller und wertschätzender Umgang','明确提出选择历史态度的规范标准'),
        'S003_U006':('anstelle der sog. Gedenkstättenfahrten','明确主张替换学校记忆资源，理由连接本运动的民族文化主题'),
        'S004_U003':('abseits der großen Szenen unserer jüngeren und jüngsten Geschichte','主动把视线转向较久远、少受注意的历史，以寻找德国性根基'),
        'S004_U004':('Festhalten an deutscher Identität und Partikularität','用民族特殊性而非普遍主义为替代包豪斯的记忆品牌辩护'),
        'P_LV_1227_U001':('Doch die Befreiung können wir nicht feiern','承认对被迫害者的解放，同时以民族灾难为拒绝庆祝的理由；保留双重限定'),
        'P_LV_1227_U002':('ein zunehmend absurder Schuldkult','给出战后纪念从追究个体责任走向集体罪责的评价，论证当下拒绝参加解放纪念'),
        'P_LV_1227_U003':('Die ewige Vergangenheitsbewältigung als gesellschaftliche Dauerbüßaufgabe','通过明确赞同的历史引语，为正常民族认同和摆脱永久赎罪式记忆作辩护'),
        'P_LV_1203_U002':('notwendigerweise selektiv','明确以记忆关联遗忘、以神话而非科学为基础，为选择性叙述提出元论证'),
        'P_LV_1203_U003':('welche Selektivität gewählt wird','明确对比肯定／敌视民族身份的两种选择性，主张前者并把AfD设为文化解放者'),
    }
    for unit in units:
        if unit['unit_id'] in memory_justifications:
            unit['ones']['N1']=memory_justifications[unit['unit_id']]
    # Manually identify context-dependent judgments instead of relying on surface terms.
    for unit in units:
        unit['inference_codes']={'S002_U003':['I1'],'S002_U007':['I1'],'S002_U012':['I1'],
            'S003_U003':['H1'],'S004_U006':['I1'],'S002_U015':['T1']}.get(unit['unit_id'],[])
        if unit['unit_id']=='S004_U013':
            unit['ones']['T1']=('aus dem unser Deutschland hervorging','把今天的我们德国直接表述为来自历史王国，连接关系是国家起源，不是仅凭今地名推断')
    export(units,pilot)


def extend_units(add):
    add('S003',4,pdf('S003',[1],'1. Die Kampagne „#deutschdenken“','kulturpolitischen Wende zuweist.'),
        '“deutschdenken”将取代州“moderndenken”运动，成为该州的新标识。由此应建立一种原则上肯定、不背负包袱、尊重且珍视德国历史的态度。这种身份及文化政策重点，应赋予该州在各州比较中的独特特征，不仅持续塑造州品牌、促进文化及文化政策旅游，还使该州在即将到来的文化政策转向中发挥领导作用。',
        '提案第一项：历史态度与州示范角色',
        {'F2':('eine Führungsrolle','要求州取得文化政策领先地位；标为未来目标，不说已经优越'),
         'I1':('unsere Landesmarke','在身份政策论证中以我们州品牌构造州共同体'),
         'T1':('Umgang mit der deutschen Geschichte','把特定的肯定历史态度直接连接当前品牌与旅游政策；资源内容由紧随的主题名单明确')},
        contexts='S003_U001',group='州共同体与德国认同',f2='示范／领先（未来目标）')
    add('S003',5,pdf('S003',[1,2],'a) Eine Straße des deutschen Reiches','in ihrer Entwicklung profitieren.'),
        '仿照罗曼式建筑之路，建立一条将十至十六世纪重要历史遗址联为旅游路线的“德意志帝国之路”。除马格德堡大教堂、梅姆莱本行宫、奎德林堡大教堂及路德在艾斯莱本、维滕贝格的活动地点外，也应纳入较少知名的历史场所，特别是城堡和宫殿，使它们的发展受益。',
        '提案第三项a：历史遗址旅游路线',
        {'H1':('historischen Stätten des 10. bis 16. Jahrhunderts','明确点名时期、建筑、行宫及路德地点'),
         'T1':('zu einer auch touristisch nutzbaren Route verbindet','把具体历史场所组织为当下可利用旅游产品；并非公众投票号召')},group='历史地点与旅游发展')
    add('S003',6,pdf('S003',[2],'b) Die Themen der Kampagne','Verbindung mit der Landeskampagne zu erinnern.'),
        '运动主题应在课程中得到更多考虑，尤其应修改德语、历史及政治／社会学课程。此外，应以与各主题相关的历史遗址考察取代目前学校与州政治教育中心合作开展的所谓纪念场所参访。州政府还应推动学校改名，以结合州运动纪念杰出的历史人物。',
        '提案第三项b：学校中的记忆资源替换',
        {'H1':('herausragende historische Persönlichkeiten','回指提案第二项具体人物名单，作为课程与校名资源'),
         'T1':('anstelle der sog. Gedenkstättenfahrten','明确提出当下学校纪念参访的资源替换；不能因Gedenkstätten一词就默认为所有参访都是集中营参访')},
        contexts='S003_U001',group='学校中的德国历史认同')
    add('S003',7,pdf('S003',[2],'e) Die Landesregierung lobt','Weiterentwicklung deutscher Identität erkennen lassen.'),
        '州政府设置奖金可观的历史学、艺术、哲学及文学奖，各奖对应运动的一项主题，奖励有关领域中能够表明对确认或进一步发展德国认同作出贡献的突出成就。',
        '提案第三项e：奖项制度与认同贡献标准',
        {'F2':('herausragende Leistungen','明确肯定对德国认同作贡献的成就；是奖项遴选规范，不是已获公众承认'),
         'I1':('Bestätigung oder Weiterentwicklung deutscher Identität','以共同的德国认同作为贡献尺度'),
         'T1':('je einem Thema der Kampagne zuordnen lassen','奖项与既列历史主题直接对应；注明跨单元的制度化联系')},
        contexts='S003_U001',group='德国认同共同体',f2='贡献／成就（规范目标）')
    add('S003',8,pdf('S003',[3],'h) Die Landesregierung führt','je mehr Stätten bereits besucht wurden.'),
        '州政府推出“自豪通行证”，可在与运动有关的所有历史遗址购买。它像集章卡一样列出相关历史遗址，去过的地点越多，门票优惠就越大。',
        '提案第三项h：产品名称并非自动自豪表达',
        {'T1':('an allen historischen Stätten, die im Zusammenhang mit der Kampagne stehen','把运动所调用的历史场所接入当下集章优惠制度；并非公众明确行动号召')},
        {'F2':('„Stolz-Pass“','自豪只是产品名；是否可单凭名称赋情感评价不清，保留?而不关键词命中即1')},
        contexts='S003_U001',group='潜在游客，未明确集体身份')

    add('S004',4,web('S004',['P010']),
        '“moderndenken”运动基于一种扁平的现代性理解，即精神贫乏、具有特定左派色彩的进步意识形态：永远向前，绝不后退！但有什么能与这种以进步自身为目的的思维相对？包豪斯现代性旨在消除民族特征，并以彻底全球化的意义解除人与民族文化土壤的联系；这种现代性因此带有强烈普遍性诉求。所以，坚持德国认同与特殊性、以“deutschdenken”相对，似乎就是州政府“moderndenken”运动真正的反命题。',
        '议会发言：包豪斯、普遍主义与德国特殊性',
        {'H1':('Modernität des Bauhauses','调用包豪斯的历史文化特征，作者对其作负面评价'),
         'I1':('Festhalten an deutscher Identität und Partikularität','明确以德国认同及特殊性为共同体尺度'),
         'B1':('spezifisch linken Progressivitätsideologie','将左派进步主义／普遍主义与德国特殊性对立'),
         'T1':('eigentliche Gegenthese zur Kampagne','从历史文化流派属性推出当前两种州品牌的对立')},group='德国民族文化共同体')
    add('S004',5,web('S004',['P014']),
        '《梅泽堡咒语》从一段几乎没有其他文献传世的时代向我们说话；今天的德国人几乎已无法理解，却又不是完全陌生。“姐妹”写作Suister，“行驶”是fuorun，“森林”是Holz，犹如我们今天仍会说的Gehölz。多数人今天大概也懂ben zibena，即“骨与骨”，或者用一种已旧却仍可使用的形式Bein zu Beine；这是来自我们历史深处的一种原初而熟悉的声音。',
        '议会发言：语言熟悉感与跨时间我们',
        {'H1':('Merseburger Zaubersprüche','具体使用古代语言文献与词例'),
         'I1':('aus den Tiefen unserer Geschichte','构造拥有同一语言历史的德国我们'),
         'T1':('wie wir heute noch sagen würden','明确比较古代词形与今天可理解的语言，建构连续性')},group='德语／德国共同体')
    add('S004',6,web('S004',['P015','P016','P018']),
        '1842年在梅泽堡大教堂图书馆发现的咒语，作为最古老的古高地德语文献，标志德语史的开端。因此，它们应在2026年被列入联合国教科文组织世界记忆名录。然而，该名录自1992年就存在。我想问：为什么三十多年后才有人想到也可收录它们？它们本应在名录设立之初就理所当然地在内。当时德国代表没有起身提出这一要求，只能以教育不足和民族自信不足来解释。我们的运动要补救这两者。',
        '议会发言：UNESCO承认延迟的指控',
        {'H1':('Beginn der deutschen Sprachgeschichte','将古文献定位为德语历史起点；历史与名录事实仅作为发言者断言'),
         'F1':('hätten wie selbstverständlich schon bei der Gründung','明确认为该文化资源应更早获国际纪念承认'),
         'F2':('als die ältesten Dokumente des Althochdeutschen','用最古老文献与语言起源肯定文化贡献及地位'),
         'I1':('nationalem Selbstbewusstsein','将个别资源承认与德国民族自信相连'),
         'B1':('der deutsche UNESCO-Vertreter damals','将延迟归于德国代表的教育／自信不足'),
         'T1':('Beidem soll unsere Kampagne abhelfen.','以所称历史资源承认不足推出当前运动的补救任务')},
        {'R1':('Beidem soll unsere Kampagne abhelfen.','提出修复任务但此段未明确党—群体代表资格；结合AfD发言者及运动归属可解释为修复者，待核')},
        group='德国文化遗产与德国民族共同体',f2='语言起源／文化贡献')
    add('S004',7,web('S004',['P028']),
        '不仅德国政治史，德国哲学史也从萨克森—安哈尔特获得重要推动。德国唯心主义向世界展示德国思维所能达到的成就后，1844年出生在今天布尔根兰县勒肯的尼采创造了某种可被称为现代的德国哲学；当然，这里的现代并非主体主义左派进步性，而指尼采超越启蒙运动陈腐的抽象与误导性科学脱离生活的特殊取向，使思想重新从生活自身出发。尼采还曾就读于今天仍存在的普福尔塔州立学校。',
        '议会发言：哲学贡献与现代性争夺',
        {'H1':('Friedrich Nietzsche','具体调用德国唯心主义、尼采及地方学校'),
         'F2':('wesentliche Impulse empfangen','明确肯定州对德国哲学的贡献'),
         'B1':('nicht im Sinne einer subjektivistisch-linken Progressivität','以否定限定划分其认可的现代性与左派进步主义')},
        {'T1':('Prädikat „modern“','与当下modern／deutschdenken争论有主题联系，但此段未直接回扣政策；须结合S004_U004而非默拼')},
        contexts='S004_U004',group='德国思想传统及州文化贡献',f2='哲学贡献')
    add('S004',8,web('S004',['P036']),
        '如同路德对抗罗马而坚持一种德国基督教，来自今天安哈尔特—比特费尔德县雷皮绍的埃克·冯·雷普高，也以《萨克森法典》首次将德国法成文化，与罗马法相对。还有作为魏玛古典主义分支的巴特劳赫施泰特歌德剧院，我们这个州因而也分享德国民族文学这一高峰。',
        '议会发言：文化贡献与历史性内外区分',
        {'H1':('Eike von Repgow','调用路德、法典、歌德剧院及魏玛古典主义'),
         'F2':('Anteile an dieser Hochphase der deutschen Nationalliteratur','明确肯定州参与民族文学高峰的贡献'),
         'I1':('unser Bundesland','将我们州嵌入德国民族文学的共同过去'),
         'B1':('einen Kontrapunkt gegen das römische Recht','以德国／罗马的历史区分建构差异；不把历史罗马直接当今日敌人')},group='州与德意志文化共同体',f2='法律／文学贡献')
    add('S004',9,web('S004',['P045','P046']),
        '认同体验、教育和休闲应组成一种别处没有的旅游体验。许多塑造德国认同的时刻发生于中世纪，因此应以“德意志帝国之路”串联运动主题。《梅泽堡咒语》、路德及歌德剧院又由语言主题联系；巴特劳赫施泰特已有德语节。我们要将它从当地活动提升为在梅泽堡、艾斯莱本、维滕贝格和巴特劳赫施泰特举办的真正州级节庆，吸引全德国热爱语言文化的爱国者。若能从2026年9月起由AfD州政府实施“deutschdenken”运动，我们就将创造一种全新的大众教育旅游，使该州成为所有德国爱国者向往的地方。',
        '议会发言：认同教育与旅游市场的结合',
        {'H1':('Merseburger Zaubersprüche, Luther und Goethe-Theater','明确历史资源和中世纪脉络'),
         'I1':('sprach- und kulturbegeisterte Patrioten aus ganz Deutschland','把全国爱国者作为共享认同的目标人群'),
         'T1':('Da viele Momente, in denen deutsche Identität','直接用历史身份形成地点推出旅游路线和节庆制度')},
        group='德国文化爱国者及州旅游目标群体')
    add('S004',10,web('S004',['P079','P081','P083']),
        '谈谈您发言的核心。您提出我忽视了多样性。——不，我们的提案恰恰是多样的。德国性的多样性清晰可见，而来自希腊的移民并不违背德国性。我想我在结尾也说清了：关键是，汇集到这里的多样性应在一个德国屋顶下统一，并受到德国性的塑造。',
        '议会答辩：在德国框架内有条件纳入多样性',
        {'I1':('unter einem deutschen Dach geeint und deutsch geprägt','明确共同体的统一与文化塑造尺度'),
         'B1':('eine Zuwanderung aus Griechenland widerspricht doch gar nicht','拒绝把一切移民都视为冲突，转而提出德国屋顶的条件性纳入边界')},
        group='德国共同体；有条件纳入外来者',stance='否定自己排除一切多样性的转述；肯定德国文化框架内的多样性')
    add('S004',11,web('S004',['P118']),
        '当然可以补上亨德尔。名单是开放的。若加入亨德尔能使这项提案对您而言可接受，我们就再加上亨德尔。那么请您投赞成票。',
        '议会答辩：名单可修改，表决对象不是公众',
        {'H1':('Händel können wir natürlich ergänzen.','把具体历史文化人物提议加入已明确的运动历史清单'),
         'T1':('Wenn der Antrag für Sie genießbar wird','将历史名单的修改直接置于当前提案协商中')},
        contexts='S003_U001',group='议员协商；非面向公众的投票动员',stance='向反对党议员提出增补与表决要求；不计公众行动A1')
    add('S004',12,web('S004',['P123']),
        '再说那个认为德国民族认同是十九世纪建构的愚蠢反驳。民族认同当然与所有文化认同及语言一样，是一种建构。但这并不意味着它任意、短暂或不稳定。在瓦尔特·冯·德·福格尔韦德那里已有体现民族意识、背后站着一个德国民族的文本——这一点我多少懂一些。您不必在那里摸自己的光头；事实就是如此。',
        '议会答辩：承认建构，同时主张历史深度',
        {'H1':('Walter von der Vogelweide','调用中世纪作者作为民族意识历史深度的资源；不认证其历史论断'),
         'I1':('ein deutsches Volk, das im Hintergrund steht','用历史文本建构跨时代德国民族'),
         'B1':('diesem blöden Einwand','与对手关于民族认同形成的观点明确对立'),
         'T1':('Aber das heißt nicht, dass es etwas Beliebiges wäre','把历史证据用于当下争论：承认建构却否定其任意短暂，主张稳定连续')},
        group='跨时代德国民族',stance='肯定认同是建构；否定由此推出任意／不稳定；不是作者接受仅十九世纪才形成的全部对手论断')
    add('S004',13,web('S004',['P020','P022']),
        '该州不仅有我们语言史的开端，也有我们国家政治史的开端。东法兰克王国的国王亨利一世葬于奎德林堡大教堂，我们的德国从那个王国而来。其子奥托一世葬于马格德堡大教堂，他被视为第一个德意志帝国的奠基者。两人都逝于该州南部的梅姆莱本。亨利也出生在梅姆莱本；奥托很可能出生在今天曼斯费尔德—南哈尔茨县的瓦尔豪森。没有一个州的王家行宫密度如此高，因此可以有理由说这里曾是中世纪帝国的中心。——图尔纳先生，您不用摇头，这个说法是我从您父亲的一本书中读来的。',
        '议会发言：奥托意义的上文，保留为定位及推断上下文',
        {'H1':('Heinrich I., König des Ostfrankenreiches','具体叙述国王、帝国及地方历史节点'),
         'F2':('Kein Bundesland weist eine solche Dichte an Kaiserpfalzen auf','明确以相对其他州的高密度历史资源肯定地方地位'),
         'I1':('aus dem unser Deutschland hervorging','把历史王国与我们德国连接，建构国家共同过去'),
         'T1':('im heutigen Landkreis','以今天地理标识定位共同历史，结合unser Deutschland的起源主张呈现连续性')},group='州—德国共同历史',f2='历史地位／相对独特性')

    add('P_LV_1129',1,web('P_LV_1129',['P004']),
        '周末我们高度团结地通过了一份执政纲领，要用它让我们美丽的州重新繁荣。它将成为由乌尔里希·西格蒙德领导的AfD州政府可能开展工作的内容基础。该纲领十分广泛，坚定主张恢复街道安全、减轻家庭负担并保障富裕，使该州成为付出终于再次值得的地方。我们的目标是充分满足公民对我们工作寄予的高期待。',
        '新闻稿：一般纲领与政府承诺的对照',{},group='州居民与政党组织',speaker='Martin Reichardt')
    add('P_LV_1129',2,web('P_LV_1129',['P006']),
        '代表们表现出的纪律也无与伦比，留下了令我充满巨大自豪的力量标志。对各章和修正案的讨论完全是建设性而目标明确的。',
        '新闻稿：自豪指向党内代表，非东部历史贡献',
        {'F2':('das mich mit großem Stolz erfüllt','明确自豪，但自豪对象是代表大会纪律及政党力量，不是东部共同体历史'),
         'I1':('Disziplin der Delegierten','结合代表大会语境，肯定作为组织共同体的代表集体；指向党组织而非州居民')},
        group='AfD代表大会／党组织',f2='政党组织成就／自豪',speaker='Martin Reichardt')
    add('P_LV_1235',1,web_slice('P_LV_1235',['P005'],'Wer 80 Prozent','sie wollen einen echten Politikwechsel.“'),
        '谁让百分之八十的公民反对联邦政府、百分之六十二反对州政府，谁就不再受人民委托执政，而是在绕过人民执政。州里的人不希望在一体化政党之间再换一批管理者，而希望真正的政策变化。',
        '新闻稿：当下代表缺失，无历史连接',
        {'F1':('regiert nicht mehr im Auftrag des Volkes','指控执政者脱离人民委托，属于代表／政治排斥框架；民调数字未独立核验'),
         'I1':('Die Menschen in Sachsen-Anhalt','明确构造具有共同政治愿望的州居民'),
         'B1':('zwischen den Einheitsparteien','把被视为同质的既有政党与人民愿望相对')},
        group='州居民／人民',f1='政治代表',speaker='Martin Reichardt',stance='党派对民意与代表关系的断言；不能当独立民调证据或选民接受历史叙事证据')
    add('P_LV_1235',2,web_slice('P_LV_1235',['P007'],'Wenn eine relative Mehrheit','mit beiden Stimmen die AfD wählen.“'),
        '若相对多数公民如今预期下届州政府由AfD领导，那是因为我们在内容上始终如一，也是因为州民深切希望有一个终于再次为本国人民施政的政府。我认真对待这一期待，但也明确说：单靠民调赢不了选举。9月6日之前，易北河还会流过许多水。我们保持踏实，继续做好且诚实的工作。真正想要变化而非州议会僵局的人，必须在9月6日把两票都投给AfD。',
        '新闻稿：为自己人民施政与明确投票号召',
        {'I1':('für das eigene Volk','界定政治服务对象为本国人民，结合州民愿望'),
         'R1':('unserer inhaltlichen Beständigkeit und dem tiefen Wunsch der Sachsen-Anhalter','以自身一致性及州民愿望论证AfD执政的资格，后续明确为自己人民施政'),
         'A1':('muss am 6. September mit beiden Stimmen die AfD wählen','明确面向公众的投票要求')},
        group='州居民／本国人民',speaker='Ulrich Siegmund')
    add('P_LV_1342',1,web('P_LV_1342',['P004']),
        '我热烈祝贺贡特·瓦坎首轮取得这个好结果。他领先所有竞争者，是个人成功，也是在当地多年可靠、贴近公民地工作的勤勉党员们的成功。我们可以为这种牢固的地方扎根感到自豪。结果说明，许多人希望政治变化。我祝瓦坎和所有支持者在第二轮充满力量。',
        '新闻稿：地方党组织成就与自豪，无历史资源',
        {'F2':('Auf diese starke regionale Verankerung können wir stolz sein.','明确对党员工作、候选人成绩与地方扎根表示自豪；不能改写为悠久地方历史贡献'),
         'I1':('unserer fleißigen Mitglieder vor Ort','把当地党员塑造为共享成就的组织共同体')},
        group='AfD地方党组织／支持者',f2='政党选举与组织成就／自豪',speaker='Martin Reichardt')
    add('P_LV_2306',1,web('P_LV_2306',['P003']),
        '我们敌人的暴力意愿和狂热已经没有边界。松动车辆轮螺母的人会造成严重事故，不仅将驾驶者、也将毫不相关者的死亡纳入风险。他们由此正在道德上接近当年RAF恐怖活动的水平。',
        '新闻稿：当代攻击与RAF恐怖的历史类比',
        {'H4':('damaligen RAF-Terrors','明确调用过去的RAF恐怖记忆，促使H4范围扩展为非DDR政治暴力；不补写文中未给年份'),
         'F1':('provoziert schwere Unfälle','将针对本方及无辜者的生命威胁描述为不正当伤害；是党派指控，未外部核实'),
         'I1':('unserer Feinde','以共同受威胁的我们／敌人关系构造党派共同体'),
         'B1':('heutigen Linksextremisten','把被指控行为归于今天的左翼极端分子；归责真实性不由本文分析认证'),
         'T1':('nähern sich die heutigen Linksextremisten','直接把今天行为与当年RAF作道德类比')},
        group='AfD及被描为受威胁者',f1='政治暴力／不正当伤害',speaker='Dr. Hans-Thomas Tillschneider',stance='党派对敌对攻击者的指控与历史类比；未外部事实核验')
    add('P_LV_2306',2,web('P_LV_2306',['P006','P007','P008']),
        '由SPD、绿党和左党在政治上多年助长的左翼街头恐怖再次发作。CDU因顾及可能的联合执政谈判而淡化它。这次遭袭的是一位在业余时间为本党工作的志愿者。我期待该州其他政党主席现在明确表态，谴责这类意在、或至少放任持不同政治观点者死亡的卑劣行为。这次攻击不会改变我们的竞选。我们不会被吓倒。',
        '新闻稿：攻击归责与本党受损，不含特定历史调用',
        {'F1':('auf den Tot politisch Andersdenkender abzielen','指控针对政治异见者的致命攻击；保留原文Tot拼写'),
         'I1':('Wir lassen uns nicht einschüchtern.','以本党竞选共同体表述共同威胁与决心'),
         'B1':('von SPD, Grünen und Linken politisch geförderte','明确归责其他政党及CDU的淡化行为')},
        group='AfD志愿者／竞选共同体',f1='政治暴力／不平等保护',speaker='Martin Reichardt',stance='党派攻击归责与要求其他党主席表态；不是面向公众的A1')
    add('P_LV_2381',1,web('P_LV_2381',['P005']),
        '我们的竞选正在进行。最新民调的百分之四十二和百分之四十九潜在支持率表明，我们朝着百分之四十五加X的目标前进。达到它，即使三个最小党中仅两个未进议会，我们也能执政。竞选旨在说服州里的人，我们准备好为这个州承担责任。为此，西格蒙德是合适的首席候选人。9月6日我们希望创造历史，以首届AfD州政府开启该州迫切需要的政治新开始。',
        '新闻稿：创造历史是未来修辞，不是过去叙事',{},group='党派竞选组织与州治理',speaker='Martin Reichardt')
    add('P_LV_2446',1,web('P_LV_2446',['P006','P007','P008']),
        '媒体尤其公共广播几乎未予关注，这已是该州AfD竞选人员第三次遇袭。此前有轮螺母被松动、十三岁少年面部遭拳击，这次除摊位财物受损外，两名本党直选候选人也遭攻击。这表明，被政治建制煽动的左派打手与罪犯已具有高度暴力性。受指令约束的宪法保卫机构、主流媒体及政治对手为竞选暴力化奠定了基础。它们随意且无依据的“纳粹”“右翼极端分子”标签，为暴力打手提供貌似的正当性。最近《明镜》把本党首席候选人西格蒙德称为德国最危险人物，是其中尤其煽动性的高点。谁长期片面报道、将民选政党代表非人化，谁就降低了实施此类行为的门槛，恶化社会气氛。对我们民主政党的攻击卑劣，理应被所有政党和媒体严厉谴责。它们未如此做，说明德国似乎有一等和二等受害者，也令人怀疑政治对手及部分媒体或许还为此高兴。',
        '新闻稿：媒体不承认与受害者等级；Nazi为当代标签',
        {'F1':('Opfer erster und zweiter Klasse','明确主张本党受害者被差别对待；不认证事件因果及媒体实际表现'),
         'I1':('unsere demokratische Partei','构造被侵害而自称民主的党组织共同体'),
         'B1':('Die Grundlagen für die Brutalisierung dieses Wahlkampfs','明确把暴力化归责政治建制、媒体和对手；不是本文研究者的事实归责')},
        group='AfD竞选人员／党组织',f1='尊重／承认与不平等保护',speaker='Martin Reichardt',stance='党派指控；转述并否定Nazi等标签，不据此赋历史NS记忆')
    add('P_LV_2446',2,web_slice('P_LV_2446',['P011','P012'],'Wenn wir in Regierungsverantwortung sind,'),
        '我们进入政府后，将充分使用法律对此类行为规定的刑罚幅度。我们不会实行宽纵司法，不论暴力来自右翼、左翼还是宗教方向。针对持不同观点者的攻击与暴力，应适用最高刑罚，以法治的一切严厉手段追究其责任。',
        '新闻稿：惩罚政策承诺，非公众行动号召',{},group='一般司法政策',speaker='Oliver Kirchner',stance='主张对各方向暴力同样处罚；不能把提到左右宗教自动赋为排斥某方')
    add('P_LV_2731',1,web('P_LV_2731',['P003']),
        '最新数字尤其证明：越来越多州民离开老牌政党，持续信任AfD。百分之四十二的结果显示，本州人已受够了管教、虚假竞选承诺、衰败、失控犯罪和一成不变。由舒尔策领衔的CDU继续失势并讨好左翼政党寻求联合执政，而我们是仅存的、可信地维护该州公民利益的政治力量。片面媒体报道和对手污名化运动，都阻挡不了人们要求根本政治变化。该州正面临方向选择，趋势不可逆：公民要转向。我们把这种强烈信任信号视为激励，继续走向一个安全、公正、有未来的州。',
        '新闻稿：无历史资源的唯一代表资格主张',
        {'F1':('Verleumdungskampagnen unserer politischen Gegner','明确声称遭污名化；未独立核验民调、污名化或趋势'),
         'I1':('Interessen unserer Bürger in Sachsen-Anhalt','构造有共同利益的州民'),
         'B1':('sind wir die einzige verbliebene politische Kraft','将CDU及左翼等竞争者置于不可信的代表一侧'),
         'R1':('glaubwürdig für die Interessen unserer Bürger in Sachsen-Anhalt einsetzt','直接主张AfD是可信维护州民利益的唯一力量')},
        group='萨克森—安哈尔特州公民',f1='象征贬损／政治排斥',speaker='Martin Reichardt',stance='党派对公众信任的自我陈述，不能据此证明真实选民接受或历史叙事效果')
    add('P_LV_2855',1,web('P_LV_2855',['P006']),
        '这些数字显示本州政治情绪发生了多大变化。但对我们而言，这不是可以松懈的理由。恰恰相反：民调不是选举结果。事情还没有定。',
        '新闻稿：民调不等于选举结果的反例',{},group='竞选程序判断，不是共同历史',speaker='Martin Reichardt')
    add('P_LV_2855',2,web('P_LV_2855',['P007']),
        '现在要在最后几天再次动员一切力量。和你们的朋友、家人、邻居谈，带上每个人去投票。想要政治变化的人，必须在9月6日把两票都投给AfD。',
        '新闻稿：无历史前提的公众投票号召',
        {'A1':('Sprecht mit euren Freunden, euren Familien und euren Nachbarn','明确要求公众交流并带人投票；后句给两票投AfD的要求')},
        group='被号召的公众与其社会网络',speaker='Martin Reichardt')


def extend_later(add):
    add('P_LV_1227',1,web('P_LV_1227',['P001']),
        '八十一年前的今天，德国国防军被迫无条件投降。对一切受纳粹政权迫害者、尤其包括德国人而言，这一天是从专断和不法中解放。但我们不能庆祝这种解放，因为代价是民族彻底战败、几乎全部基础设施被毁、数百万德国人被逐出家园，东部大片德国文化区域被切割。德国人民被一个犯罪政权带入无望处境。',
        '5月8日纪念：承认解放但拒绝庆祝',
        {'H4':('vom NS-Regime Verfolgten','明确调用NS迫害、战争失败、驱逐及领土损失；不是将政治标签当历史'),
         'F1':('einer Vertreibung Millionen deutscher Menschen aus ihrer Heimat','将德国人的驱逐和被犯罪政权带入绝境表述为受损经历；不抹去其同时承认NS受害者解放'),
         'I1':('Das deutsche Volk','共同体指向德国民族；地理上的im Osten为历史文化地区，不自动等于当代东部选民'),
         'B1':('von einem Verbrecherregime in eine ausweglose Lage manövriert','文本在此明确归责NS犯罪政权；不能替换为作者只归责同盟国')},
        group='德国民族；NS受迫害者亦被明确承认',f1='战争／驱逐损伤',speaker='Dr. Hans-Thomas Tillschneider',stance='肯定对受迫害者而言是解放；同时以民族灾难拒绝庆祝；不得删去前半限定')
    add('P_LV_1227',2,web('P_LV_1227',['P002','P003']),
        '据说恩斯特·荣格曾说：“这样的失败无法恢复。”这指向战败的精神后果：崩溃是一回事，如何应对是另一回事。战败最初几年还在追究真正有罪者并抵制德国民族集体罪责，随后却随时间产生越来越荒谬的罪责崇拜。想象中的永久集体罪责压在所有德国人身上，只能通过事后站到胜利者一边、把战败庆祝为解放来摆脱。军事投降四十年后，魏茨泽克1985年5月8日在联邦议院的讲话带来了精神投降。当时仍有三十位CDU议员保有民族自信，出于体面而不出席。今天，拒绝出席那些把战败庆祝为解放的讲话，成为AfD的责任。',
        '5月8日纪念：罪责叙事及从CDU异议者到AfD的角色转移',
        {'H4':('Richard von Weizäckers Rede am 8. Mai 1985','具体连接战争后果与1985年纪念讲话；荣格引语被原文以soll传闻式归属，未独立核验'),
         'F1':('imaginierte Kollektiv- und Dauerschuld','把全体德国人背负永久集体罪责描为想象的负担，属于象征／承认不公主张'),
         'F2':('Das nationale Selbstbewusstsein von immerhin 30 Bundestagsabgeordneten','肯定所述三十位历史CDU议员的民族自信与体面；对象不是AfD既有选民'),
         'I1':('auf allen Deutschen','以承受共同罪责的所有德国人为内群体'),
         'B1':('die Niederlage als Befreiung feierte','对纪念战败为解放的记忆实践划界；不能省略其前段对具体NS受害者解放的承认'),
         'T1':('Heute fällt es der AfD zu','明确把过去纪念争议的异议角色转移至当前AfD'),
         'R1':('Heute fällt es der AfD zu','AfD被自称赋予拒绝此类国家纪念的任务，连到捍卫民族自信；是历史角色继承主张')},
        contexts='P_LV_1227_U001',group='德国民族；历史CDU异议议员与当下AfD',f2='尊严／自信及道德肯定',speaker='Dr. Hans-Thomas Tillschneider')
    add('P_LV_1227',3,web('P_LV_1227',['P004']),
        'AfD代表一种完整德国民族情感的复兴，将之视为自信政治和有效利益代表的前提。我们以自己的行为反驳荣格的怀疑，表明：做德国人是好的！我们示范一种正常的德国认同。弗朗茨·约瑟夫·施特劳斯早在1986年已说：“把永恒反思过去变成社会性的永久赎罪任务，会使一个民族瘫痪！……我们是一个正常、勤勉、有能力的民族，不幸两次在国家领导层遭遇糟糕政治。”对此无需补充。',
        '5月8日纪念：民族肯定与代表资格的直接连接',
        {'H4':('Die ewige Vergangenheitsbewältigung als gesellschaftliche Dauerbüßaufgabe','明确承接战后罪责记忆争论；历史引语的原始归属未独立核验，分析对象是AfD如何引用'),
         'F1':('lähmt ein Volk','通过明确认可的施特劳斯引语批评永久集体赎罪的损伤，不把它误当被否定的对手说法'),
         'F2':('eine normale, tüchtige, leistungsfähige Nation','明示民族正常性、勤勉和能力，不只是历史人物出现'),
         'I1':('Es ist gut, deutsch zu sein','明确建构值得肯定的德国共同身份'),
         'T1':('Franz Josef Strauß hatte bereits 1986 erklärt','以历史引语解释并正当化当前政党的身份示范；原文末句明确赞同'),
         'R1':('Voraussetzung selbstbewusster Politik und effizienter Interessenvertretung','直接把AfD宣称的民族情感复兴与有效利益代表相连，证据不依靠跨文拼接')},
        contexts='P_LV_1227_U001|P_LV_1227_U002',group='德国民族，非特指东部德国人',f2='尊严／能力肯定',speaker='Dr. Hans-Thomas Tillschneider',stance='赞同所引施特劳斯观点，反驳所称荣格怀疑；引语归属未外部核验')
    add('P_LV_1203',1,web('P_LV_1203',['P006']),
        '声明指责我们把文化变成“制造由党派政治定义的集体身份的工具”。但文化本质上恰恰就是制造集体身份的工具。这种身份并非党派政治定义，而是以德国、俄罗斯、法国等身份的形式存在。文化若拒绝这个事实，就与自身矛盾。谁认为民族身份是“党派政治的”，谁自身就受到党派政治扭曲了认识。',
        '文化声明回应：赞同集体身份功能，否认党派定义',
        {'I1':('deutsche, russische, französische etc. Identität','明确把文化共同体组织为民族身份；不能把引用的党派定义当作作者赞同'),
         'B1':('leidet selbst unter parteipolitisch deformierter Wahrnehmung','对质疑民族认同文化政策者作认知归责')},
        group='民族文化共同体（以德国为主要对象）',speaker='Dr. Hans-Thomas Tillschneider',stance='赞同文化制造集体身份；明确否定该身份由党派政治定义的转述')
    add('P_LV_1203',2,web('P_LV_1203',['P008']),
        '这套空话让人失去继续讨论的兴趣。只说一点：签署者指责我们的记忆政治把重点从“基于科学认识的、分化的记忆文化”移向“选择性历史呈现”。且不说任何记忆文化都不以科学即逻各斯为基础，而以神话为基础，记忆本身也总与遗忘相关，因此必然具有选择性。',
        '记忆元论证：以神话、遗忘和选择性反驳批评',
        {'B1':('Die Unterzeichnenden werfen uns vor','与文化机构签署者对记忆政策的批评形成对立；作者反对他们认为选择性本身构成缺陷的立场')},
        group='记忆政策的竞争者；未在本单元具体指认历史事件',speaker='Dr. Hans-Thomas Tillschneider',stance='转述批评并反驳；肯定记忆必然选择性，不等于研究者承认科学无关')
    add('P_LV_1203',3,web('P_LV_1203',['P009']),
        '因此问题在于选择哪一种选择性：一种肯定认同、在不作政治纠缠的从容中与本民族文化和解的选择性；还是一种敌视认同、与本民族文化关系拘束并使文化服从左派教条的选择性。AfD执政后将向本州所有善意文化机构伸手合作，使文化摆脱这份拙劣反AfD檄文所体现的非法政治影响。',
        '记忆元论证：民族身份准则与AfD文化解放者',
        {'I1':('eigenen Nationalkultur','以本民族文化及肯定身份为共同体尺度'),
         'B1':('identitätsbejahende Selektivität','明确对立身份肯定／敌视两种记忆选择，并归责左派教条'),
         'R1':('um die Kultur von unzulässiger politischer Einflussnahme','AfD自称将把文化从不正当影响中解放并保护善意文化机构，超过一般资金承诺')},
        contexts='P_LV_1203_U002',group='德国民族文化共同体／本州文化机构',speaker='Dr. Hans-Thomas Tillschneider')
    add('P_LV_1132',1,web('P_LV_1132',['P005']),
        '教会领袖应证明他们所谓“人的尊严”“自由权”具体指什么，以及我们的要求为何与之相冲突。“害怕变化”是老牌政党用来把公民反对其改革——其实总是恶化——的抵抗心理化并削弱它的套话。抵抗不再被认真就事论事看待，而被当作恐惧表达。自称神职人员者也参与这种卑劣游戏，令人失望。',
        '教会批评回应：承认不足，不补入历史',
        {'F1':('nicht mehr sachlich ernst genommen','明确主张公民抵抗被心理化、被拒绝认真对待；是承认不足'),
         'I1':('Widerstand der Bürger','构造具有共同抵抗及受贬经历的公民'),
         'B1':('von den Altparteien verwendet','将心理化归于老牌政党及参与的教会领袖')},
        group='抵制改革的公民',speaker='Dr. Hans-Thomas Tillschneider')
    add('P_LV_1132',2,web('P_LV_1132',['P007']),
        '尤其令人失望的是教会也参与廉价抨击父权。基督教会应看到，社会危机的重要原因是失去了好父亲这一稳定性人物。敬奉亚伯拉罕、以撒、雅各为族长的基督徒，本应对父权有更多话可说。古代教会按宗主教区组织，这在东正教会及教皇制度中延续。我们的上帝观念本身以父子关系为基础。教会领袖却轻蔑谈论“父权角色模式”，除了撒旦启示还能如何解释？',
        '圣经与教会历史用于当代家庭规范',
        {'H1':('Abraham, Issak und Jakob','调用圣经人物与古代教会组织；保留原文Issak拼写，宗教历史叙事并非研究者考证史实'),
         'I1':('Unsere Vorstellung von Gott','构造基督教信仰共同体的共享观念'),
         'B1':('Kirchenobere abfällig über','将教会领袖批评父权的立场与作者的传统解释对立'),
         'T1':('in den orthodoxen Kirchen, aber auch im Papsttum, weiterleben','以古代教会、圣经人物和延续的父子结构论证今天应维护好父亲角色')},
        group='基督徒／信仰共同体',speaker='Dr. Hans-Thomas Tillschneider')
    add('P_LV_725',1,web('P_LV_725',['P003']),
        '萨克森—安哈尔特州AfD副主席汉斯—托马斯·蒂尔施奈德说：“一面妖魔化一个比其他任何党都更为德国基督教奋斗的政党，一面主张在教堂悬挂彩虹旗的人，自己就表明了属于什么精神阵营。',
        '教会争议：AfD作为基督教独特维护者',
        {'F1':('eine Partei verteufelt','主张本党遭妖魔化，非东部历史物质不公'),
         'B1':('gleichzeitig dafür plädiert, die Regenbogenfahne','将排斥AfD与支持彩虹旗相连，批评教会领袖的阵营立场'),
         'R1':('wie keine andere Partei für das Christentum in Deutschland kämpft','明确自称比其他党更捍卫德国基督教；代表对象为宗教共同体')},
        group='德国基督教共同体及AfD',speaker='Dr. Hans-Thomas Tillschneider')
    add('P_LV_725',2,web('P_LV_725',['P005']),
        '剩下的认识是，德国新教会完全陷于对抗上帝者之手，无可挽救地迷失。我们建议这所机构所有仍在籍者，最好今天而非明天退出，另找一家忠于信仰的小教会；感谢上帝，德国还有多家这样的教会。',
        '教会争议：明确退会行动，未调用历史事件',
        {'B1':('völlig dem Widersacher verfallen','对现有教会与忠于信仰的小教会划界'),
         'A1':('besser heute als morgen auszutreten','明确对教会成员提出退会并转向其他教会的要求；不把A1限为投票')},
        group='被号召的在籍新教会成员',speaker='Dr. Hans-Thomas Tillschneider')
    add('P_LV_682',1,web('P_LV_682',['P004']),
        '虽然德尼兹·于杰尔明确表示，在他看来该书展参展者从右翼到激进右翼都有，但他反对把“右翼”不加区分地等同“右翼极端”，并说言论自由当然也适用于右翼作者。理由很清楚：这里读书、交流思想，并非实施暴力，这必须被容忍。于杰尔批评，有时言论自由被理解为药品说明书上的小字。总的说来，他认为行政机关因言论犯罪过快启动禁令及刑事程序。这些真实而勇敢的话，让我们向于杰尔致敬。',
        '文化争议反例：赞扬外部批评者的自由立场',
        {'F1':('Meinungsfreiheit selbstverständlich auch für rechte Autoren gilt','作者明确认可所转述的言论自由保护立场及反对过快处罚，涉及政治表达排斥'),
         'B1':('undifferenzierte Gleichsetzung von ‚rechts‘ und ‚rechtsextrem‘','作者赞同对两类政治标签作区分；对立对象不是被赞扬的于杰尔')},
        group='右翼作者及表达自由主体；赞扬对象为外部作家组织发言人',speaker='Dr. Hans-Thomas Tillschneider',stance='认可被引述于杰尔的自由立场；不把个别勇敢者赞扬当作本群体历史贡献F2')
    add('P_LV_679',1,web('P_LV_679',['P005']),
        '赖夏特续称：“舒尔策站在一艘下沉的船头。CDU执政该州十四年后，内容枯竭、政治失去方向、民调下跌。但他不是纠正方向，而是靠左翼多数保权。CDU由此背叛自己的选民，再次让该州成为左派意识形态者的玩物。因此，对抗舒尔策领导的左转联盟，只有一个强大的AfD单独政府才有用。”',
        '代表资格反例：当下选民背叛，无历史文化前提',
        {'F1':('verrät die CDU ihre eigenen Wähler','明确指控对选民意愿的背叛；不是自动认为十四年等同统一后转型'),
         'I1':('macht Sachsen-Anhalt erneut zum Spielball','在州共同命运受操纵的框架中构造地方共同体'),
         'B1':('Machterhalt durch linke Mehrheiten','归责CDU联合左派保权'),
         'R1':('hilft nur eine starke AfD-Alleinregierung','明确把AfD单独政府呈为保护州免于该联盟的唯一方案')},
        group='州居民／被声称背叛的CDU选民',f1='政治代表',speaker='Martin Reichardt')
    add('P_LV_432',1,web('P_LV_432',['P002','P003']),
        'CDU几十年来把我们的州治理得衰败：经济下滑、街道不安全、完全失控的大规模移民造成乡土被出卖。部委成为安插职位的地方，数十亿流向亲党结构，州里的人却被丢下，独自面对忧虑。2026年我们有机会结束这条路线。AfD不会管理衰落，而要把安全、强大经济、良好教育和可靠基础设施置于中心。我们明确说：政治必须终于再次代表该州人民的利益！',
        '共同利益与乡土受损，无具体统一回溯',
        {'F1':('während die Menschen im Land mit ihren Sorgen allein gelassen wurden','明确主张州民被治理者抛下，涉及政治承认与代表缺失'),
         'I1':('Interessen der Menschen in Sachsen-Anhalt','以地方共同利益塑造州民'),
         'B1':('Die CDU hat unser Land','把衰败及利益忽视归于CDU'),
         'R1':('Mit der AfD gibt es keine Verwaltung des Niedergangs','对比CDU并明确承诺恢复州民利益代表，结合后句得出维护者主张')},
        group='萨克森—安哈尔特州居民',f1='政治代表／承认',speaker='AfD Landesverband Sachsen-Anhalt')
    add('P_LV_432',2,web('P_LV_432',['P005']),
        '有你们支持，我们将把我们的州夺回来。为了我们的孩子，为了我们的未来，为了萨克森—安哈尔特。',
        '共同未来与支持号召，无具体历史',
        {'I1':('Für unsere Kinder. Für unsere Zukunft.','以共同后代与未来建构州的共同命运'),
         'A1':('Mit eurer Unterstützung','面向公众寻求支持，并连到共同州未来；行动形式未明确为投票，不补入具体投票命令')},
        group='州居民及其下一代',speaker='AfD Landesverband Sachsen-Anhalt')
    add('P_LV_1218',1,web('P_LV_1218',['P004']),
        '文教部长联席会议规定，四分即及格至少需达到满分的百分之四十五。我们希望百分之五十才给及格。想通过考试，至少该知道一半。各科教育标准也将提高。通过这些及一系列措施，使该州高中毕业考试成为全德国最好的。我们不必害怕同其他州比较，但其他州或许害怕与我们比较。至少，相比之下更有理由担心不来梅高中毕业生的资格。',
        '领先地位反例：未来教育标准，无历史贡献',
        {'F2':('zum besten Abitur in ganz Deutschland','明确要求州取得全国最佳示范地位；是未来目标，不是已经存在的文化优越事实'),
         'B1':('Qualifikation der Abiturienten aus Bremen','通过贬低不来梅的资格形成州际比较')},
        group='州教育／未来高中毕业生',f2='示范／领先（未来目标）',speaker='Dr. Hans-Thomas Tillschneider')
    add('P_LV_1290',1,web('P_LV_1290',['P008']),
        '萨勒县县长选举中的这个强烈信号是政治震动。本党候选人乌韦·阿伦特以百分之四十三点三明显击败联盟党候选人。结果为九月州选带来巨大动力，因为它显示全州达到百分之四十三加X是可能的。现在要凝聚力量，赢得六月二十八日的第二轮，使阿伦特成为该州首位AfD县长。',
        '当下选举成就与动员；不把第一位当长时段历史',
        {'F2':('ein politischer Paukenschlag','明确肯定本党选举表现与候选人成就；不是东部历史贡献'),
         'I1':('Unser Kandidat','结合本党共同行动与成就，指向党组织共同体'),
         'A1':('Jetzt gilt es, die Kräfte zu bündeln','面向支持者凝聚力量争取第二轮胜选；具体说话对象为公开新闻稿读者，解释性判断')},
        group='AfD组织／支持者',f2='政党选举成就',speaker='Martin Reichardt')


def export(units,pilot):
    now=dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo('Asia/Shanghai')).isoformat()
    path=ROOT/'inputs/final_ai_decisions.json'
    if path.exists():raise SystemExit('Final decisions already exist; version before replacing')
    mismatches=[(u['unit_id'],code,pair[0]) for u in units for code,pair in {**u['ones'],**u['questions']}.items() if pair[0] not in u['german_original']]
    assert not mismatches,mismatches
    path.write_text(json.dumps(dict(version='v0.3',coder='AI',created_at=now,units=units),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (ROOT/'segments.csv').open(encoding='utf-8',newline='') as handle:segment_fields=next(csv.reader(handle))
    with (ROOT/'coding.csv').open(encoding='utf-8',newline='') as handle:coding_fields=next(csv.reader(handle))
    with (ROOT/'segments.csv').open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=segment_fields);writer.writeheader()
        writer.writerows({f:u.get(f,'') for f in segment_fields} for u in units)
    pilot_values={}
    for row in csv.DictReader((ROOT/'pilot_coding.csv').open(encoding='utf-8',newline='')):
        pilot_values[(row['unit_id'],row['code'])]=row['value']
    output=[]
    for u in units:
        assert u['reviewed_codes']==CODES
        for code in CODES:
            value='0';evidence='';reason=ZERO[code];kind='阅读后排除'
            if code in u['ones']:
                value='1';evidence,reason=u['ones'][code];kind='直接表达'
                if any(term in reason for term in ['回指','结合','语境','解释性','前页','上下文']):kind='明确上下文或解释性推断'
                if code in u.get('inference_codes',[]):kind='解释性推断，待人工复核'
            if code in u['questions']:
                value='?';evidence,reason=u['questions'][code];kind='边界待决'
            if evidence:assert evidence in u['german_original'],(u['unit_id'],code,evidence)
            row={field:'' for field in coding_fields}
            original=pilot_values.get((u['unit_id'],code),'')
            row.update(source_id=u['source_id'],unit_id=u['unit_id'],code=code,value=value,
                german_evidence=evidence,chinese_explanation=reason,
                decision_reason=f"已阅读单元的议题为「{u['topic']}」。{reason}",
                subtype=(u.get('f2_type','') if code=='F2' and value!='0' else u.get('f1_type','') if code=='F1' and value!='0' else ''),
                group_referent=u.get('group_referent',''),speaker=u['speaker'],speaker_stance=u['speaker_stance'],
                expression_type=kind,context_unit_ids=u['context_unit_ids'] if value in ['1','?'] else '',
                context_link_reason=reason if kind!='直接表达' and value in ['1','?'] else '',
                codebook_version='v0.3',coder='AI',coding_status='AI初编',human_review_status='未人工复核',
                original_ai_value=original,human_value='',revision_reason=(u.get('ai_revision_reason','') if original and original!=value else ''),coded_at=now)
            output.append(row)
    with (ROOT/'coding.csv').open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=coding_fields);writer.writeheader();writer.writerows(output)
    with (ROOT/'inputs/active_codes.csv').open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=['code','name','codebook_version','empirical_status']);writer.writeheader()
        names=['长时段历史人物与文化资源','DDR统治与反抗经验','统一后转型记忆','战争、殖民、NS与其他政治暴力记忆','不公待遇或象征贬损','贡献、尊严、自豪或优越性','内群体建构','责任归属或他者划界','历史与当下连接','政党代表资格','政治行动号召','记忆选择的正当化']
        writer.writerows(dict(code=c,name=n,codebook_version='v0.3',empirical_status='AI试用并回溯编码；未人工复核') for c,n in zip(CODES,names))
    with (ROOT/'logs/process_runs.jsonl').open('a',encoding='utf-8') as handle:
        handle.write(json.dumps(dict(script='build_final_coding.py',executed_at=now,units=len(units),
            sources=len(set(u['source_id'] for u in units)),codes=len(CODES),judgments=len(output),
            questions=sum(r['value']=='?' for r in output),human_review=False),ensure_ascii=False)+'\n')
    print(json.dumps(dict(units=len(units),sources=len(set(u['source_id'] for u in units)),judgments=len(output),questions=sum(r['value']=='?' for r in output)),ensure_ascii=False))


if __name__=='__main__':main()
