#!/usr/bin/env python3
"""Preserve raw files; extract page/paragraph-located reading copies without semantic coding."""
import csv
import datetime as dt
import json
import re
import subprocess
from pathlib import Path
from lxml import html
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def normalize(text):
    return re.sub(r'\s+', ' ', text.replace('\u00ad', '')).strip()


def main():
    with (ROOT / 'sources.csv').open(encoding='utf-8', newline='') as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    counts = {}
    for row in rows:
        if not row['local_filename']:
            continue
        raw = ROOT / row['local_filename']
        if raw.suffix == '.json':
            # Official API responses contain several posts; materialize_api.py selects by post.id.
            continue
        sid = row['source_id']
        records = []
        if raw.suffix == '.pdf':
            result=subprocess.run(['pdftotext','-layout',str(raw),'-'],capture_output=True,check=True)
            pages=result.stdout.decode('utf-8').split('\f')
            if pages and not pages[-1].strip():pages.pop()
            for i, text in enumerate(pages, 1):
                # Keep original text-layer line breaks. Quotes may be normalized only transparently.
                records.append({'locator': f'PDF:{i}', 'pdf_page_index': i,
                    'printed_page': '', 'text': text, 'extraction': 'Poppler pdftotext -layout文字层，未OCR'})
        else:
            tree = html.fromstring(raw.read_bytes())
            if sid == 'S004':
                roots = tree.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," transcript-wrapper ")]')
                selector = 'div.transcript-wrapper'
            elif sid.startswith('M'):
                roots = tree.xpath('//article') or tree.xpath('//body')
                selector = 'article或body'
            else:
                roots = tree.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," entry-content ")]') or tree.xpath('//main') or tree.xpath('//body')
                selector = 'entry-content、main或body'
            for root in roots:
                for junk in root.xpath('.//script|.//style|.//nav|.//header|.//footer|.//noscript'):
                    junk.drop_tree()
                nodes = root.xpath('.//p|.//h1|.//h2|.//h3|.//h4|.//li[not(.//p)]')
                if not nodes:
                    nodes = [root]
                for node in nodes:
                    text = normalize(node.text_content())
                    if text:
                        records.append({'locator': f'P{len(records)+1:03}', 'text': text,
                                        'html_tag': node.tag, 'selector': selector})
        filename = f'clean/{sid}_located.json'
        target = ROOT / filename
        # A new extraction may refresh this derived copy; immutable versions remain in raw/.
        target.write_text(json.dumps({'source_id': sid, 'raw_path': row['local_filename'],
            'raw_sha256': row['sha256'], 'records': records}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        (ROOT / f'clean/{sid}.txt').write_text('\n\n'.join(f"[{r['locator']}]\n{r['text']}" for r in records)+'\n', encoding='utf-8')
        row['clean_filename'] = filename
        row['readability'] = '文字层或网页正文可读取；拟引用片段需逐项核对'
        counts[sid] = len(records)
    with (ROOT / 'sources.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    now = dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo('Asia/Shanghai')).isoformat()
    with (ROOT / 'logs/process_runs.jsonl').open('a', encoding='utf-8') as log:
        log.write(json.dumps({'script':'extract_texts.py','executed_at':now,'record_counts':counts,
            'ocr_executed':False,'semantic_coding_executed':False},ensure_ascii=False)+'\n')
    print(json.dumps(counts,ensure_ascii=False))


if __name__=='__main__':
    main()
