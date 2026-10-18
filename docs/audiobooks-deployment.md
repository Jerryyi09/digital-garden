# 花园听书：双环境部署与运维

日期：2026-10-18。源码：`studio/audiobooks/`。入口由 `studio/downloads-index.json` 生成，独立应用链接使用 `data-router-ignore`，避免 Quartz SPA 接管。

## ADR：沿用静态站和 AList 鉴权

Cloudflare 只托管界面，不存音频、不代理音频、不存 AList 密钥。NUC 上 AList 继续提供目录、登录、签名下载与 Range。当前服务器游客访问已禁用，客户端使用现有 AList 用户登录；不更改 AList 账号和访问权限。暂不新增网关和数据库服务，避免扩大维护范围。播放进度使用浏览器 IndexedDB，账号分隔；不同站点通过 JSON 导入/导出迁移。未来需要多设备自动同步时再增加受鉴权的服务端进度接口。

| 环境 | 入口 | API 与媒体 |
| --- | --- | --- |
| Cloudflare | `https://notes.melyi.uk/studio/audiobooks/` | `https://melyi.uk/alist` |
| NUC 外网 HTTPS | `https://melyi.uk/studio/audiobooks/` | 同域 `/alist` |
| NUC 内网 HTTP | `http://10.0.0.85:8088/studio/audiobooks/` | 同域 `/alist` |
| NUC 内网 HTTPS | `https://melyi.uk/studio/audiobooks/`（需内网 DNS/回流） | 同域 `/alist` |

2026-10-18 实测：根域名 443 可访问 NUC Nginx；旧的外网 `:8089` 不可达；`notes.melyi.uk` 受 Cloudflare Access 保护。Docker 端口仍为 `8088:80`、`8089:443`。不要根据容器端口推断外网端口。内网 HTTP 可播放，但不能安装 Service Worker；完整 PWA 请用可信 HTTPS，不能用自签名证书或 IP 证书错误页面替代。

## 构建与发布

`npm run build` 的最后一步将 `studio/audiobooks/` 复制到 `public/studio/audiobooks/`，不手工维护输出目录。图标 PNG 已随源码提交，构建无需额外图形工具。

Cloudflare 按现有 GitHub `v5` 分支自动构建发布，不改变 Workers/Access 配置。`wrangler.jsonc` 继续使用纯静态 assets。NUC 同步构建后的静态文件到 `/home/hp/docker-compose/nginx/html/`，其中 Studio 首页是 `/home/hp/docker-compose/nginx/html/studio/index.html`。

本次功能可单独运行 `npm run deploy:audiobooks`：先构建，再通过 SSH/SCP 上传到临时目录，由部署脚本备份 Studio 和 Nginx 配置，仅更新 Studio 与播放器，补上 HTTP AList 代理、测试 Nginx 后 reload。失败恢复备份并保留失败产物。不会运行同步所有 Obsidian 笔记的 `publish-notes`。该命令不推送 Git；Cloudflare 仍通过 Git 提交发布。

NUC HTTP server 原本没有 `/alist` 代理，内网版需补上与 HTTPS 相同的代理块，并在两个代理块中关闭 `proxy_buffering`。现有 Range/If-Range 透传应保留。AList 已返回跨域允许头，Cloudflare 前端请求时使用 `credentials: omit`，令牌放在 Authorization，不依赖跨站 Cookie。

```nginx
location /alist {
  proxy_pass http://alist:5244;
  proxy_set_header Host $http_host;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header Range $http_range;
  proxy_set_header If-Range $http_if_range;
  proxy_buffering off;
  proxy_redirect / /alist/;
  proxy_redirect /alist:5244/ /alist/;
}
```

修改 Nginx 前备份配置和 Studio，先 `docker exec nginx nginx -t`，成功后 reload。若检查失败，恢复原配置再检查，不中断正在运行的服务。

## 登录和数据

首次打开使用现有 AList 账号、密码、可选 OTP。密码只在登录请求中通过 HTTPS（或用户主动选择的内网 HTTP）发送，不写入存储。默认令牌在 sessionStorage；主动勾选后才记入 localStorage。退出清理令牌并停止播放。客户端固定书库 `/750HD/有声书`，真正权限仍由 AList 账号决定；建议使用只读且根目录限定到书库的家庭账号。

本版本 AList v3.60.0 API 使用 `/alist/api/auth/login`、`/alist/api/fs/list` 和 `/alist/api/fs/get`。Client-Id 保持稳定；Device-Key 随后续请求发送。列表分页读取。音频使用 `fs/get` 返回的 sign 构建 `/alist/d/<编码后的完整路径>?sign=...`，不直接信任可能指向内网或 Docker 的 raw_url。签名不写入收听历史。

IndexedDB 保存路径、文件大小、修改时间、秒数、时长、完成状态和更新时间。文件更换后产生新 ID。播放每约 3 秒存储；暂停、隐藏、pagehide 也保存，localStorage 同步日志补偿退出时异步写入。恢复回退 3 秒。记录只在同浏览器、同域名、同账号下自动共享；Safari 与主屏幕 PWA 的存储隔离由 iOS 决定，不承诺自动互通。

## PWA 与播放限制

Service Worker scope 仅 `/studio/audiobooks/`，只缓存明确列出的界面资源；不拦截 AList API、签名 URL、Range 或其他花园页面。离线可打开界面和历史，但不能离线收听未下载音频。更新不强制 reload 或跳过等待，避免中断播放。

使用持续复用的 HTML audio、原生控制条与 Media Session。异步取签名后 Safari 可能要求再点一次播放，界面会明确提示。支持 MP3/M4A/M4B 容器，但能否解码取决于内部编码，不自动转码。M4B 内嵌章节尚未解析；文件夹中的音频文件按自然文件名顺序作为章节。搜索作用于当前目录或最近播放，不递归扫描整个磁盘。

下一节预取签名而不预下载整本音频。普通 ended 连播在某些 iOS 锁屏版本可能被系统阻止；本版本不采用静音循环等规避手段，需要实机验收，不承诺锁屏跨文件无缝连播。浏览器后台定时器会被节流，因此不提供不可靠的后台睡眠定时器。

## 验证清单

1. 构建成功，两个 Studio 入口均带 `data-router-ignore`，PWA 文件在正确子目录。
2. 内外网 API 预检和游客禁用状态保持正常；HTTPS 不向内网 HTTP 发送凭证。
3. 用现有账号登录后，分类、分页、中文/特殊字符文件名、自然排序正确。
4. 对一个真实音频发 `Range: bytes=0-1023`，检查 206、Content-Range 和返回体长度 1024；播放器拖动到远处后可继续播放。
5. iPhone Safari 和添加到主屏幕分别验证：播放、暂停、倍速、锁屏、耳机、切网络、关页后续播、文件结束连播。
6. 退出登录后音频停止；进度备份不包含密码、令牌和签名链接。
7. Cloudflare Access 未认证访问应仍跳登录；它的存在不能当成播放器部署失败，也不能当成已验证部署成功。

## 回滚

本次部署对远端 Studio 和 Nginx 配置创建带时间戳的备份。恢复对应备份、`nginx -t` 后 reload；移除入口卡片即可停止新增访问。PWA 和 IndexedDB 都使用独立路径/名称。不要删除用户进度来回滚代码。Cloudflare 通过回滚本次 Git 提交或控制台选择上一部署回滚。
