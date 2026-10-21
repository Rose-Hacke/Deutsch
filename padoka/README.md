# PADOKA 议会文件数据库

来源：[萨克森—安哈尔特州议会 PADOKA](https://padoka.landtag.sachsen-anhalt.de/portal/browse.tt.html)。

本次范围由用户指定为 **2025-01-01 至 2026-10-21（含首尾）**，使用网站“Dokumente”搜索、议会第8与第9届、日期筛选取得记录，涵盖全部主题与党派。时间依据网站的 `DAT,DDAT,SDAT` 日期索引；不是网页发布日期或 PDF 创建时间。网站会把多条议事底层记录合并为一条文档展示记录，因此底层命中数与数据库记录数不同。

本次已完成：**5,800 条文档记录、3,856 份公开 PDF（5.22 GB）、3,853 份 PDF 的全文提取**。另有 3 份没有可提取文本，原始 PDF 已保存；2,424 条目录记录没有公开附件链接。完整性检查及外键检查通过，详细统计见 `data/summary.json`。

## 下载与查询

- [下载 SQLite 数据库](https://github.com/Rose-Hacke/Deutsch/raw/refs/heads/main/padoka/data/padoka.sqlite.gz)（压缩约85 MB）：解压成 `padoka.sqlite` 后，使用 **DB Browser for SQLite** 或 `sqlite3` 打开；下方 Python 检索程序也会在首次运行时自动解压。
- `data/records.csv`：文档标题、原始书目信息、日期、编号、来源链接和来源 ID；UTF-8 BOM，便于 Excel 导入。
- `data/files.csv`：每个公开附件的原始 URL、下载状态、文件路径、SHA-256、大小和失败原因。
- `data/record_files.csv`：文档与附件的多对多关系。
- `data/summary.json`：实际记录数、文件数、全文提取情况、完整性检查结果。
- `evidence/`：搜索结果的原始 HTML 压缩存档，以及页码、抓取时间和校验值，便于复核。
- `ARCHIVE.md`：同一仓库存档分支中的 PDF 原文下载入口。每个 ZIP 分卷可独立解压；把 `files/` 解压到本目录，即可与数据库中的路径对应。

安装 Python 依赖后可搜索标题、书目信息及已提取的 PDF 全文：

```bash
cd padoka
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python padoka.py search 'Erinnerungskultur'
python padoka.py search '"AfD" AND "Geschichte"' --limit 30
```

SQL 查询例子见 [examples.sql](examples.sql)。德文标题与原文保持原样，没有自动翻译或政治倾向编码。

## 重现与继续下载

```bash
python padoka.py crawl --start 2025-01-01 --end 2026-10-21 --periods 9,8
python padoka.py download --workers 3 --delay 0.35
python padoka.py extract
python padoka.py export
```

`extract` 需要 Poppler 的 `pdftotext`（Ubuntu/Debian：`sudo apt install poppler-utils`）。扫描件没有可提取文本时会标记 `empty_scan_or_no_text`；本次没有 OCR。下载过程验证 PDF 文件头与 SHA-256；已经存在且校验通过的文件会跳过。重新抓目录使用 `crawl --refresh`，下载失败的链接可再次运行 `download` 重试。为了保持来源快照的一致性，目录刷新会重新分页核对全部结果；附件下载可以按文件恢复。

网站搜索结果有时包含标注“nicht öffentlich”的目录记录，或只列元数据而不提供附件。这些记录保留在数据库中，没有公开 URL 就不尝试猜测或访问文件。失败下载另有状态；“没有公开链接”与“下载失败”分开统计。不会绕过登录或权限限制。

## 数据结构与核验

| 表 | 内容 |
| --- | --- |
| `records` | 网站合并展示的文档、原始书目信息、稳定的 D-ID |
| `files` | 按原始 URL 去重的公开附件与实际下载状态 |
| `record_files` | 文档与附件的对应关系 |
| `queries`、`query_records` | 日期范围、原始查询式、命中数、实际分页数及完成状态 |
| `evidence` | 原始结果页存档的路径、SHA-256、抓取时间 |
| `records_fts`、`files_fts` | SQLite FTS5 元数据及 PDF 全文索引 |

只在来源搜索停止、底层命中已全部返回、分页记录数与展示总数一致、稳定 ID 去重后的数量也一致时，标记目录完成。日期从书目信息中提取；存在多个候选日期时保留候选值，`document_date` 留空，避免猜测。完整来源字符串始终保存在 `citation` 字段。

`summary.json` 的统计仅描述本次指定范围与该网站的公开搜索结果，不代表全站历届文件。原文的权利及适用条件归原始来源所有；本项目不是州议会的官方发布。
