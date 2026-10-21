#!/usr/bin/env python3
"""Correct printed-page labels using the inspected PDF layouts; preserve PDF indices separately."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    changes=[]
    for filename in ['segments.csv','pilot_segments.csv']:
        path=ROOT/filename
        with path.open(encoding='utf-8',newline='') as handle:
            reader=csv.DictReader(handle);fields=reader.fieldnames;rows=list(reader)
        for row in rows:
            if row['pdf_page_index']:
                pages=[int(p) for p in row['pdf_page_index'].split(',')]
                printed=('首页未标印刷页码'+('；印刷第'+','.join(map(str,pages[1:]))+'页' if len(pages)>1 else '')) if row['source_id']=='S003' and pages[0]==1 else '—'.join(map(str,[pages[0],pages[-1]])) if len(pages)>1 else str(pages[0])
                if row['printed_page']!=printed:
                    changes.append(dict(file=filename,unit_id=row['unit_id'],old=row['printed_page'],new=printed));row['printed_page']=printed
                if row['source_id']=='S002':
                    chapter='PRÄAMBEL' if pages[0]<10 else 'IX. Wirtschaft und Tourismus' if pages[0]==151 else 'XIII. Verkehr und Infrastruktur' if pages[0]==200 else 'XV. Medien' if pages[0]==219 else 'III. Kultur und Integration'
                    if not row['section'].startswith(chapter+' | '):row['section']=chapter+' | '+row['section']
                if row['source_id']=='S003':
                    n=int(row['unit_id'].rsplit('U',1)[1]);chapter={1:'Antrag Nr.2',2:'Begründung Abs.1',3:'Begründung Abs.2',4:'Antrag Nr.1',5:'Antrag Nr.3a',6:'Antrag Nr.3b',7:'Antrag Nr.3e',8:'Antrag Nr.3h'}[n]
                    if not row['section'].startswith(chapter+' | '):row['section']=chapter+' | '+row['section']
        with path.open('w',encoding='utf-8',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    with (ROOT/'logs/locator_corrections.json').open('w',encoding='utf-8') as handle:json.dump(changes,handle,ensure_ascii=False,indent=2)
    print(json.dumps(dict(printed_page_labels_corrected=len(changes)),ensure_ascii=False))


if __name__=='__main__':main()
