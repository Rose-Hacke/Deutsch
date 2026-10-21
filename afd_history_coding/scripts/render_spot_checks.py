#!/usr/bin/env python3
"""Re-render PDF pages used in the AI visual spot check; rendering alone is not semantic review."""
import csv
import json
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]


def main():
    sources={r['source_id']:r for r in csv.DictReader((ROOT/'sources.csv').open(encoding='utf-8',newline=''))}
    records=[]
    for sid,page,note in [('S002',56,'核对历史人物及贡献段、文字层断词'),('S002',58,'确认Revolution未注明年份；保留间接引语及优越性措辞'),('S003',4,'核对原文beigetraten拼写、理由段和签名')]:
        document=fitz.open(ROOT/sources[sid]['local_filename'])
        path=ROOT/f'checks/{sid}_PDF{page}.png'
        document[page-1].get_pixmap(matrix=fitz.Matrix(1,1)).save(path)
        records.append(dict(source_id=sid,pdf_page_index=page,image_path=str(path.relative_to(ROOT)),
            ai_visual_check='已在本次任务调用图像查看工具核对；非人类复核',note=note))
    (ROOT/'logs/visual_spot_checks.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'rendered_recorded_spot_checks':len(records),'ocr_used':False})


if __name__=='__main__':main()
