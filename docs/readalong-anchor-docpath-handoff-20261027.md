# 有声书 readalong 锚点与路径修复 —— 交接文档

**日期**：2026-10-27
**工单**：`docs/audiobooks-readalong-anchor-docpath-work-order-20261027.md`（含 19:20 追加裁决，提交 `ada64b3`）
**分支**：`v5`（**未提交、未推送**，全部改动在工作区）
**接手须知**：开工前必须先读接手手册 §0（路径见 `CLAUDE.md`），红线见该手册 §0.4。

---

## 1. 要解决的问题

### 工单原始三项

| 项 | 内容 | 状态 |
|---|---|---|
| **P1** | 切句/清理时保留被 timeline 引用的块级 id；加"timeline 每个 fragment 必须存在于最终 DOM"的生成时断言；退役按文本唯一匹配的重绑逻辑；**禁止**回退段落首句、**禁止**新增 `timingStatus` | **完成** |
| **P2** | timeline 的 `document` 统一解码为真实相对路径；tier1 去掉 `break`，保留 `%` 检测 | **完成** |
| **P3** | `practical_publisher.py` 平铺分支改为整目录 `os.replace` | **完成** |

### 工单 19:20 追加三项裁决

| 项 | 裁决 | 状态 |
|---|---|---|
| **问题 1** | 标题/短行/网址行等"夹在两段之间、自身无时间的块"，在两段之间的**时间空隙内**用逐词对齐定位；窗口严格限定在空隙内 | **代码完成，待回归验证** |
| **问题 2** | 超长块切分产生的临时 id 必须落到最终 DOM；只读扫描本地全部已发布书的悬空锚点，扫出的书全部作为目标书 | **未完成**（见 §4） |
| **问题 3** | 核实 `text/text/` 前缀是否真找不到文件 | **完成 —— 不是 bug** |

---

## 2. 当前工作区状态（重要）

```
已回退到 HEAD（无改动）：tools/readalong_fast/matcher.py
                        tools/readalong/stream_projection.py

保留改动：
  tools/readalong_fast/pipeline.py          +69/-...   P1 写盘 + 问题1 接入
  tools/readalong_fast/sentence_aligner.py  +247      问题1 的 locate_gap_blocks
  tools/readalong/tier_verifier.py          +16/-...  P2
  tools/readalong/universal_stream_aligner.py +22/-... P2
  tools/readalong/practical_publisher.py    +37/-...  P3
  tools/readalong/tests/test_tier_verifier.py        +114  P2 测试
  tools/readalong/tests/test_practical_publisher.py  +40   P3 测试
  tools/readalong_fast/tests/test_sentence_aligner.py -11  删 unwrap 专属测试（见 §5 警告）

新增文件：
  tools/readalong_fast/tests/test_gap_block_timing.py          问题1 测试（8 个）
  tools/readalong_fast/tests/test_paragraph_anchor_survives_marking.py  P1 测试（5 个 + 9 subtests）
```

**未提交**。`git diff --stat tools/` 可复核。

---

## 3. 已验证通过的结论

### 问题 3：`text/text/` 前缀 —— 不是 bug，关闭

只读扫描 49 本候选书，911 个 `text/text/` 前缀路径**全部**能在版本目录里找到对应文件（0 个找不到）。EPUB 内部本身有 `text/` 文件夹，解包到 `text/` 下自然形成 `text/text/…`。按裁决标准（版本目录能否找到文件），**不是缺陷**。

### 问题 2 前置扫描：本地已发布书 0 本带悬空锚点

扫描脚本（临时，在 `/tmp/wo-scan/scan.py`，**未入库**）扫 `/Users/jerryyi/Desktop/寒假/未命名文件夹`：
- 139 个 manifest，8 本 `readalongEnabled=False`（已排除，按手册 §0.4 第 6 条不处理）
- **131 本有效书，0 本带悬空锚点**

**但基线（HEAD）跑同一批对照输出时，4 本带悬空锚点**：

| 书 | 悬空锚点数 | 悬空秒数 |
|---|---|---|
| The Art of Logic in an Illogical World | 10878 | 18753.7 |
| A Little History of Psychology | 55 | 128.2 |
| Think It | 9 | 10.3 |
| 洗脑 | 4 | 13.5 |

这 4 本在基线里是 `SCRIPT_ERROR`（静默的部分失败），P1 修复后前 3 本转为 `USABLE_WITH_GAPS`。

### P1 修复效果（对照 HEAD 与修复后，心智成长 50 本）

| 指标 | 结果 |
|---|---|
| 未定位率 | **0 本变差**，合计 delta `0.000000` ✓ 不变量 1 满足 |
| 高亮中位数 | **0 本变短**，7 本变长 ✓ 不变量 2 满足 |
| 细粒度段（按文本+时间） | 丢失 327.5s / 21 本，新增 802.1s / 19 本，**净增 474.6s** |
| 其中**完全无覆盖** | 仅 **2 本 / 5 段 / 7.9 秒**（见问题 1） |

### 问题 1：5 个目标段已恢复

用 `locate_gap_blocks` 后，验收要求的 5 段全部重新被覆盖，时间与基线一致：

| 书 | 文本 | 修复后区间 |
|---|---|---|
| Volume 1 | `The Trolley Experiment` | 6797.12–6798.32 |
| Volume 1 | `Second-Order Problem` | 8006.48–8007.40 |
| Volume 1 | `Insurance Companies` | 9259.17–9259.89 |
| Volume 1 | `The Most Successful Detective of All Time` | 10495.30–10498.84 |
| 原子习惯 | `atomichabits.com/ parenting` | 20090.36–20092.44 |

### 测试与雷库

- 全量：**433 passed / 111 subtests**（基线 HEAD 为 415/102，**+18 tests / +9 subtests**）
- 雷库：`python -m tools.readalong_fast.sampling_regression` → **14/14 named cases matched，V3 sweep 30 verdicts 0 changed**

---

## 4. 未解决的问题（接手重点）

### 4.1 【阻塞】问题 2 的修法走错了，已回退，需重新设计

**工单原话**："切长块时生成的 id，必须是最终正文里真实存在的 id。"

**我犯的错误**：把它理解成"改 `matcher.py` 生成 id 的方式"，于是把超长块的 prefix 从
`"fast-long-"+sha256(name+ordinal)[:16]+"-"` 改成 `sha256(name)[:16]`（即精排的 `doc_id`），
想让粗排 span id 与精排同构（`c<doc_id>-segmentN`）。

**后果**：粗排按每 80 词切分、精排按句切分，两套编号用同一个 `chapter_id` → id 冲突 →
`refine`/`merge` 锚点匹配错乱 → **段数从 19673 掉到 15604**（`SENTENCE_EXACT` 3678→2598）。

**已回退 `matcher.py`**。原设计用 `fast-long-<hash>-` 前缀正是为了避开这个冲突。

**随后我又试了第二个错误方向**：退役 `stream_projection.py` 的 `unwrap_synthetic_coarse_segments`，
理由是"unwrap 剥掉粗排 span 才导致 id 对不上"。**这也错了** —— 退役后粗排的 `cfast-long-*`
span 留在 DOM，`is_document_already_marked` 返回 True，**精排跳过按句切分**，整本书退回 80 词粗块，
段数同样掉到 15664。**已回退 `stream_projection.py`**。

**当前状态**：`matcher.py` 与 `stream_projection.py` 都在 HEAD 原状。恢复原状后：
- 段数正常（19673 量级）
- **但《洗脑》重新报 `RuntimeError: Timeline anchors missing from the published DOM (4)`** —— 即问题 2 未解决。

**下一步应尝试的方向（未验证）**：
在 `pipeline.py` 的 `prepare_coarse_documents` 写盘**之前**，把粗排 DOM 里的 `cfast-long-*` span
**替换为外层块 + 稳定 id**，同时把 `paragraphs` 里对应的 `fragment` 一并改写。这样：
- 写盘 DOM 不含 `cfast-long-*` → `unwrap` 不触发 → 精排正常按句切分（粒度不退化）
- 粗排 timeline 的 `fragment` 是稳定 id，在精排 DOM 中存在（不悬空）

**验收标准**：`python -m tools.readalong_fast.benchmark ... --unit 心智成长/洗脑` 不抛异常；
`心智成长/思考快与慢` 段数回到 19673 量级（不得低于 19600）。

### 4.2 【阻塞】回归对照未完成

原计划的 53 本全批回归**被中断**（发现段数异常后停掉查因）。需在问题 2 修好后重跑，
并确认两条不变量：**未定位率 0 本变差、粒度中位数 0 本变短**。

对照基线在 `/tmp/wo-regress/baseline-growth`（HEAD 代码产物），
`/tmp/wo-regress/xz-growth`（P1-P3 产物，**注意：这批是在问题1代码之前跑的**）。
对照脚本 `/tmp/wo-scan/compare.py`（临时，未入库）。

### 4.3 【阻塞】`locate_gap_blocks` 性能

初版实现每次调用对全音轨段排序，**《思考快与慢》从 10.1s 涨到 176s**。
已优化（预排序 + 二分 + `occupied_by_track` 索引），profiler 显示 176s → 4.2s。

**但真实端到端仍约 62 秒**（基线 10.1s）。`timings` 字段只统计到 4.6s，其余在未统计区。
**需进一步定位**：可能是 `_free_windows` 的 `extra` 合并，或 `words` 过滤。

**注意**：优化过程中我曾加过一个"集合交集预筛"，因 `tokens()`（NFKD 归一化 + 撇号处理）
与 `normalize_token()`（只保留 `[a-z0-9]`）产出的字符串不一致而失效，**已删除**。
若后续再加预筛，必须用同一套归一化。

### 4.4 【未开始】目标书全流程

工单要求对《魔法的颜色》《红与黑》《1984》**以及《洗脑》和扫描出的悬空锚点书**
做：重新映射（识别全部命中缓存）→ 本地发布 → 直连同步 → 三层核验。

- 3 本目标书在 `private/readalong-sentence-level-20261026/v5_runs/文学作品-20261027T0953/inv/inventory.json`
  （unit_id：`文学作品/魔法的颜色`、`文学作品/红与黑`、`文学作品/1984 乔治 奥威尔`）
- 《洗脑》在 `心智成长-20261026T1454` 的 inventory
- 《1984》已有发布批次 `private/readalong-library-runs/文学作品-1984 乔治 奥威尔-20261027T1541`（用户此前跑的）

**同步到 NUC 已获用户授权**（工单追加部分明确："目标书的本地发布、直连同步和三层核验，
都在本工单授权范围内（手册 §0.4 第 13 条）"）。rsync 覆盖时会备份，不做删除。

**第三层 Alist 凭据**：用户已在 NUC 上创建 `/home/hp/.config/readalong/alist.json`。
**执行方不得自行写入密码。**

### 4.5 【未开始】提交与汇报

改动提交 Git（**不推送**），汇报格式按手册 §0.5，必须包含：
- 改动文件、测试数增减、逐书判定与原因
- "已识别过的音频又被识别的秒数"（必须为 0）
- 耗时分解（机器时间和返工分开写）
- 退役的代码和测试清单，及测试数变化解释

---

## 5. 经验教训（重要）

### 5.1 不要扩大改动范围

工单问题 2 的措辞是"切长块时生成的 id 必须是最终正文里真实存在的 id"。
我直接去改了 **id 的生成方式**，而没有先查清**断层到底在哪**。

**正确顺序**：先定位"生产方"和"使用方"分别是什么、在哪一行分叉，再决定改哪一侧。
实际问题出在 `stream_projection.py` 的 unwrap（使用方剥离了生产方的 id），
而 `matcher.py` 的生成逻辑本来是对的。

**代价**：两次错误的改动尝试（改 matcher、退役 unwrap），各花数轮验证才发现段数掉了 20%。

### 5.2 改动前后必须立刻验段数

段数是最灵敏的回归信号。我在改 `matcher.py` 后跑了完整 benchmark 却**没有对比段数**，
直到后来才发现 19673→15604。若当时立刻对比，能省掉几轮排查。

**建议**：任何触及 `matcher.py` / `stream_projection.py` / `sentence_aligner.py` 的改动，
改完立刻用单本（如《思考快与慢》，19756 段）对比段数与 `timingStatus` 分布。

### 5.3 性能问题要先 profile，不要猜

`locate_gap_blocks` 初版慢 17 倍。我最初怀疑是 `SequenceMatcher` 调用次数，
实际 profiler 显示 **84% 时间在 `_free_windows`**（每个锚点对全音轨段排序）。
**先 profile 再优化**能避免改错地方。

### 5.4 临时脚本不要留在 `scripts/`

`scripts/` 下一次性脚本会违反红线 10。我写的扫描脚本放在 `/tmp/wo-scan/`，
**接手方若要复用，需先确认是否该入库**（若判定为长期有用的运维工具，应入 `scripts/` 并提交）。

### 5.5 一个已被证伪的假设，别重蹈

**"基线能高亮标题段，是正确行为"** —— 部分正确。基线靠 **id 丢失 + 文本模糊匹配命中外层容器**
这个 bug 偶然捞回了标题段。P1 把 id 修对后副作用消失，标题段就掉了。
能力是真的（孩子实际在用），实现是歪的，所以按裁决是"**重新实现**"，不是"恢复 bug"。

---

## 6. 关键代码位置

### `tools/readalong_fast/sentence_aligner.py`（新增 247 行）

`locate_gap_blocks(sentence_timeline, documents, ordered_words)` —— 问题 1 的核心。
- 单次遍历建 `flat`（DOM 顺序锚点）、`siblings_of`（同父锚点）、
  `previous_located` / `following_located`（前后最近已定位锚点索引）
- 每个未定位锚点的候选窗口按优先级：
  1. **块内兄弟**锚点的时间跨度
  2. **前后邻居**之间的空隙
  3. 邻居窗口无效（空或时间倒退）时，前驱之后**有界的 30 秒尾窗**（`MAX_TRAILING_GAP_SECONDS`）
- 窗口裁剪到该音轨真正空闲的区间（`_free_windows`，预排序 + 二分）
- 逐词对齐（`_align_anchor_within`），要求匹配词全落在同一窗口、`end > start`
- **短锚点（≤ `SHORT_ANCHOR_WORDS`=3 词）用绝对词数门槛，长锚点还须过 `MIN_GAP_MATCH_RATIO`=0.75**
  （这条是因为 ASR 把 `atomichabits` 听成 `atomicabits`，3 词锚点比例掉到 0.667）

**关键**：`documents` 的 key 是**裸 spine 条目**（`text/part0005.html`），
而 timeline 的 `document` 是 `f"text/{name}"`（**双层** `text/text/...`）。
`document_order` 必须用 `f"text/{name}"` 才能与 `located` 匹配。**这是排查了很久的坑。**

### `tools/readalong_fast/pipeline.py`

- `prepare_coarse_documents`（新增，997 行附近）：粗排 + 写盘，让精排能读到粗排的 id
- `generate` 内 1257 行附近：接入 `locate_gap_blocks`，**并按 `track_order` 重新排序**
  （`resolve_boundaries` 按输入顺序处理，gap 段 append 到末尾会打乱时序 → 抛 `Unresolved timing conflict`）

### `tools/readalong/stream_projection.py`

`complete_document_marking`（58 行附近）：`cfast-long-*` 的 unwrap 逻辑。
**问题 2 的断层就在这** —— 它剥掉了粗排 span，而粗排 timeline 仍引用那些 id。

### `tools/readalong_fast/matcher.py`

129 行：超长块（>160 词）切分的 prefix 生成。**已回退到 HEAD，勿轻改**。

---

## 7. 复现命令

```bash
cd /Users/jerryyi/digital-garden

# 全量测试
tools/readalong/.venv/bin/python -m pytest tools/readalong_fast/tests/ tools/readalong/tests/ -q
# 期望：433 passed, 111 subtests passed

# 雷库
tools/readalong/.venv/bin/python -m tools.readalong_fast.sampling_regression
# 期望：14/14 named cases matched，V3 sweep 30 verdicts 0 changed

# 单本映射（缓存命中，不跑 ASR）
tools/readalong/.venv/bin/python -m tools.readalong_fast.benchmark \
  --inventory private/readalong-sentence-level-20261026/v5_runs/心智成长-20261026T1454/inv/inventory.json \
  --output /tmp/out --cache-read-root private/readalong-cache \
  --allow-new-asr --asr-engine words \
  --unit "心智成长/思考快与慢"
```

**注意**：
- 必须用 `-m` 从项目根跑（`-I` 隔离模式会找不到 `tools` 包）
- 跑之前确认无批跑在进行（`ps -Ao command | grep v5_batch_runner`，红线 11）
- `benchmark.py:97` 会检测源码在运行中被改，抛 `Benchmark source code changed`

---

## 8. TODO 清单（按优先级）

1. **[阻塞]** 按 §4.1 的方向重新实现问题 2，验收标准见该节
2. **[阻塞]** 重跑 53 本全批回归，确认两条不变量
3. **[阻塞]** 定位并修掉 `locate_gap_blocks` 剩余的性能开销（62s → 目标接近基线 10s）
4. 目标书（3 本 + 洗脑）重跑映射 → 本地发布 → 直连同步 → 三层核验
5. 若扫描脚本判定为长期有用，移入 `scripts/` 并提交；否则删除
6. 提交 Git（**不推送**）
7. 按手册 §0.5 写汇报

---

## 9. 安全约束（逐字保留，勿违反）

来自 `AGENTS.md`：
- 删除文件或目录前，必须先说明将删除的绝对路径和原因
- 不使用 `rm -rf` 删除用户数据，除非用户明确点名同意
- 能移到备份目录或废纸篓时，不直接永久删除
- 删除配置、缓存、历史记录、账号数据前，必须先备份
- 对 `.app`、`Library/Application Support`、`.claude`、`.codex`、Obsidian vault 等目录操作时，必须额外确认

来自手册 §0.4（红线）：
1. 只读本地 SSD；NUC 只作为发布目标
2. NUC 上的任何删除、覆盖、改名，都必须先列清单，经用户确认后再执行。rsync 禁止 `--delete` 类参数；覆盖时用 `--backup`
3. 禁止直接改写 NUC 上的书籍文件
4. manifest 带 `assetRevision` 时，必须同时同步对应的版本目录
5. ASR 不并发；不新建缓存目录
6. 尊重用户的纯听决定：有 `AUDIO_ONLY` 收据的书默认不处理
7. 检验只针对本次改动的书，分三层进行；不对全库做 Alist 深度扫描
8. 不恢复逐词认证门槛；不降低句级粒度
9. 前端改动：先在内置浏览器实测，再推送。推送 `v5` 等于公开上线，必须先征得用户同意
10. 一次性脚本不得留在 `scripts/`；核心代码必须提交 Git
11. 批跑与改代码必须错开
12. 批跑输出：每处理完一本才打印一行 JSON
13. **目标书（《魔法的颜色》《红与黑》《1984》《洗脑》，以及扫描出的悬空锚点书）的本地发布、直连同步、三层核验，在本工单授权范围内**

来自 `docs/audiobooks-readalong-handoff-20261027.md`：
- macOS 本地网络权限：从 Python 连 NUC 的验证请用户在终端跑，或用 bash 调 ssh
- NUC 安全：所有远端命令经 `bounded_remote` 包装，不得绕过
- 清理 NUC 进程只能用精确条件匹配，**不能用宽泛的 `pkill -f`**
- 用户的 hermes 网关（`/home/hp/.hermes/...`）不要碰
- 推送 `v5` 会触发网站构建，必须先得到用户同意

---

## 10. 环境备忘

- 本地库根：`/Users/jerryyi/Desktop/寒假/未命名文件夹/`（分类/书/readalong/）
- 唯一缓存根：`private/readalong-cache/`（**不得新建**）
- NUC 直连：`hp@10.0.0.85:2222`（`-F /dev/null` 忽略 SSH 配置）
- NUC Alist 凭据：`/home/hp/.config/readalong/alist.json`（用户已创建，**不得自行写入密码**）
- 项目 venv：`tools/readalong/.venv/bin/python`（用绝对路径，`cd /tmp` 后相对路径会失效）
- 对照基线产物：`/tmp/wo-regress/baseline-growth`（HEAD）、`/tmp/wo-regress/xz-growth`（P1-P3）
- 临时调试脚本：`/tmp/wo-scan/`（未入库）
