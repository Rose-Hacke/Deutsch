# 执行记录（2026-10-21，Asia/Shanghai）

这份摘要补充机器日志，不伪造未记录的精确时刻。原始请求时刻见JSONL，当前结果见analysis_summary.json。

1. 实际读取唯一上传任务说明，复制为inputs/task_request.txt。研究开始时既有仓库main仅有初始空提交，没有提纲、论文、德语PDF或编码材料。
2. 最初对6个主要入口作默认只读请求，均为代理CONNECT 403；对议会PDF及Mayring入口用扩大执行权限再作2次只读请求，仍为403。未发生自动审批拒绝，也未关闭TLS验证。随后保存所需域名草稿，后续collect_sources.py的9项请求实际取得8项真实内容，M002仍遭代理拒绝。网络可用性按实际响应判断，不将草稿保存视为已发布环境。
3. prepare_project.py建立来源定义、空编码模式、库存和未执行检索计划。collect_sources.py保存原始HTML/PDF及SHA-256；extract_texts.py最初使用PDF文字层／网页正文。原始PDF可提取文字，不需要OCR。
4. 阅读纲领相关页、四页提案及整段议会发言与问答上下文，make_pilot.py完成3种文类12单元120项AI试编码。议会日期未核，始终单列。H4战争记忆、R1边界及疑问修订写入手册，并保留初判。
5. discover_candidates.py执行两个党派站点各13个日期受限查询，先得111条唯一文章候选。complete_pagination.py发现WP010有3页并补2页，新增135条，最终246条。materialize_api.py以post.id将官方API全文和原搜索响应对应。法定披露与政治正文分开，不按词命中直接语义赋码。
6. fetch_auxiliary.py保存媒体库、纲领广告声明、议会检索与PADOKA界面、党团API能力探测及方法全文容器。媒体库附件1977证实当前PDF上传发布日期，非从文件名推断。正文日期6日与分发日期7日对S003分别保留；S004会议日仍未核。
7. Mayring摘要页实际给出HTML全文链接；容器中的iframe继续指向M004全文。实际阅读§1—30并核对作者、题名、卷期、文章号和DOI。Grimmer／Stewart未读取，不冒充已经参考。
8. build_final_coding.py最初输出检查发现PDF断词／页脚噪声使3个拟用证据字符串不匹配。排查后改用Poppler pdftotext -layout，移除重复页号、章节页眉及分发页脚，跨页合并断词。原pypdf副本和失败中间决策保留在logs。提案beigetraten拼写经图像证实为原文，不擅改。一次泛用HTML提取对API JSON产生空段落，已修正为JSON跳过并交materialize_api.py按post.id提取，重做后才编码，未把空提取当无内容。
9. 第一轮扩展实际完成54单元594项v0.2，快照存versions/ai_v0.2。补完分页发现5月8日署名文章与选择性记忆元论证后，新增N1并回查既有单元；当前v0.3为70单元840项，16项?，无未处理空值。此为一个AI的版本修订，不是独立编码者一致性。
10. adjudicate_sources.py登记264条来源／入口／辅助记录，19核心、1日期待核补充。220项广告披露按文类排除，9条政治消息留待扩展。normalize_locators.py更正多页范围及提案首页无印刷页码的标签，未改变德语语义或人工状态。
11. render_spot_checks.py重渲染已被图像查看工具实际核对的S002第56、58 PDF页和S003第4 PDF页；人工复核仍为0。原始PDF、文字层、图像与AI辅助译文分开保留。
12. build_tables.py、build_narratives.py生成真实分母、全部疑问及新增码／推断复核队列和12条显式叙事链；build_review.py生成不依赖外部资源的双语审阅页。validate_project.py核查全部70德语单元的定位、840项代码组合、原始哈希、证据字符串、日期范围、上下文和复核覆盖，结果见validation_report.json。

已执行脚本均在scripts/，未保存假称已运行的程序。目录中不包含凭据或令牌。上述研究步骤未进行人类编码／复核、独立编码者一致性检验、总体推断、选民效果检验、GitHub推送或本地D盘操作。后续应用户要求进行的GitHub归档以仓库提交历史为准，不改变原始研究步骤及未人工复核状态。
