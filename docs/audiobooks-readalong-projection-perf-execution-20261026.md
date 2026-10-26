# 句级投影性能工单执行记录（2026-10-26）

工单：`docs/audiobooks-readalong-projection-perf-work-order-20261026.md`

## 结果

《The Hero with a Thousand Faces》缓存命中端到端耗时从历史基线 **1393.47 秒** 降至修复后 **85.91 秒**，低于 3 分钟验收线。修复前后 timeline 文件 SHA-256 均为 `a5bb8d4ac252d14eb802b264fefd31b3b82ad36891d20b02e03f60d99f55b078`，共 22,051 条逐句映射完全一致；未定位率均为 `0.7319196%`。

profile 暴露了三处实际断层：

1. `refine_timeline_by_dom` 对重复段落反复做 BeautifulSoup ID 查找和句子抽取，并在失效锚点上重复执行模糊 `SequenceMatcher` 搜索。
2. `project_stream` 对全书和整条音轨调用 `SequenceMatcher`，片尾音乐或附录等完全无共同 7-token 锚点的区间也进入全书搜索。
3. `merge_stream_projection_with_paragraph_fallback` 对每条投影逐一扫描全部兜底区间，形成轨道数和区间数的乘积复杂度。

对应修复为：缓存文档 ID、段落恢复和句子片段；按音轨和时间建立词区间索引；以 7-token 倒排锚点索引重建原 `SequenceMatcher` 的最长连续块和同分优先顺序；按音轨对兜底区间做二分重叠查询。原有阈值、搜索窗口、匹配顺序和兜底语义保持不变。

## 十本对照

对照使用同一份库存、同一缓存根和同一批输入；修复前函数从 `sentence_aligner_before.py`、`stream_projection_before.py` 冻结加载。所有书的 timeline SHA-256、审核指标和未定位率一致。

| 书目 | 修复前秒数 | 修复后秒数 | 加速 | 未定位率 |
|---|---:|---:|---:|---:|
| 101 Essays | 18.735 | 4.022 | 4.66× | 0.0905% |
| Clear Thinking | 13.544 | 3.954 | 3.43× | 0.0235% |
| Make Your Bed | 2.605 | 1.137 | 2.29× | 0.2283% |
| Think Like a Psychologist | 4.911 | 1.863 | 2.64× | 0.0428% |
| Nexus | 155.054 | 12.553 | 12.35× | 0.0797% |
| AI Explained | 48.429 | 5.509 | 8.79× | 0.1680% |
| 麦田里的守望者 | 66.812 | 6.520 | 10.25× | 1.0856% |
| A Room of One's Own | 194.805 | 15.198 | 12.82× | 0.1905% |
| Story | 47.396 | 8.143 | 5.82× | 1.8635% |
| The Storytelling Animal | 18.500 | 3.900 | 4.74× | 0.1594% |

逐书哈希与指标证据在 `private/readalong-projection-perf-20261026/ten-comparison.json`。400 组随机 DOM/投影差分测试全部一致；7-token 索引与标准 `SequenceMatcher` 做了 6000 次逐块等价对照。

## 测试与缓存

- 全量：**398 passed，102 subtests passed，21.36 秒**；相对前一基线新增 10 个性能回归测试，没有删除专属测试。
- 雷库：**14/14**，0.09 秒。
- 重复识别：**0 秒**；所有对照报告 `segmentCachedAudioSeconds` 命中缓存，无新 ASR。
- 新增回归覆盖：多轨末尾完全不匹配、重复失效 DOM 锚点、未排序词时间区间、全量兜底区间索引、重复文本和同分匹配、跨文档锚点恢复。

profile 文件、日志、旧版函数快照和对照产物均在 `private/readalong-projection-perf-20261026/`。profile 本身包含分析器开销；正式无 profile 的十本对照总耗时为 65.20 秒。

## NUC 直连检查

按手册要求用 venv Python 的直连 SSH（`-F /dev/null -p 2222 hp@10.0.0.85`）读取备份统计，未走别名、跳板或 SMB。只读统计结果：

- `/home/hp/readalong-sync-backup/`：6,255 个文件，707,440,782 bytes，分配 720,936,960 bytes。
- 最近修改时间：2026-10-26 12:43:36 UTC（新加坡时间 20:43:36）。
- `/home/hp/readalong-manifest-backup-20261025/` 的完整结果见 `private/readalong-projection-perf-20261026/nuc-backup-report.json`。

## 发布补充与《千面英雄》拒绝原因

按后续工单要求，十本对照书均未发布。`ten-comparison.json` 中十本书的 timeline SHA-256、逐句 JSON、审核指标和未定位率均完全一致，因此无需发布；不存在需要逐本解释的差异。

《千面英雄》初次句级候选被 `publish_practical` 拒绝，触发的是候选 `practical-audit.json` 的 `DOM_REFERENCE_BROKEN`（20 条）和 `INVALID_INTERVAL`（1 条），发布层因此归类为 `STRUCTURAL_OR_PHYSICAL_SOURCE_ERROR`。20 条坏锚点集中在 Chapter-2 的三个句子（The Void 7 条、The God 5 条、The Thunderbolt 8 条）；另 1 条是第 56 轨末尾 `698.99–699.01` 超出物理时长 `699.0072s` 的舍入越界。它们不是片尾/附录三轨造成的结构拒绝。

修复逻辑改为按文档缓存规范化文本，唯一匹配时重绑到真实 DOM fragment，并将句子区间裁剪到物理时长、丢弃零长度区间。`ZERO_DURATION` 仍作为 ASR 诊断保留 1 条，但不是 practical publisher 的 hard error，也不构成拒绝原因。第 60、61、62 轨（片尾音乐/附录）仍分别为 UNALIGNED，未人为填充映射；这是允许带 gap 发布的预期结果。

修复后本地发布成功，revision 为 `08e36182096a460faf04dea5bb41b811`，审核决策 `PUBLISH_WITH_GAPS`。随后通过 `hp@10.0.0.85:2222` 直连同步到 `/mnt/750/Music/有声书/文学理论/The Hero with a Thousand Faces`。远端 manifest revision 与本地一致；本地关键哈希为 manifest `c69c442d…2401b`、timeline `5338131a…a78c4`、text tree `99505e9c…14bd`。十本对照书没有同步或发布。

三层核验中，本地静态核验通过（22,051 segments，median 1.34s，p95 4.90s）；远端目录、revision 和音轨文件已通过直连只读检查。Alist 样本检查命令在当前 NUC 网关响应超时，未将超时冒充成功；目录和 manifest 已由 SSH 直接确认存在。原段落级版本保持不变并留在 NUC 上，句级版本作为新 revision 发布。

耗时对比：旧句级基线 **1393.47s（23.22 分钟）**；修复后无 profile 实测 **59.43s**（约 0.99 分钟），约 **23.4×** 加速，满足 ≤3 分钟目标。带 profile 的一次实测为 85.91s，仅含分析器开销，不作为正式验收数字。
