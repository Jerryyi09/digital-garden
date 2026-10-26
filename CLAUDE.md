# 有声书跟读（readalong）工作须知

凡是涉及有声书映射、发布、同步到 NUC、播放器跟读（`tools/readalong*`、`scripts/readalong*`、`studio/audiobooks/`）的任务，**开工前必须先读完**接手手册第 0 节：

`/Users/jerryyi/Library/Mobile Documents/iCloud~md~obsidian/Documents/学习笔记/03 Archives/Rosemary Garden/交付版本 01 文档/25 有声书映射审核发布实现与接手手册.md` §0

其中写明了目标、运行环境（本地 SSD 路径、唯一缓存根、MLX 不能在沙箱里跑、NUC 直连 `hp@10.0.0.85:2222`、播放器经 `v5` 分支由 Cloudflare 自动部署）、脚本入口、红线（NUC 上删除或覆盖先经用户确认、禁止直接改写 NUC 文件、检验只针对改动的书）以及修订方式。`docs/audiobooks-claude-code-handoff.md` 等 10-19 的旧交接文档已作废。
