> [!warning] 已作废（2026-10-26）：本文是 10-19 的早期交接，内容已过时。请改读接手手册 25 §0（路径见仓库根目录 `CLAUDE.md`）。

# Claude Code 开发交接：独立有声书 PWA 与英文 EPUB 音文同步

交接日期：2026-10-18，Asia/Singapore。

本文是后续开发的任务书，覆盖整个独立有声书 PWA 的完善，以及英文 EPUB/音频自动映射工具。现有验证结果、尚未实现的能力、建议接口和验收条件分别标明；不要把规划中的命令当作已经存在的程序。

## 1. 用户目标与范围

用户在家庭 Linux NUC 上存有 MP3、M4A、M4B 有声书，以及部分对应的 EPUB/PDF/MOBI。服务器现有 Docker Nginx、AList、Music Assistant。目标是在 iPhone 上通过独立 PWA 听书，并从 Rosemary Garden 的 Studio 进入。

用户已明确的偏好与要求：

- 中文界面与沟通；代码注释英文；默认 2 空格缩进。
- 书库和最近播放使用列表，不恢复为大卡片网格。
- 支持分类、文件名查找、最近播放、记录进度、恢复上次位置。
- 区分 Cloudflare 外网静态部署和 NUC 内网部署。
- EPUB 音文同步本阶段只针对英文有声书。
- 复用现成开源制作/渲染能力，不从零开发语音识别、强制对齐或 EPUB 排版引擎。
- 后续希望通过一个脚本命令完成单本映射，进一步支持递归批处理。
- 完善整个独立有声书 PWA，不只制作一次性样书。

推荐本阶段范围：英文 EPUB 跟读优先；PDF/MOBI 保留后续扩展点。不要让 OCR、MOBI 转换或跨设备同步阻塞英文 EPUB 主线，也不要对未实现能力显示可用按钮。

## 2. 第一轮必须先读什么

同一台 Mac 的项目目录：

```text
/Users/jerryyi/digital-garden
```

按顺序阅读：

1. 本文。
2. `docs/audiobooks-deployment.md`：现有双环境部署和播放器行为。
3. `studio/audiobooks/index.html`、`app.js`、`config.js`、`app.css`、`sw.js`。
4. `scripts/copy-html.mjs`、`scripts/generate-garden-pages.mjs`、`studio/downloads-index.json`。
5. `scripts/deploy-audiobooks.mjs`、`scripts/deploy-audiobooks-remote.py`、`wrangler.jsonc`。
6. `private/audiobook-validation/power-of-habit/README.md` 和下面列出的样书报告。

历史 Obsidian 文档在：

```text
/Users/jerryyi/Library/Mobile Documents/iCloud~md~obsidian/Documents/学习笔记/03 Archives/Rosemary Garden/交付版本 01 文档
```

历史文档中的 `:8089` 外网地址和部分项目路径已过时。以本交接记录、仓库当前代码和新取得的现场证据为准，不盲目覆盖现有线上配置。

开始前运行 `git status --short`，保护用户已有改动，检查适用的 AGENTS.md。本文交付时只新增交接材料，不代表已开始后续功能开发。

## 3. 已完成与未完成

| 能力 | 当前实际状态 | 后续任务 |
| --- | --- | --- |
| 独立入口 `/studio/audiobooks/` | 已实现；Studio 链接绕过 Quartz SPA | 保持独立、稳定构建 |
| 内外网地址选择 | 已实现自动/外网/内网模式 | 分环境回归、改善错误提示 |
| AList 登录 | 账号、密码、可选 OTP；默认会话令牌，主动勾选才持久化 | 处理过期、账号切换、目录权限及异常 |
| 分类/目录浏览 | 已实现，分页取全、自然文件名排序 | 增加书籍模型，避免把文件夹层级直接等同完整书籍结构 |
| 书库/最近播放 | 已改成单列列表 | 保持列表、改善大量条目和重复章节名的识别 |
| 搜索 | 仅当前目录或已存历史 | 明示范围；若做全库搜索，建立受控目录索引 |
| 音频播放 | 单个复用 HTML audio，倍速、后退/前进、原生进度条 | 网络异常、过期签名、切换竞态等稳定性完善 |
| 进度 | IndexedDB＋同步日志、约 3 秒保存、恢复回退 3 秒 | 书级/章节级进度、迁移与更充分的生命周期验证 |
| 锁屏控制 | 已接 Media Session | iPhone 实机验证；后台跨文件连播未保证 |
| M4B 章节 | 没有解析内嵌章节 | 服务器预处理章节元数据、原文件内 seek |
| PWA | manifest、PNG 图标、应用范围 SW | 更新体验、旧缓存迁移、离线状态说明 |
| 离线音频 | 未实现 | 不把界面缓存说成已支持离线听书 |
| EPUB 阅读/跟读 | 正式 PWA 未实现 | 接阅读引擎、映射、阅读位置和跟随交互 |
| 英文样书映射 | 完整序言已验证 | 工具产品化、全书验证、再批处理 |
| 跨设备进度同步 | 未实现，当前支持 JSON 进度导入/导出 | 后续独立设计鉴权同步接口，不默认新增后台 |

已有相关提交：

```text
44fa668 Add audiobook PWA with Cloudflare and NUC deployment support
4acc6a3 Match NUC LAN IP in audiobook HTTP deployment
c866258 Use list layout for audiobook library and recent playback
```

这些提交在现有 `v5` 分支。Cloudflare 自动部署绑定该分支。不要为迁移框架或部署机制顺手扩大本次任务。

## 4. 当前前端结构与重要行为

源码在 `studio/audiobooks/`，不是构建产物 `public/`。

| 文件 | 用途 |
| --- | --- |
| `index.html` | 中文界面、连接对话框、列表容器、原生 audio、播放器控制 |
| `app.js` | AList API、目录、历史、播放生命周期、Media Session、进度导入/导出 |
| `config.js` | ROOT、内外网 endpoint、路径约束、签名流地址、文件身份 |
| `app.css` | 暖纸色/深绿色视觉、响应式单列列表、底部固定播放器 |
| `sw.js` | 仅缓存白名单界面资源；当前缓存版本 v2 |
| `manifest.webmanifest` | `/studio/audiobooks/` 的独立 PWA 配置 |
| `config.test.mjs` | 现有 6 项地址、路径和文件身份测试，不复制到发布目录 |

`npm run build` 最后通过 `scripts/copy-html.mjs` 将应用复制到 `public/studio/audiobooks/`。Studio 卡片来自 `studio/downloads-index.json`，生成器设置 `data-router-ignore`。不要只修改远端 `index.html` 或 `public/`，否则下次构建丢失。

源码可以按职责拆成 API/存储/播放器/书库/阅读器模块，但无需仅为组织代码引入 Vue/React 或更换 Quartz。先完成行为和测试，再判断是否有框架需求。

当前书库根目录：

```text
/750HD/有声书
```

实际 AList v3.60.0，游客访问已禁用。API 前缀为 `/alist/api/`；已使用 `auth/login`、`fs/list`、`fs/get`。通过 `fs/get` 的 sign 构造 `/alist/d/<编码路径>?sign=...`；不要把可能含内网/Docker 地址的 raw_url 直接交给 Cloudflare 页面。

令牌仅发送到登录时使用的 endpoint，后续请求保留同一个 Client-Id；目录密码目前只在内存。不要把账号密码、访问令牌、device key 或签名 URL写入源码、日志、导出的收听记录或生成的映射文件。

若未来采用 AList 根目录限定的只读账号，必须验证用户可见路径是否相对其 base_path；不能只改账号根目录，却继续假设所有账号都接受同一个绝对路径。

## 5. 双环境部署：不能混用地址

| 使用环境 | 页面地址 | 数据/媒体来源 |
| --- | --- | --- |
| Cloudflare | `https://notes.melyi.uk/studio/audiobooks/` | `https://melyi.uk/alist` |
| NUC 公网 HTTPS | `https://melyi.uk/studio/audiobooks/` | 同域 `/alist` |
| NUC 内网 HTTP | `http://10.0.0.85:8088/studio/audiobooks/` | 同域 `/alist` |
| Mac 开发预览 | `http://127.0.0.1:8766/studio/audiobooks/` | 默认公共 HTTPS AList |
| 样书独立试听 | `http://127.0.0.1:8768/` | 本机私有生成产物，仅用于验证 |

Cloudflare 只托管前端静态文件，`notes.melyi.uk` 受 Cloudflare Access 保护。NUC 托管实际书库；HTTPS 页面不要请求 `http://10.0.0.85`。局域网普通 HTTP 可播放，但不能据此承诺可安装完整 PWA；可信 HTTPS 的 Safari/主屏幕模式需单独验证。

Docker 端口为 `8088:80`、`8089:443`；2026-10-18 实测公网根域名 443 正常，旧的公网 `:8089` 不可达。以后现场状态可能改变，发布前复核。

服务器：`hp@10.0.0.85`，SSH 2222；用户确认其终端能连接：

```bash
ssh -p 2222 -i /Users/jerryyi/.ssh/id_rsa hp@10.0.0.85
```

Nginx 位置：

```text
/home/hp/docker-compose/nginx/conf.d/melyi.uk.conf
/home/hp/docker-compose/nginx/html/studio/index.html
/home/hp/docker-compose/nginx/html/studio/audiobooks/
```

独立部署现有命令：

```bash
cd /Users/jerryyi/digital-garden
npm run deploy:audiobooks
```

会构建、上传、备份 Studio 与 Nginx、检查后 reload；仅更新请求范围，不同步整个 Obsidian 库，也不推送 Git。Cloudflare 通过源码 Git 提交与 push 自动发布，应检查部署状态，不把 push 成功当成部署成功。

已知 Nginx 有两个 HTTP server 重复声明 `melyi.uk`，会出现 warning。部署脚本已为内容站补上 `10.0.0.85` 的显式匹配；HTTP/HTTPS AList 代理均透传 Range/If-Range，并关闭媒体代理 buffering。处理 warning 前先查清默认虚拟主机，不直接删除另一个配置。

用户上次部署成功的备份目录：

```text
/home/hp/docker-compose/nginx/backups/audiobooks-20261018T094901Z
```

先前 Codex 执行环境曾持续返回 `No route to host`，但用户 Terminal 能连；备用公网 SSH 返回了不同主机密钥，未接受、未修改 known_hosts。Claude Code 应先正常重试；若仍受环境限制，给用户一条可直接执行的部署命令，不反复索要已确认的 SSH 参数，不绕过主机密钥检查。

## 6. 样书：现场事实与证据

输入目录：

```text
/Volumes/750/Music/有声书/心智成长/The Power of Habit - Charles Duhigg
```

文件：

```text
The Power of Habit - Charles Duhigg.epub
The Power of Habit By Charles Duhigg.m4b
The Power of Habit By Charles Duhigg.art[0].png
```

EPUB 元数据：Charles Duhigg，The Power of Habit，en-US；正文 `.htm`，不是仅 `.xhtml`。原书无 SMIL。

- M4B 时长：37,621.959977 秒，约 10 小时 27 分钟。
- M4B 章节标记：39 个。开头有约 16.908 秒 introduction。
- 本次只取 Prologue：源音频 16.908–1,407.441 秒，长度 1,390.533 秒。
- 样本音频分为三个约 600、600、190.5 秒片段。
- 三段均匹配到 `OEBPS/Duhi_9780679603856_epub_prl_r1.htm`。
- 生成 1 个 SMIL、430 个文字位置与音频区间映射、约 14 MB 样本 EPUB。
- 修复后工具 10 项检查通过；独立检查与源文件 SHA-256 复核通过。
- 英文 tiny.en 转写阶段日志耗时约 19.4 秒；不是首次安装耗时，也不是全书耗时或准确率指标。
- 当前 `run-result.json` 的约 0.82 秒是最终复用转写后的增量重跑，不是端到端首跑时间。

原文件 SHA-256：

```text
M4B   40cb0bc15787bfd8b9a3b90c53b791f1deb9bb79017458dc27a207aba3f6b793
EPUB  7e4ff971d08ab82f447bbd1dc77a9ed9c5cce6174b271555cf620640e8f3a85d
```

不能据此声称：全书已完成、误差达到毫秒级、iPhone 已实机验收、原版上游工具无需修复即可处理全库、CTC 强制对齐已经验证。

## 7. 私有产物在哪里

以下均在同一台 Mac，本地 Git 忽略目录；其他电脑仅 clone 仓库不会得到这些文件：

```text
/Users/jerryyi/digital-garden/private/audiobook-validation/power-of-habit/
  README.md
  input-report.json                 输入、源偏移、源文件 SHA-256
  run-result.json                   实际模型、方法、局部修复
  independent-validation.json      独立结构检查与源文件未变证明
  browser-review.json              浏览器功能测试，不是人耳验收
  prologue.m4a                     提取的序言，仅样本
  prepare_sample.py                准备样本，当前路径写死
  run_validation.py                临时验证入口，不是生产 CLI
  build_validation_preview.py      解包、检查 SMIL、导出试听时间轴
  serve_preview.py                 127.0.0.1:8768，支持 HTTP Range
  upstream-local-fixes.patch       对原始上游提交的三文件修复补丁
  tool-source/                    修正后的制作工具源码副本
  runtime-snapshot/
    requirements-macos-arm64.txt  实测环境 62 个依赖的确切版本
    models/tiny.en/config.json
    models/tiny.en/weights.npz    已完成下载的英文识别模型，约 71 MB
    nltk_data/tokenizers/punkt_tab/english/
  baseline/                       首轮有缺口的样书、SMIL 与报告，保留用于回归
  work/
    state.json
    matched_list.json
    segmented.epub3
    validation.json
    logs/pipeline.log
    run/                         三段音频、带词时间戳的 JSON 等
  generated/
    The Power of Habit - Charles Duhigg.media-overlay.epub
  preview/
    index.html
    timeline.json
    book/                        从生成 EPUB 解出的正文与媒体，仅本地试听
```

不要把本目录复制到 `html/`、`content/` 或 `public/`；不要强制加入 Git。它含整本正文、音频与转写。实现代码可以另行整理到正常源码目录，测试使用短小的自制/合成输入，不把这本版权书作为公开测试夹具。

原临时环境：

```text
/private/tmp/garden-readalong.bEtqci/venv/bin/python
/private/tmp/garden-readalong.bEtqci/source/
/private/tmp/garden-readalong.bEtqci/models/tiny.en/
```

现在 `run_validation.py` 仍使用上述临时路径。为避免被系统清理后丢失关键材料，源码、模型、英文分句数据和依赖清单已经另存到上述持久私有目录。它尚未变成无需调整的正式安装器。不要把临时 venv 整目录搬成跨平台环境；根据锁定依赖重建并验证。

持久模型校验值：

```text
config.json  452e616242261333a661bc86db762b3720d6cc7e2eccd3d8e19a631871c26dd9
weights.npz  4627203f0807d6496dda0d200e893b04ff24c98e73aa51c485c06203a0330b17
```

## 8. 复用工具、实际方法和修复内容

上游：<https://github.com/seedds/epub-media-overlay>。

固定来源提交：`5fed058fd01e7ea3d6099fa73ecb448baf435eee`。优先对照 `tool-source/` 和 `upstream-local-fixes.patch`，不要重新拉最新版覆盖局部修复。检查上游许可证和分发方式后，再决定 fork/vendor 的公开发布策略；本次仅保存在私有验证目录，没有发布源码副本。

本次复用其章节识别、正文匹配、分句/ID 插入、SMIL 生成、EPUB OPF 重写、打包、检查等能力。ASR 为 Apple Silicon MLX，模型 `mlx-community/whisper-tiny.en-mlx`。

时间戳来源是 `mlx-whisperx` 包内 vendored MLX Whisper 的原生 cross-attention/DTW 词时间戳，`word_timestamps=True`。没有使用外置 wav2vec2 CTC 模型；此前 CTC 下载尝试已停止。不要把两种方法混写成同一个已验证后端。

### 8.1 环境与兼容性修复

1. 上游 requirements 实际漏了 `tinycss2`，已补装。
2. NLTK 使用现代 `punkt_tab`；英语分句验证过 `Mr.` 不误切句。已保存英文 tokenizer 数据。
3. 验证副本的 `_get_nltk_cache_dir()` 曾改为临时路径，正式版本必须使用可配置持久缓存。
4. `generate_epub_overlay.atomic_copy()` 用 `copyfile` 替代 `copy2`，避免外置卷 flags 导致目标 `chflags` 失败。保持字节复制与原子替换，不复制源 flags。

### 8.2 工作副本过早失效

上游在 split/transcribe 完成后的 downstream invalidation 中，会清理 segment 阶段的 working EPUB；match 阶段还要读取该文件，首跑因此失败。

局部修复：`run_match_stage()` 检查 working EPUB 是否存在，不存在时从 run 内未修改的源副本重新 `preprocess()`，再匹配。正式整理时应明确每阶段输入、输出及缓存失效边界，避免恢复旧的已加 ID/已合并音频的文件作为新输入。

### 8.3 同段文字跨音频候选错误

原 `pipeline_core.resolve_segment_clips()` 偏向整个章节的 dominant audio。序言跨三个同长度片段，某些重复短语被较早片段末尾的弱匹配抢走。

真实回归案例：

- 目标：`cseg_oebps_duhi_9780679603856_epub_prl_r1-segment293`。
- 原结果错误指向 `000.m4a` 的 599.84–600.039 秒。
- 正确词证据位于 `001.m4a` 的 307.16–308.98 秒。
- 原版因此在 `001.m4a` 中漏覆盖 1.82 秒，不是单纯静音。
- 局部修复按每个候选直接匹配的 token 数优先，再以有效时长破同分；保留原算法其他步骤。

这是已在一组样本验证的修复，不是所有重复句/错版音频的通用正确性证明。正式版本要测试跨文件接缝、重复句、插播、短章节和同一章节跨多个音频；不能通过扩大自动补齐、延长前一句或降低告警阈值隐藏错配。

## 9. “以后运行一个脚本”应交付成什么

结论：同版本、已明确配对的英文 EPUB 与音频，可以把处理、映射、打包、验证、缓存和报告封装为一个命令。首次仍需环境准备和模型下载；错版、删节版或配对含糊的书应输出待审核结果，不假装全部自动完成。

下面是建议 CLI 合同，**目前不存在 `scripts/readalong`，需要 Claude Code 实现**：

```bash
# 仅扫描与预检，不运行模型、不写源目录
./scripts/readalong scan --root "/Volumes/750/Music/有声书" --language en --dry-run

# 单本，可恢复；bootstrap 与对齐统一从该入口进入
./scripts/readalong align \
  --book-dir "/Volumes/750/Music/有声书/心智成长/The Power of Habit - Charles Duhigg" \
  --language en --timing whisper-word --resume

# 已审定配对之后递归处理；默认一个推理任务，失败不拖垮全部书
./scripts/readalong batch --root "/Volumes/750/Music/有声书" --language en --resume

# 只检查已有产物，不重新转写
./scripts/readalong validate --book-id "<book-id>"

# 显式列出发布内容后，再安装到受鉴权的 NUC 目录
./scripts/readalong install --book-id "<book-id>" --target nuc --dry-run
```

实现可以是 shell 启动器＋Python CLI，内部采用 argparse/Typer 均可；接口需稳定。把路径、缓存、模型、镜像、后端、采样范围写入配置，不能保留用户目录或本次书名的硬编码。新源码建议放 `tools/readalong/`，启动器放 `scripts/`；不要把音频处理混进前端 `npm run build`。

### 9.1 自动化必须具备的行为

- 支持一 EPUB＋一 M4B，也支持一 EPUB＋有序多 MP3/M4A；忽略 `.DS_Store`、`._*` 和已生成目录。
- AList 目录是逻辑路径，不是 NUC 真实文件系统路径；Mac 的 `/Volumes/750/...` 也不能照抄为 NUC 路径。通过挂载/配置确认本地根目录到 AList 的映射。
- 多 EPUB、多录音版本、音频顺序不明时生成 pairing 清单，允许人工指定；不按第一个文件盲配。
- 使用 EPUB spine 顺序，不用压缩包条目排序；支持 `.htm/.html/.xhtml`，以及缺少原句 ID 的 EPUB。
- 保留原 EPUB 和音频，结果放独立输出目录；不默认覆盖源书或重编码全库。
- 明确书/音频/映射身份，记录原文件大小与哈希，以及程序、模型、tokenizer、timing engine 和 schema 版本。
- 断点恢复缓存按上述身份校验；`whisper-word` 与 CTC 的结果不能因为 backend 都写 mlx 而被错用。
- 单本/阶段/片段分别记录耗时、状态和失败原因。重跑不重复 ASR，不盲删无关文件。
- 首次安装后可离线复用本地模型和分句数据；网络镜像是配置，不全局改系统网络设置。
- Mac Apple Silicon 与 Linux CPU/CUDA 后端隔离依赖。Mac 的 `mlx-metal` 锁文件不能拿到 NUC 直接安装。
- 控制推理并发、内存与剩余空间，支持停止后恢复。默认不对整库并行加载多个模型。
- 返回有意义的退出状态，例如成功、待审核、硬失败；批处理输出成功/跳过/失败/待配对计数，不只打印一行 Done。
- 不把访问令牌、密码或签名 URL写入发布清单；不要上传用户书籍到在线转写服务。

## 10. 标准 EPUB 与 PWA 流式数据如何衔接

以 EPUB 3 Media Overlays 的 SMIL＋正文定位为标准输出，JSON 是为当前 PWA 提供的派生查询索引，不再维护一套互相独立、会漂移的时间轴。

制作完整 EPUB 时，必须同时有：正文 ID、SMIL、OPF manifest 与 `media-overlay` 关联、音频项、时长元数据、需要的样式。仅在原 EPUB 旁放一个 `.smil` 不会让现有 PWA 自动支持跟读。

对于 iPhone，含整本音频的 EPUB 可能很大。不要把唯一在线方案做成每次都下载并解压数百 MB EPUB。建议产物同时支持：

1. 便于其他阅读器使用的标准音文 EPUB（可选导出）。
2. 放在 NUC 受鉴权目录中的阅读资源与 JSON 索引，音频仍使用 AList Range 流式播放。

建议目录和接口（均为待实现设计，不是当前生产格式）：

```text
<generated-output>/<book-id>/
  readalong.manifest.json
  timeline.json
  text/                    保留原书样式和必要资源，禁用主动脚本
  validation.json
  source-manifest.json
  book.readalong.epub       可选标准导出
```

建议 JSON 核心数据：

```json
{
  "schemaVersion": 1,
  "bookId": "<stable-book-id>",
  "language": "en",
  "sourceEpubSha256": "<sha256>",
  "timing": { "engine": "whisper-word", "model": "<pinned-model>" },
  "audioSources": [
    { "id": "original-m4b", "alistPath": "/750HD/有声书/<book>/<audio>.m4b", "sha256": "<sha256>" }
  ],
  "segments": [
    {
      "audioSourceId": "original-m4b",
      "start": 924.068,
      "end": 925.888,
      "document": "text/OEBPS/<chapter>.htm",
      "fragment": "<verified-fragment-id>",
      "reviewStatus": "unreviewed"
    }
  ]
}
```

示例数字用于说明源音频的时间坐标，不能照抄为生产测量值。正式输出要明确 `start/end` 是当前音频文件内的绝对秒数，不能混入章节局部秒数。

本样本从原 M4B 的 16.908 秒开始，随后又分片。若 PWA 播放原 M4B，必须把样本偏移和分片偏移转换回原时间。分片实际时长、AAC priming 和 seek 方式会影响边界，不能只以 `片号 × 600` 猜测所有书的时间。保存并验证源坐标转换表，或播放被明确映射的分片本身；不要混用两种方案。

EPUB 正文位置以 href＋真实 fragment ID/CFI 表示，不存随字号变化的屏幕页码。中文/空格/特殊字符路径要逐段正确编码。路径引用解析与规范化后应保持在书籍资源范围内；既防 ZIP 路径越界，也不要误拒绝 EPUB 内合法的相对引用。

## 11. 整个 PWA 的后续任务顺序

每阶段交付可测试结果，避免先大改所有界面再接真实媒体。

### P0：固化现有能力与可复现环境

- 保持现有列表、播放、续播、账号与内外网路由工作。
- 整理职责模块与错误状态，补必要行为测试；不为了拆模块改变功能。
- 清除临时路径依赖，建立持久模型/资源缓存，保存上游固定版本与修复来源。
- 将本样书整理为本机私有回归输入；公开测试用自制小 EPUB/音频/时间轴。
- 先复现 430 段和 10 项检查，再做后续开发。

完成条件：新建隔离环境后能从持久快照重现序言；不依赖本次临时 venv；现有音频 PWA 构建和关键交互无回归。

### P1：音频播放器、书籍和进度完善

- 建立书、音频文件、章节和目录的清晰数据模型。多文件一本书显示总进度，最近播放能辨识书名和章节，避免只有“第01节”。
- 解析 M4B 内嵌章节的工作放到本地/服务器预处理，前端轻量读取元数据并 seek 原文件；不要求手机下载完整 M4B 才能列章节。
- 正确处理结束/完成状态、再次从头听、切书前保存、手动 seek、恢复过早写零、快速连点切书、待完成异步请求污染新书。
- 遇签名失效、断网或 401 时保留进度，给出重试/重登录路径；避免无限重试和恢复时重置进度。
- 播放按钮状态以 audio 事件和 play Promise 为准，处理 Safari 用户手势要求；Media Session 不支持的 action 降级。
- 在已载入目录中搜索时明确标识范围。全库索引按需刷新，有缓存/取消/分页，不能每次击键递归扫描整块磁盘。
- 改善列表的加载、空目录、错误、重试、路径导航、无障碍焦点、长文件名、移动触摸区域和底部安全区。
- 进度 schema 升级有迁移和导出/导入兼容性，不用清空用户数据库来解决版本问题。

完成条件：真实书与多文件夹具覆盖上述路径，进度能连续恢复，列表可用，播放器不出现多个 audio 同时播放。

### P2：正式单本英文映射工具

- 实现第 9 节的单本 CLI、配置、预检、缓存、报告和独立验证。
- 固定现有通过的词时间戳路线为 baseline，允许选择更大英文模型或 CTC 对比；不同路线分别缓存和报告。
- 处理 The Power of Habit 全书，而不是把序言改名当全书。覆盖其全部实际朗读的章节，书中附录/注释若音频未读，应明确标记，不伪造映射。
- 在全书中抽查开始/中间/结尾、章节边界、分片边界、重复句；检查跳回旧音频、错版和未朗读文字。

完成条件：一次命令得到可验证的全书产物，二次运行跳过兼容的昂贵阶段；中断可恢复，失败退出码与报告准确。人耳验收状态与结构通过状态分别保存。

### P3：PWA 应用内 EPUB 阅读和跟读

- 复用合适的 EPUB 阅读引擎；先验证固定版本能满足本项目的 iframe/CFI、滚动、样式与资源加载需求。不要笼统假设任何 Readium/epub.js 版本都自动完整支持 SMIL。
- 列表区分音频、电子书和已验证的跟读产物。音频的 AUDIO 正则目前会过滤电子书；新增文件类型后不能把 EPUB 当音轨塞进章节队列。
- 使用同一个 audio 与播放器状态，在“纯听书”和“边听边读”间切换，不暂停或重建音频会话。
- 按 audio.currentTime 二分查找映射；timeupdate/seeked 驱动位置变化。只在高亮段变化或段落离开视野时滚动，不每 200ms 重复 smooth scroll。
- 手动滚动时暂停跟随，显示“回到朗读位置”；保留阅读进度与音频进度，避免手动翻书立刻触发音频跳转。
- 字号、布局和方向改变后依旧定位同一段；点读跳转音频如实现，应区分用户点击和自动跟随，避免事件循环。
- 无映射/低质量区段保持音频播放，提示定位不可用，不强跳任意位置；不把不同版本 EPUB 套上同一时间轴。
- Cloudflare 端经 HTTPS AList 签名读取书籍、资源和索引；处理跨域、资源类型和签名刷新。不要直接嵌入 NUC 跨域 iframe 后假设父页面可以任意访问其 DOM。
- 禁止电子书主动脚本访问用户会话；阅读器 sandbox/CSP/资源范围策略明确，保留正文与字体图片排版所需能力。

完成条件：英文样书在 Cloudflare 和 NUC 下都可边听边读；seek、倍速、手动浏览、回到朗读、刷新恢复均正确。iPhone Safari 与主屏幕模式实测通过后才声明支持。

### P4：递归批处理与数据安装

- 实现 scan/dry-run、显式配对清单、可取消队列、逐书恢复、错误隔离和汇总报告。
- 无源变化时跳过；源书/音频/方法/模型发生变化时只失效相关阶段，不能复用旧映射。
- 跳过 generated/work/cache/private snapshot 等输出树，不递归处理自己生成的 EPUB。
- 不限制为“每目录一文件”的隐式规则；目录层级是类别/书/音轨时要能通过配置表达。
- 确认 NUC 实际存储挂载后，将通过的产物显式安装到 AList 可读且保留鉴权的目录；不要拷贝模型和私有日志到静态公开站。
- 安装与前端部署分离，有计划预览、增量同步、备份和失败恢复；避免半写产物被前端识别为已完成。

完成条件：至少验证多个自制/允许测试的书籍案例，包括单 M4B、多 MP3、缺 EPUB、多版本、源变化、中断和失败；用户可以用一个 batch 命令处理已明确配对的英文库。

### P5：iPhone、PWA 与部署收尾

- 真机测试锁屏/耳机控制、Safari/主屏幕、切后台/回前台、来电中断、网络切换、重新进入与播放结束。
- 系统后台限制按实测报告，不承诺 WebKit 在所有版本下自动跨文件连播。章节内 seek 与跨文件播放分别验证。
- Service Worker 范围只在本应用；不拦截 AList API、Range 或大媒体，不在播放中强制刷新。可提示更新并在用户接受/安全时应用。
- 更新状态、存储失败和离线状态可见；“离线界面”和“已下载可离线音频”区分。
- 若做离线下载，另行定义容量、Range 响应、清理和删除确认；不作为本轮英文跟读必交付功能。
- Cloudflare 与 NUC 分别部署、验证、记录版本与回滚点；不以本机预览证明线上成功。

完成条件：发布记录列明两个环境的版本、测试证据、未完成项；用户已有进度和账号保持兼容。

## 12. 必须保留的验证与回归案例

### 12.1 制作端

- 合法 EPUB：mimetype、container、OPF、spine、nav、资源与命名空间；需要时使用 EPUBCheck，但它也不验证听感对齐。
- 每条 SMIL text fragment 存在，音频存在，clipBegin/clipEnd 合法且在时长内。
- 音频播放顺序不能倒退，不能重复使用相同片段造成复读；检查跨分片候选选择。
- 缺口告警有定位信息。分清自然停顿、未读段落和实际丢词；不只降低阈值让报告变绿。
- 检查应明确未匹配/已覆盖/待审核，结构检查不能当成识别准确率。
- 源文件前后哈希一致；打包后与被验证文件哈希一致，不能复用另一个产物的旧验证报告。
- 回归本样本 segment293；要同时验证后续句、前一片段尾部和音频顺序，不能仅硬编码纠正这句话。
- 改变输入、模型或 timing 后失效旧缓存；同配置重跑应复用转写。检查原先 working EPUB 被清理的首跑故障。

### 12.2 前端与真实媒体

- 真实 Range 请求得到 206、Content-Range 和请求的字节长度；模拟数据不能替代实流测试。
- 浏览器 play Promise、seek、恢复、完成状态和切书竞态得到行为验证。
- 对齐时间在原 M4B 与切片之间转换正确，不能存在固定整体偏移。
- 原音频 23 分钟序言回归：片段 1 的 120 秒对应 segment42；片段 2 的 307.8 秒对应 segment293。ID 变化时应重建样本并更新证据，不能改测试来绕过结果变化。
- 1.5 倍速音频推进与高亮推进一致；手动关闭跟随后不抢滚动，重新开启可回到当前段。
- 中文/特殊字符路径、超长文件名、空库、失效登录、过期签名、权限不足、断网都有可理解的界面。
- 手机宽度下无横向溢出，底部控制不遮住阅读文字和最后一行。
- 无鉴权跨站访问仍遵守 Cloudflare Access/AList 策略，不为了让演示通过而开放游客或硬编码管理令牌。

## 13. 当前可用命令和注意事项

这些命令已经存在：

```bash
cd /Users/jerryyi/digital-garden
node --test studio/audiobooks/config.test.mjs
npm run build
npm run deploy:audiobooks
```

仅在临时环境仍存在时，可重跑旧的验证入口：

```bash
cd /Users/jerryyi/digital-garden
/private/tmp/garden-readalong.bEtqci/venv/bin/python private/audiobook-validation/power-of-habit/run_validation.py
python3 private/audiobook-validation/power-of-habit/build_validation_preview.py
python3 private/audiobook-validation/power-of-habit/serve_preview.py
```

第三个命令启动 8768 端口；先检查是否已有本次服务，不为释放端口终止用户无关进程。现有 8766 是音频 PWA 开发预览，8768 是独立样书验证，两者不同。

网络经验：本机一度直连 GitHub/PyPI/Hugging Face 超时；依赖通过 PyPI 国内镜像获得，模型走可用公开端点下载；模型和 tokenizer 已保存。不要假设用户每次都能联网、需要重复下载，也不要未经说明全局改代理或换后端。复现优先使用本地快照，所用镜像与依赖来源记录在配置/日志。

## 14. 交付清单与最终报告要求

Claude Code 完成后应交付：

1. 可从干净环境安装、从持久缓存运行的单一 CLI 入口及文档；第 9 节示例落实为真实可执行命令。
2. 可审计的上游版本、适配层、局部修复与必要回归测试，不依赖散落的 monkey patch 和临时路径。
3. 单本完整处理、断点恢复、批处理配对/队列、结构与质量报告。
4. The Power of Habit 全书结果和试听证据；明确人工审核尚未完成的区段，不以序言报告代替。
5. 完善的独立有声书 PWA：书籍/章节、列表/搜索、稳定播放与进度、应用内英文 EPUB 跟读。
6. 内外网实际部署与验证记录，iPhone 实机结果，回滚方式和已知限制。
7. 更新 `docs/audiobooks-deployment.md` 及本交接状态；必要时同步 Rosemary Garden 的 Obsidian 项目文档。

最终说明必须分别回答：映射生成是否完成、结构检查是否通过、人工听感是否验收、PWA 是否接入、Cloudflare/NUC 是否部署、iPhone 是否实测。不得用其中一项替代其余各项。

## 15. 可直接发给 Claude Code 的启动任务

```text
请接手 /Users/jerryyi/digital-garden 的独立有声书 PWA 与英文 EPUB 音文同步开发。
先完整阅读 docs/audiobooks-claude-code-handoff.md，再阅读其中列出的源码、部署文档和私有样书报告。
目标同时包括：
1. 把现有英文样书管线整理成可复现的一键单本/批处理工具；
2. 完善现有有声书 PWA 的播放、书籍/章节、列表/搜索、进度和 iPhone 体验；
3. 集成应用内英文 EPUB 阅读、SMIL 跟读、高亮与滚动；
4. 分别验证 Cloudflare 与 NUC 的部署。
不要从零重写 ASR 或 EPUB 渲染引擎。现阶段只要求英文跟读，PDF/MOBI 和跨设备同步暂不阻塞主线。
从 P0 开始落实，保护原音频/EPUB、用户进度和已有改动。保留私有产物，不上传书籍、转写、模型或凭证。
已有序言样书验证通过，但只有约 23 分钟，不是全书；上游有已修复缺陷，请保留回归案例。
按文档阶段交付可运行结果并持续推进，在实际需要用户选择或权限时明确指出阻塞。
```

## 16. 标准与上游参考

- EPUB 3.3 Media Overlays：<https://www.w3.org/TR/epub-33/#sec-media-overlays>
- EPUB CFI：<https://w3c.github.io/epub-specs/epub33/epubcfi/>
- 本次复用的制作工具：<https://github.com/seedds/epub-media-overlay>
- MLX 适配实际使用包版本：见持久依赖清单，不推定所有新版兼容。
- 备选完整平台 Storyteller：<https://storyteller-platform.dev/docs/welcome/>。若选择它替代/补充自有 PWA，应先向用户说明新增服务、账号和部署变化，不把替换产品当作默认重构。

本文记录截至交接时的状态。后续开发者应把新增验证和部署事实更新到文档，而不是把未来计划原样写成已完成结果。
