#!/usr/bin/env python3
"""Package the review documents separately; original archives remain in the full ZIP."""
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
FILES=[
    'README.md','review.html','sources.csv','segments.csv','codebook.md','coding.csv',
    'review_queue.csv','narrative_memo.md','method_draft.md','narrative_chains.csv',
    'pilot_report.md','pilot_segments.csv','pilot_coding.csv','selection_audit.csv',
    'code_distribution.csv','f1_f2_comparison.csv','source_code_matrix.csv',
    'code_cooccurrence.csv','search_protocol.md','logs/validation_report.json',
]


def main():
    target=ROOT.parent/'afd_history_review_only.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:archive.write(ROOT/name,'afd_history_review/'+name)
        archive.writestr('afd_history_review/轻量版说明.txt',
            '此包用于审阅，包含研究正文、编码表、复核队列及独立HTML审阅页；不含原始PDF、网页存档、clean目录或执行脚本。'
            '完整原始材料仍在afd_history_coding.zip中。全部语义判断仍为AI初编，未人工复核。\n')
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:raise SystemExit('Archive integrity check failed')
        print(json.dumps(dict(zip_path=str(target),bytes=target.stat().st_size,
            files=len(archive.namelist()),integrity='passed'),ensure_ascii=False))


if __name__=='__main__':main()
