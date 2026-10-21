#!/usr/bin/env python3
"""Build a standalone bilingual review page; it does not assert or save human review completion."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    data={}
    for key in ['segments','coding','sources']:
        with (ROOT/f'{key}.csv').open(encoding='utf-8',newline='') as handle:data[key]=list(csv.DictReader(handle))
    payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AfD历史叙事：AI初编审阅</title><style>
body{font-family:system-ui,"Microsoft YaHei",sans-serif;margin:24px auto;padding:0 18px;max-width:1160px;line-height:1.6;background:#f7f7f4;color:#19242d}h1{font-size:26px}header,.unit{background:white;padding:22px;border:1px solid #d9dfdf;border-radius:10px;margin-bottom:18px}label{display:inline-block;margin:8px 14px 8px 0}input,select{padding:7px;max-width:460px}a{color:#005a80}.meta{font-size:14px;color:#53616a}.texts{display:grid;grid-template-columns:1fr 1fr;gap:22px}.german,.chinese{white-space:pre-wrap}table{border-collapse:collapse;width:100%;font-size:14px;margin-top:15px}th,td{text-align:left;padding:8px;border-bottom:1px solid #ddd;vertical-align:top}th{background:#eef3f4}.v1{color:#18633c;font-weight:bold}.vq{color:#934b00;font-weight:bold}.v0{color:#66727a}details{margin-top:12px}code{font-size:13px}#count{font-weight:600}@media(max-width:760px){.texts{grid-template-columns:1fr}table{font-size:12px}th,td{padding:5px}}
</style><header><h1>AfD历史叙事：AI初编审阅</h1><p>暂定工作范围：2025-01-01至2026-09-06。19份已定年核心来源＋1份日期待核补充；70个选定意义单元，840项判断。<strong>全部尚未人工复核。</strong></p><p>0＝阅读后排除，1＝符合规则，?＝待决；中文为AI辅助译文。此页用于查看，审核决定请保存在CSV副本，不能把打开页面当作完成复核。</p>
<p><a href="README.md">项目说明</a> · <a href="codebook.md">编码手册</a> · <a href="coding.csv">完整编码CSV</a> · <a href="review_queue.csv">人工复核队列</a> · <a href="method_draft.md">方法初稿</a></p>
<label>来源 <select id="source"><option value="">全部</option></select></label><label>代码 <select id="code"><option value="">全部</option></select></label><label><input type="checkbox" id="questions">只看有?的单元</label><label>查找 <input id="query" placeholder="单元ID、德语或中文"></label><p id="count"></p></header><main id="list"></main>
<script id="data" type="application/json">PAYLOAD</script><script>
const D=JSON.parse(document.getElementById('data').textContent),bySource=Object.fromEntries(D.sources.map(s=>[s.source_id,s])),byUnit={};for(const c of D.coding)(byUnit[c.unit_id]??=[]).push(c);
const el=(tag,text,cls)=>{const x=document.createElement(tag);if(text!==undefined)x.textContent=text;if(cls)x.className=cls;return x};
const source=document.getElementById('source'),code=document.getElementById('code'),questions=document.getElementById('questions'),query=document.getElementById('query');
for(const id of [...new Set(D.segments.map(s=>s.source_id))].sort()){const o=el('option',id+' · '+bySource[id].title);o.value=id;source.append(o)}for(const c of [...new Set(D.coding.map(c=>c.code))]){const o=el('option',c);o.value=c;code.append(o)}
function render(){const list=document.getElementById('list');list.replaceChildren();const q=query.value.toLocaleLowerCase();let n=0;for(const u of D.segments){const codes=byUnit[u.unit_id],visible=codes.filter(c=>(!code.value||c.code===code.value));if(source.value&&source.value!==u.source_id)continue;if(questions.checked&&!visible.some(c=>c.value==='?'))continue;if(q&&!(u.unit_id+' '+u.german_original+' '+u.chinese_translation).toLocaleLowerCase().includes(q))continue;n++;const card=el('article',undefined,'unit');card.id=u.unit_id;card.append(el('h2',u.unit_id+' · '+u.section));const s=bySource[u.source_id];card.append(el('p',s.title+' | '+s.inclusion_decision,'meta'));card.append(el('p','印刷页：'+(u.printed_page||'不适用')+'；PDF页序：'+(u.pdf_page_index||'不适用')+'；网页／API段落：'+(u.web_paragraph_locator||'不适用')+'；发言者：'+u.speaker,'meta'));const link=el('a','打开原始来源');if(s.original_url.startsWith('https://'))link.href=s.original_url;link.target='_blank';link.rel='noopener';card.append(link);const texts=el('div',undefined,'texts');for(const [label,text,cls] of [['德语原文',u.german_original,'german'],['中文AI辅助译文（待人工复核）',u.chinese_translation,'chinese']]){const box=el('section');box.append(el('h3',label),el('p',text,cls));texts.append(box)}card.append(texts);const table=el('table'),head=el('tr');for(const h of ['代码／值','德语证据','中文理由／边界'])head.append(el('th',h));table.append(head);for(const c of visible){const tr=el('tr');tr.append(el('td',c.code+' = '+c.value,c.value==='1'?'v1':c.value==='?'?'vq':'v0'),el('td',c.german_evidence||'阅读后排除，见理由'),el('td',c.chinese_explanation));table.append(tr)}card.append(table);const details=el('details');details.append(el('summary','上下文与立场'));details.append(el('p','上下文ID：'+(u.context_unit_ids||'无额外单元')+'；'+u.context_relation),el('p',u.speaker_stance),el('p',u.translation_status));card.append(details);list.append(card)}document.getElementById('count').textContent='当前显示 '+n+' / '+D.segments.length+' 个选定意义单元。'}
for(const x of [source,code,questions,query])x.addEventListener('input',render);render();
</script></html>'''.replace('PAYLOAD',payload)
    (ROOT/'review.html').write_text(page,encoding='utf-8')
    print({'review_units':len(data['segments']),'judgments':len(data['coding']),'external_dependencies':0})


if __name__=='__main__':main()
