# 大型 timeline 分片试验记录（2026-10-27）

## 目标

以《The Hero with a Thousand Faces》为样板，将超过 300 MB 的单一 timeline 拆成按音轨加载的小文件；保留旧版单文件 manifest 兼容性，不发布、不同步 NUC。

## 实现

- 新增 `tools/readalong/timeline_shards.py`。
- timeline 小于 300 MB 时继续生成 `timeline.json`。
- 超过阈值时生成 `timeline-index.json` 和 `timeline-shards/<audioSourceId>.<hash>.json`。
- manifest 增加 `timelineFormat: per-audio-source-v1` 与 `timelineIndex`。
- 发布审核、权威校验和 Tier 1/Tier 2 读取逻辑支持两种格式。
- 前端先读取 manifest/index，再只读取当前音轨 shard；旧版 `timeline.json` 仍按原逻辑读取。
- manifest 成功后即可显示 EPUB 按钮，不再等待整本 timeline 下载完成。

## 《千面英雄》本地样板

- 原 timeline：约 1.02 GB，22,051 条句级片段。
- 分片：62 个音轨文件，最大 shard 约 64.4 MB，index 约 7.4 KB。
- 重新生成使用既有缓存，未重新识别音频；本次 benchmark 总耗时约 65.63 秒。
- 句级结果与原结果保持相同：22,051 条，指标仍为 `USABLE_WITH_GAPS`，未定位率 `0.7319%`。
- 本地 `publish_practical(..., dry_run=True)` 通过：`PUBLISH_WITH_GAPS`、`hardErrors=[]`。

## 本地验证

- 分片读写测试：2 个通过。
- 前端 timeline loader 测试：2 个通过。
- 原有前端相关测试合计：19 个通过。
- Python 语法检查通过。
- 未推送 `v5`，未发布或同步《千面英雄》的新分片版本。

## 外网收益

公网首次只需下载当前音轨 shard，而不是约 1 GB 的整本 JSON；EPUB 按钮在 manifest/index 成功后即可显示。下一步可再加入下一音轨预加载和 immutable revision 缓存策略。
