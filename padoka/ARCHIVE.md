# PDF 原文存档

本次共抓取 **3,856 份公开 PDF，5,219,246,322 字节（约 5.22 GB）**，覆盖 2025-01-01 至 2026-10-21 的网站文档搜索结果。全部下载成功并记录 SHA-256。

原文按 ZIP 分卷保存到同一 GitHub 仓库的 **padoka-pdf-archive-20261021** 存档分支：

- [PDF 分卷目录与下载入口](https://github.com/Rose-Hacke/Deutsch/blob/padoka-pdf-archive-20261021/padoka/archives/README.md)
- [按文件查找对应 ZIP 卷号](data/file-volumes.csv)
- [分卷 SHA-256 校验表](data/archive-SHA256SUMS)
- [分卷机器可读清单](data/volumes.json)

每个 ZIP 可独立解压，不需要拼接。将其中的 `files/` 目录解压到本目录，与数据库 `files.local_path` 对应。每卷包含该卷的原始 URL、文件路径、大小与 SHA-256 清单。

存档分支仅用于保存 PDF 分卷；默认主分支保存数据库、CSV、程序及网页证据。只下载数据库时，可直接下载 `data/padoka.sqlite.gz`。

原先规划使用 GitHub Release 保存大附件，但当前云环境未允许 `uploads.github.com`，且提供给助手的工具只能读取网络配置，不能修改白名单。本次使用正常 Git 推送完成仓库存档。`upload_release.py` 保留了将这些已核验分卷上传至 Release 的能力，可在具备该域名访问权限的环境中使用。
