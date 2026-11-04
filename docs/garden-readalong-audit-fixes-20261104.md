# 数字花园与有声书审计修订验收（2026-11-04）

## 已完成修订

- `studio/audiobooks/app.js`、`readalong-loader.js`：请求失效后停止修改界面；逐层查找 manifest 到书库根；完整路径优先匹配音源，拒绝同名歧义；纯听书 EPUB 分页查找；新书按钮立即绑定正确处理器。
- 播放器缓存最多保留 32 个 manifest、4 个时间轴/索引且合计不超过 50,000 条时间轴记录；超过上限的单份时间轴正常使用但不缓存。缓存 30 秒后重新获取，并按端点、账号隔离；退出时清空。该限制是记录数限制，不是浏览器堆内存字节上限。
- `sw.js` 缓存版本升级至 v59，并包含新模块。
- `practical_publisher.py`、`tree_swap.py`：平铺发布和回滚在替换失败时恢复旧入口；持久化交换记录，进程中断后下一次发布或回滚先恢复。恢复失败时保留记录、暂存目录及旧树以便重试。
- `release_integrity.py`、`tier_verifier.py`：索引和全部时间轴分片参与内容哈希；记录抽样不再截断文件存在性核验；按块读取哈希，避免额外整文件副本。生成的远端 Python 使用与本地同一哈希函数，并对 shell 参数转义。
- `scripts/readalong-publish-nuc`：全部成功退出 0，任意失败退出 1，无候选退出 2。`auto_batch_scheduler.py` 保留 stdout/stderr 的错误摘要并记录 PUBLICATION_FAILED。
- `garden.inline.ts`：仅切换排序时重排 DOM；搜索复用行列表和归一化搜索文本。
- `generate-garden-pages.mjs`：仅当缺少权威日期时惰性加载 Git 历史。审计时 Git 历史单次约 40 ms，不声称这是当前构建瓶颈。

## 测试结果

| 检查 | 结果 |
|---|---|
| `tools/readalong/.venv/bin/python -m pytest -q tools/readalong/tests tools/readalong_fast/tests` | 447 passed，111 subtests passed；23.33 秒 |
| `node --test studio/audiobooks/*.test.mjs tools/readalong/tests/*.mjs` | 46 passed；约 0.25 秒 |
| `node --import tsx --test quartz/**/*.test.ts` | 100 passed；约 0.29 秒 |
| `node_modules/.bin/tsc --noEmit` | 通过 |
| `npm run build` | 通过；Quartz 构建阶段约 2 秒，生成 112 个文件 |
| 本次文件的 `git diff --check` | 通过 |

新增 22 项测试：Python 12 项、播放器 JavaScript 9 项、花园 1 项。未删除测试。两个既有 VM 前端测试补齐实际运行依赖，使它们继续执行真实函数，而非绕过断言。

新增后端测试覆盖替换失败、交换前/交换中/交换后进程中断、恢复本身失败后再次恢复、首片超过 50 条但后片丢失、后片同长度内容损坏，以及成功/部分失败/全失败/无候选退出码。

## 本地浏览器与逐样本判定

内置浏览器使用仅监听 localhost 的临时服务器，清除该测试 origin 的 Service Worker 和缓存。播放器使用当前源码、实际 DOM 和本地模拟 API，跳过真实账号初始化；未连接家庭书库或 NUC。

| 临时样本 | 判定与依据 |
|---|---|
| `Book/Volume 2/disc/01.mp3` | PASS：跨两层子目录找到 manifest；同名音轨选中第二卷；iframe 显示 SECOND VOLUME 正文 |
| `Only/01.mp3` | PASS：第 201 项 EPUB 被发现，按钮正确显示 |
| `Slow/01.mp3` → 第二卷 | PASS：延迟旧请求返回后，第二卷跟读界面和时间轴保持有效 |
| 发布用临时书籍 | PASS：注入安装失败后，旧 manifest 字节保持一致；重启恢复保留旧树或已提交的新树 |
| 分片用临时书籍 | PASS：完整版本通过；后片丢失、同长度损坏均被拒绝；生成的远端校验脚本只在本地执行 |
| Library 搜索 | PASS：“三峡”返回 1 项；不存在标题返回空结果；切换标题排序和恢复搜索正常 |

![播放器切书验收](audit-assets/readalong-20261104.png)
![花园搜索验收](audit-assets/garden-search-20261104.png)

## 边界与耗时

- 未修改真实书籍，未执行 ASR，已识别音频再次识别秒数为 **0**。
- 未执行 NUC 发布、覆盖、同步或线上三层核验，也未推送 v5。线上发布仍需用户授权并用一册真实书试点。
- 目录交换采用恢复日志与补偿恢复，两个 rename 之间仍有短暂入口缺失窗口；SIGKILL 后要在下次发布/回滚时恢复，并不宣称跨两次 rename 的整体原子性或断电级文件系统事务。
- 机器验证时间见上表。返工包括补齐两个旧测试的隔离依赖，以及绕过 tsx CLI 的沙箱 IPC 限制改用 Node loader；没有重新识别或重做书籍映射。人工修订/等待时间未独立计时。
- 本地提交纳入发布脚本已有的失败记录及 heredoc 传参改动，作为准确退出状态的必要前提；候选发现、路径映射、摘要生成及其他政策改动仍保留在工作区。仓库其他未提交工作保留；其已有空白格式问题不纳入本次修订。
