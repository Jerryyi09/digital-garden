# 同步器审查修复执行记录（2026-10-26）

状态：代码修复完成；NUC 实书重发、第二/三层核验及实际备份统计待网络恢复与覆盖清单确认。未推送 v5。

## 现状与修正

- `nuc_syncer.py`：本地名称原样拼接远端路径、shell mkdir → 单次只读 SSH 取得分类/书目录，按 NFC + 首尾去空格 + 私有区字符转空格匹配。优先规范名称，否则沿用唯一真实目录名；多个非规范匹配时报错。新书只用规范名称。
- 远端目录由 rsync `-R` 的隐含目录创建。本地临时目录仅以符号链接提供规范路径，明确列入选中的资产，不复制整个书库、不修改源书目录；SSH 路径参数通过 JSON stdin 传递。
- 跟读组：`readalong/`、当前版本、封面、简介，保留 `--backup`。源文件组：manifest 音频和 EPUB，仅 `--ignore-existing`，无备份、无覆盖。均保留直连、`-s`、`--iconv`、无删除参数。
- 同步返回远端实际分类/书名，V5 和发布入口将它用于后续核验。新增 dry-run 支持和传输统计。
- 发布入口另修两个已存在的问题：末尾多余 Python/Shell 引号导致语法错误；五字段核验 payload 被解包为三个变量。
- 发布锁测试在已有真实发布者占锁时直接验证拒绝并发，不释放真实锁，不截断锁文件。

## 一次性脚本退役

以下四个原本未纳入 Git 的脚本已移入 `/Users/jerryyi/.Trash/readalong-retired-20261026-194333/`，没有永久删除：

- `publish_v4_seven_books.py`：发布/同步由 V5 与正式发布入口承接。
- `remap_101_and_catcher.py`：识别、映射、发布由 V5 承接。
- `republish_corrected_seven_books.py`：本地发布与 manifest/timeline/正文树哈希由正式发布入口和 tier2 承接。
- `v4_play_sampler.py`：抽样逻辑迁入 `tools/readalong/playback_samples.py`，支持任意 timeline 的 20%、50%、80% 点；明确这是数据抽样，不冒充真实听读验证。

使用：`tools/readalong/.venv/bin/python -m tools.readalong.playback_samples <timeline.json>`。

## 只读备份统计

运行 `tools/readalong/.venv/bin/python -m tools.readalong.nuc_backup_report`。

单次直连 SSH 报告 `/home/hp/readalong-sync-backup/` 和 `/home/hp/readalong-manifest-backup-20261025/` 的总量及一级子目录：文件数、逻辑字节、分配字节、最近修改 UTC 时间；不存在则报告缺失。没有清理功能。因 NUC 不可达，本次未取得实际统计值。

## 本地待改名清单（尚未改名）

根目录 `/Users/jerryyi/Desktop/寒假/未命名文件夹/`；以下用 ␠ 显示待移除的空格：

- `科学技术/The Structure of Scientific Revolutions␠`
- `科学技术/A Brief History of The Universe␠`
- `科学技术/History of Science- A Beginner's Guide␠`
- `complete/The World Behind the World␠`
- `政治/␠Between Thought and Expression`

工单中的《悉达多 Siddhartha␠》在当前文学作品目录未找到。改名前需用户确认，并核对发布 manifest 中基于路径的字段；缓存身份不改。

## 验收证据与逐书判定

- 《Clear Thinking》：仅本地只读检查，PASS；8083 句，中位数 1.96s、P95 5.38s、兜底 0；未同步、未声称上线。
- 《悉达多 Siddhartha␠》：当前预期路径未找到，未处理。
- 其他书：未映射、未发布、未深度核验。
- 雷库：14/14；30 条历史 verdict 重算无变化。
- 真实本地 rsync 回归覆盖特殊引号、美元符号、反引号、隐含链接目录、已有音频时间戳不同仍不覆盖、缺失 EPUB 补齐、未列入文件不传输。命令测试覆盖尾空格、PUA 真实目录、dry-run 两组同一路径。
- 本地 1 MiB 相同音频、不同 mtime 对照：旧命令文件数据 1,048,576 bytes，发送/接收 1,048,930/35 bytes；新命令文件数据 0 bytes，发送/接收 59/12 bytes。这是本地构造实测，**不是已上线书 NUC 重发的实测**。
- 私有证据：`private/readalong-syncer-review-20261026/`。无新增 ASR，无已识别音频重复识别，均为 **0 秒**。

## 未完成项与后续顺序

非沙箱直连 `hp@10.0.0.85:2222` 返回 `No route to host`，未绕道别名/路由器/SMB。没有对 NUC 进行删除、覆盖或改名。

1. 网络恢复后，确认共享发布锁空闲，选择一本本地与 NUC 均已发布、书名带空格的书。
2. 在锁内调用同步器 `dry_run=True` 生成真实目录和逐文件覆盖/新增清单；另用旧命令仅 dry-run 比较预计传输量，禁止为测量而重传音频。
3. 按手册 §0.4 将具体覆盖清单交用户确认，然后执行一次新同步，保存 rsync stats。
4. 同一书执行第二层哈希、第三层 Alist 抽样；确认目录无新增重复、源文件数据零传输。
5. 报告实书传输数据；实际历史传输字节若无旧日志应标记不可测，不能将 dry-run 估计标成实际传输。

工单尚未全部验收，不应以本地回归替代实机验收。

## 测试数量与耗时

最终非沙箱全套：**388 passed，102 subtests passed，20.73s**。相对原有 379 个测试新增 9 个，无删除；原测试数按此次新增测试函数数回算，未声称原始基线曾全绿。新增包括同步器 6 项、运维工具 2 项、Shell 语法 1 项。雷库另计 14/14，0.10s。`bash -n` 和 `git diff --check` 通过。

机器有效验证：最终全量 20.73s + 雷库 0.10s；本地 rsync 对照及单书静态检验合计约 0.26s。NUC 连接失败约 7s。返工验证另计：前两次全量 23.22s（真实发布锁导致测试准备失败）、22.61s（386 项通过，随后静态检查发现入口原有语法错误，补测后再运行）；首次误在沙箱运行导致 MLX 导入中止，未计为业务测试失败。实现、阅读和整理为人工/代理工作时间，未作精确计时；无 ASR 或映射机器耗时。
